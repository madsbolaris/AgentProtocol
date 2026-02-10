# Streaming

Get real-time responses as agents generate them.

## Overview

Streaming delivers agent responses token-by-token in real time, creating responsive, ChatGPT-like user experiences. Instead of waiting for the complete response, your application receives incremental updates as the agent generates content.

---

## Why Stream?

**Without Streaming:**

```python
# User waits 5-10 seconds for complete response
response = await client.complete_chat("Write a long story")
print(response)  # All at once
```

**With Streaming:**

```python
# User sees immediate feedback
await client.stream_chat(
    "Write a long story",
    on_text_chunk=lambda text: print(text, end="", flush=True)
)
# O... n... c... e...  u... p... o... n...  a...  t... i... m... e...
```

**Benefits:**

- **Better UX** - Immediate feedback, no blank loading screens
- **Perceived Performance** - Feels faster even if total time is the same
- **Early Cancellation** - Stop generation if output isn't useful
- **Progressive Rendering** - Display partial results (e.g., in markdown)

---

## Basic Streaming

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient

    client = AgentProtocolClient("http://localhost:5000")

    # Simple streaming with text callback
    await client.stream_chat(
        "Count to 5",
        on_text_chunk=lambda text: print(text, end="", flush=True)
    )
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    // Simple streaming with text callback
    await client.streamChat(
        "Count to 5",
        { onTextChunk: (text) => process.stdout.write(text) }
    );
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    // Simple streaming with text callback
    await client.StreamChatAsync(
        "Count to 5",
        onTextChunk: text => Console.Write(text)
    );
    ```

---

## Event-Based Streaming

For more control, subscribe to specific event types:

=== "Python"

    ```python
    async def on_text(text: str):
        print(text, end="", flush=True)

    async def on_function_call(name: str, arguments: dict):
        print(f"\n[Calling {name}...]")

    async def on_function_result(name: str, result: str):
        print(f"\n[{name} returned: {result}]")

    await client.stream_chat(
        "What's the weather in Paris?",
        on_text_chunk=on_text,
        on_function_call=on_function_call,
        on_function_result=on_function_result
    )
    ```

=== "TypeScript"

    ```typescript
    await client.streamChat(
        "What's the weather in Paris?",
        {
            onTextChunk: (text) => process.stdout.write(text),
            onFunctionCall: (name, args) => console.log(`\n[Calling ${name}...]`),
            onFunctionResult: (name, result) => console.log(`\n[${name} returned: ${result}]`)
        }
    );
    ```

=== "C#"

    ```csharp
    await client.StreamChatAsync(
        "What's the weather in Paris?",
        onTextChunk: text => Console.Write(text),
        onFunctionCall: (name, args) => Console.WriteLine($"\n[Calling {name}...]"),
        onFunctionResult: (name, result) => Console.WriteLine($"\n[{name} returned: {result}]")
    );
    ```

---

## Event Types

The SDK emits these streaming events:

| Event | Description | Callback Signature |
|-------|-------------|--------------------|
| `text_chunk` | Incremental text tokens | `(text: string) => void` |
| `function_call` | Agent is calling a tool | `(name: string, args: dict) => void` |
| `function_result` | Tool execution completed | `(name: string, result: string) => void` |
| `run_started` | Run execution began | `(run_id: string) => void` |
| `run_completed` | Run finished successfully | `(run_id: string) => void` |
| `run_failed` | Run encountered an error | `(error: Error) => void` |
| `message_created` | New message added to thread | `(message: Message) => void` |

---

## Streaming with Conversations

Stream responses in persistent conversations:

=== "Python"

    ```python
    conversation = client.create_conversation()

    # First turn
    await conversation.send_stream(
        "Tell me about Mars",
        on_text_chunk=lambda text: print(text, end="", flush=True)
    )
    print("\n")

    # Second turn (context preserved)
    await conversation.send_stream(
        "What about its moons?",
        on_text_chunk=lambda text: print(text, end="", flush=True)
    )
    ```

=== "TypeScript"

    ```typescript
    const conversation = client.createConversation();

    // First turn
    await conversation.sendStream(
        "Tell me about Mars",
        { onTextChunk: (text) => process.stdout.write(text) }
    );
    console.log("\n");

    // Second turn (context preserved)
    await conversation.sendStream(
        "What about its moons?",
        { onTextChunk: (text) => process.stdout.write(text) }
    );
    ```

=== "C#"

    ```csharp
    var conversation = client.CreateConversation();

    // First turn
    await conversation.SendStreamAsync(
        "Tell me about Mars",
        onTextChunk: text => Console.Write(text)
    );
    Console.WriteLine();

    // Second turn (context preserved)
    await conversation.SendStreamAsync(
        "What about its moons?",
        onTextChunk: text => Console.Write(text)
    );
    ```

---

## Advanced Patterns

### Buffered Streaming

Buffer chunks for smoother rendering:

```python
buffer = []
buffer_size = 5

async def buffered_callback(text: str):
    buffer.append(text)
    if len(buffer) >= buffer_size:
        print(''.join(buffer), end="", flush=True)
        buffer.clear()

await client.stream_chat(message, on_text_chunk=buffered_callback)

# Flush remaining
if buffer:
    print(''.join(buffer), end="", flush=True)
```

### Progress Tracking

Track streaming progress:

```python
class StreamProgress:
    def __init__(self):
        self.tokens = 0
        self.chars = 0

    async def on_chunk(self, text: str):
        self.tokens += 1
        self.chars += len(text)
        print(text, end="", flush=True)

progress = StreamProgress()
await client.stream_chat(message, on_text_chunk=progress.on_chunk)
print(f"\n\nReceived {progress.tokens} tokens, {progress.chars} characters")
```

### Cancellation

Cancel streaming mid-generation:

=== "Python"

    ```python
    import asyncio

    async def stream_with_timeout():
        try:
            await asyncio.wait_for(
                client.stream_chat("Write a very long story", on_text_chunk=print),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            print("\n[Cancelled after 5 seconds]")
    ```

=== "TypeScript"

    ```typescript
    const controller = new AbortController();

    // Cancel after 5 seconds
    setTimeout(() => controller.abort(), 5000);

    try {
        await client.streamChat(
            "Write a very long story",
            {
                onTextChunk: (text) => console.log(text),
                signal: controller.signal
            }
        );
    } catch (error) {
        console.log("\n[Cancelled after 5 seconds]");
    }
    ```

=== "C#"

    ```csharp
    var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));

    try
    {
        await client.StreamChatAsync(
            "Write a very long story",
            onTextChunk: text => Console.Write(text),
            cancellationToken: cts.Token
        );
    }
    catch (OperationCanceledException)
    {
        Console.WriteLine("\n[Cancelled after 5 seconds]");
    }
    ```

---

## Technical Details

### Server-Sent Events (SSE)

The Client SDK uses Server-Sent Events (SSE) over HTTP for streaming:

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: text_chunk
data: {"text": "Hello"}

event: text_chunk
data: {"text": " world"}

event: run_completed
data: {"run_id": "run_123"}
```

The SDK automatically:

- Maintains the SSE connection
- Parses event types and data
- Dispatches to your callbacks
- Handles reconnection on network errors

### Automatic Reconnection

If the stream is interrupted, the SDK automatically reconnects:

```python
await client.stream_chat(
    message,
    on_text_chunk=callback,
    max_retries=3,          # Retry up to 3 times
    retry_delay=1.0         # Wait 1 second between retries
)
```

### Backpressure Handling

The SDK buffers events if your callbacks are slow:

```python
async def slow_callback(text: str):
    await asyncio.sleep(0.1)  # Simulate slow processing
    print(text)

# SDK buffers incoming chunks while slow_callback processes
await client.stream_chat(message, on_text_chunk=slow_callback)
```

---

## Best Practices

1. **Use Streaming for Long Responses**
   - Streaming is ideal for summaries, articles, creative writing
   - For short responses ("Yes/No"), regular completion is simpler

2. **Handle Errors in Callbacks**
   ```python
   async def safe_callback(text: str):
       try:
           print(text, end="", flush=True)
       except Exception as e:
           logging.error(f"Callback error: {e}")
   ```

3. **Flush Output Buffers**
   - Always use `flush=True` in Python or `Console.Out.Flush()` in C# for real-time display

4. **Don't Block in Callbacks**
   - Keep callbacks fast to avoid backpressure
   - Use queues for expensive operations:
   ```python
   queue = asyncio.Queue()

   async def callback(text: str):
       await queue.put(text)  # Fast enqueue

   async def processor():
       while True:
           text = await queue.get()
           await expensive_operation(text)  # Slow processing
   ```

5. **Test Network Interruptions**
   - Verify your app handles reconnection gracefully
   - Set appropriate timeouts and retry limits

---

## Next Steps

<div class="grid cards" markdown>

- **:material-tools: Tools & Functions**

    Stream tool calls and results

    [:octicons-arrow-right-24: Learn Tools](tools.md)

- **:material-alert-circle: Error Handling**

    Handle streaming errors

    [:octicons-arrow-right-24: Error Handling](error-handling.md)

- **:material-book-open: How-To: Handle Streaming**

    Practical streaming guide

    [:octicons-arrow-right-24: How-To Guide](../guides/handle-streaming.md)

</div>
