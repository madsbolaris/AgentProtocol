# Advanced Patterns

This guide covers advanced patterns for building sophisticated agent applications. These patterns are designed for production use cases requiring reliability, scalability, and complex workflows.

## Overview

Advanced patterns in the Agent Protocol enable:

- **Ephemeral Runs**: Stateless execution with automatic cleanup
- **Background Runs**: Async workflows with parallel execution
- **Stream Reconnection**: Network-resilient streaming with multiple observers
- **Thread Management**: Conversation branching and A/B testing
- **Hooks**: Event-driven interception and custom business logic
- **Auto-Response**: Proactive agent participation in conversations
- **Remote Endpoints**: Delegate logic to your custom services

---

## Ephemeral Runs

### When to Use

Use ephemeral runs for stateless operations where you don't need conversation history:

- **One-shot queries**: Simple questions with single responses
- **Data extraction**: Parse structured data from text
- **CLI tools**: Command-line applications without state
- **Stateless APIs**: RESTful services without session management
- **Chatbots**: Simple interactions without context retention

### Why Ephemeral Runs?

| Benefit | Description |
|---------|-------------|
| **No thread management** | Automatic cleanup eliminates storage overhead |
| **Simpler API** | No thread creation or lifecycle management |
| **Resource efficient** | No orphaned threads or memory leaks |
| **Perfect for scale** | Ideal for high-volume stateless operations |

### Pattern 1: Blocking Wait

Use `POST /runs/wait` for simple queries that need immediate results.

```python
def one_shot_query(question: str) -> str:
    """Execute one-shot query with automatic cleanup"""
    response = requests.post(
        f"{API_BASE}/runs/wait",
        headers=headers,
        json={
            "agentId": "agent-123",
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": question}]
            }]
            # Default: threadCleanup="keep" (thread persists)
        }
    )

    result = response.json()
    # threadId is null - thread was auto-deleted
    return result['output'][0]['contents'][0]['text']

# Example usage
answer = one_shot_query("What's 25 * 17?")
print(f"Answer: {answer}")  # Output: Answer: 425

# Extract structured data
result = one_shot_query("Extract the email from: Contact John at john@example.com")
print(result)  # Output: john@example.com
```

### Pattern 2: Streaming

Use `POST /runs/stream` for real-time output in ephemeral contexts.

```python
import sseclient  # pip install sseclient-py

def one_shot_query_streaming(question: str):
    """Execute one-shot query with real-time streaming"""
    response = requests.post(
        f"{API_BASE}/runs/stream",
        headers=headers,
        json={
            "agentId": "agent-123",
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": question}]
            }]
        },
        stream=True
    )

    client = sseclient.SSEClient(response)
    for event in client.events():
        data = json.loads(event.data)

        if event.event == 'message.delta':
            # Stream text chunks
            print(data['delta'], end='', flush=True)

        elif event.event == 'run.completed':
            # Final state
            print(f"\n\nCompleted in {data['usage']['totalTokens']} tokens")
            return data

# Example usage - watch the response stream in real-time
print("Question: Tell me a story")
one_shot_query_streaming("Tell me a short story about a robot")
```

**Output:**
```text
Question: Tell me a short story about a robot
Once upon a time, there was a little robot named Bolt who dreamed of exploring...

Completed in 245 tokens
```

!!! tip "Use Cases for Ephemeral Runs"
    - **CLI tools**: No persistent state needed
    - **Chatbots**: Simple Q&A without memory
    - **Data extraction**: Parse emails, addresses, structured data
    - **API gateways**: Stateless microservices

---

## Background Runs

### When to Use

Use background runs for async workflows where you need:

- **Long-running tasks**: Analysis, data processing, report generation
- **Parallel execution**: Run multiple agents simultaneously
- **Webhook notifications**: Get notified when operations complete
- **Non-blocking workflows**: Start task, continue other work, check later

### Why Background Runs?

| Benefit | Description |
|---------|-------------|
| **Non-blocking** | Start run immediately, wait when ready |
| **Parallel processing** | Execute multiple runs concurrently |
| **Webhook support** | Get notified on completion |
| **Resource efficient** | Don't block client while waiting |

### Pattern 1: Background with Wait

Use `POST /runs` + `GET /runs/{id}/wait` for async workflows.

```python
def background_run_with_wait(agent_id: str, input_messages: list) -> dict:
    """Start run in background, wait for completion later"""

    # Step 1: Start run (returns immediately)
    create_response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agentId": agent_id,
            "input": input_messages,
            "webhook": "https://myapp.com/webhooks/run-completed"  # Optional
        }
    )

    run_id = create_response.json()['runId']
    print(f"✓ Run {run_id} started in background")

    # Step 2: Do other work while run executes
    print("→ Doing other work while waiting...")
    time.sleep(1)  # Simulate other operations

    # Step 3: Wait for completion (blocks until done)
    print(f"→ Waiting for run {run_id} to complete...")
    wait_response = requests.get(
        f"{API_BASE}/runs/{run_id}/wait",
        headers=headers
    )

    result = wait_response.json()
    print(f"✓ Run completed: {result['status']}")

    return result

# Example usage - long-running analysis
result = background_run_with_wait(
    agent_id="agent-456",
    input_messages=[{
        "role": "user",
        "contents": [{
            "kind": "text",
            "text": "Analyze this large dataset and provide insights: [dataset...]"
        }]
    }]
)

print(f"\nAnalysis: {result['output'][0]['contents'][0]['text']}")
print(f"Tokens used: {result['usage']['totalTokens']}")
```

**Output:**
```text
✓ Run run-abc123 started in background
→ Doing other work while waiting...
→ Waiting for run run-abc123 to complete...
✓ Run completed: completed

Analysis: Based on the dataset analysis, key insights are...
Tokens used: 5432
```

### Pattern 2: Parallel Execution

Run multiple analyses concurrently for maximum throughput.

```python
from concurrent.futures import ThreadPoolExecutor

def parallel_analysis(questions: list[str]) -> list[dict]:
    """Run multiple analyses in parallel"""

    # Start all runs
    run_ids = []
    for q in questions:
        response = requests.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "agentId": "agent-123",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": q}]}]
            }
        )
        run_ids.append(response.json()['runId'])

    print(f"✓ Started {len(run_ids)} runs in parallel")

    # Wait for all completions
    def wait_for_run(run_id: str) -> dict:
        response = requests.get(f"{API_BASE}/runs/{run_id}/wait", headers=headers)
        return response.json()

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(wait_for_run, run_ids))

    print(f"✓ All {len(results)} runs completed")
    return results

# Example usage
questions = [
    "Summarize Q1 earnings",
    "Analyze Q2 trends",
    "Forecast Q3 revenue"
]

results = parallel_analysis(questions)
for i, result in enumerate(results):
    print(f"\nQuestion {i+1}: {questions[i]}")
    print(f"Answer: {result['output'][0]['contents'][0]['text'][:100]}...")
```

!!! warning "Rate Limits"
    When running multiple parallel requests, be mindful of API rate limits. Implement exponential backoff and respect `Retry-After` headers.

!!! tip "Webhook Pattern"
    For true fire-and-forget workflows, use webhooks instead of polling:
    ```python
    requests.post(
        f"{API_BASE}/runs",
        json={
            "agentId": "agent-123",
            "input": [...],
            "webhook": "https://myapp.com/webhooks/run-completed"
        }
    )
    # Your webhook endpoint receives completion notification
    ```

---

## Stream Reconnection

### When to Use

Use reconnectable streams when you need:

- **Network resilience**: Recover from connection drops
- **Multiple observers**: Dashboard + CLI + monitoring all watching same run
- **Late joining**: Start run, navigate away, return and resume streaming
- **Production reliability**: Handle network instability gracefully

### Why Reconnectable Streams?

| Benefit | Description |
|---------|-------------|
| **Network resilience** | Automatically recover from disconnections |
| **Multiple observers** | Multiple clients stream same run simultaneously |
| **Late joining** | Connect to stream after run starts |
| **Production-ready** | Handle real-world network conditions |

### Pattern 1: Automatic Reconnection

Use `POST /runs` + `GET /runs/{id}/stream` for reconnectable streams.

```python
import sseclient
import requests

def stream_with_reconnection(agent_id: str, input_messages: list):
    """Stream run output with automatic reconnection"""

    # Step 1: Start run
    create_response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agentId": agent_id,
            "input": input_messages
        }
    )

    run_id = create_response.json()['runId']
    print(f"✓ Run {run_id} started")

    # Step 2: Stream with reconnection logic
    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            print(f"\n→ Connecting to stream (attempt {retry_count + 1})...")

            response = requests.get(
                f"{API_BASE}/runs/{run_id}/stream",
                headers=headers,
                stream=True
            )

            client = sseclient.SSEClient(response)

            for event in client.events():
                data = json.loads(event.data)

                if event.event == 'message.delta':
                    # Stream text chunks
                    print(data['delta'], end='', flush=True)

                elif event.event == 'run.completed':
                    # Done!
                    print(f"\n\n✓ Run completed successfully")
                    return data

                elif event.event == 'run.failed':
                    print(f"\n\n✗ Run failed: {data['error']['message']}")
                    return data

            # Stream ended normally
            break

        except (requests.exceptions.RequestException, ConnectionError) as e:
            print(f"\n\n⚠ Connection lost: {e}")
            retry_count += 1

            if retry_count < max_retries:
                print(f"→ Reconnecting in 2s...")
                time.sleep(2)
            else:
                print(f"✗ Max retries reached, giving up")
                # Fallback: get final result via GET /runs/{id}
                response = requests.get(f"{API_BASE}/runs/{run_id}", headers=headers)
                return response.json()

# Example usage
result = stream_with_reconnection(
    agent_id="agent-789",
    input_messages=[{
        "role": "user",
        "contents": [{
            "kind": "text",
            "text": "Write a detailed article about quantum computing"
        }]
    }]
)
```

**Output:**
```text
✓ Run run-xyz789 started

→ Connecting to stream (attempt 1)...
Quantum computing represents a paradigm shift in computation...

⚠ Connection lost: Connection reset by peer

→ Reconnecting in 2s...
→ Connecting to stream (attempt 2)...
...building on the principles of quantum mechanics to solve problems...

✓ Run completed successfully
```

### Pattern 2: Multi-Observer

Multiple clients can stream the same run simultaneously.

```python
import threading

def observe_run(run_id: str, observer_name: str):
    """Multiple clients observing the same run"""
    print(f"[{observer_name}] Connecting to stream...")

    response = requests.get(
        f"{API_BASE}/runs/{run_id}/stream",
        headers=headers,
        stream=True
    )

    client = sseclient.SSEClient(response)

    for event in client.events():
        if event.event == 'message.delta':
            data = json.loads(event.data)
            print(f"[{observer_name}] {data['delta']}", end='', flush=True)

        elif event.event == 'run.completed':
            print(f"\n[{observer_name}] Stream complete")
            break

# Start a run
response = requests.post(
    f"{API_BASE}/runs",
    headers=headers,
    json={
        "agentId": "agent-123",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Count to 10"}]}]
    }
)
run_id = response.json()['runId']

# Multiple observers watch the same run
threads = []
for observer in ["Dashboard", "CLI", "Monitoring"]:
    t = threading.Thread(target=observe_run, args=(run_id, observer))
    t.start()
    threads.append(t)

for t in threads:
    t.join()
```

### Comparison: Run Patterns

| Feature | Ephemeral<br>`POST /runs/wait` | Background<br>`POST /runs` + wait | Reconnectable<br>`POST /runs` + stream |
|---------|-------------------------------|-----------------------------------|---------------------------------------|
| **Thread cleanup** | Auto-delete | Manual | Manual |
| **Reconnection** | ❌ No | ❌ No | ✅ Yes |
| **Multiple observers** | ❌ No | ❌ No | ✅ Yes |
| **Webhook support** | ❌ No | ✅ Yes | ✅ Yes |
| **Blocking** | ✅ Yes | ⚠️ On wait only | ⚠️ While streaming |
| **Best for** | Simple queries | Async workflows | Dashboards, debugging |

!!! tip "Production Streaming"
    For production dashboards, always implement reconnection logic. Network hiccups are inevitable, and reconnectable streams ensure users never lose visibility into long-running operations.

---

## Thread Management

### When to Use

Use thread management patterns for:

- **Conversation branching**: Explore "what if" scenarios
- **A/B testing**: Compare different agents/prompts on same context
- **Templates**: Reuse thread structure for consistent setup
- **Experimentation**: Safe playground for testing changes

### Why Thread Management?

| Benefit | Description |
|---------|-------------|
| **Non-destructive** | Explore alternatives without losing original |
| **Comparison** | Test multiple approaches side-by-side |
| **Templates** | Standardize thread setup across use cases |
| **Safe experimentation** | Playground for testing without consequences |

### Pattern 1: Conversation Branching

Create branches to explore alternative conversation paths.

```python
def branch_conversation(original_thread_id: str, branch_reason: str):
    """Create a branch from an existing conversation"""

    # Copy the thread with full history
    response = requests.post(
        f"{API_BASE}/threads/{original_thread_id}/copy",
        headers=headers,
        json={
            "includeHistory": True,
            "metadata": {
                "original_thread_id": original_thread_id,
                "branch_reason": branch_reason
            }
        }
    )

    new_thread = response.json()
    print(f"✓ Created branch: {new_thread['threadId']}")
    print(f"  Original: {original_thread_id}")
    print(f"  Messages copied: {len(new_thread['messages'])}")

    return new_thread['threadId']

# Example: User wants to try a different approach
original_thread = "thread-123"
branch_thread = branch_conversation(
    original_thread,
    "Try alternative problem-solving approach"
)

# Continue conversation in branch with different strategy
response = requests.post(
    f"{API_BASE}/threads/{branch_thread}/runs",
    headers=headers,
    json={
        "agentId": "agent-456",
        "input": [{
            "role": "user",
            "contents": [{
                "kind": "text",
                "text": "Let's try a different approach using recursion instead"
            }]
        }]
    }
)
```

**Output:**
```text
✓ Created branch: thread-new-456
  Original: thread-123
  Messages copied: 8
```

### Pattern 2: A/B Testing Agents

Compare multiple agent configurations on the same conversation.

```python
def ab_test_agents(thread_id: str, agent_configs: list[dict]) -> dict:
    """Test multiple agent configurations on same conversation"""

    results = {}

    for i, agent_config in enumerate(agent_configs):
        # Create branch for this variant
        branch_response = requests.post(
            f"{API_BASE}/threads/{thread_id}/copy",
            headers=headers,
            json={
                "includeHistory": True,
                "metadata": {
                    "original_thread_id": thread_id,
                    "variant": f"agent-{i+1}",
                    "agent_name": agent_config['name']
                }
            }
        )

        branch_thread_id = branch_response.json()['threadId']
        print(f"✓ Testing variant {i+1}: {agent_config['name']}")

        # Run agent on branch
        run_response = requests.post(
            f"{API_BASE}/threads/{branch_thread_id}/runs",
            headers=headers,
            json={
                "agent": agent_config,
                "input": [{
                    "role": "user",
                    "contents": [{
                        "kind": "text",
                        "text": "Summarize our conversation so far"
                    }]
                }]
            }
        )

        run_id = run_response.json()['runId']

        # Wait for completion
        result = requests.get(
            f"{API_BASE}/runs/{run_id}/wait",
            headers=headers
        ).json()

        results[agent_config['name']] = {
            "thread_id": branch_thread_id,
            "output": result['output'][0]['contents'][0]['text'],
            "tokens": result['usage']['totalTokens']
        }

    return results

# Test two different agents on same conversation
agents = [
    {
        "kind": "prompt",
        "name": "Concise Agent",
        "model": "gpt-4o-mini",
        "instructions": "Be extremely concise. Use bullet points."
    },
    {
        "kind": "prompt",
        "name": "Detailed Agent",
        "model": "gpt-4o",
        "instructions": "Provide detailed, comprehensive explanations."
    }
]

results = ab_test_agents("thread-123", agents)

# Compare results
for name, result in results.items():
    print(f"\n{name}:")
    print(f"  Output: {result['output'][:100]}...")
    print(f"  Tokens: {result['tokens']}")
```

**Output:**
```text
✓ Testing variant 1: Concise Agent
✓ Testing variant 2: Detailed Agent

Concise Agent:
  Output: • Initial problem: Database connection timeout
• Root cause: Connection pool exhaustion
• Solution: I...
  Tokens: 156

Detailed Agent:
  Output: Throughout our conversation, we've been troubleshooting a database connection timeout issue. Th...
  Tokens: 423
```

### Pattern 3: Template Threads

Create new threads from templates (structure only, no history).

```python
def create_from_template(template_id: str, user_id: str) -> str:
    """Create new thread from template (structure only, no history)"""

    response = requests.post(
        f"{API_BASE}/threads/{template_id}/copy",
        headers=headers,
        json={
            "includeHistory": False,  # Template structure only
            "metadata": {
                "template_id": template_id,
                "user_id": user_id,
                "created_from": "template"
            }
        }
    )

    new_thread = response.json()
    print(f"✓ Created thread from template: {new_thread['threadId']}")
    print(f"  Participants: {len(new_thread['participants'])}")
    print(f"  Messages: {len(new_thread['messages'])}")  # Should be 0

    return new_thread['threadId']

# Create customer support thread from template
support_thread = create_from_template(
    template_id="thread-support-template",
    user_id="user-789"
)
```

!!! tip "Use Cases for Thread Management"
    - **Branching**: "Let's try a different approach" scenarios
    - **A/B Testing**: Compare agent prompts, models, or configurations
    - **Templates**: Standardize onboarding flows, support tickets
    - **Experimentation**: Test changes without affecting production threads

---

## Thread-Scoped Runs

### When to Use

Use thread-scoped endpoints for:

- **Multi-turn conversations**: Natural conversation flow
- **Thread-centric workflows**: When thread is primary context
- **RESTful APIs**: Clearer resource nesting
- **Thread history analysis**: Debug specific conversations

### Why Thread-Scoped Runs?

| Benefit | Description |
|---------|-------------|
| **RESTful conventions** | Natural resource nesting (threads → runs) |
| **Clearer intent** | Explicit thread context in URL |
| **Better discoverability** | Easier API navigation |
| **Thread-centric workflows** | Natural fit for conversation apps |

### Pattern 1: Multi-Turn Conversation

Execute multi-turn conversations using thread-scoped endpoints.

```python
def multi_turn_conversation(thread_id: str, agent_id: str, turns: list[str]):
    """Execute multi-turn conversation using thread-scoped endpoints"""

    for i, user_message in enumerate(turns):
        print(f"\n=== Turn {i + 1} ===")
        print(f"User: {user_message}")

        # Create run in thread context (RESTful)
        response = requests.post(
            f"{API_BASE}/threads/{thread_id}/runs",
            headers=headers,
            json={
                "agentId": agent_id,
                "input": [{
                    "role": "user",
                    "contents": [{
                        "kind": "text",
                        "text": user_message
                    }]
                }]
            }
        )

        run_id = response.json()['runId']

        # Wait for completion
        result = requests.get(
            f"{API_BASE}/runs/{run_id}/wait",
            headers=headers
        ).json()

        assistant_message = result['output'][0]['contents'][0]['text']
        print(f"Assistant: {assistant_message}")
        print(f"Tokens: {result['usage']['totalTokens']}")

# Execute conversation
multi_turn_conversation(
    thread_id="thread-123",
    agent_id="agent-456",
    turns=[
        "What's the capital of France?",
        "What's the population?",
        "What are the top tourist attractions?"
    ]
)
```

**Output:**
```text
=== Turn 1 ===
User: What's the capital of France?
Assistant: The capital of France is Paris.
Tokens: 25

=== Turn 2 ===
User: What's the population?
Assistant: Paris has a population of approximately 2.2 million people within the city limits...
Tokens: 48

=== Turn 3 ===
User: What are the top tourist attractions?
Assistant: The top tourist attractions in Paris include: 1) Eiffel Tower, 2) Louvre Museum...
Tokens: 127
```

### Pattern 2: Thread Run History

Analyze all runs in a thread for debugging and analytics.

```python
def analyze_thread_runs(thread_id: str):
    """Analyze all runs in a thread for debugging/analytics"""

    # Get all runs in thread (RESTful)
    response = requests.get(
        f"{API_BASE}/threads/{thread_id}/runs",
        headers=headers,
        json={"limit": 100}
    )

    runs = response.json()

    print(f"\n=== Thread {thread_id} Analysis ===")
    print(f"Total runs: {len(runs)}")

    # Aggregate statistics
    total_tokens = sum(r.get('usage', {}).get('totalTokens', 0) for r in runs)
    failed_runs = [r for r in runs if r['status'] == 'failed']
    avg_duration = sum(
        (parse_time(r['completedAt']) - parse_time(r['createdAt'])).total_seconds()
        for r in runs if r.get('completedAt')
    ) / len(runs) if runs else 0

    print(f"Total tokens used: {total_tokens:,}")
    print(f"Failed runs: {len(failed_runs)}")
    print(f"Average duration: {avg_duration:.2f}s")

    # Show recent runs
    print(f"\nRecent runs:")
    for run in runs[-5:]:
        print(f"  {run['runId']}: {run['status']} ({run['createdAt']})")

    return {
        "total_runs": len(runs),
        "total_tokens": total_tokens,
        "failed_count": len(failed_runs),
        "avg_duration": avg_duration
    }

from dateutil.parser import parse as parse_time

# Analyze thread
stats = analyze_thread_runs("thread-123")
```

**Output:**
```text
=== Thread thread-123 Analysis ===
Total runs: 12
Total tokens used: 3,456
Failed runs: 1
Average duration: 2.34s

Recent runs:
  run-abc123: completed (2026-02-06T10:00:00Z)
  run-def456: completed (2026-02-06T10:01:00Z)
  run-ghi789: failed (2026-02-06T10:02:00Z)
  run-jkl012: completed (2026-02-06T10:03:00Z)
  run-mno345: completed (2026-02-06T10:04:00Z)
```

### Comparison: Endpoint Approaches

| Approach | Endpoint | Best For |
|----------|----------|----------|
| **Thread-scoped (RESTful)** | `POST /threads/{id}/runs` | Multi-turn conversations, thread-centric workflows |
| **Global (flexible)** | `POST /runs` with threadId | Cross-thread operations, optional thread context |
| **Thread-scoped listing** | `GET /threads/{id}/runs` | Thread history, debugging specific conversation |
| **Global listing** | `GET /runs?threadId={id}` | Cross-thread queries, flexible filtering |

!!! note "Both Approaches Are Valid"
    Use thread-scoped endpoints for clearer intent and RESTful navigation. Use global endpoints for flexibility. Both are functionally equivalent.

---

## Hooks

### When to Use

Use hooks for event-driven interception:

- **Content moderation**: Block or review sensitive content
- **Approval workflows**: Require human approval for actions
- **Logging and telemetry**: Track events for analytics
- **Custom business logic**: Enforce policies and rules

### Why Hooks?

| Benefit | Description |
|---------|-------------|
| **Event-driven** | React to run lifecycle events automatically |
| **Policy enforcement** | Block operations based on conditions |
| **Observability** | Send telemetry to analytics platforms |
| **Flexibility** | Delegate decisions to external services |

### Hook Types

| Hook Type | Purpose | Blocking |
|-----------|---------|----------|
| **BlockHook** | Pause execution based on conditions | ✅ Yes |
| **ModifyHook** | Transform content inline | ⚠️ Optional |
| **TelemetryHook** | Send analytics events | ❌ No |
| **RemoteHook** | Delegate to external service | ✅ Yes |

### Pattern 1: Content Moderation

Use hooks to block or review sensitive content.

```python
def create_run_with_moderation_hook(prompt: str):
    """Create run with hooks for content moderation"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": {
                "kind": "prompt",
                "name": "CustomerServiceAgent",
                "model": "gpt-4o",
                "instructions": "You help customers with support questions",
                "hooks": [
                    {
                        # Block hook - simple policy enforcement
                        "kind": "block",
                        "name": "content-filter",
                        "condition": {
                            "kind": "content",
                            "contentTypes": ["text"]
                        },
                        "message": "Content violates policy"
                    },
                    {
                        # Remote hook - call external service for approval
                        "kind": "remote",
                        "name": "review-content",
                        "endpoint": "https://hooks.example.com/review-content",
                        "connection": {
                            "kind": "apiKey",
                            "key": "hook_secret_123",
                            "headerName": "X-Hook-Secret"
                        }
                    }
                ]
            },
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }],
            "threadCleanup": "delete"
        }
    )

    result = response.json()
    print(f"Run created: {result['runId']}")
    print(f"Status: {result['status']}")  # Will be 'failed' if hook blocked

    return result

# Example usage
run = create_run_with_moderation_hook("Transfer $1000 to account 12345")

# If run requires approval, handle it
if run['status'] == 'requires_action':
    print("\n⚠️  Approval required for tool execution")
    print("Agent requested: transfer_money($1000, account=12345)")

    # User approves via webhook or API
    # Server automatically resumes run after approval
```

### Pattern 2: Telemetry

Send analytics events to external platforms.

```python
def create_run_with_telemetry(prompt: str):
    """Create run with telemetry hook for logging"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": {
                "kind": "prompt",
                "name": "CustomerServiceAgent",
                "model": "gpt-4o",
                "instructions": "You help customers",
                "hooks": [
                    {
                        "kind": "telemetry",
                        "name": "analytics",
                        "endpoint": "https://analytics.example.com/events",
                        "connection": {
                            "kind": "apiKey",
                            "key": "telemetry_secret_123",
                            "headerName": "X-API-Key"
                        },
                        "event": "run.lifecycle"
                    }
                ]
            },
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }],
            "threadCleanup": "delete"
        }
    )

    return response.json()

# Server automatically sends telemetry events to analytics endpoint
result = create_run_with_telemetry("What's my order status?")
print(f"Run completed: {result['runId']}")
print("Telemetry events sent to analytics endpoint (async, non-blocking)")
```

!!! warning "Hook Security"
    - Store hook secrets securely (environment variables, secret managers)
    - Use HTTPS for all remote endpoints
    - Validate webhook signatures to prevent spoofing
    - Implement timeout and retry logic for remote hooks

!!! tip "Hook Use Cases"
    - **Content moderation**: Block harmful or policy-violating content
    - **Approval workflows**: Human-in-the-loop for sensitive operations
    - **Compliance**: Log all operations for audit trails
    - **Cost control**: Block expensive operations based on budget

---

## Auto-Response

### When to Use

Use auto-response for proactive agent participation:

- **Support agents**: Automatically respond to user questions
- **Supervisor agents**: Monitor conversations and provide guidance
- **Notification agents**: Alert users based on events
- **Multi-agent systems**: Coordinate between multiple agents

### Why Auto-Response?

| Benefit | Description |
|---------|-------------|
| **Proactive participation** | Agents respond without explicit run creation |
| **Multi-agent coordination** | Multiple agents collaborate automatically |
| **Event-driven** | React to thread activity in real-time |
| **Reduced complexity** | No manual run management for each interaction |

### Pattern 1: Thread Watch (Single Thread)

Subscribe specific agent to specific thread.

```python
def setup_auto_response_thread():
    """Create thread with auto-responding agent"""

    # Create thread
    thread_response = requests.post(
        f"{API_BASE}/threads",
        headers=headers,
        json={
            "participants": [{"id": "user", "role": "user"}],
            "metadata": {"type": "support"}
        }
    )
    thread_id = thread_response.json()["threadId"]

    # Subscribe agent to watch thread (agent automatically runs when user posts)
    # Note: agent must have autoResponse config with runCondition for user messages
    watch = requests.post(
        f"{API_BASE}/threads/{thread_id}/watch",
        headers=headers,
        json={
            "agentId": "agent-support"
        }
    ).json()

    print(f"Thread created: {thread_id}")
    print(f"Agent watching thread: {watch['watchId']}")

    # Now when user posts, agent automatically responds
    message_response = requests.post(
        f"{API_BASE}/threads/{thread_id}/messages",
        headers=headers,
        json={
            "role": "user",
            "contents": [{"kind": "text", "text": "I need help with my account"}]
        }
    )

    print("\nUser message added - agent will automatically respond!")

    return thread_id

# Setup auto-response
thread_id = setup_auto_response_thread()
```

### Pattern 2: Supervisor Agent

Create supervisor that monitors multiple threads.

```python
def create_supervisor_agent():
    """Create supervisor that monitors ALL threads"""

    response = requests.post(
        f"{API_BASE}/agents",
        headers=headers,
        json={
            "name": "Support Supervisor",
            "kind": "prompt",
            "model": "gpt-4o",
            "instructions": """You are a senior support supervisor.
            Provide expert guidance when explicitly mentioned.""",
            "autoResponse": {
                "runCondition": {
                    "kind": "mention",
                    "requireExplicitMention": True
                },
                "maxConsecutiveRuns": 1
            }
        }
    )

    agent_id = response.json()["agentId"]
    print(f"Supervisor created: {agent_id}")
    print("Now responds when @mentioned in ANY thread")

    return agent_id

# Create supervisor
supervisor_id = create_supervisor_agent()

# In any thread, mention supervisor
requests.post(
    f"{API_BASE}/threads/any-thread-id/messages",
    headers=headers,
    json={
        "role": "user",
        "contents": [{"kind": "text", "text": "@supervisor Please review this solution"}]
    }
)
# Supervisor automatically creates run and responds
```

### Auto-Response Patterns

| Pattern | Scope | Trigger | Use Case |
|---------|-------|---------|----------|
| **Thread Watch** | Single thread | User message in watched thread | Dedicated support agent per conversation |
| **Global Watch** | All threads | Mention (@agent) | Supervisor agents available everywhere |
| **Conditional** | Filtered threads | Custom conditions | Specialized agents for specific scenarios |

!!! warning "Loop Prevention"
    Use `maxConsecutiveRuns` to prevent infinite agent-to-agent loops:
    ```python
    "autoResponse": {
        "runCondition": {...},
        "maxConsecutiveRuns": 3  # Prevent infinite loops
    }
    ```

!!! tip "Auto-Response Use Cases"
    - **Support bots**: Automatically respond to customer questions
    - **Escalation**: Supervisor agents monitor and intervene when needed
    - **Notifications**: Alert users based on thread activity
    - **Multi-agent**: Coordinate multiple specialized agents

---

## Remote Endpoints

### When to Use

Use remote endpoints to delegate logic to your services:

- **Custom business logic**: Complex operations in your codebase
- **Data access**: Connect to your databases and APIs
- **Security**: Keep sensitive operations behind your firewall
- **Language flexibility**: Use any programming language or framework

### Why Remote Endpoints?

| Benefit | Description |
|---------|-------------|
| **Custom logic** | Implement complex operations in your stack |
| **Data access** | Direct access to your databases and services |
| **Security** | Sensitive operations stay in your infrastructure |
| **Flexibility** | Use any language, framework, or tool |

### Pattern 1: Remote Agent

Delegate entire agent logic to your endpoint.

```python
def create_remote_agent():
    """Create agent that delegates to remote endpoint"""

    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": {
                "kind": "remote",
                "name": "CustomBusinessLogicAgent",
                "remoteEndpoint": {
                    "url": "https://myapp.example.com/agent",
                    "secret": "shared-secret-123"
                }
            },
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": "Process customer refund"}]
            }],
            "threadCleanup": "delete"
        }
    )

    return response.json()

# Your remote endpoint receives:
# POST https://myapp.example.com/agent
# {
#   "input": [...],
#   "threadId": "...",
#   "runId": "..."
# }
#
# Your endpoint returns:
# {
#   "output": [{
#     "role": "assistant",
#     "contents": [{"kind": "text", "text": "Refund processed"}]
#   }]
# }

result = create_remote_agent()
print(f"Remote agent run: {result['runId']}")
print(f"Response: {result['output'][0]['contents'][0]['text']}")
```

### Pattern 2: Remote Tool

Implement specific tools as remote endpoints.

```python
def create_agent_with_remote_tool():
    """Create agent with tool that calls remote endpoint"""

    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": {
                "kind": "prompt",
                "name": "OrderAgent",
                "model": "gpt-4o",
                "instructions": "You help process orders",
                "tools": [
                    {
                        "kind": "remote",
                        "name": "check_inventory",
                        "description": "Check product inventory",
                        "remoteEndpoint": {
                            "url": "https://inventory.example.com/check",
                            "secret": "secret123"
                        },
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "productId": {"type": "string"},
                                "quantity": {"type": "number"}
                            },
                            "required": ["productId"]
                        }
                    }
                ]
            },
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": "Do you have product XYZ in stock?"}]
            }],
            "threadCleanup": "delete"
        }
    )

    return response.json()

result = create_agent_with_remote_tool()
print(f"Agent used remote tool for inventory check")
print(f"Response: {result['output'][0]['contents'][0]['text']}")
```

### Remote Endpoint Security

!!! warning "Security Best Practices"
    - **Shared secrets**: Validate requests using shared secrets
    - **HTTPS only**: Never use HTTP for remote endpoints
    - **Timeouts**: Implement reasonable timeouts (5-30s)
    - **Retries**: Handle transient failures gracefully
    - **Validation**: Validate all inputs before processing

```python
# Example endpoint implementation (Flask)
from flask import Flask, request, jsonify
import hmac
import hashlib

app = Flask(__name__)
SECRET = "shared-secret-123"

@app.route('/agent', methods=['POST'])
def handle_agent_request():
    # Validate secret
    provided_secret = request.headers.get('X-Agent-Secret')
    if not hmac.compare_digest(provided_secret, SECRET):
        return jsonify({"error": "Unauthorized"}), 401

    # Process request
    data = request.json
    input_text = data['input'][0]['contents'][0]['text']

    # Your custom business logic here
    result = process_business_logic(input_text)

    # Return response
    return jsonify({
        "output": [{
            "role": "assistant",
            "contents": [{"kind": "text", "text": result}]
        }]
    })
```

!!! tip "Remote Endpoint Use Cases"
    - **Database queries**: Fetch data from your databases
    - **Payment processing**: Process transactions securely
    - **Legacy systems**: Integrate with existing infrastructure
    - **Specialized operations**: Machine learning, image processing, etc.

---

## Summary

### Quick Reference

| Pattern | Best For | Key Benefit |
|---------|----------|-------------|
| **Ephemeral Runs** | Stateless operations | Automatic cleanup, simple API |
| **Background Runs** | Long-running tasks | Non-blocking, parallel execution |
| **Stream Reconnection** | Production dashboards | Network resilience, multiple observers |
| **Thread Management** | A/B testing, branching | Non-destructive experimentation |
| **Thread-Scoped Runs** | Conversation apps | RESTful conventions, clear intent |
| **Hooks** | Policy enforcement | Event-driven interception |
| **Auto-Response** | Multi-agent systems | Proactive participation |
| **Remote Endpoints** | Custom business logic | Maximum flexibility |

### Production Checklist

When building production agent applications:

- [ ] Implement reconnection logic for streaming
- [ ] Use background runs for long operations
- [ ] Add hooks for content moderation and compliance
- [ ] Configure auto-response for proactive agents
- [ ] Use thread branching for safe experimentation
- [ ] Implement exponential backoff for retries
- [ ] Monitor token usage and costs
- [ ] Set up webhook handlers for async notifications
- [ ] Use remote endpoints for sensitive operations
- [ ] Configure rate limiting and quotas

---

## Navigation

<div class="grid cards" markdown>

-   :material-book-open-page-variant:{ .lg .middle } __Getting Started Guide__

    ---

    Learn the basics of the Agent Protocol

    [:octicons-arrow-right-24: Getting Started](index.md)

-   :material-file-document:{ .lg .middle } __API Reference__

    ---

    Complete API documentation with all endpoints

    [:octicons-arrow-right-24: API Reference](../api/index.md)

-   :material-webhook:{ .lg .middle } __Proactive Messaging__

    ---

    Learn about auto-response and thread watch patterns

    [:octicons-arrow-right-24: Proactive Messaging](proactive-messaging.md)

-   :material-hook:{ .lg .middle } __Hooks Specification__

    ---

    Deep dive into hook types and configurations

    [:octicons-arrow-right-24: Hooks](../specifications/hooks.md)

</div>
