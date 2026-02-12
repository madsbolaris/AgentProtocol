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
    ) -> AsyncIterable[IStreamable]:
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

    async IAsyncEnumerable<IStreamable> CommandRouter(
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
        contentStream: AsyncIterable<TextContent>,
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

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable

    async def uppercase_content(
        content_stream: AsyncIterable[TextContent],
        thread: IThread
    ) -> AsyncIterable[IStreamable]:
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

    async IAsyncEnumerable<IStreamable> UppercaseContent(
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
            # Wait for complete reaction content
            reaction = await content_stream.wait()

            # Convert reaction to a message the agent can understand
            developer_msg = DeveloperMessage(content=[
                TextContent(text=f"User reacted with {reaction.emoji} to a previous message.")
            ])
            yield reaction
            yield developer_msg  # Yield so LLM can process the notification

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
        async IAsyncEnumerable<IStreamable> Process()
        {
            // Wait for complete reaction content
            var reaction = await contentStream.WaitForCompletionAsync();

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
            yield return reaction;
            yield return developerMsg;  // Yield so LLM can process the notification
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
            // Wait for complete reaction content
            const reaction = await contentStream.value;

            // Convert reaction to a message the agent can understand
            const developerMsg = new DeveloperMessage({
                content: [
                    new TextContent({
                        text: `User reacted with ${reaction.emoji} to a previous message.`
                    })
                ]
            });
            yield reaction;
            yield developerMsg;  // Yield so LLM can process the notification
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
