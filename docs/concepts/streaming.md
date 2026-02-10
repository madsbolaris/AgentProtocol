# Streaming

**Streaming** delivers agent responses in real-time as they're generated, rather than waiting for the entire response to complete.

## What is Streaming?

Instead of this:
```
User sends message → [wait 10 seconds] → Complete response appears
```

Streaming gives you this:
```
User sends message → "The" → "weather" → "is" → "sunny" → ...
```

## Why Stream?

### Better User Experience
- **Perceived speed** - Users see progress immediately
- **Engagement** - Feels more conversational
- **Cancelation** - Stop long responses early

### Efficient Resources
- **Progressive rendering** - Display content as it arrives
- **Early feedback** - React to partial responses
- **Reduced timeouts** - No waiting for full completion

## How Streaming Works

### Server-Sent Events (SSE)
The protocol uses SSE for streaming:

```
Client                          Server
  |                               |
  |--- Start stream ----------->  |
  |                               |
  |<-- event: text_chunk ------   |
  |    data: "The"                |
  |                               |
  |<-- event: text_chunk ------   |
  |    data: " weather"           |
  |                               |
  |<-- event: completed -------   |
```

### Stream Events

**text_chunk** - Partial text response
```json
{
  "type": "text_chunk",
  "text": "The weather is"
}
```

**function_call_start** - Tool call beginning
```json
{
  "type": "function_call_start",
  "name": "get_weather",
  "call_id": "call_123"
}
```

**function_call_args** - Tool arguments streaming
```json
{
  "type": "function_call_args",
  "args_chunk": "{\"location\":"
}
```

**completed** - Stream finished
```json
{
  "type": "completed",
  "run_id": "run_123",
  "status": "completed"
}
```

**error** - Stream error
```json
{
  "type": "error",
  "message": "Connection timeout"
}
```

## Streaming Patterns

### Text Streaming
Stream text responses character-by-character or token-by-token:

```python
async for chunk in client.stream_chat("Tell me a story"):
    print(chunk, end="", flush=True)
```

### Tool Call Streaming
Stream tool invocations as they're decided:

```python
async for event in client.stream_chat("What's the weather?"):
    if event.type == "function_call_start":
        print(f"Calling {event.name}...")
    elif event.type == "text_chunk":
        print(event.text, end="")
```

### Multi-turn Streaming
Stream multiple agent responses in sequence:

```python
conversation = client.create_conversation()
async for chunk in conversation.stream("Tell me three facts"):
    # Streams all three facts as they're generated
    print(chunk, end="")
```

## Streaming Modes

### Full Streaming
Receive every token as generated:
```
"T" → "h" → "e" → " " → "w" → "e" → "a" → ...
```

### Chunk Streaming
Receive small batches of tokens:
```
"The " → "weather " → "is " → "sunny"
```

### Event Streaming
Receive structured events with metadata:
```
{type: "text_chunk", text: "The", index: 0}
{type: "text_chunk", text: " weather", index: 1}
```

## Handling Streams

### Callback Pattern
Process chunks as they arrive:

```typescript
client.streamChat("Hello", (chunk) => {
    display.append(chunk);
});
```

### Iterator Pattern
Loop over stream events:

```python
async for chunk in stream:
    handle_chunk(chunk)
```

### Event Pattern
React to specific event types:

```typescript
stream.on('text_chunk', (text) => append(text));
stream.on('completed', () => finalize());
stream.on('error', (err) => handle_error(err));
```

## Stream Lifecycle

```
start → [events...] → completed
                   → error
                   → cancelled
```

### Start
Stream begins, connection established

### Events
Continuous flow of data chunks

### End States
- **completed** - Successful finish
- **error** - Something went wrong
- **cancelled** - User stopped stream

## Error Handling

### Network Errors
```python
try:
    async for chunk in stream:
        process(chunk)
except ConnectionError:
    # Retry or fallback
```

### Timeout Errors
```python
try:
    async for chunk in stream:
        process(chunk)
except TimeoutError:
    # Stream took too long
```

### Parse Errors
```python
try:
    async for chunk in stream:
        process(chunk)
except JSONDecodeError:
    # Malformed event data
```

## Related Concepts

- **[Runs](runs.md)** - Streaming happens during runs
- **[Messages](messages.md)** - Stream output becomes messages
- **[Agents](agents.md)** - Agents generate streamed content

## Best Practices

✅ **Do:**
- Handle all stream events
- Implement error recovery
- Show progress indicators
- Allow stream cancellation
- Buffer for smooth display

❌ **Don't:**
- Block on each chunk
- Ignore error events
- Forget to clean up connections
- Parse incomplete JSON
- Skip timeout handling

## Streaming vs. Polling

| Aspect | Streaming | Polling |
|--------|-----------|---------|
| Latency | Immediate | Delayed |
| Efficiency | One connection | Multiple requests |
| Complexity | Event handling | Simple |
| User experience | Real-time | Batch updates |

**Use streaming when:**
- Responses are long
- User experience matters
- Real-time feedback needed

**Use polling when:**
- Responses are short
- Simplicity preferred
- Network unstable

## Next Steps

- Learn about [Runs](runs.md) to create streamable executions
- Explore the [Client SDK](../products/client-sdk/) for streaming APIs
- See streaming examples in [Client SDK Examples](../products/client-sdk/examples.md)
