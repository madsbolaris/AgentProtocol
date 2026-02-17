# Quickstart

Build production-ready AI agents that handle conversations, call tools, and scale automatically.

**This version uses the `next()` callback approach** similar to Express.js, Koa, and ASP.NET Core middleware.

---

## Prerequisites & Setup

### What You Need

- .NET 8+ SDK, Python 3.9+, or Node.js 18+
- An LLM API key (OpenAI, Azure OpenAI, Anthropic, etc.)

### Get Your API Key

=== "Python"

    ```bash
    # For OpenAI
    export OPENAI_API_KEY="sk-..."

    # Or create .env file
    echo "OPENAI_API_KEY=sk-..." > .env
    ```

=== "C#"

    ```json
    // appsettings.json
    {
      "OpenAI": {
        "ApiKey": "sk-..."
      }
    }
    ```

=== "TypeScript"

    ```bash
    # .env file
    OPENAI_API_KEY=sk-...
    ```



### Installation

=== "Python"

    ```bash
    pip install microsoft-agents-protocol-hosting
    pip install python-dotenv  # For loading .env
    ```

=== "C#"

    ```bash
    dotnet add package Microsoft.Agents.Protocol.Hosting
    ```

=== "TypeScript"

    ```bash
    npm install @microsoft/agents-protocol-hosting
    npm install dotenv
    ```

---

## Step 1: Hello World

Create your first agent in under 2 minutes.

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    import os

    --8<-- test::quickstart/hosting-hello-world
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    --8<-- test::quickstart/hosting-hello-world
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    --8<-- test::quickstart/hosting-hello-world
    ```

**Test it:**

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient

    async def test():
        client = AgentProtocolClient("http://localhost:5000")
        response = await client.complete_chat("Hello!")
        print(f"Agent: {response.text}")

    import asyncio
    asyncio.run(test())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");
    var response = await client.CompleteChatAsync("Hello!");
    Console.WriteLine($"Agent: {response.Text}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol';

    const client = new AgentProtocolClient("http://localhost:5000");
    const response = await client.completeChat("Hello!");
    console.log(`Agent: ${response.text}`);
    ```

**Output:**

```text
Agent: Hello! How can I help you today?
```

🎉 **Congratulations!** You've built your first agent. The LLM automatically handles incoming messages and generates responses.

---

## Step 2: Multi-Agent Support

Register multiple specialized agents and route requests to the right agent based on capabilities.

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    import os

    # Create agent host
    host = AgentHost()

    # Register a weather expert agent (default)
    weather_config = AgentConfig(
        agent_id="weather-agent",
        model="gpt-4",
        api_key=os.environ["OPENAI_API_KEY"],
        instructions="You are a weather expert. Provide accurate weather information and forecasts.",
        is_default=True  # This agent handles requests without explicit agent_id
    )
    host.add_agent(weather_config)

    # Register a travel planning agent
    travel_config = AgentConfig(
        agent_id="travel-agent",
        model="gpt-4",
        api_key=os.environ["OPENAI_API_KEY"],
        instructions="You are a travel planning assistant. Help users plan trips and find destinations."
    )
    host.add_agent(travel_config)

    # Start the server
    host.run(port=5000)
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    var builder = WebApplication.CreateBuilder(args);

    // Register multiple agents
    builder.Services
        .AddAgentHost()
        .AddAgent("weather-agent", config =>
        {
            config.Model = "gpt-4";
            config.Instructions = "You are a weather expert. Provide accurate weather information and forecasts.";
            config.IsDefault = true;  // This agent handles requests without explicit agent_id
        })
        .AddAgent("travel-agent", config =>
        {
            config.Model = "gpt-4";
            config.Instructions = "You are a travel planning assistant. Help users plan trips and find destinations.";
        });

    var app = builder.Build();
    app.MapAgentProtocol();
    app.Run();
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    const host = new AgentHost();

    // Register a weather expert agent (default)
    host.addAgent({
        agentId: "weather-agent",
        model: "gpt-4",
        apiKey: process.env.OPENAI_API_KEY!,
        instructions: "You are a weather expert. Provide accurate weather information and forecasts.",
        isDefault: true  // This agent handles requests without explicit agent_id
    });

    // Register a travel planning agent
    host.addAgent({
        agentId: "travel-agent",
        model: "gpt-4",
        apiKey: process.env.OPENAI_API_KEY!,
        instructions: "You are a travel planning assistant. Help users plan trips and find destinations."
    });

    // Start the server
    host.listen(5000);
    ```

**Test it from the client:**

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Create a conversation (uses default agent: weather-agent)
        conversation = client.create_conversation()

        # First message goes to default weather agent
        response1 = await conversation.send("What's the weather in Paris?")
        print(f"Weather: {response1.text}")

        # Switch to travel agent for same conversation
        response2 = await conversation.send(
            "Plan a 3-day trip there",
            agent_id="travel-agent"
        )
        print(f"Travel: {response2.text}")

        # Back to weather agent (uses conversation's default)
        response3 = await conversation.send("What should I pack?")
        print(f"Weather: {response3.text}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    // Create a conversation (uses default agent: weather-agent)
    var conversation = client.CreateConversation();

    // First message goes to default weather agent
    var response1 = await conversation.SendAsync("What's the weather in Paris?");
    Console.WriteLine($"Weather: {response1.Text}");

    // Switch to travel agent for same conversation
    var response2 = await conversation.SendAsync(
        "Plan a 3-day trip there",
        agentId: "travel-agent"
    );
    Console.WriteLine($"Travel: {response2.Text}");

    // Back to weather agent (uses conversation's default)
    var response3 = await conversation.SendAsync("What should I pack?");
    Console.WriteLine($"Weather: {response3.Text}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    // Create a conversation (uses default agent: weather-agent)
    const conversation = client.createConversation();

    // First message goes to default weather agent
    const response1 = await conversation.send("What's the weather in Paris?");
    console.log(`Weather: ${response1.text}`);

    // Switch to travel agent for same conversation
    const response2 = await conversation.send(
        "Plan a 3-day trip there",
        { agentId: "travel-agent" }
    );
    console.log(`Travel: ${response2.text}`);

    // Back to weather agent (uses conversation's default)
    const response3 = await conversation.send("What should I pack?");
    console.log(`Weather: ${response3.text}`);
    ```

!!! tip "What this does"
    - Multiple agents can coexist on the same server
    - Mark one agent as default with `is_default=True` (or `IsDefault`, `isDefault`)
    - If no default is set, the first agent added becomes the default
    - Default agent handles requests that don't specify an `agent_id`
    - Clients can explicitly route to any agent using `agent_id` parameter
    - Each agent has its own model, instructions, and tools
    - Agents can share the same thread for context continuity

---

## Step 3: Adding Tools

Agents become powerful when they can call functions to get real-time data or take actions.

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    import os
    from datetime import datetime, timezone

    --8<-- test::quickstart/hosting-adding-tools
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    --8<-- test::quickstart/hosting-adding-tools
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    --8<-- test::quickstart/hosting-adding-tools
    ```

### Error Handling in Tools

Tools should handle errors gracefully and return error messages that the LLM can explain to the user:

=== "Python"

    ```python
    import httpx

    --8<-- test::quickstart/hosting-tool-error-handling
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    --8<-- test::quickstart/hosting-tool-error-handling
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    --8<-- test::quickstart/hosting-tool-error-handling
    ```

---

## Step 4: Client-Provided Functions

Allow clients to provide their own function implementations that the agent can call.

### Server Configuration

Configure your agent to accept client-provided functions:

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig

    --8<-- test::quickstart/hosting-client-functions
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    --8<-- test::quickstart/hosting-client-functions
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    --8<-- test::quickstart/hosting-client-functions
    ```

### Client Implementation

Clients provide function implementations when sending messages:

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient, ToolCollection
    import os

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Define client-side tool implementations
        tools = ToolCollection()

        @tools.function("send_email")
        async def send_email(to: str, subject: str, body: str = "") -> str:
            """Send an email via user's email client"""
            print(f"📧 Sending email to {to}: {subject}")
            return "Email sent successfully"

        @tools.function("get_local_files")
        async def get_local_files() -> str:
            """List files in user's current directory"""
            files = os.listdir(".")
            return f"Found {len(files)} files: {', '.join(files[:5])}"

        # Send message with client-provided tools
        response = await client.complete_chat(
            "Send an email to bob@example.com with subject 'Meeting' and list my local files",
            tools=tools
        )
        print(response)

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;
    using System.IO;

    var client = new AgentProtocolClient("http://localhost:5000");

    // Define client-side tool implementations
    var tools = new ToolCollection()
        .Add("send_email", "Send an email via user's email client",
            (string to, string subject, string body = "") =>
            {
                Console.WriteLine($"📧 Sending email to {to}: {subject}");
                return "Email sent successfully";
            })
        .Add("get_local_files", "List files in user's current directory",
            () =>
            {
                var files = Directory.GetFiles(".");
                return $"Found {files.Length} files: {string.Join(", ", files.Take(5))}";
            });

    // Send message with client-provided tools
    var response = await client.CompleteChatAsync(
        "Send an email to bob@example.com with subject 'Meeting' and list my local files",
        tools: tools
    );
    Console.WriteLine(response.Text);
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, ToolCollection } from '@microsoft/agents-protocol-client';
    import * as fs from 'fs';

    const client = new AgentProtocolClient("http://localhost:5000");

    // Define client-side tool implementations
    const tools = new ToolCollection()
        .add("send_email", "Send an email via user's email client",
            async (to: string, subject: string, body: string = "") => {
                console.log(`📧 Sending email to ${to}: ${subject}`);
                return "Email sent successfully";
            })
        .add("get_local_files", "List files in user's current directory",
            async () => {
                const { readdir } = await import('fs/promises');
                const files = await readdir('.');
                return `Found ${files.length} files: ${files.slice(0, 5).join(', ')}`;
            });

    // Send message with client-provided tools
    const response = await client.completeChat(
        "Send an email to bob@example.com with subject 'Meeting' and list my local files",
        { tools }
    );
    console.log(response.text);
    ```

**Expected Output:**

```xml
<thread thread-id="thread_abc123">
  <agent>
    <function-call call-id="call_001" name="send_email">
      {"to":"bob@example.com","subject":"Meeting","body":""}
    </function-call>
    <function-call call-id="call_002" name="get_local_files">
      {}
    </function-call>
  </agent>
  <tool call-id="call_001">
    Email sent successfully
  </tool>
  <tool call-id="call_002">
    Found 15 files: file1.txt, file2.py, README.md, config.json, package.json
  </tool>
  <agent>
    I've sent an email to bob@example.com with subject 'Meeting'. You have 15 files in your current directory including: file1.txt, file2.py, README.md, config.json, and package.json.
  </agent>
</thread>
```

---

## Step 5: Understanding Middleware

Middleware lets you intercept and modify messages **before and after** they're processed. Think of it as a pipeline where you control each stage.

### Middleware Types

There are two types of middleware:

1. **`Middleware<T>`** - Default (80% of cases)
   - Processes and yields items from a stream
   - No `next()` callback overhead
   - Use for transforming, filtering, or augmenting content

2. **`ChainedMiddleware<T>`** - Advanced (20% of cases)
   - Includes `next()` callback for before/after processing
   - Use for timing, error handling, resource management

**When to Use Which?**

| Pattern                     | Use Case                                          | Example                                         |
|-----------------------------|---------------------------------------------------|-------------------------------------------------|
| **`Middleware<T>`**         | Transform content, filter items, augment messages | Uppercase text, command routing, add context    |
| **`ChainedMiddleware<T>`**  | Before/after logic, timing, error boundaries      | Performance monitoring, exception handling      |

### Your First Middleware

Let's build a simple command router that intercepts commands (like `/help`) and handles them without calling the LLM.

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    from microsoft.agents.protocol import TextContent, Thread, IStreamable
    from typing import AsyncIterable
    import os

    --8<-- test::quickstart/hosting-command-router
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;
    using Microsoft.Agents.Protocol.Hosting;
    using System.Runtime.CompilerServices;

    --8<-- test::quickstart/hosting-command-router
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { TextContent, Thread, IStreamable } from '@microsoft/agents-protocol';

    --8<-- test::quickstart/hosting-command-router
    ```

**Example Output:**

When a client sends `/help`:

```
Available commands:
/help - Show this help
```

When a client sends "Hello, how are you?" (not a command), it passes through to the LLM normally.

### Processing Multimodal Content in Middleware

Use content middleware to process specific content types. This allows you to augment the LLM's capabilities by converting system events, channel events, or custom content types into messages the agent can understand.

=== "Python"

    ```python
    from microsoft.agents.protocol import (
        MessageReactionContent,
        DeveloperMessage,
        TextContent,
        Thread,
        IStreamable
    )
    from typing import AsyncIterable

    --8<-- test::quickstart/hosting-reaction-handler
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;
    using System.Runtime.CompilerServices;

    --8<-- test::quickstart/hosting-reaction-handler
    ```

=== "TypeScript"

    ```typescript
    import { MessageReactionContent, DeveloperMessage, TextContent, Thread, IStreamable } from '@microsoft/agents-protocol';

    --8<-- test::quickstart/hosting-reaction-handler
    ```

### Streaming Processing

Process content chunk-by-chunk as it streams in real-time. This uses the default `Middleware<T>` type without the `next()` callback.

**Signature:**

=== "Python"

    ```python
    from typing import TypeAlias, Callable, AsyncIterable, TypeVar

    T = TypeVar('T', bound=IStreamable)

    # Generic type alias for simple middleware
    Middleware: TypeAlias = Callable[
        [AsyncIterable[T], Thread],
        AsyncIterable[IStreamable]
    ]

    # Use with specific content type
    uppercase: Middleware[TextContentChunk] = async def (stream, thread):
        # Your implementation
    ```

=== "TypeScript"

    ```typescript
    import { Thread, IStreamable, TextContentChunk } from '@microsoft/agents-protocol';

    // Generic type alias for simple middleware
    type Middleware<T extends IStreamable = IStreamable> = (
        stream: AsyncIterable<T>,
        thread: Thread
    ) => AsyncIterable<IStreamable>;

    // Use with specific content type
    const uppercase: Middleware<TextContentChunk> = async function* (stream, thread) {
        // Your implementation
    };
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    // Generic delegate for simple middleware
    public delegate IAsyncEnumerable<IStreamable> Middleware<T>(
        IAsyncEnumerable<T> stream,
        Thread thread
    ) where T : IStreamable;

    // Use with specific content type
    Middleware<TextContentChunk> uppercase = async (stream, thread) =>
    {
        // Your implementation
    };
    ```

**Example:**

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable

    --8<-- test::quickstart/hosting-streaming-middleware
    ```

=== "C#"

    ```csharp
    using System.Runtime.CompilerServices;

    --8<-- test::quickstart/hosting-streaming-middleware
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { TextContent, Thread } from '@microsoft/agents-protocol';

    --8<-- test::quickstart/hosting-streaming-middleware
    ```

### Before and After Middleware

Use the `next()` callback pattern when you need to execute code **before** the middleware chain starts and **after** it completes. This is essential for timing, error handling, and resource management.

**Signature:**

=== "Python"

    ```python
    from typing import TypeAlias, Callable, Awaitable, AsyncIterable, TypeVar

    T = TypeVar('T', bound=IStreamable)

    # Generic type alias for chained middleware
    ChainedMiddleware: TypeAlias = Callable[
        [AsyncIterable[T], Thread,
         Callable[[AsyncIterable[IStreamable]], Awaitable[AsyncIterable[T]]]],
        AsyncIterable[IStreamable]
    ]

    # Use with specific content type
    time_streaming: ChainedMiddleware[TextContentChunk] = async def (stream, thread, next):
        # Your implementation
    ```

=== "TypeScript"

    ```typescript
    import { Thread, IStreamable, TextContentChunk } from '@microsoft/agents-protocol';

    // Generic type alias for chained middleware
    type ChainedMiddleware<T extends IStreamable = IStreamable> = (
        stream: AsyncIterable<T>,
        thread: Thread,
        next: (stream: AsyncIterable<IStreamable>) => Promise<AsyncIterable<T>>
    ) => AsyncIterable<IStreamable>;

    // Use with specific content type
    const timeStreaming: ChainedMiddleware<TextContentChunk> = async function* (stream, thread, next) {
        // Your implementation
    };
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    // Generic delegate for chained middleware
    public delegate IAsyncEnumerable<IStreamable> ChainedMiddleware<T>(
        IAsyncEnumerable<T> stream,
        Thread thread,
        Func<IAsyncEnumerable<IStreamable>, Task<IAsyncEnumerable<T>>> next
    ) where T : IStreamable;

    // Use with specific content type
    ChainedMiddleware<TextContentChunk> timeStreaming = async (stream, thread, next) =>
    {
        // Your implementation
    };
    ```

**Type Explanation:**

- **Input**: `AsyncIterable<T>` - Pre-filtered stream of specific type (e.g., `TextContentChunk`)
- **next() input**: `AsyncIterable<IStreamable>` - Generic streamable content (middleware output becomes next input)
- **next() output**: `AsyncIterable<T>` - Strongly-typed items for post-processing transformations
- **Middleware output**: `AsyncIterable<IStreamable>` - Can yield any streamable type

**Key Change**: Constraint expanded from `AIContentChunk` to `IStreamable`, enabling middleware for messages, complete content, and chunks.

=== "Python"

    ```python
    from typing import Callable, Awaitable
    import time

    --8<-- test::quickstart/hosting-before-after
    ```

=== "C#"

    ```csharp
    using System.Diagnostics;

    --8<-- test::quickstart/hosting-before-after
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { TextContent, Thread } from '@microsoft/agents-protocol';

    --8<-- test::quickstart/hosting-before-after
    ```

### Message Middleware

Message middleware runs once per message and works at a higher level than content middleware. Use it for cross-cutting concerns like logging, authentication, and rate limiting.

**Signature:**

=== "Python"

    ```python
    from typing import TypeAlias, Callable, Awaitable

    # Type alias for message middleware
    MessageMiddleware: TypeAlias = Callable[
        [ChatMessage, Thread, Callable[[], Awaitable[None]]],
        Awaitable[None]
    ]

    # Use the alias
    logging: MessageMiddleware = async def (message, thread, next):
        # Your implementation
    ```

=== "TypeScript"

    ```typescript
    import { ChatMessage, Thread } from '@microsoft/agents-protocol';

    // Type alias for message middleware
    type MessageMiddleware = (
        message: ChatMessage,
        thread: Thread,
        next: () => Promise<void>
    ) => Promise<void>;

    // Use the alias
    const logging: MessageMiddleware = async (message, thread, next) => {
        // Your implementation
    };
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    // Delegate for message middleware
    public delegate Task MessageMiddleware(
        ChatMessage message,
        Thread thread,
        Func<Task> next
    );

    // Use the alias
    MessageMiddleware logging = async (message, thread, next) =>
    {
        // Your implementation
    };
    ```

=== "Python"

    ```python
    import time

    --8<-- test::quickstart/hosting-message-middleware
    ```

=== "C#"

    ```csharp
    using System.Diagnostics;

    --8<-- test::quickstart/hosting-message-middleware
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { ChatMessage, Thread } from '@microsoft/agents-protocol';

    --8<-- test::quickstart/hosting-message-middleware
    ```

### Error Handling

Use the wrap pattern with try/catch to handle errors gracefully in your middleware:

=== "Python"

    ```python
    from typing import AsyncIterable

    --8<-- test::quickstart/hosting-error-handling
    ```

=== "C#"

    ```csharp
    using System.Runtime.CompilerServices;

    --8<-- test::quickstart/hosting-error-handling
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { ChatMessage, Thread, AgentMessage, TextContent } from '@microsoft/agents-protocol';

    --8<-- test::quickstart/hosting-error-handling
    ```

---

## Step 7: Persistent Conversations

By default, conversations are stored in memory. For production, use durable storage.

### In-Memory Storage (Default)

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    import os

    --8<-- test::quickstart/hosting-inmemory-storage
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    --8<-- test::quickstart/hosting-inmemory-storage
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    --8<-- test::quickstart/hosting-inmemory-storage
    ```

### Client Example: Testing Persistence

Here's how clients interact with persistent conversations:

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient

    client = AgentProtocolClient("http://localhost:5000")

    # First message - creates a new thread
    response1 = await client.complete("My name is Alice")
    print(f"Thread ID: {response1.thread_id}")
    print(f"Response: {response1.text}")

    # Second message - uses same thread
    response2 = await client.complete(
        "What's my name?",
        thread_id=response1.thread_id
    )
    print(f"Response: {response2.text}")
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    // First message - creates a new thread
    var response1 = await client.CompleteAsync("My name is Alice");
    Console.WriteLine($"Thread ID: {response1.ThreadId}");
    Console.WriteLine($"Response: {response1.Text}");

    // Second message - uses same thread
    var response2 = await client.CompleteAsync(
        "What's my name?",
        threadId: response1.ThreadId
    );
    Console.WriteLine($"Response: {response2.Text}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:5000");

    // First message - creates a new thread
    const response1 = await client.complete("My name is Alice");
    console.log(`Thread ID: ${response1.threadId}`);
    console.log(`Response: ${response1.text}`);

    // Second message - uses same thread
    const response2 = await client.complete(
        "What's my name?",
        { threadId: response1.threadId }
    );
    console.log(`Response: ${response2.text}`);
    ```

**Output:**

First message:

```xml
<agent thread-id="thread_abc123">
  Nice to meet you, Alice! How can I help you today?
</agent>
```

Thread ID: `thread_abc123`

Second message (same thread):

```xml
<agent thread-id="thread_abc123">
  Your name is Alice.
</agent>
```

### Durable Storage

For production, use database-backed storage:

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    from microsoft.agents.protocol.storage import SqlStorageProvider
    import os

    --8<-- test::quickstart/hosting-durable-storage
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;
    using Microsoft.Agents.Protocol.Storage;

    --8<-- test::quickstart/hosting-durable-storage
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { SqlStorageProvider } from '@microsoft/agents-protocol-storage';

    --8<-- test::quickstart/hosting-durable-storage
    ```
