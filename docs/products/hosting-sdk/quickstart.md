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
    from dotenv import load_dotenv

    load_dotenv()  # Load .env file

    config = AgentConfig(
        model="gpt-4",
        instructions="You are a helpful assistant.",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = AgentHost(config)

    if __name__ == "__main__":
        agent.run()  # Starts server on http://localhost:5000
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    var builder = WebApplication.CreateBuilder(args);

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"]
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);

    var app = builder.Build();
    app.MapAgentProtocol();
    app.Run();
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import 'dotenv/config';

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!
    };

    const agent = new AgentHost(config);
    agent.listen(5000);
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

## Step 2: Adding Tools

Agents become powerful when they can call functions to get real-time data or take actions.

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    import os
    from datetime import datetime, timezone

    def get_weather(location: str) -> str:
        """Get current weather for a location"""
        # In production, call a real weather API
        return f"The weather in {location} is sunny and 72°F"

    def get_time() -> str:
        """Get current time in UTC"""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    config = AgentConfig(
        model="gpt-4",
        instructions="You are a helpful assistant.",
        api_key=os.getenv("OPENAI_API_KEY"),
        functions=[get_weather, get_time]
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;

    var builder = WebApplication.CreateBuilder(args);

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Functions = new[]
        {
            ("get_weather", "Get current weather for a location", (Func<string, string>)((string location) => $"The weather in {location} is sunny and 72°F")),
            ("get_time", "Get current time in UTC", (Func<string>)(() => DateTime.UtcNow.ToString("O")))
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

    function getWeather(location: string): string {
        // In production, call a real weather API
        return `The weather in ${location} is sunny and 72°F`;
    }

    function getTime(): string {
        return new Date().toISOString();
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        functions: [
            { name: "get_weather", description: "Get current weather for a location", fn: getWeather },
            { name: "get_time", description: "Get current time in UTC", fn: getTime }
        ]
    };

    const agent = new AgentHost(config);
    ```

### Error Handling in Tools

Tools should handle errors gracefully and return error messages that the LLM can explain to the user:

=== "Python"

    ```python
    import httpx

    async def get_weather(location: str) -> str:
        """Get current weather for a location"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.weather.com/v1/current",
                    params={"location": location}
                )
                response.raise_for_status()
                return f"Weather in {location}: {response.json()['temp']}°F"
        except httpx.HTTPError as e:
            # Return error message - LLM will explain to user
            return f"Sorry, couldn't fetch weather: {str(e)}"
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Functions = new[]
        {
            ("get_weather", "Get current weather", (Func<string, Task<string>>)(async (string location) =>
            {
                try
                {
                    // ⚠️ Production: Use IHttpClientFactory, not 'new HttpClient()'
                    // This example simplified for clarity
                    using var client = new HttpClient();
                    var url = $"https://api.weather.com/v1/current?location={Uri.EscapeDataString(location)}";
                    var response = await client.GetStringAsync(url);
                    return $"Weather in {location}: {response}";
                }
                catch (HttpRequestException ex)
                {
                    return $"Sorry, couldn't fetch weather: {ex.Message}";
                }
            }))
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function getWeather(location: string): Promise<string> {
        try {
            const response = await fetch(
                `https://api.weather.com/v1/current?location=${location}`
            );
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            const data = await response.json();
            return `Weather in ${location}: ${data.temp}°F`;
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            return `Sorry, couldn't fetch weather: ${errorMsg}`;
        }
    }
    ```

---

## Step 3: Client-Provided Functions

Allow clients to provide their own function implementations that the agent can call.

### Server Configuration

Configure your agent to accept client-provided functions:

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        allow_client_functions=True  # Enable client functions
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        AllowClientFunctions = true  // Enable client functions
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        allowClientFunctions: true  // Enable client functions
    };

    const agent = new AgentHost(config);
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
  </agent>
  <tool call-id="call_001">
    Email sent successfully
  </tool>
  <agent>
    <function-call call-id="call_002" name="get_local_files">
      {}
    </function-call>
  </agent>
  <tool call-id="call_002">
    Found 15 files: file1.txt, file2.py, README.md, config.json, package.json
  </tool>
  <agent>
    I've sent an email to bob@example.com with subject 'Meeting'. You have 15 files in your current directory including: file1.txt, file2.py, README.md, config.json, and package.json.
  </agent>
</thread>
```

---

## Step 4: Understanding Middleware

Middleware lets you intercept and modify messages **before and after** they're processed. Think of it as a pipeline where you control each stage.

### Your First Middleware

Let's build a simple command router that intercepts commands (like `/help`) and handles them without calling the LLM.

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    from microsoft.agents.protocol import TextContent, IThread
    from typing import AsyncIterable
    import os

    async def command_router(
        content_stream: AsyncIterable[TextContent],
        thread: IThread
    ) -> AsyncIterable[TextContent]:
        # Wait for all chunks to assemble into complete text
        complete_text = await content_stream.wait()

        # Check if it's the /help command
        if complete_text.text.strip() == "/help":
            # Handle command - return result without calling LLM
            yield TextContent(text="Available commands:\n/help - Show this help")
        else:
            # Pass through to LLM
            yield complete_text

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, command_router)
        ]
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;
    using Microsoft.Agents.Protocol.Hosting;
    using System.Runtime.CompilerServices;

    async IAsyncEnumerable<TextContent> CommandRouter(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        // Wait for all chunks to assemble into complete text
        var completeText = await contentStream.WaitForCompletionAsync();

        // Check if it's the /help command
        if (completeText.Text.Trim() == "/help")
        {
            // Handle command - return result without calling LLM
            yield return new TextContent
            {
                Text = "Available commands:\n/help - Show this help"
            };
        }
        else
        {
            // Pass through to LLM
            yield return completeText;
        }
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"]
            ?? throw new InvalidOperationException("OpenAI:ApiKey not configured"),
        Middleware = new MiddlewareCollection
        {
            CommandRouter  // Type inferred from method signature
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { TextContent, IThread } from '@microsoft/agents-protocol';

    async function* commandRouter(
        contentStream: AsyncIterable<IStreamable>,
        thread: IThread
    ): AsyncIterable<IStreamable> {
        // Wait for all chunks to assemble into complete text
        const completeText = await contentStream.value;

        // Check if it's the /help command
        if (completeText.text.trim() === '/help') {
            // Handle command - return result without calling LLM
            yield new TextContent({
                text: 'Available commands:\n/help - Show this help'
            });
        } else {
            // Pass through to LLM
            yield completeText;
        }
    }

    const apiKey = process.env.OPENAI_API_KEY;
    if (!apiKey) {
        throw new Error("OPENAI_API_KEY environment variable is required");
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey,
        middleware: [
            [TextContent, commandRouter]
        ]
    };

    const agent = new AgentHost(config);
    ```

**Example Output:**

When a client sends `/help`:

```
Available commands:
/help - Show this help
```

When a client sends "Hello, how are you?" (not a command), it passes through to the LLM normally.

### Streaming Processing

Process content chunk-by-chunk as it streams in real-time. This is the most common pattern for transforming or observing streaming data.

#### Content Middleware

Transform each chunk as it flows through:

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable

    async def uppercase_content(
        content_stream: AsyncIterable[TextContent],
        thread: IThread
    ) -> AsyncIterable[TextContent]:
        async for chunk in content_stream:
            chunk.text = chunk.text.upper()
            yield chunk

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, log_text_content),
        ]
    )
    ```

=== "C#"

    ```csharp
    using System.Runtime.CompilerServices;

    async IAsyncEnumerable<TextContent> UppercaseContent(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await foreach (var chunk in contentStream.WithCancellation(cancellationToken))
        {
            chunk.Text = chunk.Text.ToUpper();
            yield return chunk;
        }
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            UppercaseContent  // Type inferred from method signature
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function* uppercaseContent(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread
    ): AsyncIterable<TextContent> {
        for await (const chunk of contentStream) {
            chunk.text = chunk.text.toUpperCase();
            yield chunk;
        }
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, uppercaseContent],
        ]
    };
    ```

### Before and After Middleware

Use the `next()` callback pattern when you need to execute code **before** the middleware chain starts and **after** it completes. This is essential for timing, error handling, and resource management.

=== "Python"

    ```python
    from typing import Callable, Awaitable
    import time

    # Example 1: Time the stream
    async def time_streaming(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        start = time.time()
        print(f"🚀 Starting stream")

        await next(content_stream)

        print(f"✅ Stream completed in {time.time() - start:.2f}s")

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, time_streaming),
            (TextContent, catch_errors),
        ]
    )
    ```

=== "C#"

    ```csharp
    using System.Diagnostics;

    async Task TimeStreaming(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken = default)
    {
        var sw = Stopwatch.StartNew();
        Console.WriteLine("🚀 Starting stream");

        await next(contentStream);

        sw.Stop();
        Console.WriteLine($"✅ Stream completed in {sw.ElapsedMilliseconds}ms");
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            TimeStreaming  // Type inferred from method signature
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function timeStreaming(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        const start = Date.now();
        console.log("🚀 Starting stream");

        await next(contentStream);

        console.log(`✅ Stream completed in ${Date.now() - start}ms`);
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, timeStreaming],
        ]
    };
    ```

### Message Middleware

Message middleware runs once per message and works at a higher level than content middleware. Use it for cross-cutting concerns like logging, authentication, and rate limiting.

=== "Python"

    ```python
    import time

    async def timing_middleware(
        message: IMessage,
        thread: IThread,
        next: Callable[[], Awaitable[None]]
    ) -> None:
        start = time.time()
        print(f"⏱️ Processing started for thread {thread.id}")

        await next()  # Let other middleware and LLM process

        elapsed = time.time() - start
        print(f"✅ Completed in {elapsed:.2f}s")

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[timing_middleware]
    )
    ```

=== "C#"

    ```csharp
    using System.Diagnostics;

    async Task TimingMiddleware(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken cancellationToken)
    {
        var sw = Stopwatch.StartNew();
        Console.WriteLine($"⏱️ Processing started for thread {thread.Id}");

        await next();

        sw.Stop();
        Console.WriteLine($"✅ Completed in {sw.ElapsedMilliseconds}ms");
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)TimingMiddleware
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function timingMiddleware(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ): Promise<void> {
        const start = Date.now();
        console.log(`⏱️ Processing started for thread ${thread.id}`);

        await next();  // Let other middleware and LLM process

        const elapsed = Date.now() - start;
        console.log(`✅ Completed in ${elapsed}ms`);
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [timingMiddleware]
    };
    ```

### Error Handling

Use the wrap pattern with try/catch to handle errors gracefully in your middleware:

=== "Python"

    ```python
    async def error_middleware(message, thread, next):
        try:
            await next()
        except Exception as e:
            print(f"❌ Error processing message: {e}")
            # Add error message to thread
            error_msg = AgentMessage(content=[
                TextContent(text="Sorry, something went wrong. Please try again.")
            ])
            thread.add_message(error_msg)

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[error_middleware, other_middleware]  # error_middleware first
    )
    ```

=== "C#"

    ```csharp
    async Task ErrorMiddleware(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken cancellationToken)
    {
        try
        {
            await next();
        }
        catch (Exception ex)
        {
            Console.WriteLine($"❌ Error: {ex.Message}");
            var errorMsg = new AgentMessage
            {
                Content = new[] { new TextContent { Text = "Sorry, something went wrong." } }
            };
            thread.AddMessage(errorMsg);
        }
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)ErrorMiddleware
            // ... other middleware
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function errorMiddleware(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ): Promise<void> {
        try {
            await next();
        } catch (error) {
            const errorMsg = error instanceof Error ? error.message : String(error);
            console.error(`❌ Error: ${errorMsg}`);
            const errorResponse = new AgentMessage({
                content: [new TextContent({ text: "Sorry, something went wrong." })]
            });
            thread.addMessage(errorResponse);
        }
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [errorMiddleware]  // Add first to catch all errors
    };
    ```

### Processing Multimodal Content in Middleware

Use content middleware to process specific content types. This allows you to augment the LLM's capabilities by converting system events, channel events, or custom content types into messages the agent can understand.

=== "Python"

    ```python
    from microsoft.agents.protocol import (
        MessageReactionContent,
        DeveloperMessage,
        TextContent
    )
    from typing import AsyncIterable, Callable, Awaitable

    async def handle_reactions(
        content_stream: AsyncIterable[MessageReactionContent],
        thread: IThread,
        next: Callable[[AsyncIterable[MessageReactionContent]], Awaitable[None]]
    ) -> None:
        async def process():
            async for reaction in content_stream:
                # Convert reaction to a message the agent can understand
                developer_msg = DeveloperMessage(content=[
                    TextContent(text=f"User reacted with {reaction.emoji} to a previous message.")
                ])
                thread.add_message(developer_msg)
                yield reaction

        await next(process())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (MessageReactionContent, handle_reactions),
        ]
    )
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    async Task HandleReactions(
        IAsyncEnumerable<MessageReactionContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<MessageReactionContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<MessageReactionContent> Process()
        {
            await foreach (var reaction in contentStream)
            {
                // Convert reaction to a message the agent can understand
                var developerMsg = new DeveloperMessage
                {
                    Content = new[]
                    {
                        new TextContent
                        {
                            Text = $"User reacted with {reaction.Emoji} to a previous message."
                        }
                    }
                };
                thread.AddMessage(developerMsg);
                yield return reaction;
            }
        }

        await next(Process());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            HandleReactions  // Type inferred from method signature
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import { MessageReactionContent, DeveloperMessage, TextContent } from '@microsoft/agents-protocol';

    async function handleReactions(
        contentStream: AsyncIterable<MessageReactionContent>,
        thread: IThread,
        next: (stream: AsyncIterable<MessageReactionContent>) => Promise<void>
    ): Promise<void> {
        async function* process() {
            for await (const reaction of contentStream) {
                // Convert reaction to a message the agent can understand
                const developerMsg = new DeveloperMessage({
                    content: [
                        new TextContent({
                            text: `User reacted with ${reaction.emoji} to a previous message.`
                        })
                    ]
                });
                thread.addMessage(developerMsg);
                yield reaction;
            }
        }

        await next(process());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [MessageReactionContent, handleReactions],
        ]
    };
    ```

---

## Step 6: Persistent Conversations

By default, conversations are stored in memory. For production, use durable storage.

### In-Memory Storage (Default)

=== "Python"

    ```python
    # Default - no configuration needed
    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    # Conversations stored in memory (lost on restart)
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"]
    };
    // Default: in-memory storage
    ```

=== "TypeScript"

    ```typescript
    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!
    };
    // Default: in-memory storage
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

!!! success "What this demonstrates"
    - The agent remembers "Alice" from the first message
    - Same thread ID used for both messages
    - Conversation context automatically maintained
    - Works with both in-memory and durable storage

**When to use:**
- Development and testing
- Stateless agents (no conversation history needed)
- Short-lived demos

**Limitations:**
- Lost on restart
- Not shared across workers
- Limited by memory

### Durable Storage

For production, use database-backed storage:

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    from microsoft.agents.protocol.storage import SqlStorageProvider
    import os

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        storage=SqlStorageProvider(os.getenv("DATABASE_URL"))
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;
    using Microsoft.Agents.Protocol.Storage;

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Storage = new SqlStorageProvider(builder.Configuration["DatabaseUrl"])
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import { SqlStorageProvider } from '@microsoft/agents-protocol-storage';

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        storage: new SqlStorageProvider(process.env.DATABASE_URL!)
    };

    const agent = new AgentHost(config);
    ```

**Supported storage providers:**
- `SqlStorageProvider` - PostgreSQL, MySQL, SQL Server
- `CosmosDbStorageProvider` - Azure Cosmos DB
- `MongoDbStorageProvider` - MongoDB
- `RedisStorageProvider` - Redis
- Custom providers (implement `IStorageProvider`)

**What's stored:**
- Thread metadata (ID, created time, etc.)
- Message history (all messages in conversation)
- Function call results
- Thread state (custom key-value data)

### Production Defaults

Enable production features with one line:

=== "Python"

    ```python
    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        production=True  # Enables all production features
    )
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Production = true  // Enables all production features
    };
    ```

=== "TypeScript"

    ```typescript
    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        production: true  // Enables all production features
    };
    ```

**What `production=True` does:**

1. **Durable storage**: Automatically configures database storage
2. **Error handling**: Graceful error responses
3. **Rate limiting**: Protects against abuse
4. **Logging**: Structured logs for monitoring
5. **Metrics**: Performance tracking
6. **Health checks**: `/health` endpoint

**You still need to provide:**
- Database connection string (via environment variable)
- Monitoring service credentials (optional)

### Resource Management

The SDK automatically handles resource management:

=== "Python"

    ```python
    # Automatic cleanup when agent stops
    agent = AgentHost(config)

    try:
        agent.run()
    finally:
        agent.close()  # Closes connections, flushes logs
    ```

=== "C#"

    ```csharp
    // ASP.NET Core handles cleanup automatically
    var app = builder.Build();
    app.MapAgentProtocol();
    await app.RunAsync();  // Graceful shutdown on Ctrl+C
    ```

=== "TypeScript"

    ```typescript
    // Automatic cleanup on process exit
    const agent = new AgentHost(config);
    agent.listen(5000);

    process.on('SIGTERM', async () => {
        await agent.close();  // Graceful shutdown
        process.exit(0);
    });
    ```

**What's cleaned up:**
- Database connections
- HTTP clients
- Pending requests
- Background tasks

---


---

## Production Agent Patterns

The middleware examples above cover basic patterns. This section covers **agent-specific patterns** essential for production systems.

### Pattern 1: Tool Access Control

**Problem:** Not all users should have access to all tools (e.g., admin-only commands, sensitive APIs).

**Solution:** Filter tool calls based on user permissions.

=== "Python"

    ```python
    # Define role-based tool permissions
    ROLE_PERMISSIONS = {
        "admin": ["execute_command", "delete_user", "get_weather"],
        "user": ["get_weather"],
        "guest": []
    }

    async def enforce_tool_permissions(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        user_role = thread.metadata.get("user_role", "guest")
        allowed_tools = ROLE_PERMISSIONS.get(user_role, [])
        
        # Filter tool calls in message
        if message.tool_calls:
            allowed_calls = [
                call for call in message.tool_calls
                if call.function.name in allowed_tools
            ]
            
            if len(allowed_calls) < len(message.tool_calls):
                # Some tools were blocked
                blocked = len(message.tool_calls) - len(allowed_calls)
                logger.warning(
                    f"Blocked {blocked} unauthorized tool calls",
                    extra={"user_role": user_role, "thread_id": thread.id}
                )
            
            # Create new message with filtered tools
            message.tool_calls = allowed_calls
        
        yield message

    config = AgentConfig(
        middleware=[enforce_tool_permissions, ...],
        functions=all_available_functions  # Tools filtered per-user
    )
    ```

### Pattern 2: Memory Injection (RAG)

**Problem:** Agents need relevant context from knowledge bases or conversation history.

**Solution:** Inject retrieved context before the agent processes the message.

=== "Python"

    ```python
    from typing import List
    import logging

    logger = logging.getLogger(__name__)

    # Simulated vector store
    class VectorStore:
        async def search(self, query: str, top_k: int = 3) -> List[str]:
            # In production: query embedding database (Pinecone, Weaviate, etc.)
            return [
                "Relevant document 1...",
                "Relevant document 2...",
                "Relevant document 3..."
            ]

    vector_store = VectorStore()

    async def inject_rag_context(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        if message.role == "user":
            # Extract text from message
            text_parts = []
            async for content in message.content:
                if isinstance(content, TextContent):
                    chunk_text = await content.wait()
                    text_parts.append(chunk_text.text)
            
            query = " ".join(text_parts)
            
            # Retrieve relevant documents
            relevant_docs = await vector_store.search(query, top_k=3)
            
            # Prepend context to message
            context_text = "\n\n".join([
                "**Relevant Context:**",
                *relevant_docs,
                "**User Question:**"
            ])
            
            context_content = TextContent(text=context_text)
            
            # Create enriched message
            enriched_message = AgentMessage(
                role=message.role,
                content=[context_content] + list(message.content)
            )
            
            logger.info(f"Injected {len(relevant_docs)} docs for context")
            yield enriched_message
        else:
            # Agent messages pass through unchanged
            yield message
    ```

### Pattern 3: Token Budget Enforcement

**Problem:** Long conversations or large contexts can exceed model token limits.

**Solution:** Track token usage and truncate/summarize when approaching limits.

=== "Python"

    ```python
    import tiktoken  # pip install tiktoken

    class TokenBudgetEnforcer:
        def __init__(self, max_tokens: int = 4000, model: str = "gpt-4"):
            self.max_tokens = max_tokens
            self.encoder = tiktoken.encoding_for_model(model)
        
        def count_tokens(self, text: str) -> int:
            return len(self.encoder.encode(text))
        
        async def enforce_budget(
            self,
            message: IMessage,
            thread: IThread
        ) -> AsyncIterable[IMessage]:
            # Count tokens in current message
            text_parts = []
            async for content in message.content:
                if isinstance(content, TextContent):
                    chunk = await content.wait()
                    text_parts.append(chunk.text)
            
            message_text = " ".join(text_parts)
            message_tokens = self.count_tokens(message_text)
            
            # Track cumulative tokens in thread
            thread_tokens = thread.metadata.get("total_tokens", 0)
            new_total = thread_tokens + message_tokens
            
            if new_total > self.max_tokens:
                logger.warning(
                    f"Token budget exceeded: {new_total}/{self.max_tokens}. "
                    f"Consider summarizing conversation history."
                )
                
                # Option 1: Reject message
                # raise ValueError(f"Token limit exceeded: {new_total}/{self.max_tokens}")
                
                # Option 2: Truncate message (shown here)
                # In production, use smarter summarization
                truncated = message_text[:self.max_tokens * 3]  # Rough estimate
                truncated_content = TextContent(text=truncated + "... [truncated]")
                
                truncated_message = AgentMessage(
                    role=message.role,
                    content=[truncated_content]
                )
                
                thread.metadata["total_tokens"] = self.max_tokens
                yield truncated_message
            else:
                # Within budget
                thread.metadata["total_tokens"] = new_total
                yield message

    # Usage
    budget_enforcer = TokenBudgetEnforcer(max_tokens=8000)
    config = AgentConfig(
        middleware=[budget_enforcer.enforce_budget, ...]
    )
    ```

### Pattern 4: Multi-Agent Routing

**Problem:** Different types of questions need different specialist agents.

**Solution:** Route messages to appropriate agents based on intent classification.

=== "Python"

    ```python
    from enum import Enum

    class AgentType(Enum):
        GENERAL = "general"
        TECHNICAL = "technical"
        SALES = "sales"
        SUPPORT = "support"

    async def classify_intent(message_text: str) -> AgentType:
        # In production: use ML classifier or LLM
        if any(word in message_text.lower() for word in ["bug", "error", "broken"]):
            return AgentType.SUPPORT
        elif any(word in message_text.lower() for word in ["price", "purchase", "buy"]):
            return AgentType.SALES
        elif any(word in message_text.lower() for word in ["api", "code", "implement"]):
            return AgentType.TECHNICAL
        else:
            return AgentType.GENERAL

    async def route_to_specialist(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        if message.role == "user":
            # Extract text
            text_parts = []
            async for content in message.content:
                if isinstance(content, TextContent):
                    chunk = await content.wait()
                    text_parts.append(chunk.text)
            
            message_text = " ".join(text_parts)
            
            # Classify intent
            agent_type = await classify_intent(message_text)
            
            # Store routing decision in thread metadata
            thread.metadata["assigned_agent"] = agent_type.value
            
            logger.info(
                f"Routed to {agent_type.value} agent",
                extra={"thread_id": thread.id, "intent": agent_type.value}
            )
            
            # Add routing context to message
            routing_note = f"[Routed to {agent_type.value} specialist]\n\n"
            routed_content = TextContent(text=routing_note + message_text)
            
            routed_message = AgentMessage(
                role=message.role,
                content=[routed_content]
            )
            
            yield routed_message
        else:
            yield message

    # In a multi-agent system, you'd have different AgentConfig instances
    # and select which one to use based on thread.metadata["assigned_agent"]
    ```

### Pattern 5: Conversation State Management

**Problem:** Track conversation goals, subtasks, or branching paths.

**Solution:** Maintain structured state in thread metadata.

=== "Python"

    ```python
    from dataclasses import dataclass, asdict
    from typing import Optional, List
    from datetime import datetime

    @dataclass
    class ConversationState:
        goal: str
        subtasks: List[str]
        completed_subtasks: List[str]
        current_step: int
        started_at: datetime
        last_updated: datetime
        
        def to_dict(self):
            return {
                **asdict(self),
                "started_at": self.started_at.isoformat(),
                "last_updated": self.last_updated.isoformat()
            }

    async def track_conversation_state(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        # Load or initialize state
        state_dict = thread.metadata.get("conversation_state")
        
        if state_dict:
            # Restore state (in production, use proper deserialization)
            state = ConversationState(
                goal=state_dict["goal"],
                subtasks=state_dict["subtasks"],
                completed_subtasks=state_dict["completed_subtasks"],
                current_step=state_dict["current_step"],
                started_at=datetime.fromisoformat(state_dict["started_at"]),
                last_updated=datetime.now()
            )
        else:
            # Initialize new conversation
            state = ConversationState(
                goal="Help user with their request",
                subtasks=[],
                completed_subtasks=[],
                current_step=0,
                started_at=datetime.now(),
                last_updated=datetime.now()
            )
        
        # Update state based on message
        if message.role == "user":
            # Extract potential new subtask
            # In production: use LLM to identify subtasks
            state.current_step += 1
        
        # Save updated state
        thread.metadata["conversation_state"] = state.to_dict()
        
        # Add state context to message if helpful
        if message.role == "user" and len(state.completed_subtasks) > 0:
            context = f"[Progress: {len(state.completed_subtasks)}/{len(state.subtasks)} subtasks complete]\n\n"
            # Could prepend to message content
        
        yield message
    ```

### Pattern 6: Reflection & Self-Critique

**Problem:** Agent responses may contain errors or low-quality outputs.

**Solution:** Add reflection middleware that critiques and optionally regenerates responses.

=== "Python"

    ```python
    async def reflection_middleware(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        if message.role == "agent":
            # Extract agent response
            text_parts = []
            async for content in message.content:
                if isinstance(content, TextContent):
                    chunk = await content.wait()
                    text_parts.append(chunk.text)
            
            response_text = " ".join(text_parts)
            
            # Simple quality checks (in production: use LLM to critique)
            issues = []
            
            if len(response_text) < 20:
                issues.append("Response too short")
            
            if "I don't know" in response_text and len(response_text) < 50:
                issues.append("Unhelpful response")
            
            if response_text.count("?") > 3:
                issues.append("Too many questions, not enough answers")
            
            if issues:
                logger.warning(
                    f"Reflection found issues: {issues}",
                    extra={"thread_id": thread.id}
                )
                
                # Option 1: Add critique note to response
                critique = f"\n\n[Reflection: {', '.join(issues)}]"
                critiqued_content = TextContent(text=response_text + critique)
                
                critiqued_message = AgentMessage(
                    role=message.role,
                    content=[critiqued_content]
                )
                
                yield critiqued_message
                
                # Option 2: Trigger regeneration (not shown - would need callback to LLM)
            else:
                yield message
        else:
            yield message
    ```



### Pattern 7: Planning & Task Decomposition

**Problem:** Complex user requests need to be broken down into subtasks and executed step-by-step.

**Solution:** Add planning middleware that decomposes goals into actionable steps.

=== "Python"

    ```python
    from dataclasses import dataclass
    from typing import List
    import json

    @dataclass
    class Plan:
        goal: str
        steps: List[str]
        completed_steps: List[str]
        current_step_index: int

    async def planning_middleware(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        if message.role == "user":
            # Extract user request
            text_parts = []
            async for content in message.content:
                if isinstance(content, TextContent):
                    chunk = await content.wait()
                    text_parts.append(chunk.text)
            
            user_request = " ".join(text_parts)
            
            # Check if we have an active plan
            plan_data = thread.metadata.get("active_plan")
            
            if not plan_data:
                # Create new plan by asking LLM to decompose the task
                # In production: use LLM to generate steps
                steps = await decompose_task(user_request)
                
                plan = Plan(
                    goal=user_request,
                    steps=steps,
                    completed_steps=[],
                    current_step_index=0
                )
                
                thread.metadata["active_plan"] = {
                    "goal": plan.goal,
                    "steps": plan.steps,
                    "completed_steps": plan.completed_steps,
                    "current_step_index": plan.current_step_index
                }
                
                # Add plan context to message
                plan_text = f"\n\n**Plan Created:**\n" + "\n".join([
                    f"{i+1}. {step}" for i, step in enumerate(steps)
                ]) + f"\n\n**Starting Step 1**: {steps[0]}\n\n"
                
                enriched_message = AgentMessage(
                    role=message.role,
                    content=[TextContent(text=plan_text + user_request)]
                )
                
                logger.info(f"Created plan with {len(steps)} steps")
                yield enriched_message
            else:
                # Continue with existing plan
                plan = Plan(**plan_data)
                
                if plan.current_step_index < len(plan.steps):
                    current_step = plan.steps[plan.current_step_index]
                    
                    # Mark current step as completed
                    plan.completed_steps.append(current_step)
                    plan.current_step_index += 1
                    
                    # Update metadata
                    thread.metadata["active_plan"] = {
                        "goal": plan.goal,
                        "steps": plan.steps,
                        "completed_steps": plan.completed_steps,
                        "current_step_index": plan.current_step_index
                    }
                    
                    if plan.current_step_index < len(plan.steps):
                        next_step = plan.steps[plan.current_step_index]
                        context = f"\n\n**Progress**: {len(plan.completed_steps)}/{len(plan.steps)} steps completed\n**Next Step**: {next_step}\n\n"
                    else:
                        context = f"\n\n**Plan Complete!** All {len(plan.steps)} steps finished.\n\n"
                        # Clear the plan
                        del thread.metadata["active_plan"]
                    
                    enriched_message = AgentMessage(
                        role=message.role,
                        content=[TextContent(text=context + user_request)]
                    )
                    
                    yield enriched_message
                else:
                    yield message
        else:
            yield message

    async def decompose_task(task: str) -> List[str]:
        # In production: use LLM to break down the task
        # For demo, simple heuristic:
        if "and" in task.lower():
            parts = [p.strip() for p in task.split("and")]
            return parts
        else:
            return [task]
    ```

### Pattern 8: Human-in-the-Loop (HITL)

**Problem:** Some agent actions require human approval before execution (e.g., sending emails, making purchases, deleting data).

**Solution:** Add approval gates that pause execution and wait for human confirmation.

=== "Python"

    ```python
    from enum import Enum
    from datetime import datetime
    from typing import Optional, Callable, Awaitable

    class ApprovalStatus(Enum):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    class ApprovalRequest:
        def __init__(self, action: str, details: dict, thread_id: str):
            self.id = f"approval_{datetime.now().timestamp()}"
            self.action = action
            self.details = details
            self.thread_id = thread_id
            self.status = ApprovalStatus.PENDING
            self.approved_at: Optional[datetime] = None

    # Global approval store (in production: use Redis or database)
    approval_requests: dict[str, ApprovalRequest] = {}

    def requires_approval(tool_name: str) -> bool:
        """Check if a tool requires human approval"""
        high_risk_tools = [
            "send_email",
            "delete_file",
            "make_purchase",
            "execute_command",
            "modify_database"
        ]
        return tool_name in high_risk_tools

    async def human_in_the_loop_middleware(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        if message.role == "agent" and message.tool_calls:
            # Check if any tool calls require approval
            pending_approvals = []
            approved_calls = []
            
            for tool_call in message.tool_calls:
                if requires_approval(tool_call.function.name):
                    # Create approval request
                    approval = ApprovalRequest(
                        action=tool_call.function.name,
                        details={
                            "arguments": tool_call.function.arguments,
                            "call_id": tool_call.id
                        },
                        thread_id=thread.id
                    )
                    
                    approval_requests[approval.id] = approval
                    pending_approvals.append(approval)
                    
                    logger.info(
                        f"Tool '{tool_call.function.name}' requires approval",
                        extra={"approval_id": approval.id, "thread_id": thread.id}
                    )
                else:
                    # No approval needed
                    approved_calls.append(tool_call)
            
            if pending_approvals:
                # Create approval message for user
                approval_text = "⚠️ **Approval Required**\n\n"
                approval_text += "The following actions require your approval:\n\n"
                
                for i, approval in enumerate(pending_approvals, 1):
                    approval_text += f"{i}. **{approval.action}**\n"
                    approval_text += f"   Details: {json.dumps(approval.details['arguments'], indent=2)}\n"
                    approval_text += f"   Approval ID: `{approval.id}`\n\n"
                
                approval_text += "\nTo approve: Reply with 'approve <approval_id>'\n"
                approval_text += "To reject: Reply with 'reject <approval_id>'\n"
                
                # Store pending approvals in thread metadata
                thread.metadata["pending_approvals"] = [a.id for a in pending_approvals]
                
                # Return approval request message
                approval_message = AgentMessage(
                    role="agent",
                    content=[TextContent(text=approval_text)],
                    tool_calls=approved_calls  # Only execute approved calls
                )
                
                yield approval_message
            else:
                # No approvals needed, continue
                yield message
        
        elif message.role == "user":
            # Check if this is an approval response
            text_parts = []
            async for content in message.content:
                if isinstance(content, TextContent):
                    chunk = await content.wait()
                    text_parts.append(chunk.text)
            
            user_text = " ".join(text_parts).lower()
            
            if user_text.startswith("approve ") or user_text.startswith("reject "):
                parts = user_text.split()
                action = parts[0]  # "approve" or "reject"
                approval_id = parts[1] if len(parts) > 1 else None
                
                if approval_id and approval_id in approval_requests:
                    approval = approval_requests[approval_id]
                    
                    if action == "approve":
                        approval.status = ApprovalStatus.APPROVED
                        approval.approved_at = datetime.now()
                        
                        # Execute the approved action
                        response_text = f"✅ Approved and executing: {approval.action}"
                        logger.info(f"Tool '{approval.action}' approved", extra={"approval_id": approval_id})
                    else:
                        approval.status = ApprovalStatus.REJECTED
                        response_text = f"❌ Rejected: {approval.action}"
                        logger.info(f"Tool '{approval.action}' rejected", extra={"approval_id": approval_id})
                    
                    # Remove from pending
                    if "pending_approvals" in thread.metadata:
                        thread.metadata["pending_approvals"] = [
                            a for a in thread.metadata["pending_approvals"] 
                            if a != approval_id
                        ]
                    
                    response_message = AgentMessage(
                        role="agent",
                        content=[TextContent(text=response_text)]
                    )
                    
                    yield response_message
                else:
                    yield message
            else:
                yield message
        else:
            yield message
    ```

**Integration with both patterns:**

```python
config = AgentConfig(
    model="gpt-4",
    instructions="You are a helpful assistant.",
    api_key=os.getenv("OPENAI_API_KEY"),
    middleware=[
        error_handler,
        authenticate,
        planning_middleware,              # Pattern 7: Break down complex tasks
        human_in_the_loop_middleware,     # Pattern 8: Require approval for high-risk actions
        enforce_tool_permissions,
        inject_rag_context,
        track_conversation_state,
        log_for_production,
    ],
    functions=[send_email, delete_file, get_weather, ...]  # All tools available
)
```

**Pattern 7 benefits:**
- Handles complex multi-step requests automatically
- Tracks progress across conversation turns
- Provides clear visibility into what's being done
- Can be combined with HITL for approval at each step

**Pattern 8 benefits:**
- Safety: Prevents unauthorized or unintended actions
- Compliance: Meets regulatory requirements for human oversight
- Transparency: User sees exactly what will happen before it happens
- Flexibility: Can approve/reject individual actions

### Combining Agent Patterns

In production, combine these patterns:

```python
config = AgentConfig(
    model="gpt-4",
    instructions="You are a helpful assistant.",
    api_key=os.getenv("OPENAI_API_KEY"),
    middleware=[
        error_handler,                    # Catch all errors
        authenticate,                     # Verify user
        planning_middleware,              # Pattern 7: Planning & task decomposition
        human_in_the_loop_middleware,     # Pattern 8: Human approval gates
        enforce_tool_permissions,         # Pattern 1: Tool access control
        budget_enforcer.enforce_budget,   # Pattern 3: Token limits
        route_to_specialist,              # Pattern 4: Multi-agent routing
        inject_rag_context,               # Pattern 2: Memory/RAG
        track_conversation_state,         # Pattern 5: State management
        log_for_production,               # Structured logging
        reflection_middleware,            # Pattern 6: Self-critique
    ]
)
```

**Key takeaways:**
- Middleware order matters: auth → permissions → routing → context → business logic
- Use thread.metadata to persist state across messages
- Combine patterns for production-grade agents
- Add comprehensive logging and metrics

### Post-process after LLM

Transform LLM output before it reaches the client:

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable

    async def add_emojis(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def transform():
            async for chunk in content_stream:
                # Add emoji to each text chunk
                modified = TextContent(text=f"✨ {chunk.text}")
                yield modified

        await next(transform())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, add_emojis),  # Content middleware as tuple
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task AddEmojis(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> Transform()
        {
            await foreach (var chunk in contentStream)
            {
                yield return new TextContent { Text = $"✨ {chunk.Text}" };
            }
        }

        await next(Transform());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            AddEmojis  // Type inferred from method signature  // Content middleware (tuple)
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function addEmojis(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* transform() {
            for await (const chunk of contentStream) {
                yield new TextContent({ text: `✨ ${chunk.text}` });
            }
        }

        await next(transform());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, addEmojis],  // Content middleware (array)
        ]
    };
    ```

### Intercepting Function Calls

Process function calls before they execute:

=== "Python"

    ```python
    from microsoft.agents.protocol import FunctionCallContent, FunctionResultContent
    from typing import AsyncIterable, Callable, Awaitable

    async def log_function_calls(
        content_chunks: AsyncIterable[FunctionCallContent],
        thread: IThread,
        next: Callable[[AsyncIterable[FunctionCallContent]], Awaitable[None]]
    ) -> None:
        # Wait for all chunks to assemble into complete function call
        complete_call = await content_chunks.wait()
        print(f"🔧 Function call: {complete_call.name}({complete_call.arguments})")

        async def process():
            yield complete_call

        await next(process())

    async def log_function_results(
        content_chunks: AsyncIterable[FunctionResultContent],
        thread: IThread,
        next: Callable[[AsyncIterable[FunctionResultContent]], Awaitable[None]]
    ) -> None:
        # Wait for all chunks to assemble into complete function result
        complete_result = await content_chunks.wait()
        print(f"✅ Function result: {complete_result.result}")

        async def process():
            yield complete_result

        await next(process())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        functions=[get_weather],
        middleware=[
            (FunctionCallContent, log_function_calls),     # Content middleware (tuple)
            (FunctionResultContent, log_function_results),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    async Task LogFunctionCalls(
        IAsyncEnumerable<FunctionCallContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<FunctionCallContent>, Task> next,
        CancellationToken cancellationToken)
    {
        // Wait for all chunks to assemble into complete function call
        var completeCall = await contentChunks.WaitForCompletionAsync();
        Console.WriteLine($"🔧 Function call: {completeCall.Name}({completeCall.Arguments})");

        async IAsyncEnumerable<FunctionCallContent> Process()
        {
            yield return completeCall;
        }

        await next(Process());
    }

    async Task LogFunctionResults(
        IAsyncEnumerable<FunctionResultContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<FunctionResultContent>, Task> next,
        CancellationToken cancellationToken)
    {
        // Wait for all chunks to assemble into complete function result
        var completeResult = await contentChunks.WaitForCompletionAsync();
        Console.WriteLine($"✅ Function result: {completeResult.Result}");

        async IAsyncEnumerable<FunctionResultContent> Process()
        {
            yield return completeResult;
        }

        await next(Process());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Functions = new[] { ("get_weather", "Get weather", GetWeather) },
        Middleware = new MiddlewareCollection
        {
            LogFunctionCalls,     // Tuple
            LogFunctionResults  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import { FunctionCallContent, FunctionResultContent } from '@microsoft/agents-protocol';

    async function logFunctionCalls(
        contentChunks: AsyncIterable<FunctionCallContent>,
        thread: IThread,
        next: (stream: AsyncIterable<FunctionCallContent>) => Promise<void>
    ): Promise<void> {
        // Wait for all chunks to assemble into complete function call
        const completeCall = await contentChunks.value;
        console.log(`🔧 Function call: ${completeCall.name}(${JSON.stringify(completeCall.arguments)})`);

        async function* process() {
            yield completeCall;
        }

        await next(process());
    }

    async function logFunctionResults(
        contentChunks: AsyncIterable<FunctionResultContent>,
        thread: IThread,
        next: (stream: AsyncIterable<FunctionResultContent>) => Promise<void>
    ): Promise<void> {
        // Wait for all chunks to assemble into complete function result
        const completeResult = await contentChunks.value;
        console.log(`✅ Function result: ${completeResult.result}`);

        async function* process() {
            yield completeResult;
        }

        await next(process());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        functions: [getWeather],
        middleware: [
            [FunctionCallContent, logFunctionCalls],      // Content middleware (array)
            [FunctionResultContent, logFunctionResults],  // Content middleware (array)
        ]
    };
    ```

---


## Advanced: Stream Flow Control

Sometimes you need fine-grained control over how content flows through the pipeline.

### The Challenge

By default, content flows linearly:

```
LLM → Middleware 1 → Middleware 2 → Client
```

But what if you want to:
- Buffer chunks and send them in batches
- Drop certain chunks entirely
- Duplicate chunks to multiple destinations
- Transform chunk order

### Core Patterns

#### Pattern 1: Buffer and Batch

Collect chunks and send them in larger batches:

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable, Callable, Awaitable

    async def batch_content(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def batched():
            buffer = []
            async for chunk in content_stream:
                buffer.append(chunk.text)

                # Send every 5 chunks
                if len(buffer) >= 5:
                    yield TextContent(text="".join(buffer))
                    buffer = []

            # Send remaining
            if buffer:
                yield TextContent(text="".join(buffer))

        await next(batched())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, batch_content),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task BatchContent(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> Batched()
        {
            var buffer = new List<string>();

            await foreach (var chunk in contentStream)
            {
                buffer.Add(chunk.Text);

                if (buffer.Count >= 5)
                {
                    yield return new TextContent { Text = string.Join("", buffer) };
                    buffer.Clear();
                }
            }

            if (buffer.Any())
                yield return new TextContent { Text = string.Join("", buffer) };
        }

        await next(Batched());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            BatchContent  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function batchContent(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* batched() {
            const buffer: string[] = [];

            for await (const chunk of contentStream) {
                buffer.push(chunk.text);

                if (buffer.length >= 5) {
                    yield new TextContent({ text: buffer.join("") });
                    buffer.length = 0;
                }
            }

            if (buffer.length > 0) {
                yield new TextContent({ text: buffer.join("") });
            }
        }

        await next(batched());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, batchContent],  // Content middleware (array)
        ]
    };
    ```

#### Pattern 2: Filter/Drop Chunks

Remove unwanted content:

=== "Python"

    ```python
    async def filter_profanity(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def filtered():
            async for chunk in content_stream:
                # Drop chunks with profanity
                if not contains_profanity(chunk.text):
                    yield chunk

        await next(filtered())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, filter_profanity),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task FilterProfanity(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> Filtered()
        {
            await foreach (var chunk in contentStream)
            {
                if (!ContainsProfanity(chunk.Text))
                    yield return chunk;
            }
        }

        await next(Filtered());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            FilterProfanity  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function filterProfanity(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* filtered() {
            for await (const chunk of contentStream) {
                if (!containsProfanity(chunk.text)) {
                    yield chunk;
                }
            }
        }

        await next(filtered());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, filterProfanity],  // Content middleware (array)
        ]
    };
    ```

#### Pattern 3: Duplicate/Tee Streams

Send chunks to multiple destinations:

=== "Python"

    ```python
    async def tee_to_analytics(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def forwarding():
            async for chunk in content_stream:
                # Send to analytics (non-blocking)
                send_to_analytics(chunk.text)

                # Forward to client
                yield chunk

        await next(forwarding())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, tee_to_analytics),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task TeeToAnalytics(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> Forwarding()
        {
            await foreach (var chunk in contentStream)
            {
                _ = SendToAnalyticsAsync(chunk.Text);  // Fire and forget
                yield return chunk;
            }
        }

        await next(Forwarding());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            TeeToAnalytics  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function teeToAnalytics(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* forwarding() {
            for await (const chunk of contentStream) {
                sendToAnalytics(chunk.text);  // Fire and forget
                yield chunk;
            }
        }

        await next(forwarding());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, teeToAnalytics],  // Content middleware (array)
        ]
    };
    ```

#### Pattern 4: Rate Limiting

Slow down chunk delivery:

=== "Python"

    ```python
    import asyncio

    async def rate_limit(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def throttled():
            async for chunk in content_stream:
                yield chunk
                await asyncio.sleep(0.1)  # 100ms delay between chunks

        await next(throttled())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, rate_limit),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task RateLimit(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> Throttled()
        {
            await foreach (var chunk in contentStream)
            {
                yield return chunk;
                await Task.Delay(100, cancellationToken);  // 100ms delay
            }
        }

        await next(Throttled());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            RateLimit  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function rateLimit(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* throttled() {
            for await (const chunk of contentStream) {
                yield chunk;
                await new Promise(resolve => setTimeout(resolve, 100));  // 100ms delay
            }
        }

        await next(throttled());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, rateLimit],  // Content middleware (array)
        ]
    };
    ```

#### Pattern 5: Transform and Aggregate

Combine chunks in complex ways:

=== "Python"

    ```python
    async def markdown_to_html(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def transformed():
            buffer = []
            async for chunk in content_stream:
                buffer.append(chunk.text)

                # When we have a complete markdown block
                if "```" in chunk.text and len(buffer) > 1:
                    markdown = "".join(buffer)
                    html = convert_markdown_to_html(markdown)
                    yield TextContent(text=html)
                    buffer = []

            # Flush remaining
            if buffer:
                markdown = "".join(buffer)
                html = convert_markdown_to_html(markdown)
                yield TextContent(text=html)

        await next(transformed())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (TextContent, markdown_to_html),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task MarkdownToHtml(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> Transformed()
        {
            var buffer = new List<string>();

            await foreach (var chunk in contentStream)
            {
                buffer.Add(chunk.Text);

                if (chunk.Text.Contains("```") && buffer.Count > 1)
                {
                    var markdown = string.Join("", buffer);
                    var html = ConvertMarkdownToHtml(markdown);
                    yield return new TextContent { Text = html };
                    buffer.Clear();
                }
            }

            if (buffer.Any())
            {
                var markdown = string.Join("", buffer);
                var html = ConvertMarkdownToHtml(markdown);
                yield return new TextContent { Text = html };
            }
        }

        await next(Transformed());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new MiddlewareCollection
        {
            MarkdownToHtml  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function markdownToHtml(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* transformed() {
            const buffer: string[] = [];

            for await (const chunk of contentStream) {
                buffer.push(chunk.text);

                if (chunk.text.includes("```") && buffer.length > 1) {
                    const markdown = buffer.join("");
                    const html = convertMarkdownToHtml(markdown);
                    yield new TextContent({ text: html });
                    buffer.length = 0;
                }
            }

            if (buffer.length > 0) {
                const markdown = buffer.join("");
                const html = convertMarkdownToHtml(markdown);
                yield new TextContent({ text: html });
            }
        }

        await next(transformed());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [TextContent, markdownToHtml],  // Content middleware (array)
        ]
    };
    ```

---

## Complete Example

Here's a production-ready agent with multiple middleware:

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHost, AgentConfig
    from microsoft.agents.protocol import (
        IMessage, IThread, UserMessage, AgentMessage, TextContent,
        FunctionCallContent, FunctionResultContent
    )
    from microsoft.agents.protocol.storage import SqlStorageProvider
    from typing import Callable, Awaitable, AsyncIterable
    import os
    import time

    # Content middleware for logging incoming text
    async def log_text(
        content_chunks: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        # Wait for complete text content
        complete_text = await content_chunks.wait()
        print(f"📨 [{thread.id}] Received: {complete_text.text}")

        async def process():
            yield complete_text
        await next(process())

    # Message middleware for command routing (needs cross-content logic)
    async def handle_commands(
        message: IMessage,
        thread: IThread,
        next: Callable[[], Awaitable[None]]
    ) -> None:
        if not isinstance(message, UserMessage):
            await next()
            return

        # Extract text from message contents
        text_parts = []
        async for content in message.content:
            if isinstance(content, TextContent):
                text_parts.append(await content.wait())
        command = "".join(c.text for c in text_parts).strip()

        if command == "/help":
            response = AgentMessage(content=[
                TextContent(text="Available commands: /help, /status, /clear")
            ])
            thread.add_message(response)
            return
        elif command == "/status":
            response = AgentMessage(content=[
                TextContent(text=f"Thread ID: {thread.id}")
            ])
            thread.add_message(response)
            return
        await next()

    # Content middleware for streaming LLM text chunks
    async def log_text_chunks(
        content_chunks: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def process():
            async for chunk in content_chunks:
                print(f"📝 LLM: {chunk.text}")
                yield chunk
        await next(process())

    # Content middleware for logging function calls
    async def log_function_calls(
        content_chunks: AsyncIterable[FunctionCallContent],
        thread: IThread,
        next: Callable[[AsyncIterable[FunctionCallContent]], Awaitable[None]]
    ) -> None:
        # Wait for all chunks to assemble into complete function call
        complete_call = await content_chunks.wait()
        print(f"🔧 Calling: {complete_call.name}({complete_call.arguments})")

        async def process():
            yield complete_call
        await next(process())

    # Content middleware for logging function results
    async def log_function_results(
        content_chunks: AsyncIterable[FunctionResultContent],
        thread: IThread,
        next: Callable[[AsyncIterable[FunctionResultContent]], Awaitable[None]]
    ) -> None:
        # Wait for complete result
        complete_result = await content_chunks.wait()
        print(f"✅ Result: {complete_result.result}")

        async def process():
            yield complete_result
        await next(process())

    # Functions
    def get_weather(location: str) -> str:
        """Get current weather for a location"""
        return f"Weather in {location}: Sunny, 72°F"

    def get_time() -> str:
        """Get current time"""
        return time.strftime("%Y-%m-%d %H:%M:%S")

    # Configure agent with new pattern
    config = AgentConfig(
        model="gpt-4",
        instructions="You are a helpful assistant with access to weather and time information.",
        api_key=os.getenv("OPENAI_API_KEY"),
        storage=SqlStorageProvider(os.getenv("DATABASE_URL")),
        functions=[get_weather, get_time],
        middleware=[
            (TextContent, log_text),                      # Content middleware - log incoming text
            handle_commands,                              # Message middleware - command routing
            (TextContent, log_text_chunks),               # Content middleware - stream LLM text
            (FunctionCallContent, log_function_calls),    # Content middleware - log function calls
            (FunctionResultContent, log_function_results) # Content middleware - log function results
        ]
    )
    agent = AgentHost(config)

    if __name__ == "__main__":
        agent.run()
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;
    using Microsoft.Agents.Protocol.Hosting;
    using Microsoft.Agents.Protocol.Storage;

    var builder = WebApplication.CreateBuilder(args);

    // Content middleware for logging incoming text
    async Task LogText(
        IAsyncEnumerable<TextContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken ct)
    {
        // Wait for complete text content
        var completeText = await contentChunks.WaitForCompletionAsync();
        Console.WriteLine($"📨 [{thread.Id}] Received: {completeText.Text}");

        async IAsyncEnumerable<TextContent> Process()
        {
            yield return completeText;
        }
        await next(Process());
    }

    // Message middleware for command routing (needs cross-content logic)
    async Task HandleCommands(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken ct)
    {
        if (message is not UserMessage)
        {
            await next();
            return;
        }

        // Extract text from message contents
        var textParts = new List<TextContent>();
        await foreach (var content in message.Content)
        {
            if (content is TextContent textContent)
            {
                textParts.Add(await textContent.WaitForCompletionAsync());
            }
        }
        var command = string.Join("", textParts.Select(c => c.Text)).Trim();

        if (command == "/help")
        {
            thread.AddMessage(new AgentMessage
            {
                Content = new[] { new TextContent { Text = "Available commands: /help, /status" } }
            });
            return;
        }
        await next();
    }

    // Content middleware for streaming LLM text chunks
    async Task LogTextChunks(
        IAsyncEnumerable<TextContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken ct)
    {
        async IAsyncEnumerable<TextContent> Process()
        {
            await foreach (var chunk in contentChunks)
            {
                Console.WriteLine($"📝 LLM: {chunk.Text}");
                yield return chunk;
            }
        }
        await next(Process());
    }

    // Content middleware for logging function calls
    async Task LogFunctionCalls(
        IAsyncEnumerable<FunctionCallContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<FunctionCallContent>, Task> next,
        CancellationToken ct)
    {
        // Wait for all chunks to assemble into complete function call
        var completeCall = await contentChunks.WaitForCompletionAsync();
        Console.WriteLine($"🔧 Calling: {completeCall.Name}({completeCall.Arguments})");

        async IAsyncEnumerable<FunctionCallContent> Process()
        {
            yield return completeCall;
        }
        await next(Process());
    }

    // Content middleware for logging function results
    async Task LogFunctionResults(
        IAsyncEnumerable<FunctionResultContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<FunctionResultContent>, Task> next,
        CancellationToken ct)
    {
        // Wait for complete result
        var completeResult = await contentChunks.WaitForCompletionAsync();
        Console.WriteLine($"✅ Result: {completeResult.Result}");

        async IAsyncEnumerable<FunctionResultContent> Process()
        {
            yield return completeResult;
        }
        await next(Process());
    }

    // Functions
    string GetWeather(string location) => $"Weather in {location}: Sunny, 72°F";
    string GetTime() => DateTime.Now.ToString("O");

    // Configure agent with new pattern
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are a helpful assistant with access to weather and time information.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Storage = new SqlStorageProvider(builder.Configuration["DatabaseUrl"]),
        Functions = new[]
        {
            ("get_weather", "Get current weather", (Func<string, string>)GetWeather),
            ("get_time", "Get current time", (Func<string>)GetTime)
        },
        Middleware =
        [
            LogText,                       // Content middleware - log incoming text
            HandleCommands,                                       // Message middleware - command routing
            LogTextChunks,                 // Content middleware - stream LLM text
            LogFunctionCalls,      // Content middleware - log function calls
            LogFunctionResults   // Content middleware - log function results
        ]
    };

    builder.Services.AddDefaultAgent(agentOptions);

    var app = builder.Build();
    app.MapAgentProtocol();
    await app.RunAsync();
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
    import {
        IMessage, IThread, UserMessage, AgentMessage, TextContent,
        FunctionCallContent, FunctionResultContent
    } from '@microsoft/agents-protocol';
    import { SqlStorageProvider } from '@microsoft/agents-protocol-storage';
    import 'dotenv/config';

    // Content middleware for logging incoming text
    async function logText(
        contentChunks: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ) {
        // Wait for complete text content
        const completeText = await contentChunks.value;
        console.log(`📨 [${thread.id}] Received: ${completeText.text}`);

        async function* process() {
            yield completeText;
        }
        await next(process());
    }

    // Message middleware for command routing (needs cross-content logic)
    async function handleCommands(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ) {
        if (!(message instanceof UserMessage)) {
            await next();
            return;
        }

        // Extract text from message contents
        const textParts: TextContent[] = [];
        for await (const content of message.content) {
            if (content instanceof TextContent) {
                textParts.push(await content.value);
            }
        }
        const command = textParts.map(c => c.text).join("").trim();

        if (command === "/help") {
            thread.addMessage(new AgentMessage({
                content: [new TextContent({ text: "Available commands: /help, /status" })]
            }));
            return;
        }
        await next();
    }

    // Content middleware for streaming LLM text chunks
    async function logTextChunks(
        contentChunks: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ) {
        async function* process() {
            for await (const chunk of contentChunks) {
                console.log(`📝 LLM: ${chunk.text}`);
                yield chunk;
            }
        }
        await next(process());
    }

    // Content middleware for logging function calls
    async function logFunctionCalls(
        contentChunks: AsyncIterable<FunctionCallContent>,
        thread: IThread,
        next: (stream: AsyncIterable<FunctionCallContent>) => Promise<void>
    ) {
        // Wait for all chunks to assemble into complete function call
        const completeCall = await contentChunks.value;
        console.log(`🔧 Calling: ${completeCall.name}(${JSON.stringify(completeCall.arguments)})`);

        async function* process() {
            yield completeCall;
        }
        await next(process());
    }

    // Content middleware for logging function results
    async function logFunctionResults(
        contentChunks: AsyncIterable<FunctionResultContent>,
        thread: IThread,
        next: (stream: AsyncIterable<FunctionResultContent>) => Promise<void>
    ) {
        // Wait for complete result
        const completeResult = await contentChunks.value;
        console.log(`✅ Result: ${completeResult.result}`);

        async function* process() {
            yield completeResult;
        }
        await next(process());
    }

    // Functions
    function getWeather(location: string): string {
        return `Weather in ${location}: Sunny, 72°F`;
    }

    function getTime(): string {
        return new Date().toISOString();
    }

    // Configure agent with new pattern
    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are a helpful assistant with access to weather and time information.",
        apiKey: process.env.OPENAI_API_KEY!,
        storage: new SqlStorageProvider(process.env.DATABASE_URL!),
        functions: [
            { name: "get_weather", description: "Get current weather", fn: getWeather },
            { name: "get_time", description: "Get current time", fn: getTime }
        ],
        middleware: [
            [TextContent, logText],                        // Content middleware - log incoming text
            handleCommands,                                // Message middleware - command routing
            [TextContent, logTextChunks],                  // Content middleware - stream LLM text
            [FunctionCallContent, logFunctionCalls],       // Content middleware - log function calls
            [FunctionResultContent, logFunctionResults]    // Content middleware - log function results
        ]
    };
    const agent = new AgentHost(config);

    agent.listen(5000);
    ```

---

## What's Next?

You now know the fundamentals of the Agent Protocol Hosting SDK. Here are some next steps:

### Learn More

- **[API Reference](/api)** - Complete API documentation
- **[Middleware Guide](/guides/middleware)** - Deep dive into middleware patterns
- **[Function Calling](/guides/functions)** - Advanced function calling patterns
- **[Storage Providers](/guides/storage)** - Configure durable storage
- **[Deployment](/guides/deployment)** - Deploy to production

### Examples

- **[Multi-Agent Systems](/examples/multi-agent)** - Multiple agents working together
- **[RAG Agent](/examples/rag)** - Retrieval-augmented generation
- **[Code Interpreter](/examples/code-interpreter)** - Execute Python code safely
- **[Customer Support](/examples/customer-support)** - Full customer support bot

### Get Help

- **[GitHub Discussions](https://github.com/microsoft/agent-protocol/discussions)** - Ask questions
- **[Discord](https://discord.gg/agent-protocol)** - Join the community
- **[Stack Overflow](https://stackoverflow.com/questions/tagged/agent-protocol)** - Search existing questions

---

## Appendix: Middleware Patterns Summary

This section provides quick reference templates for both middleware patterns.

### Content Middleware

Content middleware processes streaming chunks from the LLM. Choose between transform (recommended) and wrap (advanced) patterns.

#### Transform Pattern (Recommended)

Use when transforming, filtering, or logging chunks:

=== "Python"

    ```python
    async def my_content_middleware(
        content_stream: AsyncIterable[TextContent],
        thread: IThread
    ) -> AsyncIterable[TextContent]:
        async for chunk in content_stream:
            # Process chunk
            print(f"Chunk: {chunk.text}")
            yield chunk  # Forward to next middleware

    # Register as tuple: (ContentType, function)
    config = AgentConfig(middleware=[
        (TextContent, my_content_middleware)
    ])
    ```

=== "C#"

    ```csharp
    async IAsyncEnumerable<TextContent> MyContentMiddleware(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await foreach (var chunk in contentStream.WithCancellation(cancellationToken))
        {
            // Process chunk
            Console.WriteLine($"Chunk: {chunk.Text}");
            yield return chunk; // Forward to next middleware
        }
    }

    // Register as tuple
    var agentOptions = new AgentOptions
    {
        Middleware = new MiddlewareCollection
        {
            MyContentMiddleware
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function* myContentMiddleware(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread
    ): AsyncIterable<TextContent> {
        for await (const chunk of contentStream) {
            // Process chunk
            console.log(`Chunk: ${chunk.text}`);
            yield chunk; // Forward to next middleware
        }
    }

    // Register as tuple
    const config = new AgentConfig({
        middleware: [
            [TextContent, myContentMiddleware]
        ]
    });
    ```

#### Wrap Pattern (Advanced)

Use when adding before/after logic (timing, error handling):

=== "Python"

    ```python
    async def my_content_middleware(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        # Before streaming
        print("Starting stream")

        await next(content_stream)  # Continue to next middleware

        # After streaming
        print("Stream complete")

    # Register as tuple
    config = AgentConfig(middleware=[
        (TextContent, my_content_middleware)
    ])
    ```

=== "C#"

    ```csharp
    async Task MyContentMiddleware(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken = default)
    {
        // Before streaming
        Console.WriteLine("Starting stream");

        await next(contentStream); // Continue to next middleware

        // After streaming
        Console.WriteLine("Stream complete");
    }

    // Register as tuple
    var agentOptions = new AgentOptions
    {
        Middleware = new MiddlewareCollection
        {
            MyContentMiddleware
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function myContentMiddleware(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        // Before streaming
        console.log("Starting stream");

        await next(contentStream); // Continue to next middleware

        // After streaming
        console.log("Stream complete");
    }

    // Register as tuple
    const config = new AgentConfig({
        middleware: [
            [TextContent, myContentMiddleware]
        ]
    });
    ```

### Message Middleware

Message middleware processes entire messages (user or agent). The framework handles different yield granularities automatically.

#### Transform Pattern (Recommended)

Use for logging, moderation, rate limiting, or filtering:

=== "Python"

    ```python
    # Yield the message (most common)
    async def my_message_middleware(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[IMessage]:
        print(f"Message from {message.role}")
        yield message  # Framework handles streaming

    # Or yield content to filter by type
    async def filter_images(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[Content]:
        async for content in message.content:
            if isinstance(content, TextContent):
                yield content  # Only yield text

    # Or yield chunks for fine-grained control
    async def track_tokens(
        message: IMessage,
        thread: IThread
    ) -> AsyncIterable[Chunk]:
        token_count = 0
        async for content in message.content:
            async for chunk in content:
                token_count += len(chunk.text.split())
                yield chunk
        print(f"Tokens: {token_count}")

    # Register as plain function
    config = AgentConfig(middleware=[my_message_middleware])
    ```

=== "C#"

    ```csharp
    // Yield the message (most common)
    async IAsyncEnumerable<IMessage> MyMessageMiddleware(
        IMessage message,
        IThread thread,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        Console.WriteLine($"Message from {message.Role}");
        yield return message; // Framework handles streaming
    }

    // Or yield content to filter by type
    async IAsyncEnumerable<Content> FilterImages(
        IMessage message,
        IThread thread,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        await foreach (var content in message.Content.WithCancellation(cancellationToken))
        {
            if (content is TextContent textContent)
            {
                yield return textContent; // Only yield text
            }
        }
    }

    // Or yield chunks for fine-grained control
    async IAsyncEnumerable<Chunk> TrackTokens(
        IMessage message,
        IThread thread,
        [EnumeratorCancellation] CancellationToken cancellationToken = default)
    {
        var tokenCount = 0;
        await foreach (var content in message.Content.WithCancellation(cancellationToken))
        {
            await foreach (var chunk in content.WithCancellation(cancellationToken))
            {
                tokenCount += chunk.Text.Split().Length;
                yield return chunk;
            }
        }
        Console.WriteLine($"Tokens: {tokenCount}");
    }

    // Register as plain function
    var agentOptions = new AgentOptions
    {
        Middleware = new MiddlewareCollection { MyMessageMiddleware }
    };
    ```

=== "TypeScript"

    ```typescript
    // Yield the message (most common)
    async function* myMessageMiddleware(
        message: IMessage,
        thread: IThread
    ): AsyncIterable<IMessage> {
        console.log(`Message from ${message.role}`);
        yield message; // Framework handles streaming
    }

    // Or yield content to filter by type
    async function* filterImages(
        message: IMessage,
        thread: IThread
    ): AsyncIterable<Content> {
        for await (const content of message.content) {
            if (content instanceof TextContent) {
                yield content; // Only yield text
            }
        }
    }

    // Or yield chunks for fine-grained control
    async function* trackTokens(
        message: IMessage,
        thread: IThread
    ): AsyncIterable<Chunk> {
        let tokenCount = 0;
        for await (const content of message.content) {
            for await (const chunk of content) {
                tokenCount += chunk.text.split(' ').length;
                yield chunk;
            }
        }
        console.log(`Tokens: ${tokenCount}`);
    }

    // Register as plain function
    const config = new AgentConfig({
        middleware: [myMessageMiddleware]
    });
    ```

#### Wrap Pattern (Advanced)

Use when adding before/after logic (timing, error handling):

=== "Python"

    ```python
    async def my_message_middleware(
        message: IMessage,
        thread: IThread,
        next: Callable[[], Awaitable[None]]
    ) -> None:
        # Before processing
        print(f"Processing message from {message.role}")

        await next()  # Continue to next middleware/LLM

        # After processing
        print("Processing complete")

    # Register as plain function
    config = AgentConfig(middleware=[my_message_middleware])
    ```

=== "C#"

    ```csharp
    async Task MyMessageMiddleware(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken cancellationToken = default)
    {
        // Before processing
        Console.WriteLine($"Processing message from {message.Role}");

        await next(); // Continue to next middleware/LLM

        // After processing
        Console.WriteLine("Processing complete");
    }

    // Register as plain function
    var agentOptions = new AgentOptions
    {
        Middleware = new MiddlewareCollection
        {
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)MyMessageMiddleware
        }
    };
    ```

=== "TypeScript"

    ```typescript
    async function myMessageMiddleware(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ): Promise<void> {
        // Before processing
        console.log(`Processing message from ${message.role}`);

        await next(); // Continue to next middleware/LLM

        // After processing
        console.log("Processing complete");
    }

    // Register as plain function
    const config = new AgentConfig({
        middleware: [myMessageMiddleware]
    });
    ```

### Choosing the Right Middleware

This comprehensive guide helps you decide which middleware type and pattern to use.

#### Step 1: Message or Content Middleware?

| Question | Answer | Use |
| -------- | ------ | --- |
| Does it run once per message (user or agent)? | Yes | **Message middleware** |
| Does it process individual streaming chunks? | Yes | **Content middleware** |
| Does it need to see the complete message? | Yes | **Message middleware** |
| Does it transform text as it streams? | Yes | **Content middleware** |

**Examples:**
- **Message middleware**: Authentication, rate limiting, routing, message-level logging, content moderation
- **Content middleware**: Transform text (uppercase), filter chunks, log each chunk, streaming metrics

**Registration:**
- **Message middleware**: Plain function in middleware array
- **Content middleware**: Tuple `(ContentType, function)` in middleware array

#### Step 2: Transform or Wrap Pattern?

| Question | Answer | Use |
| -------- | ------ | --- |
| Do you need to modify or filter data? | Yes | **Transform pattern** (async generator with `yield`) |
| Do you only need before/after logic? | Yes | **Wrap pattern** (`next()` callback) |
| Do you need to change the stream? | Yes | **Transform pattern** |
| Do you need timing or error handling? | Yes | **Wrap pattern** |

**Transform pattern examples:**
- Uppercase text, filter images, remove PII, log each chunk, enrich with metadata, rate limiting

**Wrap pattern examples:**
- Measure time before/after, error handling (try/catch), buffer entire response, add headers

#### Step 3: Middleware Ordering

**Order matters!** Middleware runs in array order. Follow these principles:

**Recommended order:**
```
1. Error handling (wrap) - catches errors from all middleware below
2. Timing/metrics (wrap) - measures total time
3. Authentication (message, transform) - verify user FIRST
4. Rate limiting (message, transform) - prevent abuse EARLY
5. Logging (message, transform) - log after auth succeeds
6. Content transformation (content, transform) - modify streaming data
7. Business logic middleware
```

**Example:**
```python
middleware=[
    error_handler,           # 1. Catch all errors (wrap, message)
    time_message,            # 2. Measure time (wrap, message)
    authenticate,            # 3. Verify user (transform, message)
    rate_limit,              # 4. Check limits (transform, message)
    log_for_debugging,       # 5. Log requests (transform, message)
    (TextContent, uppercase) # 6. Transform content (transform, content)
]
```

**Why this order?**
- **Error handler first**: Catches exceptions from all other middleware
- **Authentication before rate limiting**: Don't waste rate limit checks on invalid users
- **Logging after authentication**: Don't log rejected requests (reduce noise)
- **Content transformation last**: Operates on validated, authorized requests

#### Step 4: Error Handling

**What happens if middleware throws an exception?**

1. **Transform pattern**: Exception stops the pipeline, no more items yielded
2. **Wrap pattern**: Exception propagates up the stack
3. **No automatic retry**: You must handle errors explicitly

**Best practice: Add error handling middleware first**

```python
# Wrap pattern - catches errors from all middleware
async def error_handler(message: IMessage, thread: IThread, next):
    try:
        await next()  # Run remaining middleware
    except Exception as e:
        logger.error(f"Middleware error: {e}")
        # Send error message to user
        error_content = TextContent(text="Sorry, something went wrong.")
        error_msg = AgentMessage(content=[error_content])
        thread.add_message(error_msg)
```

#### Quick Reference Table

| Use Case | Middleware Type | Pattern | Example |
| -------- | --------------- | ------- | ------- |
| Verify user identity | Message | Transform | `if not valid: return; yield message` |
| Check usage limits | Message | Transform | `if over_limit: raise; yield message` |
| Log message metadata | Message | Transform | `logger.info(...); yield message` |
| Measure message time | Message | Wrap | `start = time(); await next(); log(time()-start)` |
| Uppercase streaming text | Content | Transform | `yield {...chunk, text: chunk.text.upper()}` |
| Log each chunk | Content | Transform | `logger.debug(chunk); yield chunk` |
| Buffer complete response | Content | Wrap | `chunks = []; async for c in stream: chunks.append(c)` |
| Error handling | Message | Wrap | `try: await next(); except: handle()` |

### Unified Middleware Array

Mix both types and patterns in a single array:

=== "Python"

    ```python
    config = AgentConfig(
        middleware=[
            log_message,                        # Message middleware (transform or wrap)
            rate_limit,                         # Message middleware (transform or wrap)
            (TextContent, uppercase_content),   # Content middleware (transform or wrap)
            (ImageContent, filter_images),      # Content middleware (transform or wrap)
        ]
    )
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Middleware = new MiddlewareCollection
        {
            (Func<IMessage, IThread, CancellationToken, IAsyncEnumerable<IMessage>>)LogMessage,
            (Func<IMessage, IThread, CancellationToken, IAsyncEnumerable<IMessage>>)RateLimit,
            UppercaseContent,
            FilterImages
        }
    };
    ```

=== "TypeScript"

    ```typescript
    const config = new AgentConfig({
        middleware: [
            logMessage,                    // Message middleware (transform or wrap)
            rateLimit,                     // Message middleware (transform or wrap)
            [TextContent, uppercaseContent], // Content middleware (transform or wrap)
            [ImageContent, filterImages]     // Content middleware (transform or wrap)
        ]
    });
    ```

**Key points:**

- **Message middleware**: Plain function, runs once per message
- **Content middleware**: Tuple `(ContentType, function)`, runs for streaming chunks
- **Transform pattern**: Return `AsyncIterable`, yield items (recommended for 90% of cases)
- **Wrap pattern**: Accept `next` parameter, call `await next()` (advanced, 10% of cases)
- **Execution order**: Array order
- **Granularity**: Yield messages, content, or chunks - framework handles it
- **Stop processing**: Don't yield/call `next()`
