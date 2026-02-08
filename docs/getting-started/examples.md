# Code Examples

Practical, copy-paste code patterns for common Agent Runtime API scenarios.

## Table of Contents

- [Retry Logic](#retry-logic)
- [Batch Processing](#batch-processing)
- [Image Analysis](#image-analysis)
- [Context Management](#context-management)

---

## Retry Logic

### Description

Implement robust retry logic with exponential backoff to handle rate limits, transient network errors, and API timeouts gracefully. This pattern is essential for production applications that need to handle temporary failures without crashing.

!!! warning "Handle Rate Limits"

    Always implement retry logic with exponential backoff to handle rate limits and transient errors gracefully.

### Code

```python
import time
import random
import asyncio
from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

client = AgentProtocolClient(AgentProtocolClientOptions(
    base_url="https://agents.example.com/v1",
    api_key="your-api-key"
))

async def create_run_with_retry(
    agent: dict,
    input: list,
    max_retries: int = 3,
    base_delay: float = 1.0
):
    """Create run with automatic retry on transient errors"""
    for attempt in range(max_retries):
        try:
            async with client:
                result = await client.runs.create({
                    "agent": agent,
                    "input": input,
                    "threadCleanup": "delete"
                })
                return result

        except Exception as e:
            # Check for rate limit (429)
            if hasattr(e, 'status_code') and e.status_code == 429:
                retry_after = int(getattr(e, 'retry_after', 60))
                print(f"Rate limited. Waiting {retry_after}s...")
                await asyncio.sleep(retry_after)
                continue

            if attempt == max_retries - 1:
                raise

            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** attempt), 60)
            jitter = delay * random.uniform(0.5, 1.0)
            print(f"Attempt {attempt + 1} failed. Retrying in {jitter:.1f}s...")
            await asyncio.sleep(jitter)

    raise Exception("Max retries exceeded")
```

### Usage

```python
# Basic usage with default retry settings
result = await create_run_with_retry(
    agent={
        "name": "Agent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "You are a helpful assistant."
    },
    input=[{
        "role": "user",
        "contents": [{"kind": "text", "text": "Hello"}]
    }]
)
print(result)
```

### Output

```
Attempt 1 failed. Retrying in 0.8s...
Attempt 2 failed. Retrying in 1.6s...
{
  "runId": "run_abc123",
  "status": "completed",
  "output": [...],
  "usage": {"totalTokens": 150}
}
```

!!! tip "Production Best Practices"

    - **Jitter**: Add randomness to backoff delays to prevent thundering herd problems
    - **Max Delay**: Cap the maximum retry delay (e.g., 60 seconds)
    - **Respect Retry-After**: Always honor the `Retry-After` header for 429 responses
    - **Logging**: Log retry attempts for debugging and monitoring

---

## Batch Processing

### Description

Process multiple prompts in parallel using thread pools to maximize throughput while respecting rate limits. This pattern is ideal for bulk operations like analyzing multiple documents, answering FAQ lists, or processing queues.

### Code

```python
import asyncio
from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

client = AgentProtocolClient(AgentProtocolClientOptions(
    base_url="https://agents.example.com/v1",
    api_key="your-api-key"
))

async def process_batch(prompts: list[str], max_workers: int = 5):
    """Process multiple prompts in parallel"""
    agent = {
        "name": "BatchAgent",
        "kind": "prompt",
        "model": "gpt-4o",
        "instructions": "Provide concise answers."
    }

    async def process_one(prompt: str):
        async with client:
            result = await client.runs.create({
                "agent": agent,
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": prompt}]
                }],
                "threadCleanup": "delete"
            })
            return {
                "prompt": prompt,
                "response": result['output'][0]['contents'][0]['text'],
                "tokens": result['usage']['totalTokens']
            }

    # Process with concurrency limit
    results = []
    semaphore = asyncio.Semaphore(max_workers)

    async def process_with_semaphore(prompt: str):
        async with semaphore:
            try:
                result = await process_one(prompt)
                print(f"✓ Completed: {result['prompt'][:50]}... ({result['tokens']} tokens)")
                return result
            except Exception as e:
                print(f"✗ Failed: {prompt[:50]}... - {e}")
                raise

    tasks = [process_with_semaphore(p) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Filter out exceptions
    results = [r for r in results if not isinstance(r, Exception)]
    return results
```

### Usage

```python
# Process 10 questions in parallel
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

results = await process_batch(questions, max_workers=5)
print(f"\nProcessed {len(results)}/{len(questions)} questions")
print(f"Total tokens: {sum(r['tokens'] for r in results)}")
```

### Output

```
✓ Completed: What is the capital of France?... (45 tokens)
✓ Completed: What year did WWII end?... (42 tokens)
✓ Completed: Who wrote Hamlet?... (38 tokens)
✓ Completed: Explain photosynthesis briefly... (67 tokens)
✓ Completed: Define machine learning... (58 tokens)
✓ Completed: What is the speed of light?... (43 tokens)
✓ Completed: Explain DNA structure... (72 tokens)
✓ Completed: What causes seasons?... (61 tokens)
✓ Completed: Define entropy... (54 tokens)
✓ Completed: Who invented the telephone?... (41 tokens)

Processed 10/10 questions
Total tokens: 521
```

!!! tip "Tuning Concurrency"

    - Start with `max_workers=5` and adjust based on rate limits
    - Monitor response times to find the optimal concurrency level
    - Combine with retry logic for production resilience
    - Consider using `threadCleanup="delete"` for stateless batch operations

!!! warning "Rate Limit Considerations"

    Too many concurrent requests can trigger rate limits. Start conservatively and monitor error rates. Implement the retry pattern above to handle 429 responses automatically.

---

## Image Analysis

### Description

Analyze images by sending them to vision-capable models. Images are encoded as base64 data URIs and included in the message content alongside text prompts. This pattern works for single images, multiple images, or batch image processing.

### Code

```python
import base64
from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

client = AgentProtocolClient(AgentProtocolClientOptions(
    base_url="https://agents.example.com/v1",
    api_key="your-api-key"
))

async def analyze_image(image_path: str, question: str):
    """Analyze image with agent"""
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    async with client:
        result = await client.runs.create({
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
```

### Usage

```python
# Single image analysis
response = analyze_image("photo.jpg", "What's in this image?")
print(response)

# Batch process multiple images
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

### Output

```
photo.jpg: What's in this image?
The image shows a sunset over a beach with palm trees silhouetted against an orange and pink sky. Two people are walking along the shoreline.

img1.jpg: Describe this image in detail
This is a close-up photograph of a red rose with water droplets on its petals. The background is softly blurred, creating a bokeh effect. The lighting emphasizes the vibrant red color and the delicate texture of the petals.

img2.jpg: What objects are visible?
I can see a wooden desk with a laptop computer, a coffee mug, a notebook with a pen, and a small succulent plant in a white ceramic pot. There's also a desk lamp in the background.

img3.jpg: What's the mood or atmosphere?
The atmosphere is calm and serene. The soft lighting and muted colors create a peaceful, contemplative mood. The composition suggests a quiet morning or evening moment.
```

!!! tip "Image Best Practices"

    - **Supported Formats**: JPEG, PNG, GIF, WebP
    - **Size Limits**: Keep images under 20MB for optimal performance
    - **Model Selection**: Use vision-capable models like `gpt-4o` or `claude-3-sonnet`
    - **Multiple Images**: You can include multiple images in a single message by adding more image content blocks

!!! warning "Check Model Capabilities"

    Not all models support image analysis. Use the `/agents/inspect` endpoint to verify a model has `"supportsVision": true` before sending images.

---

## Context Management

### Description

Manage conversation history to prevent context window overflow. This pattern truncates old messages while preserving system instructions and recent context, ensuring long-running conversations don't exceed model limits.

### Code

```python
import requests

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
```

### Usage

```python
# Run a long conversation with automatic truncation
long_conversation()
```

### Output

```
Turn 1: completed (128 tokens)
Turn 2: completed (145 tokens)
Turn 3: completed (132 tokens)
...
Turn 18: completed (156 tokens)
Turn 19: completed (148 tokens)
Turn 20: completed (151 tokens)
Turn 21: completed (159 tokens)
Truncated: 43 → 28 messages (~7856 tokens)
Turn 22: completed (163 tokens)
Truncated: 45 → 28 messages (~7912 tokens)
Turn 23: completed (147 tokens)
...
Turn 50: completed (154 tokens)
```

!!! tip "Advanced Context Management"

    - **Token Estimation**: Use a proper tokenizer (e.g., tiktoken) for accurate counts
    - **Sliding Window**: Keep the N most recent messages for better context
    - **Summarization**: Summarize old messages instead of discarding them
    - **System Message**: Always preserve system instructions when truncating

!!! warning "Context Limits by Model"

    Different models have different context windows:
    - GPT-4o: 128K tokens
    - GPT-4o-mini: 128K tokens
    - Claude 3 Sonnet: 200K tokens
    - Claude 3 Haiku: 200K tokens

    Adjust `max_tokens` based on your model's limits.

---

## Navigation

**Related Guides:**

- [Getting Started Guide](index.md) - Complete integration walkthrough
- [Proactive Messaging](proactive-messaging.md) - Event-driven agent patterns
- [Voice Integration](voice-integration.md) - Audio streaming examples
- [Multi-Agent](multi-agent.md) - Agent orchestration patterns

**API Reference:**

- [Runs API](../api-reference/runs.md) - Run creation and management
- [Threads API](../api-reference/threads.md) - Thread and message management
- [Agents API](../api-reference/agents.md) - Agent configuration
- [Streaming](../specifications/streaming.md) - Streaming patterns and SSE
