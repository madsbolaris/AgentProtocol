# Client SDK Quickstart

**Send your first message in 5 minutes**

This quickstart walks you through the essential ways to interact with agents: simple completions, multimodal content, persistent conversations, tool usage, and streaming responses.

---

## Prerequisites

- An Agent Protocol API endpoint (or use the [emoji sample agent](../../examples/))
- API credentials (API key or OAuth2)
- Python 3.9+, Node.js 18+, or .NET 8+

---

## Installation

=== "Python"

    ```bash
    pip install microsoft-agents-protocol
    ```

=== "C#"

    ```bash
    dotnet add package Microsoft.Agents.Protocol.Client
    ```

=== "TypeScript"

    ```bash
    npm install @microsoft/agents-protocol-client
    ```

---

## Step 1: Simple Completion

The absolute simplest interaction - one line to get a response.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        # Create client with your endpoint
        client = AgentProtocolClient("http://localhost:5000")

        --8<-- "docs/snippets/python/client-simple-completion_main.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    // Create client with your endpoint
    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-simple-completion_main.cs"
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    // Create client with your endpoint
    const client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/typescript/client-simple-completion_main.ts"
    ```

**Expected Output:**

```xml
<agent thread-id="thread_abc123">
  I can help you with analysis, writing, coding, research, and problem-solving tasks.
</agent>
```

!!! tip "What this does"
    - Uses the server's default agent
    - Creates an ephemeral thread (no state persisted)
    - Returns the complete response when finished

---

## Step 2: Sending Multimodal Content

Send images, files, or other media along with text to the agent.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient, ImageContent

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Send a message with an image
        response = await client.complete_chat(
            contents=[
                {"type": "text", "text": "What's in this image?"},
                {"type": "image", "uri": "https://example.com/photo.jpg"}
            ]
        )
        print(f"Agent: {response.text}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    // Send a message with an image
    var response = await client.CompleteChatAsync(new[]
    {
        new TextContent { Text = "What's in this image?" },
        new ImageContent { Uri = "https://example.com/photo.jpg" }
    });

    Console.WriteLine($"Agent: {response.Text}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    // Send a message with an image
    const response = await client.completeChat([
        { type: "text", text: "What's in this image?" },
        { type: "image", uri: "https://example.com/photo.jpg" }
    ]);

    console.log(`Agent: ${response.text}`);
    ```

**Output:**

```xml
<agent thread-id="thread_def456">
  This image shows the Eiffel Tower in Paris during sunset, with beautiful orange and pink hues in the sky.
</agent>
```

!!! tip "What this does"
    - Sends multiple content types in a single message
    - Agent can analyze images, documents, audio, and more
    - Content can be URLs or base64-encoded data

---

## Step 3: Persistent Conversations

Maintain conversation context across multiple turns automatically.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        --8<-- "docs/snippets/python/client-conversation_main.py"

        # Save thread ID to resume later
        print(f"Thread ID: {conversation.thread_id}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-conversation_main.cs"

    // Save thread ID to resume later
    Console.WriteLine($"Thread ID: {conversation.ThreadId}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/typescript/client-conversation_main.ts"
    ```

**Output:**

First message:

```xml
<agent thread-id="thread_abc123">
  Nice to meet you, Alice! How can I help you today?
</agent>
```

Second message:

```xml
<agent thread-id="thread_abc123">
  Your name is Alice.
</agent>
```

!!! tip "What this does"
    - Creates a persistent thread on the server
    - Maintains full conversation history automatically
    - No manual thread management required

**Resume later:**

=== "Python"

    ```python
    --8<-- "docs/snippets/python/client-resume-conversation_main.py"
    ```

=== "C#"

    ```csharp
    --8<-- "docs/snippets/csharp/client-resume-conversation_main.cs"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "docs/snippets/typescript/client-resume-conversation_main.ts"
    ```

---

## Step 4: Tools/Functions

Register tools that agents can call automatically.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient, ToolCollection

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        --8<-- "docs/snippets/python/client-tools_main.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-tools_main.cs"
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, ToolCollection } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/typescript/client-tools_main.ts"
    ```

**Output:**

```xml
<thread thread-id="thread_xyz789">
  <agent>
    <function-call call-id="call_abc123" name="get_weather">
      {"location":"Seattle"}
    </function-call>
  </agent>
  <tool call-id="call_abc123">
    {"temperature": "72°F", "condition": "sunny", "location": "Seattle"}
  </tool>
  <agent>
    The weather in Seattle is sunny and 72°F
  </agent>
</thread>
```

!!! tip "What this does"
    - Registers tools with simple lambda functions
    - SDK automatically executes when agent requests
    - Returns final response with tool results incorporated

---

## Step 5: Streaming Responses

Stream responses in real-time for better user experience.

!!! info "Learning Path"
    The recommended order is: Step 1 (Simple) → Step 2 (Multimodal) → Step 3 (Conversations) → Step 4 (Tools) → Step 5 (Streaming). Learn non-streaming patterns first, then progress to streaming.

### Simple Text Streaming

Get tokens as they're generated (typewriter effect).

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        --8<-- "docs/snippets/python/client-streaming_main.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-streaming_main.cs"
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/typescript/client-streaming_main.ts"
    ```

**You'll see tokens appear progressively:**

```text
Agent: Once upon a time, there was a curious robot named Byte who loved to explore...
```

!!! tip "What this does"
    - Streams text as it's generated (real-time)
    - Callback fires for each text chunk
    - Perfect for building responsive UIs

### Rich Content Streaming

Handle multiple content types like text and images in a single message stream.

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient

    client = AgentProtocolClient("http://localhost:5000")

    # Stream messages with multiple content types
    async for message in client.stream_messages("Show me a photo of Paris and describe it"):
        async for content in message.stream_contents():
            if content.kind == "text":
                # Text streams incrementally
                print(content.text, end="", flush=True)
            elif content.kind == "image":
                # Image URI becomes available when ready
                print(f"\n[Image: {content.uri}]")
        print()  # New line after message
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    await foreach (var message in client.StreamMessagesAsync("Show me a photo of Paris and describe it"))
    {
        await foreach (var content in message.StreamContentsAsync())
        {
            switch (content)
            {
                case TextContent text:
                    // Text streams incrementally
                    Console.Write(text.Text);
                    break;

                case ImageContent image:
                    // Image URI becomes available when ready
                    Console.WriteLine($"\n[Image: {image.Uri}]");
                    break;
            }
        }
        Console.WriteLine(); // New line after message
    }
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    for await (const message of client.streamMessages("Show me a photo of Paris and describe it")) {
        for await (const content of message.streamContents()) {
            switch (content.kind) {
                case "text":
                    // Text streams incrementally
                    process.stdout.write(content.text);
                    break;

                case "image":
                    // Image URI becomes available when ready
                    console.log(`\n[Image: ${content.uri}]`);
                    break;
            }
        }
        console.log(); // New line after message
    }
    ```

**Output:**

```text
Here's a beautiful view of the Eiffel Tower at sunset.
[Image: https://example.com/paris-eiffel-tower.jpg]
```

!!! tip "What this does"
    - Text streams as it's generated (typewriter effect)
    - Images, audio, and other media appear when ready
    - Single message can contain multiple content types
    - Simple pattern scales to any content type

!!! info "More Content Types"
    The SDK supports 20+ content types: audio, video, documents, function calls, typing indicators, reactions (metadata about previous messages), and more. See the [Multimodal Content Guide](../how-to/multimodal/) for advanced examples.

### Thread Streaming

Monitor a thread for messages from all participants - users, agents, and other clients.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")
        thread_id = "thread_abc123"

        # Stream all messages on the thread in real-time
        async for message in client.stream_thread_messages(thread_id):
            sender = message.role  # 'user' or 'agent'
            text = message.contents[0].text if message.contents else ""
            print(f"{sender}: {text}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");
    var threadId = "thread_abc123";

    // Stream all messages on the thread in real-time
    await foreach (var message in client.StreamThreadMessagesAsync(threadId))
    {
        var sender = message.Role;  // "user" or "agent"
        var text = message.Contents.Count > 0 ? message.Contents[0].Text : "";
        Console.WriteLine($"{sender}: {text}");
    }
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");
    const threadId = "thread_abc123";

    // Stream all messages on the thread in real-time
    for await (const message of client.streamThreadMessages(threadId)) {
        const sender = message.role;  // 'user' or 'agent'
        const text = message.contents[0]?.text || "";
        console.log(`${sender}: ${text}`);
    }
    ```

**Output:**

```text
user: What's the weather in Paris?
agent: Let me check that for you...
agent: The current weather in Paris is 18°C and partly cloudy.
user: Thanks!
```

!!! tip "Use Cases"
    - **Multi-user chat**: Monitor group conversations with multiple users
    - **Collaborative agents**: Watch thread for messages from multiple agents
    - **Real-time notifications**: Get notified when anyone posts to the thread
    - **Chat UI**: Build responsive chat interfaces that update in real-time

---

## Complete Example

Here's a full example combining all concepts:

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Simple completion
        print("=== Simple Completion ===")
        response = await client.complete_chat("Hello!")
        print(response)  # Prints XML response
        print(f"\nAgent: {response.text}\n")  # Extract just the text

        # Streaming
        print("=== Streaming ===")
        print("Agent: ", end="", flush=True)
        await client.stream_chat(
            "Count to 5",
            on_text_chunk=lambda text: print(text, end="", flush=True)
        )
        print("\n")

        # Conversation
        print("=== Conversation ===")
        conversation = client.create_conversation()

        msg1 = await conversation.send("Hi, I'm learning about planets")
        print(f"Agent: {msg1.text}")

        msg2 = await conversation.send("Tell me about Mars")
        print(f"Agent: {msg2.text}")

        print(f"Thread: {conversation.thread_id}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        static async Task Main()
        {
            var client = new AgentProtocolClient("http://localhost:5000");

            // Simple completion
            Console.WriteLine("=== Simple Completion ===");
            var response = await client.CompleteChatAsync("Hello!");
            Console.WriteLine(response);  // Prints XML response
            Console.WriteLine($"\nAgent: {response.Text}\n");  // Extract just the text

            // Streaming
            Console.WriteLine("=== Streaming ===");
            Console.Write("Agent: ");
            await client.StreamChatAsync(
                "Count to 5",
                onTextChunk: text => Console.Write(text)
            );
            Console.WriteLine("\n");

            // Conversation
            Console.WriteLine("=== Conversation ===");
            var conversation = client.CreateConversation();

            var msg1 = await conversation.SendAsync("Hi, I'm learning about planets");
            Console.WriteLine($"Agent: {msg1.Text}");

            var msg2 = await conversation.SendAsync("Tell me about Mars");
            Console.WriteLine($"Agent: {msg2.Text}");

            Console.WriteLine($"Thread: {conversation.ThreadId}");
        }
    }
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    async function main() {
        const client = new AgentProtocolClient("http://localhost:5000");

        // Simple completion
        console.log("=== Simple Completion ===");
        const response = await client.completeChat("Hello!");
        console.log(response);  // Prints XML response
        console.log(`\nAgent: ${response.text}\n`);  // Extract just the text

        // Streaming
        console.log("=== Streaming ===");
        process.stdout.write("Agent: ");
        await client.streamChat(
            "Count to 5",
            { onTextChunk: (text) => process.stdout.write(text) }
        );
        console.log("\n");

        // Conversation
        console.log("=== Conversation ===");
        const conversation = client.createConversation();

        const msg1 = await conversation.send("Hi, I'm learning about planets");
        console.log(`Agent: ${msg1.text}`);

        const msg2 = await conversation.send("Tell me about Mars");
        console.log(`Agent: ${msg2.text}`);

        console.log(`Thread: ${conversation.threadId}`);
    }

    main();
    ```

---

## Next Steps

Now that you've completed the quickstart, explore these topics:

::cards:: cols=4

- title: Core Concepts
  eyebrow: LEARN
  description: Understand runs, threads, and streaming
  url: concepts/

- title: How-To Guides
  eyebrow: GUIDES
  description: Authentication, error handling, multimodal content
  url: how-to/

- title: Multimodal Content
  eyebrow: MEDIA
  description: Send images, audio, files to agents
  url: how-to/multimodal/

- title: Advanced Tools
  eyebrow: ADVANCED
  description: Complex tool patterns and orchestration
  url: how-to/tools/

::/cards::

## Advanced Topics & Integrations

Explore advanced features and integrations to build powerful agent applications:

::cards:: cols=3

- title: Framework Integrations
  eyebrow: UI
  description: React, Vue, Angular components for seamless UI integration
  url: "#"

- title: Multi-Agent Systems
  eyebrow: COLLABORATION
  description: Build teams of agents that work together on complex tasks
  url: "#"

- title: Planning & Orchestration
  eyebrow: WORKFLOWS
  description: Auto-plan and execute multi-step workflows
  url: "#"

- title: Agent Roles & Personalities
  eyebrow: CONFIGURATION
  description: Configure agent behavior, goals, and backstories
  url: "#"

- title: Observability & Tracing
  eyebrow: MONITORING
  description: Monitor, trace, and debug agent interactions
  url: "#"

- title: Service Integrations
  eyebrow: CONNECT
  description: Connect to databases, APIs, and popular services
  url: "#"

::/cards::

**Questions?** Check the [FAQ](../../community/#faq) or [open a discussion](https://github.com/madsbolaris/AgentProtocol/discussions).
