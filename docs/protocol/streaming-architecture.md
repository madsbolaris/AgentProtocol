# Streaming Architecture

This document explains how Agent Protocol handles streaming and complete content, the architectural decisions behind the design, and best practices for working with both.

## The Problem

During agent interactions, content can arrive in two fundamentally different ways:

1. **Complete/Buffered**: Content is fully assembled and ready to use (e.g., from storage, user input, or after streaming finishes)
2. **Streaming**: Content arrives incrementally as chunks during LLM generation or other async operations

Initially, using a single `TextContent` type for both cases created confusion:
- Is this `TextContent` complete or partial?
- Can I safely access the full `.text` property?
- When is it safe to serialize or store this content?

**The solution**: Separate type hierarchies for complete content and streaming chunks, with clear lifecycle stages.

---

## Architecture Overview

### Type Hierarchy

```
AIContentBase (base for all content)
├── AIContent (complete, finalized content)
│   ├── TextContent
│   ├── FunctionCallContent
│   ├── FunctionResultContent
│   ├── ErrorContent
│   └── ... (other complete types)
│
└── AIContentChunkBase (adds streaming metadata)
    └── AIContentChunk (streaming, partial content)
        ├── TextContentChunk
        ├── FunctionCallContentChunk
        ├── FunctionResultContentChunk
        ├── ErrorContentChunk
        └── ... (other chunk types)
```

### Key Types

**AIContent** - Union of all complete (non-chunked) content types
```typescript
union AIContent {
  TextContent,
  FunctionCallContent,
  FunctionResultContent,
  ErrorContent,
  // ... other complete types
}
```

**AIContentChunk** - Union of all chunk (partial) content types
```typescript
union AIContentChunk {
  TextContentChunk,
  FunctionCallContentChunk,
  FunctionResultContentChunk,
  ErrorContentChunk,
  // ... other chunk types
}
```

**IStreamable** - Union of both (used in middleware and streaming contexts)
```typescript
union IStreamable {
  AIContent,      // Complete content can be yielded
  AIContentChunk, // Chunks are streamed
}
```

---

## Lifecycle Stages

### Stage 1: Direct Creation (Complete Content)

Content created directly is immediately complete:

=== "Python"
    ```python
    from microsoft.agents.protocol import TextContent

    # Created with all data upfront
    content = TextContent(text="Hello world")
    print(content.text)  # ✅ Always safe: "Hello world"
    print(content.kind)  # "text"
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Protocol;

    // Created with all data upfront
    var content = new TextContent
    {
        Text = "Hello world"
    };
    Console.WriteLine(content.Text);  // ✅ Always safe: "Hello world"
    Console.WriteLine(content.Kind);  // "text"
    ```

=== "TypeScript"
    ```typescript
    import { TextContent } from '@microsoft/agents-protocol';

    // Created with all data upfront
    const content = new TextContent({
        text: "Hello world"
    });
    console.log(content.text);  // ✅ Always safe: "Hello world"
    console.log(content.kind);  // "text"
    ```

### Stage 2: Streaming (Chunks)

During streaming, only chunks exist:

=== "Python"
    ```python
    from microsoft.agents.protocol import TextContentChunk

    # During streaming - chunks arrive incrementally
    async for chunk in llm_stream:
        print(chunk.text)          # Partial text in this chunk
        print(chunk.kind)          # "textChunk"
        print(chunk.chunkIndex)    # Position in stream
        print(chunk.isLastChunk)   # True if final chunk
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Protocol;

    // During streaming - chunks arrive incrementally
    await foreach (var chunk in llmStream)
    {
        Console.WriteLine(chunk.Text);         // Partial text in this chunk
        Console.WriteLine(chunk.Kind);         // "textChunk"
        Console.WriteLine(chunk.ChunkIndex);   // Position in stream
        Console.WriteLine(chunk.IsLastChunk);  // True if final chunk
    }
    ```

=== "TypeScript"
    ```typescript
    import { TextContentChunk } from '@microsoft/agents-protocol';

    // During streaming - chunks arrive incrementally
    for await (const chunk of llmStream) {
        console.log(chunk.text);          // Partial text in this chunk
        console.log(chunk.kind);          // "textChunk"
        console.log(chunk.chunkIndex);    // Position in stream
        console.log(chunk.isLastChunk);   // True if final chunk
    }
    ```

### Stage 3: Assembly (Chunks → Complete)

After streaming finishes, assemble chunks into complete content:

=== "Python"
    ```python
    from microsoft.agents.protocol import TextContent, TextContentChunk

    # Collect chunks during streaming
    chunks = []
    full_text = ""
    async for chunk in llm_stream:
        chunks.append(chunk)
        full_text += chunk.text

    # Create complete content after stream ends
    content = TextContent(
        text=full_text,
        _chunks=chunks  # Optional: preserve original chunks
    )

    print(content.text)  # ✅ Complete text available
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Protocol;

    // Collect chunks during streaming
    var chunks = new List<TextContentChunk>();
    var fullText = new StringBuilder();
    await foreach (var chunk in llmStream)
    {
        chunks.Add(chunk);
        fullText.Append(chunk.Text);
    }

    // Create complete content after stream ends
    var content = new TextContent
    {
        Text = fullText.ToString(),
        Chunks = chunks  // Optional: preserve original chunks
    };

    Console.WriteLine(content.Text);  // ✅ Complete text available
    ```

=== "TypeScript"
    ```typescript
    import { TextContent, TextContentChunk } from '@microsoft/agents-protocol';

    // Collect chunks during streaming
    const chunks: TextContentChunk[] = [];
    let fullText = "";
    for await (const chunk of llmStream) {
        chunks.push(chunk);
        fullText += chunk.text;
    }

    // Create complete content after stream ends
    const content = new TextContent({
        text: fullText,
        _chunks: chunks  // Optional: preserve original chunks
    });

    console.log(content.text);  // ✅ Complete text available
    ```

---

## Helper Methods (SDK-Level)

SDKs provide convenience methods for assembly:

### From Stream (Assembly Helper)

=== "Python"
    ```python
    # Helper method to assemble from stream
    content = await TextContent.from_stream(llm_stream)
    print(content.text)  # Complete text

    # Or with explicit assembly
    async def assemble_text(stream: AsyncIterable[TextContentChunk]) -> TextContent:
        chunks = []
        full_text = ""
        async for chunk in stream:
            chunks.append(chunk)
            full_text += chunk.text
        return TextContent(text=full_text, _chunks=chunks)
    ```

=== "C#"
    ```csharp
    // Helper method to assemble from stream
    var content = await TextContent.FromStreamAsync(llmStream);
    Console.WriteLine(content.Text);  // Complete text

    // Or with explicit assembly
    public static async Task<TextContent> AssembleTextAsync(
        IAsyncEnumerable<TextContentChunk> stream)
    {
        var chunks = new List<TextContentChunk>();
        var fullText = new StringBuilder();
        await foreach (var chunk in stream)
        {
            chunks.Add(chunk);
            fullText.Append(chunk.Text);
        }
        return new TextContent
        {
            Text = fullText.ToString(),
            Chunks = chunks
        };
    }
    ```

=== "TypeScript"
    ```typescript
    // Helper method to assemble from stream
    const content = await TextContent.fromStream(llmStream);
    console.log(content.text);  // Complete text

    // Or with explicit assembly
    async function assembleText(
        stream: AsyncIterable<TextContentChunk>
    ): Promise<TextContent> {
        const chunks: TextContentChunk[] = [];
        let fullText = "";
        for await (const chunk of stream) {
            chunks.push(chunk);
            fullText += chunk.text;
        }
        return new TextContent({
            text: fullText,
            _chunks: chunks
        });
    }
    ```

### Iteration (Complete → Chunks)

Complete content can be iterated to yield chunks:

=== "Python"
    ```python
    # Complete content implements AsyncIterable[Chunk]
    content = TextContent(text="Hello world")

    # Iterate yields single chunk (or preserved chunks)
    async for chunk in content:
        print(chunk.text)  # "Hello world"
        print(chunk.isLastChunk)  # True
    ```

=== "C#"
    ```csharp
    // Complete content implements IAsyncEnumerable<Chunk>
    var content = new TextContent { Text = "Hello world" };

    // Iterate yields single chunk (or preserved chunks)
    await foreach (var chunk in content)
    {
        Console.WriteLine(chunk.Text);        // "Hello world"
        Console.WriteLine(chunk.IsLastChunk); // True
    }
    ```

=== "TypeScript"
    ```typescript
    // Complete content implements AsyncIterable<Chunk>
    const content = new TextContent({ text: "Hello world" });

    // Iterate yields single chunk (or preserved chunks)
    for await (const chunk of content) {
        console.log(chunk.text);          // "Hello world"
        console.log(chunk.isLastChunk);   // true
    }
    ```

---

## Chunk Preservation (Optional)

When assembling from chunks, SDKs can optionally preserve the original chunks for later re-streaming:

```python
# During assembly, preserve chunks
chunks = []
full_text = ""
async for chunk in llm_stream:
    chunks.append(chunk)
    full_text += chunk.text

# Create content that "remembers" its chunks
content = TextContent(text=full_text, _chunks=chunks)

# Later: re-iterate yields original chunks (zero-copy!)
async for chunk in content:
    await websocket.send(chunk)  # Send original 20 chunks, not synthetic one
```

**Benefits:**
- Lossless replay for logging/debugging
- Re-streaming preserves original chunking
- Zero-copy iteration when chunks are available

**Trade-offs:**
- Doubles memory usage (both full text and chunks)
- Optional - only enable when needed

---

## Type Safety Benefits

The separation provides compile-time safety:

=== "Python"
    ```python
    def save_to_database(content: TextContent):
        """Only accepts complete content."""
        db.save(content.text)  # ✅ Type-safe: always complete

    async def process_stream(chunks: AsyncIterable[TextContentChunk]):
        """Only accepts streaming chunks."""
        async for chunk in chunks:
            display(chunk.text)  # ✅ Type-safe: clearly partial

    # You can't pass a stream to save_to_database
    # You can't pass complete content to process_stream
    # The type system prevents mixing concerns
    ```

=== "C#"
    ```csharp
    void SaveToDatabase(TextContent content)
    {
        // Only accepts complete content
        db.Save(content.Text);  // ✅ Type-safe: always complete
    }

    async Task ProcessStreamAsync(IAsyncEnumerable<TextContentChunk> chunks)
    {
        // Only accepts streaming chunks
        await foreach (var chunk in chunks)
        {
            Display(chunk.Text);  // ✅ Type-safe: clearly partial
        }
    }

    // You can't pass a stream to SaveToDatabase
    // You can't pass complete content to ProcessStreamAsync
    // The type system prevents mixing concerns
    ```

=== "TypeScript"
    ```typescript
    function saveToDatabase(content: TextContent): void {
        // Only accepts complete content
        db.save(content.text);  // ✅ Type-safe: always complete
    }

    async function processStream(chunks: AsyncIterable<TextContentChunk>): Promise<void> {
        // Only accepts streaming chunks
        for await (const chunk of chunks) {
            display(chunk.text);  // ✅ Type-safe: clearly partial
        }
    }

    // You can't pass a stream to saveToDatabase
    // You can't pass complete content to processStream
    // The type system prevents mixing concerns
    ```

---

## Middleware Patterns

Middleware uses `IStreamable` to accept both complete and chunks:

=== "Python"
    ```python
    async def uppercase_middleware(
        content: AsyncIterable[TextContentChunk],  # Input: chunks
        thread: Thread
    ) -> AsyncIterable[IStreamable]:  # Output: chunks or complete
        async for chunk in content:
            chunk.text = chunk.text.upper()
            yield chunk  # Yield transformed chunk

    # Or buffer and yield complete
    async def buffer_middleware(
        content: AsyncIterable[TextContentChunk],
        thread: Thread
    ) -> AsyncIterable[IStreamable]:
        # Assemble complete content
        complete = await TextContent.from_stream(content)
        # Yield as single complete item
        yield complete
    ```

=== "C#"
    ```csharp
    async IAsyncEnumerable<IStreamable> UppercaseMiddleware(
        IAsyncEnumerable<TextContentChunk> content,  // Input: chunks
        Thread thread)
    {
        await foreach (var chunk in content)
        {
            chunk.Text = chunk.Text.ToUpper();
            yield return chunk;  // Yield transformed chunk
        }
    }

    // Or buffer and yield complete
    async IAsyncEnumerable<IStreamable> BufferMiddleware(
        IAsyncEnumerable<TextContentChunk> content,
        Thread thread)
    {
        // Assemble complete content
        var complete = await TextContent.FromStreamAsync(content);
        // Yield as single complete item
        yield return complete;
    }
    ```

=== "TypeScript"
    ```typescript
    async function* uppercaseMiddleware(
        content: AsyncIterable<TextContentChunk>,  // Input: chunks
        thread: Thread
    ): AsyncIterable<IStreamable> {  // Output: chunks or complete
        for await (const chunk of content) {
            chunk.text = chunk.text.toUpperCase();
            yield chunk;  // Yield transformed chunk
        }
    }

    // Or buffer and yield complete
    async function* bufferMiddleware(
        content: AsyncIterable<TextContentChunk>,
        thread: Thread
    ): AsyncIterable<IStreamable> {
        // Assemble complete content
        const complete = await TextContent.fromStream(content);
        // Yield as single complete item
        yield complete;
    }
    ```

---

## Best Practices

### 1. Use the Right Type

```python
# ✅ Good: Clear intent
def store_message(content: TextContent):
    """Store complete content to database."""
    pass

async def display_stream(chunks: AsyncIterable[TextContentChunk]):
    """Display streaming chunks to user."""
    pass

# ❌ Bad: Ambiguous
def process_content(content):  # Complete or streaming?
    pass
```

### 2. Assemble After Streaming

```python
# ✅ Good: Clear lifecycle
chunks = []
async for chunk in stream:
    chunks.append(chunk)
    display_partial(chunk.text)

# Stream complete - now assemble
content = TextContent.from_stream(chunks)
store_to_database(content)

# ❌ Bad: Trying to use incomplete data
content = None
async for chunk in stream:
    content = TextContent(text=chunk.text)  # Overwrites each time?
    store_to_database(content)  # Stores incomplete data
```

### 3. Preserve Chunks When Needed

```python
# ✅ Good: Preserve for replay
content = await TextContent.from_stream(llm_stream)  # Auto-preserves
await log_chunks(content)  # Re-streams original chunks

# ✅ Also Good: Don't preserve if not needed
content = TextContent(text="Direct creation")
# No chunks to preserve, saves memory
```

### 4. Type Annotations Matter

```python
# ✅ Good: Clear types
async def process(
    stream: AsyncIterable[TextContentChunk]
) -> TextContent:
    return await TextContent.from_stream(stream)

# ❌ Bad: Untyped
async def process(stream):  # What kind of stream?
    return await something(stream)  # What returns?
```

---

## Common Patterns

### Pattern 1: Stream → Store

```python
# Receive stream, assemble, store
async def handle_llm_response(stream: AsyncIterable[TextContentChunk]):
    # Stream to user in real-time
    chunks = []
    async for chunk in stream:
        chunks.append(chunk)
        await websocket.send(chunk.text)

    # After streaming complete, store
    content = TextContent.from_stream(chunks)
    await database.save_message(content)
```

### Pattern 2: Store → Stream

```python
# Retrieve from storage, stream to client
async def replay_message(message_id: str):
    # Load complete content
    content = await database.get_message(message_id)

    # Stream to client (yields original chunks if preserved)
    async for chunk in content:
        await websocket.send(chunk)
```

### Pattern 3: Middleware Buffering

```python
# Buffer entire stream, transform, yield complete
async def wait_for_complete(
    chunks: AsyncIterable[TextContentChunk],
    thread: Thread
) -> AsyncIterable[IStreamable]:
    # Assemble complete content
    content = await TextContent.from_stream(chunks)

    # Transform complete content
    content.text = transform(content.text)

    # Yield as single item
    yield content
```

---

## FAQ

### Q: When should I use complete vs chunk types?

**Complete types** (`TextContent`) when:
- Content is fully available
- Storing to database
- Serializing to JSON/XML
- Passing to functions that need full context

**Chunk types** (`TextContentChunk`) when:
- Content is streaming from LLM
- Processing partial updates in real-time
- Middleware transforming stream

### Q: Can I convert between complete and chunks?

Yes:
- **Chunks → Complete**: Use `TextContent.from_stream()` after streaming finishes
- **Complete → Chunks**: Iterate over complete content to yield chunks

### Q: Why preserve chunks?

Preserving original chunks enables:
- Lossless replay for debugging
- Re-streaming with original chunking
- Zero-copy iteration

But it doubles memory usage. Only preserve when needed.

### Q: What's `IStreamable`?

`IStreamable` is a union of complete content and chunks. Use it when you need to accept **either**:
- Middleware output (can yield chunks or complete items)
- Generic processing functions
- Storage that handles both

### Q: Are chunks serialized differently?

No - chunks serialize the same as complete content in XML/JSON. The chunk metadata (`chunkIndex`, `isLastChunk`) is marked `@xmlIgnore` and not serialized.

---

## Summary

The streaming architecture provides:

✅ **Type Safety** - Compile-time distinction between complete and partial content
✅ **Clear Lifecycle** - Explicit stages: streaming → assembly → storage
✅ **Flexibility** - Work with streams or complete content as needed
✅ **Zero-Copy Replay** - Optional chunk preservation for re-streaming
✅ **Middleware Composability** - Unified `IStreamable` interface

By separating complete and chunked content, Agent Protocol ensures you can't accidentally:
- Store incomplete data
- Access partial content as if it were complete
- Mix streaming and buffered concerns

The type system guides you to the correct usage patterns at compile time.
