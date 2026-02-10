# Streaming

Real-time streaming allows you to receive agent responses token-by-token as they're generated, rather than waiting for the complete response.

## Why Use Streaming?

**Benefits:**
- ✅ Better user experience with immediate feedback
- ✅ Reduced perceived latency
- ✅ Ability to cancel long-running operations
- ✅ Real-time progress monitoring

**Use streaming when:**
- Building chat interfaces where users expect instant responses
- Generating long-form content (articles, emails, reports)
- Processing requests that take >2 seconds

**Don't use streaming when:**
- You need the complete response for processing
- Building batch operations
- The response is very short (<50 tokens)

## Basic Streaming

=== "Python"
    ```python
    from microsoft.agents.protocol import AgentProtocolClient
    import asyncio

    async def stream_example():
        client = AgentProtocolClient("http://localhost:3978")

        # Stream chat response
        async for chunk in client.stream_chat("Tell me a story"):
            print(chunk, end="", flush=True)
        print()  # New line when done

    asyncio.run(stream_example())
    ```

=== "TypeScript"
    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol';

    async function streamExample() {
        const client = new AgentProtocolClient("http://localhost:3978");

        // Stream chat response
        for await (const chunk of client.streamChat("Tell me a story")) {
            process.stdout.write(chunk);
        }
        console.log(); // New line when done
    }
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Protocol.Client;

    async Task StreamExample()
    {
        using var client = new AgentProtocolClient("http://localhost:3978");

        // Stream chat response
        await foreach (var chunk in client.StreamChatAsync("Tell me a story"))
        {
            Console.Write(chunk);
        }
        Console.WriteLine(); // New line when done
    }
    ```

## Streaming with Callbacks

For more control over streaming events:

=== "Python"
    ```python
    async def on_chunk(text: str):
        print(text, end="", flush=True)

    async def on_complete():
        print("\n[Stream complete]")

    await client.stream_chat(
        "Explain quantum computing",
        on_text_chunk=on_chunk,
        on_complete=on_complete
    )
    ```

=== "TypeScript"
    ```typescript
    await client.streamChat("Explain quantum computing", {
        onTextChunk: (text) => process.stdout.write(text),
        onComplete: () => console.log("\n[Stream complete]")
    });
    ```

=== "C#"
    ```csharp
    await client.StreamChatAsync(
        "Explain quantum computing",
        onTextChunk: text => Console.Write(text),
        onComplete: () => Console.WriteLine("\n[Stream complete]")
    );
    ```

## Streaming with Conversations

Stream responses in multi-turn conversations:

=== "Python"
    ```python
    conversation = client.create_conversation()

    # First message
    async for chunk in conversation.stream_user_message("What's AI?"):
        print(chunk, end="", flush=True)
    print()

    # Follow-up
    async for chunk in conversation.stream_user_message("Give an example"):
        print(chunk, end="", flush=True)
    print()
    ```

=== "TypeScript"
    ```typescript
    const conversation = client.createConversation();

    // First message
    for await (const chunk of conversation.streamUserMessage("What's AI?")) {
        process.stdout.write(chunk);
    }
    console.log();

    // Follow-up
    for await (const chunk of conversation.streamUserMessage("Give an example")) {
        process.stdout.write(chunk);
    }
    console.log();
    ```

=== "C#"
    ```csharp
    var conversation = client.CreateConversation();

    // First message
    await foreach (var chunk in conversation.StreamUserMessageAsync("What's AI?"))
    {
        Console.Write(chunk);
    }
    Console.WriteLine();

    // Follow-up
    await foreach (var chunk in conversation.StreamUserMessageAsync("Give an example"))
    {
        Console.Write(chunk);
    }
    Console.WriteLine();
    ```

## Error Handling in Streams

Handle errors gracefully during streaming:

=== "Python"
    ```python
    try:
        async for chunk in client.stream_chat("Your question"):
            print(chunk, end="", flush=True)
    except ConnectionError as e:
        print(f"\n[Connection lost: {e}]")
    except TimeoutError:
        print("\n[Request timed out]")
    finally:
        print()
    ```

=== "TypeScript"
    ```typescript
    try {
        for await (const chunk of client.streamChat("Your question")) {
            process.stdout.write(chunk);
        }
    } catch (error) {
        if (error instanceof ConnectionError) {
            console.error("\n[Connection lost]");
        } else if (error instanceof TimeoutError) {
            console.error("\n[Request timed out]");
        }
    } finally {
        console.log();
    }
    ```

=== "C#"
    ```csharp
    try
    {
        await foreach (var chunk in client.StreamChatAsync("Your question"))
        {
            Console.Write(chunk);
        }
    }
    catch (ConnectionException ex)
    {
        Console.WriteLine($"\n[Connection lost: {ex.Message}]");
    }
    catch (TimeoutException)
    {
        Console.WriteLine("\n[Request timed out]");
    }
    finally
    {
        Console.WriteLine();
    }
    ```

## Cancellation

Cancel streaming operations when needed:

=== "Python"
    ```python
    import asyncio

    async def cancelable_stream():
        try:
            async for chunk in client.stream_chat(
                "Write a long essay",
                timeout=30.0
            ):
                print(chunk, end="", flush=True)

                # Cancel after certain condition
                if "stop word" in chunk:
                    break
        except asyncio.CancelledError:
            print("\n[Stream cancelled]")
    ```

=== "TypeScript"
    ```typescript
    const controller = new AbortController();

    // Cancel after 5 seconds
    setTimeout(() => controller.abort(), 5000);

    try {
        for await (const chunk of client.streamChat(
            "Write a long essay",
            { signal: controller.signal }
        )) {
            process.stdout.write(chunk);
        }
    } catch (error) {
        if (error.name === 'AbortError') {
            console.log("\n[Stream cancelled]");
        }
    }
    ```

=== "C#"
    ```csharp
    using var cts = new CancellationTokenSource();

    // Cancel after 5 seconds
    cts.CancelAfter(TimeSpan.FromSeconds(5));

    try
    {
        await foreach (var chunk in client.StreamChatAsync(
            "Write a long essay",
            cancellationToken: cts.Token
        ))
        {
            Console.Write(chunk);
        }
    }
    catch (OperationCanceledException)
    {
        Console.WriteLine("\n[Stream cancelled]");
    }
    ```

## Best Practices

### Do:
- ✅ Handle connection errors gracefully
- ✅ Provide visual feedback (loading indicators, cursor)
- ✅ Implement cancellation for long operations
- ✅ Buffer small chunks to reduce UI updates

### Don't:
- ❌ Block the UI thread while streaming
- ❌ Ignore error states
- ❌ Stream without timeout limits
- ❌ Forget to cleanup resources

## Performance Tips

1. **Buffer Small Chunks**: Reduce UI updates by buffering
   ```python
   buffer = ""
   async for chunk in stream:
       buffer += chunk
       if len(buffer) > 50:  # Update every 50 chars
           print(buffer, end="", flush=True)
           buffer = ""
   ```

2. **Set Appropriate Timeouts**: Prevent hanging connections
   ```python
   client = AgentProtocolClient(base_url, timeout=60.0)
   ```

3. **Use Cancellation Tokens**: Allow users to stop long operations
   ```python
   async for chunk in stream:
       if user_cancelled:
           break
   ```

## Next Steps

- [Tool Execution](tools.md) - Using tools during streaming
- [Error Handling](error-handling.md) - Complete error handling guide
- [Runs, Threads, Messages](runs-threads-messages.md) - Understanding the data model
