# Getting Started Guide

**Version**: 1.0

## Overview

This guide walks you through your first integration with the Agent Runtime API, from basic request/response to streaming and tool execution.

**What You'll Learn:**
- Create your first agent and run
- Handle streaming responses
- Execute tools with the agent
- Manage conversation threads
- Handle errors and retries

## Prerequisites

- **API Access**: Agent Runtime API endpoint and credentials
- **Programming Language**: Examples in Python, JavaScript (adaptable to any language)
- **HTTP Client**: requests (Python), fetch (JavaScript), or curl
- **OAuth2 (Optional)**: For Microsoft Graph integration

## Use Cases

This guide is for:
- **First-time integrators** - Learn the basics
- **Prototype builders** - Get working code quickly
- **SDK developers** - Understand core patterns
- **QA engineers** - Test basic flows

## Architecture

### Basic Flow

```
Client                    API                      LLM Provider
  |                        |                            |
  | POST /runs             |                            |
  |----------------------->|                            |
  |                        | Generate response          |
  |                        |--------------------------->|
  |                        |                            |
  |                        |<---------------------------|
  | Run response           |                            |
  |<-----------------------|                            |
```

### Streaming Flow

```
Client                    API (SSE)                LLM Provider
  |                        |                            |
  | POST /runs?stream=true |                            |
  |----------------------->|                            |
  |                        | Stream tokens              |
  |                        |<-------------------------->|
  | data: {text:"Hello"}   |                            |
  |<-----------------------|                            |
  | data: {text:" world"}  |                            |
  |<-----------------------|                            |
  | data: [DONE]           |                            |
  |<-----------------------|                            |
```

## Implementation

### Step 0: Capability Discovery

Before creating your first run, it's useful to check what capabilities a model supports. The `/agents/inspect` endpoint lets you discover model capabilities without creating a persisted agent.

#### Check Model Capabilities

**Python:**
```python
import requests

API_BASE = "https://agents.example.com/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def check_capabilities(model_id: str):
    """Check what a model can do"""
    response = requests.post(
        f"{API_BASE}/agents/inspect",
        headers=headers,
        json={
            "agent": {
                "kind": "prompt",
                "name": "temp-agent",
                "model": model_id,
                "instructions": "You are a helpful assistant."
            }
        }
    )

    result = response.json()
    capabilities = result['capabilities']

    print(f"\n=== {model_id} Capabilities ===")
    print(f"Vision: {capabilities['vision']}")
    print(f"Function Calling: {capabilities['functionCalling']}")
    print(f"Structured Output: {capabilities['structuredOutput']}")
    print(f"Streaming: {capabilities['streaming']}")
    print(f"Extended Thinking: {capabilities['thinking']}")
    print(f"Parallel Tool Calls: {capabilities['parallelToolCalls']}")
    print(f"Max Tokens: {capabilities['maxTokens']:,}")
    print(f"Max Output Tokens: {capabilities['maxOutputTokens']:,}")
    print(f"Content Types: {', '.join(capabilities['supportedContentTypes'])}")
    print(f"Provider: {capabilities['provider']}")
    print(f"Model Family: {capabilities['modelFamily']}")

    return capabilities

# Check different models
gpt4o_caps = check_capabilities("gpt-4o")
claude_caps = check_capabilities("claude-3-sonnet")
```

**Expected Output:**
```
=== gpt-4o Capabilities ===
Vision: True
Function Calling: True
Structured Output: True
Streaming: True
Extended Thinking: False
Parallel Tool Calls: True
Max Tokens: 128,000
Max Output Tokens: 16,384
Content Types: text, image, audio
Provider: openai
Model Family: gpt-4

=== claude-3-sonnet Capabilities ===
Vision: True
Function Calling: True
Structured Output: True
Streaming: True
Extended Thinking: True
Parallel Tool Calls: True
Max Tokens: 200,000
Max Output Tokens: 4,096
Content Types: text, image
Provider: anthropic
Model Family: claude-3
```

#### Validate Before Sending

Use capabilities to validate requests before sending:

**Python:**
```python
def create_run_with_validation(agent_def: dict, input_messages: list, validate: bool = True):
    """Create run with automatic capability validation"""

    if validate:
        # Check capabilities first
        response = requests.post(
            f"{API_BASE}/agents/inspect",
            headers=headers,
            json={"agent": agent_def}
        )
        capabilities = response.json()['capabilities']

        # Check if input contains images
        has_images = any(
            content['kind'] == 'image'
            for msg in input_messages
            for content in msg['contents']
        )

        if has_images and not capabilities['vision']:
            raise ValueError(
                f"Model {agent_def['model']} doesn't support vision. "
                f"Use a vision-capable model like gpt-4o or claude-3-sonnet."
            )

        # Check if agent uses tools
        has_tools = 'tools' in agent_def and len(agent_def['tools']) > 0

        if has_tools and not capabilities['functionCalling']:
            raise ValueError(
                f"Model {agent_def['model']} doesn't support function calling. "
                f"Use a model like gpt-4o, claude-3-sonnet, or gpt-3.5-turbo."
            )

        print(f"✓ Validation passed for {agent_def['model']}")

    # Create run
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent_def,
            "input": input_messages,
            "threadCleanup": "delete"  # Ephemeral run with auto-cleanup
        }
    )

    return response.json()

# Example: Try to send image to non-vision model (caught early)
try:
    create_run_with_validation(
        agent_def={
            "kind": "prompt",
            "name": "TextOnlyAgent",
            "model": "gpt-3.5-turbo",  # No vision support
            "instructions": "Analyze this image"
        },
        input_messages=[{
            "role": "user",
            "contents": [
                {"kind": "image", "dataUri": "data:image/jpeg;base64,..."},
                {"kind": "text", "text": "What's in this image?"}
            ]
        }]
    )
except ValueError as e:
    print(f"✗ Error: {e}")
    print("→ Switching to gpt-4o instead")
```

**Output:**
```
✗ Error: Model gpt-3.5-turbo doesn't support vision. Use a vision-capable model like gpt-4o or claude-3-sonnet.
→ Switching to gpt-4o instead
```

#### Select Best Model for Task

Use capabilities to automatically select the best model:

**Python:**
```python
def select_model_for_task(
    requires_vision: bool = False,
    requires_tools: bool = False,
    requires_thinking: bool = False,
    max_budget_tokens: int = 128000
):
    """Select best model based on requirements"""

    # Available models (in preference order)
    candidates = [
        "gpt-4o",
        "claude-3-sonnet",
        "gpt-4o-mini",
        "gpt-3.5-turbo"
    ]

    for model_id in candidates:
        # Check capabilities
        response = requests.post(
            f"{API_BASE}/agents/inspect",
            headers=headers,
            json={
                "agent": {
                    "kind": "prompt",
                    "name": "temp",
                    "model": model_id,
                    "instructions": "..."
                }
            }
        )

        caps = response.json()['capabilities']

        # Check requirements
        if requires_vision and not caps['vision']:
            print(f"✗ {model_id}: No vision support")
            continue

        if requires_tools and not caps['functionCalling']:
            print(f"✗ {model_id}: No function calling")
            continue

        if requires_thinking and not caps['thinking']:
            print(f"✗ {model_id}: No extended thinking")
            continue

        if caps['maxTokens'] < max_budget_tokens:
            print(f"✗ {model_id}: Context window too small ({caps['maxTokens']} < {max_budget_tokens})")
            continue

        # Found a match
        print(f"✓ Selected: {model_id}")
        print(f"  Provider: {caps['provider']}")
        print(f"  Max tokens: {caps['maxTokens']:,}")
        print(f"  Vision: {caps['vision']}, Tools: {caps['functionCalling']}, Thinking: {caps['thinking']}")
        return model_id

    raise ValueError("No model found matching requirements")

# Example: Find model for image analysis with tools
model = select_model_for_task(
    requires_vision=True,
    requires_tools=True,
    requires_thinking=False
)

# Example: Find model for complex reasoning
reasoning_model = select_model_for_task(
    requires_vision=False,
    requires_tools=False,
    requires_thinking=True
)
```

**Output:**
```
✓ Selected: gpt-4o
  Provider: openai
  Max tokens: 128,000
  Vision: True, Tools: True, Thinking: False

✗ gpt-4o: No extended thinking
✓ Selected: claude-3-sonnet
  Provider: anthropic
  Max tokens: 200,000
  Vision: True, Tools: True, Thinking: True
```

---

### Step 1: Basic Request/Response

#### Create Your First Run

**Python:**
```python
import requests

API_BASE = "https://agents.example.com/v1"
API_KEY = "your-api-key"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Create a simple run
response = requests.post(
    f"{API_BASE}/runs",
    headers=headers,
    json={
        "agent": {
            "name": "HelloAgent",
            "kind": "prompt",
            "model": "gpt-4o",
            "instructions": "You are a helpful assistant. Keep responses concise."
        },
        "input": [{
            "role": "user",
            "contents": [{
                "kind": "text",
                "text": "What is the capital of France?"
            }]
        }],
        "threadCleanup": "delete"  # Auto-cleanup for quickstart
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Response: {result['output'][0]['contents'][0]['text']}")
```

**JavaScript:**
```javascript
const API_BASE = "https://agents.example.com/v1";
const API_KEY = "your-api-key";

async function createRun() {
    const response = await fetch(`${API_BASE}/runs`, {
        method: "POST",
        headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            agent: {
                name: "HelloAgent",
                kind: "prompt",
                model: "gpt-4o",
                instructions: "You are a helpful assistant."
            },
            input: [{
                role: "user",
                contents: [{
                    kind: "text",
                    text: "What is the capital of France?"
                }]
            }],
            threadCleanup: "delete"
        })
    });

    const result = await response.json();
    console.log(`Status: ${result.status}`);
    console.log(`Response: ${result.output[0].contents[0].text}`);
}

createRun();
```

**Expected Output:**
```json
{
  "runId": "run_abc123",
  "status": "completed",
  "output": [{
    "role": "assistant",
    "contents": [{
      "kind": "text",
      "text": "The capital of France is Paris."
    }]
  }],
  "usage": {
    "inputTokens": 15,
    "outputTokens": 8,
    "totalTokens": 23
  }
}
```

### Step 2: Streaming Responses

#### Server-Sent Events (SSE)

**Python:**
```python
import requests
import json

def stream_run(prompt: str):
    """Stream agent response token by token"""
    response = requests.post(
        f"{API_BASE}/runs",
        headers={**headers, "Accept": "text/event-stream"},
        json={
            "agent": {
                "name": "StreamingAgent",
                "kind": "prompt",
                "model": "gpt-4o",
                "instructions": "You are a helpful assistant.",
                "options": {"stream": True}
            },
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }],
            "threadCleanup": "delete"
        },
        stream=True  # Enable streaming
    )

    print("Streaming response:")
    for line in response.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                data = line[6:]  # Remove 'data: ' prefix
                if data == '[DONE]':
                    print("\n[Stream complete]")
                    break
                try:
                    chunk = json.loads(data)
                    if 'text' in chunk:
                        print(chunk['text'], end='', flush=True)
                except json.JSONDecodeError:
                    pass

# Example usage
stream_run("Explain quantum computing in simple terms")
```

**Output:**
```
Streaming response:
Quantum computing uses quantum bits (qubits) that can be 0, 1, or both simultaneously...
[Stream complete]
```

### Step 3: Conversation Threads

#### Stateful Multi-Turn Conversation

**Python:**
```python
class ConversationClient:
    def __init__(self, api_base: str, api_key: str, agent_id: str):
        self.api_base = api_base
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.agent_id = agent_id
        self.thread_id = None

    def create_thread(self):
        """Create a new conversation thread"""
        response = requests.post(
            f"{self.api_base}/threads",
            headers=self.headers,
            json={"metadata": {"source": "quickstart"}}
        )
        result = response.json()
        self.thread_id = result['threadId']
        print(f"Created thread: {self.thread_id}")
        return self.thread_id

    def send_message(self, text: str):
        """Send message and get response"""
        if not self.thread_id:
            self.create_thread()

        # Create run with thread
        response = requests.post(
            f"{self.api_base}/runs",
            headers=self.headers,
            json={
                "agentId": self.agent_id,
                "threadId": self.thread_id,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": text}]
                }]
            }
        )

        result = response.json()
        if result['status'] == 'completed':
            reply = result['output'][0]['contents'][0]['text']
            return reply
        else:
            raise Exception(f"Run failed: {result.get('error')}")

    def get_history(self):
        """Get conversation history"""
        response = requests.get(
            f"{self.api_base}/threads/{self.thread_id}/messages",
            headers=self.headers
        )
        return response.json()

# Example: Multi-turn conversation
client = ConversationClient(API_BASE, API_KEY, "agent_123")

# Turn 1
print("User: Tell me about Paris")
response = client.send_message("Tell me about Paris")
print(f"Assistant: {response}")

# Turn 2 (maintains context)
print("\nUser: What's the population?")
response = client.send_message("What's the population?")
print(f"Assistant: {response}")

# Turn 3
print("\nUser: And the famous landmarks?")
response = client.send_message("And the famous landmarks?")
print(f"Assistant: {response}")

# View full history
history = client.get_history()
print(f"\nTotal messages in thread: {len(history['data'])}")
```

### Step 4: Tool Execution

#### Agent with Tools

**Python:**
```python
import json
from datetime import datetime

def create_agent_with_tools():
    """Create agent with weather and time tools"""
    return {
        "name": "ToolAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "You are a helpful assistant with access to weather and time information.",
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "default": "celsius"
                        }
                    },
                    "required": ["location"]
                }
            },
            {
                "name": "get_current_time",
                "description": "Get current time in a timezone",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "Timezone (e.g., America/New_York)"
                        }
                    },
                    "required": ["timezone"]
                }
            }
        ]
    }

# Mock tool implementations
def execute_tool(tool_name: str, arguments: dict) -> str:
    """Execute tool and return result"""
    if tool_name == "get_weather":
        location = arguments['location']
        unit = arguments.get('unit', 'celsius')
        # Mock response
        return f"The weather in {location} is 22°{unit[0].upper()}, partly cloudy."

    elif tool_name == "get_current_time":
        timezone = arguments['timezone']
        # Mock response
        return f"Current time in {timezone}: {datetime.now().strftime('%H:%M:%S')}"

    return "Tool not found"

def run_with_tools(prompt: str):
    """Execute run with tool calling"""
    agent = create_agent_with_tools()

    # Initial run
    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": agent,
            "input": [{
                "role": "user",
                "contents": [{"kind": "text", "text": prompt}]
            }],
            "threadCleanup": "delete"
        }
    )

    result = response.json()
    run_id = result['runId']

    # Handle tool calls
    while result['status'] == 'requires_action':
        print(f"Status: {result['status']}")

        # Extract tool calls
        tool_calls = [
            content for content in result['output'][0]['contents']
            if content['kind'] == 'functionCall'
        ]

        print(f"Agent requested {len(tool_calls)} tool(s):")
        for call in tool_calls:
            print(f"  - {call['name']}({call['arguments']})")

        # Execute tools
        tool_outputs = []
        for call in tool_calls:
            arguments = json.loads(call['arguments']) if isinstance(call['arguments'], str) else call['arguments']
            result_text = execute_tool(call['name'], arguments)
            print(f"  → Result: {result_text}")

            tool_outputs.append({
                "tool_call_id": call['callId'],
                "output": result_text
            })

        # Submit tool results
        response = requests.post(
            f"{API_BASE}/runs/{run_id}/submit_tool_outputs",
            headers=headers,
            json={"tool_outputs": tool_outputs}
        )
        result = response.json()

    # Final response
    if result['status'] == 'completed':
        final_text = result['output'][-1]['contents'][0]['text']
        print(f"\nFinal response: {final_text}")
        return final_text
    else:
        raise Exception(f"Run failed: {result.get('error')}")

# Example: Tool calling
print("=== Example 1: Single Tool ===")
run_with_tools("What's the weather in Paris?")

print("\n=== Example 2: Multiple Tools ===")
run_with_tools("What's the weather in Tokyo and what time is it there?")
```

**Output:**
```
=== Example 1: Single Tool ===
Status: requires_action
Agent requested 1 tool(s):
  - get_weather({"location": "Paris", "unit": "celsius"})
  → Result: The weather in Paris is 22°C, partly cloudy.

Final response: The weather in Paris is currently 22°C and partly cloudy.

=== Example 2: Multiple Tools ===
Status: requires_action
Agent requested 2 tool(s):
  - get_weather({"location": "Tokyo", "unit": "celsius"})
  → Result: The weather in Tokyo is 22°C, partly cloudy.
  - get_current_time({"timezone": "Asia/Tokyo"})
  → Result: Current time in Asia/Tokyo: 14:30:00

Final response: In Tokyo, it's currently 22°C and partly cloudy. The local time is 14:30.
```

## Examples

### Example 1: Retry with Exponential Backoff

```python
import time
import random

def create_run_with_retry(
    agent: dict,
    input: list,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """Create run with automatic retry on transient errors"""
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{API_BASE}/runs",
                headers=headers,
                json={"agent": agent, "input": input, "threadCleanup": "delete"},
                timeout=30
            )

            # Check for rate limit
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after}s...")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** attempt), 60)
            jitter = delay * random.uniform(0.5, 1.0)
            print(f"Attempt {attempt + 1} failed. Retrying in {jitter:.1f}s...")
            time.sleep(jitter)

    raise Exception("Max retries exceeded")

# Usage
result = create_run_with_retry(
    agent={"name": "Agent", "kind": "prompt", "model": "gpt-4o", "instructions": "..."},
    input=[{"role": "user", "contents": [{"kind": "text", "text": "Hello"}]}]
)
```

### Example 2: Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_batch(prompts: list[str], max_workers: int = 5):
    """Process multiple prompts in parallel"""
    agent = {
        "name": "BatchAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "Provide concise answers."
    }

    def process_one(prompt: str):
        response = requests.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "agent": agent,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": prompt}]
                }],
                "threadCleanup": "delete"
            }
        )
        result = response.json()
        return {
            "prompt": prompt,
            "response": result['output'][0]['contents'][0]['text'],
            "tokens": result['usage']['totalTokens']
        }

    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process_one, p): p for p in prompts}

        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
                print(f"✓ Completed: {result['prompt'][:50]}... ({result['tokens']} tokens)")
            except Exception as e:
                prompt = futures[future]
                print(f"✗ Failed: {prompt[:50]}... - {e}")

    return results

# Example: Process 10 questions in parallel
questions = [
    "What is the capital of France?",
    "Explain photosynthesis briefly",
    "What year did WWII end?",
    "Define machine learning",
    "Who wrote Hamlet?",
    "What is the speed of light?",
    "Explain DNA structure",
    "What causes seasons?",
    "Define entropy",
    "Who invented the telephone?"
]

results = process_batch(questions, max_workers=5)
print(f"\nProcessed {len(results)}/{len(questions)} questions")
print(f"Total tokens: {sum(r['tokens'] for r in results)}")
```

### Example 3: Image Analysis

```python
import base64

def analyze_image(image_path: str, question: str):
    """Analyze image with agent"""
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    response = requests.post(
        f"{API_BASE}/runs",
        headers=headers,
        json={
            "agent": {
                "name": "VisionAgent",
                "kind": "prompt",
                "model": "gpt-4o",  # Vision-capable model
                "instructions": "You are an image analysis assistant. Describe what you see."
            },
            "input": [{
                "role": "user",
                "contents": [
                    {
                        "kind": "image",
                        "dataUri": f"data:image/jpeg;base64,{image_data}"
                    },
                    {
                        "kind": "text",
                        "text": question
                    }
                ]
            }],
            "threadCleanup": "delete"
        }
    )

    result = response.json()
    return result['output'][0]['contents'][0]['text']

# Example usage
response = analyze_image("photo.jpg", "What's in this image?")
print(response)

# Stress test: Multiple images
image_paths = ["img1.jpg", "img2.jpg", "img3.jpg"]
questions = [
    "Describe this image in detail",
    "What objects are visible?",
    "What's the mood or atmosphere?"
]

for img, q in zip(image_paths, questions):
    print(f"\n{img}: {q}")
    print(analyze_image(img, q))
```

### Example 4: Context Window Management

```python
def truncate_history(messages: list, max_tokens: int = 8000):
    """Truncate conversation history to fit context window"""
    # Simple token estimation: ~4 chars per token
    def estimate_tokens(text: str) -> int:
        return len(text) // 4

    # Always keep system message (first)
    system_msg = messages[0] if messages[0]['role'] == 'system' else None
    recent_msgs = messages[1:] if system_msg else messages

    # Keep most recent messages that fit
    total_tokens = estimate_tokens(system_msg['contents'][0]['text']) if system_msg else 0
    truncated = []

    for msg in reversed(recent_msgs):
        msg_text = msg['contents'][0]['text']
        msg_tokens = estimate_tokens(msg_text)

        if total_tokens + msg_tokens > max_tokens:
            break

        truncated.insert(0, msg)
        total_tokens += msg_tokens

    if system_msg:
        truncated.insert(0, system_msg)

    print(f"Truncated: {len(messages)} → {len(truncated)} messages (~{total_tokens} tokens)")
    return truncated

# Example: Long conversation
def long_conversation():
    """Simulate long conversation with truncation"""
    thread_id = requests.post(
        f"{API_BASE}/threads",
        headers=headers,
        json={}
    ).json()['threadId']

    for i in range(50):  # 50 turns
        # Get history
        history = requests.get(
            f"{API_BASE}/threads/{thread_id}/messages",
            headers=headers
        ).json()['data']

        # Truncate if needed
        if len(history) > 20:
            history = truncate_history(history, max_tokens=8000)

        # Send message
        response = requests.post(
            f"{API_BASE}/runs",
            headers=headers,
            json={
                "agentId": "agent_123",
                "threadId": thread_id,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": f"Question {i + 1}"}]
                }]
            }
        )

        result = response.json()
        print(f"Turn {i + 1}: {result['status']} ({result['usage']['totalTokens']} tokens)")

long_conversation()
```

### Example 5: Ephemeral Runs (One-Shot Execution)

Use `/runs/wait` and `/runs/stream` for stateless execution with automatic cleanup.

#### Pattern 1: Blocking Wait (for simple queries)

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

#### Pattern 2: Streaming (for real-time output)

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

#### Output

```text
Question: Tell me a short story about a robot
Once upon a time, there was a little robot named Bolt who dreamed of exploring...

Completed in 245 tokens
```

#### Why use ephemeral runs?

- No persistent thread (saves storage)
- Simpler API (no thread management)
- Perfect for: chatbots, CLI tools, stateless APIs
- Automatic cleanup (no orphaned threads)

### Example 6: Background Runs with Wait

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

#### Example: Multiple Parallel Runs

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

#### Why use background runs with wait?

- Start run immediately, wait when ready
- Non-blocking: do other work while run executes
- Webhook support: get notified when done
- Perfect for: async workflows, batch processing, long-running tasks

### Example 7: Stream Reconnection (Resilient Streaming)

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
            "text": "Write a detailed article about quantum computing (simulate network issues)"
        }]
    }]
)
```

**Output:**
```
✓ Run run-xyz789 started

→ Connecting to stream (attempt 1)...
Quantum computing represents a paradigm shift in computation...

⚠ Connection lost: Connection reset by peer

→ Reconnecting in 2s...
→ Connecting to stream (attempt 2)...
...building on the principles of quantum mechanics to solve problems...

✓ Run completed successfully
```

**Example: Multi-Observer Pattern**

Multiple clients can stream the same run simultaneously:

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

**Why use reconnectable streams?**

- Network resilience: automatically recover from disconnections
- Multiple observers: dashboard + CLI + monitoring all streaming same run
- Late joining: start run, navigate away, return and continue streaming
- Perfect for: dashboards, debugging, distributed systems

**Comparison: Ephemeral vs Background vs Reconnectable**

| Feature | Ephemeral<br>`POST /runs/wait` | Background<br>`POST /runs` + wait | Reconnectable<br>`POST /runs` + stream |
|---------|-------------------------------|-----------------------------------|---------------------------------------|
| **Thread cleanup** | Auto-delete | Manual | Manual |
| **Reconnection** | ❌ No | ❌ No | ✅ Yes |
| **Multiple observers** | ❌ No | ❌ No | ✅ Yes |
| **Webhook support** | ❌ No | ✅ Yes | ✅ Yes |
| **Best for** | Simple queries | Async workflows | Dashboards, debugging |

### Example 8: Thread Copy and Branching

Use `POST /threads/{threadId}/copy` to create conversation branches and explore alternative paths.

#### Pattern 1: Conversation Branching

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

#### Pattern 2: A/B Testing Different Agents

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

#### Pattern 3: Template Threads

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

**Why use thread copy?**

- **Branching**: Explore "what if" scenarios without losing original
- **A/B testing**: Compare agent/prompt variations on same context
- **Templates**: Reuse thread structure for consistent setup
- **Experimentation**: Safe playground for testing changes

---

### Example 9: Thread-Scoped Runs (RESTful Pattern)

Use `POST /threads/{threadId}/runs` and `GET /threads/{threadId}/runs` for clearer thread-centric API navigation.

#### Pattern 1: Multi-Turn Conversation with Thread Scope

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

#### Pattern 2: Thread Run History Analysis

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

#### Comparison: Thread-Scoped vs Global Run Endpoints

| Approach | Endpoint | Best For |
|----------|----------|----------|
| **Thread-scoped (RESTful)** | `POST /threads/{id}/runs` | Multi-turn conversations, thread-centric workflows |
| **Global (flexible)** | `POST /runs` with threadId | Cross-thread operations, optional thread context |
| **Thread-scoped listing** | `GET /threads/{id}/runs` | Thread history, debugging specific conversation |
| **Global listing** | `GET /runs?threadId={id}` | Cross-thread queries, flexible filtering |

**Both approaches are equivalent** - use thread-scoped for clearer intent and RESTful navigation, use global for flexibility.

**Why use thread-scoped runs?**

- **RESTful conventions**: Natural resource nesting (threads → runs)
- **Clearer intent**: Explicit thread context in URL
- **Better discoverability**: Easier API navigation
- **Thread-centric workflows**: Natural fit for conversation-focused apps

---

### Step 5: Advanced Features (Phase 2)

#### Hooks - Event-Driven Interception

Hooks enable event-driven interception of run lifecycle events. Use hooks to implement approval workflows, logging, or custom business logic.

**Example - Content Moderation Hook:**

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

**Example - Telemetry Hook:**

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

**Hook Types:**

- **BlockHook**: Pause execution based on conditions
- **ModifyHook**: Transform content inline
- **TelemetryHook**: Send analytics events
- **RemoteHook**: Delegate to external service

See [Hooks Specification](../specifications/hooks.md) for complete details.

---

#### Auto-Response - Proactive Agent Participation

Configure agents to automatically respond to thread activity without explicit run creation.

**Example - Auto-Responding Support Agent:**

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

**Example - Supervisor Agent with ThreadWatch:**

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

**Auto-Response Patterns:**

- **Thread Watch (Single-Thread)**: Subscribe specific agent to specific thread via `POST /threads/{threadId}/watch`
- **Thread Watch (Multi-Thread)**: Agent monitors multiple threads via `autoResponse` configuration
- **Run Conditions**: Configure when agents participate (roles, content, mention)
- **Loop Prevention**: `maxConsecutiveRuns` prevents infinite agent-to-agent loops

See [Proactive Messaging Guide](proactive-messaging.md) and [Agent Auto-Response Specification](../specifications/agent-auto-response.md) for complete details.

---

#### Remote Endpoints - Custom Agent Logic

Delegate agent logic to remote HTTP endpoints for maximum flexibility.

**Example - Remote Agent:**

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

**Example - Remote Tool:**

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

**Remote Endpoint Benefits:**

- **Custom business logic**: Implement complex operations in your codebase
- **Data access**: Connect to your databases and APIs
- **Security**: Keep sensitive operations behind your firewall
- **Flexibility**: Use any programming language or framework

See [Agent Auto-Response Specification](../specifications/agent-auto-response.md) for remote condition details.

---

## Troubleshooting

### Issue 1: 401 Unauthorized

**Problem**: API returns 401 status

**Solutions:**
```python
# Check API key
print(f"API Key: {API_KEY[:10]}...")  # First 10 chars

# Check headers
print(headers)

# Try with explicit auth
response = requests.post(
    f"{API_BASE}/runs",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={...}
)
```

### Issue 2: 429 Rate Limited

**Problem**: Too many requests

**Solutions:**
```python
# Implement backoff
if response.status_code == 429:
    retry_after = int(response.headers.get('Retry-After', 60))
    time.sleep(retry_after)
    # Retry request

# Or use exponential backoff (see Example 1)
```

### Issue 3: Run Stuck in `in_progress`

**Problem**: Run never completes

**Solutions:**
```python
import time

def wait_for_completion(run_id: str, timeout: int = 300):
    """Poll run until completion"""
    start = time.time()
    while time.time() - start < timeout:
        response = requests.get(
            f"{API_BASE}/runs/{run_id}",
            headers=headers
        )
        result = response.json()

        if result['status'] in ['completed', 'failed', 'cancelled']:
            return result

        print(f"Status: {result['status']} (elapsed: {time.time() - start:.1f}s)")
        time.sleep(2)

    raise TimeoutError(f"Run {run_id} did not complete within {timeout}s")

# Usage
result = wait_for_completion("run_123")
```

### Issue 4: Tool Results Not Accepted

**Problem**: submit_tool_outputs returns error

**Solutions:**
```python
# Ensure all tool calls have results
tool_calls = [c for c in output['contents'] if c['kind'] == 'functionCall']
tool_outputs = []

for call in tool_calls:
    tool_outputs.append({
        "tool_call_id": call['callId'],  # Must match exactly
        "output": execute_tool(call['name'], call['arguments'])
    })

# Check all callIds are provided
call_ids = {c['callId'] for c in tool_calls}
output_ids = {o['tool_call_id'] for o in tool_outputs}
assert call_ids == output_ids, f"Missing results for: {call_ids - output_ids}"
```

### Issue 5: Context Length Exceeded

**Problem**: 422 error with "CONTEXT_LENGTH_EXCEEDED"

**Solutions:**
```python
# Option 1: Truncate history (see Example 4)

# Option 2: Use smaller model
agent['model'] = "gpt-4o-mini"  # Has larger context

# Option 3: Summarize old messages
def summarize_history(messages: list) -> list:
    """Summarize old messages to reduce tokens"""
    if len(messages) < 10:
        return messages

    # Keep system + recent 5
    system = messages[0] if messages[0]['role'] == 'system' else None
    recent = messages[-5:]

    # Summarize middle
    middle = messages[1:-5] if system else messages[:-5]
    summary_text = "Previous conversation summary: " + summarize(middle)

    result = []
    if system:
        result.append(system)
    result.append({
        "role": "system",
        "contents": [{"kind": "text", "text": summary_text}]
    })
    result.extend(recent)

    return result
```

## Next Steps

Now that you've mastered the basics:

1. **[Proactive Messaging](proactive-messaging.md)** - Event-driven agents
2. **[Voice Integration](voice-integration.md)** - Audio streaming
3. **[Multi-Agent](multi-agent.md)** - Agent orchestration
4. **[Human-in-Loop](human-in-loop.md)** - Approval workflows
5. **[Webhooks](webhooks.md)** - Real-time notifications

## Related Documentation

- **[API Reference](../api-reference/index.md)** - Full API documentation
- **[Specifications](../specifications/index.md)** - Behavioral requirements
- **[Run Lifecycle](../specifications/run-lifecycle.md)** - Run state machine
- **[Streaming](../specifications/streaming.md)** - Streaming patterns
- **[Tool Execution](../specifications/tool-execution.md)** - Tool execution flow
