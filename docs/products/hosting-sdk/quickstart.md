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

**Run it:**

=== "Python"

    ```bash
    python agent.py

    # Output:
    # ✓ Agent host started on http://localhost:5000
    # ✓ Ready to receive messages
    ```

=== "C#"

    ```bash
    dotnet run

    # Output:
    # info: Microsoft.Hosting.Lifetime[14]
    #       Now listening on: http://localhost:5000
    ```

=== "TypeScript"

    ```bash
    node agent.js

    # Output:
    # ✓ Agent host started on http://localhost:5000
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

**What this does:**

- SDK generates JSON schema from function signatures
- LLM decides when to call functions
- SDK executes functions and returns results to LLM
- LLM generates final response


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
                    using var client = new HttpClient();
                    var response = await client.GetStringAsync(
                        $"https://api.weather.com/v1/current?location={location}");
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
            return `Sorry, couldn't fetch weather: ${error.message}`;
        }
    }
    ```

**Best practices:**
- Catch exceptions and return user-friendly error messages
- Let the LLM explain the error to the user in natural language
- Log errors for debugging but don't expose internal details to users

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

**What happens now:**
- Clients can register their own functions
- Agent calls back to client to execute functions
- Client returns results to agent
- Agent continues processing

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
            () => {
                const files = fs.readdirSync('.');
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
  <user>Send an email to bob@example.com with subject 'Meeting' and list my local files</user>
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

!!! tip "What this shows"
    - Client provides function implementations when sending the message
    - Agent calls back to client to execute functions (send_email, get_local_files)
    - Client executes functions locally and returns results
    - Agent receives results and generates final response

**Flow:**

```
1. Client sends message with function schemas
2. Agent processes with LLM
3. LLM decides to call client function
4. Agent sends function_call_request to client
5. Client executes function locally
6. Client sends function_call_result back
7. Agent continues with LLM
8. Agent returns final response
```

**Security considerations:**
- Only enable `allow_client_functions` if you trust clients
- Client functions execute in client's environment (not server)
- Validate function results before using them
- Consider rate limiting function calls

---

## Step 4: Understanding Middleware

Middleware lets you intercept and modify messages **before and after** they're processed. Think of it as a pipeline where you control each stage.

This is **the most powerful feature** of the SDK. You can:
- Log all messages
- Route messages to different handlers
- Validate/sanitize inputs
- Add authentication
- Transform LLM outputs
- Implement custom logic

### What is Middleware?

Middleware is a function that:
1. **Receives** a message and the current thread
2. **Optionally processes** the message (logs, validates, modifies)
3. **Calls `next()`** to continue processing (or doesn't, to stop)
4. **Optionally processes again** after `next()` returns (post-processing)

### Your First Middleware

Let's add simple logging to see what's happening:

=== "Python"

    ```python
    from microsoft.agents.protocol.hosting import AgentHostBuilder
    from microsoft.agents.protocol import TextContent, IThread
    from typing import Callable, Awaitable, AsyncIterable
    import os

    async def log_text(
        content_chunks: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        # Wait for complete text content
        complete_text = await content_chunks.wait()

        print(f"📨 Received: {complete_text.text}")

        # Yield complete content to next middleware
        async def process():
            yield complete_text

        await next(process())  # Continue processing
        print(f"✅ Processed message")

    agent = (
        AgentHostBuilder()
            .use_model("gpt-4", "You are helpful.")
            .use_api_key(os.getenv("OPENAI_API_KEY"))
            .on_content(TextContent, log_text)
            .build()
    )
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;
    using Microsoft.Agents.Protocol.Hosting;

    async Task LogText(
        IAsyncEnumerable<TextContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        // Wait for complete text content
        var completeText = await contentChunks.WaitForCompletionAsync();

        Console.WriteLine($"📨 Received: {completeText.Text}");

        // Yield complete content to next middleware
        async IAsyncEnumerable<TextContent> Process()
        {
            yield return completeText;
        }

        await next(Process());
        Console.WriteLine($"✅ Processed message");
    }

    var agent = new AgentHostBuilder()
        .UseModel("gpt-4", "You are helpful.")
        .UseApiKey(builder.Configuration["OpenAI:ApiKey"])
        .OnContent<TextContent>(LogText)
        .Build();

    builder.Services.AddAgentHost(agent);
    ```

=== "TypeScript"

    ```typescript
    import { AgentHostBuilder } from '@microsoft/agents-protocol-hosting';
    import { TextContent, IThread } from '@microsoft/agents-protocol';

    async function logText(
        contentChunks: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        // Wait for complete text content
        const completeText = await contentChunks.value;

        console.log(`📨 Received: ${completeText.text}`);

        // Yield complete content to next middleware
        async function* process() {
            yield completeText;
        }

        await next(process());
        console.log(`✅ Processed message`);
    }

    const agent = new AgentHostBuilder()
        .useModel("gpt-4", "You are helpful.")
        .useApiKey(process.env.OPENAI_API_KEY!)
        .onContent(TextContent, logText)
        .build();
    ```

**Example Output:**

When a client sends the message "Hello, how are you?", you'll see:

```
📨 Received: Hello, how are you?
✅ Processed message
```

The middleware logs the incoming message before processing, then logs completion after the LLM generates a response.

### Command Routing Middleware

Route specific commands to custom handlers without calling the LLM:

!!! note "Why Message Middleware?"
    Command routing uses **message middleware** (not content middleware) because it needs to:

    - Check text content to detect commands
    - Make flow control decisions (skip LLM vs continue)
    - Short-circuit the pipeline with early return

    This is cross-content logic that requires message-level control.

=== "Python"

    ```python
    from microsoft.agents.protocol import UserMessage, AgentMessage, TextContent
    from microsoft.agents.protocol.hosting import AgentHostBuilder

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
        text = "".join(c.text for c in text_parts).strip()

        if text == "/help":
            # Handle directly - don't call next()
            response = AgentMessage(content=[
                TextContent(text="Available commands: /help, /status")
            ])
            thread.add_message(response)
            return

        if text == "/status":
            response = AgentMessage(content=[
                TextContent(text=f"Thread ID: {thread.id}")
            ])
            thread.add_message(response)
            return

        # Not a command - continue to LLM
        await next()

    agent = (
        AgentHostBuilder()
            .use_model("gpt-4", "You are helpful.")
            .use_api_key(os.getenv("OPENAI_API_KEY"))
            .on_message(handle_commands)
            .build()
    )
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;
    using Microsoft.Agents.Protocol.Hosting;
    using System.Linq;

    async Task HandleCommands(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken cancellationToken)
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
        var text = string.Join("", textParts.Select(c => c.Text)).Trim();

        if (text == "/help")
        {
            var response = new AgentMessage
            {
                Content = new[] { new TextContent { Text = "Available commands: /help, /status" } }
            };
            thread.AddMessage(response);
            return;  // Don't call next()
        }

        if (text == "/status")
        {
            var response = new AgentMessage
            {
                Content = new[] { new TextContent { Text = $"Thread ID: {thread.Id}" } }
            };
            thread.AddMessage(response);
            return;
        }

        await next();  // Not a command - continue to LLM
    }

    var agent = new AgentHostBuilder()
        .UseModel("gpt-4", "You are helpful.")
        .UseApiKey(builder.Configuration["OpenAI:ApiKey"])
        .OnMessage(HandleCommands)
        .Build();

    builder.Services.AddAgentHost(agent);
    ```

=== "TypeScript"

    ```typescript
    import { UserMessage, AgentMessage, TextContent, IMessage, IThread } from '@microsoft/agents-protocol';
    import { AgentHostBuilder } from '@microsoft/agents-protocol-hosting';

    async function handleCommands(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ): Promise<void> {
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
        const text = textParts.map(c => c.text).join("").trim();

        if (text === "/help") {
            const response = new AgentMessage({
                content: [new TextContent({ text: "Available commands: /help, /status" })]
            });
            thread.addMessage(response);
            return;  // Don't call next()
        }

        if (text === "/status") {
            const response = new AgentMessage({
                content: [new TextContent({ text: `Thread ID: ${thread.id}` })]
            });
            thread.addMessage(response);
            return;
        }

        await next();  // Not a command - continue to LLM
    }

    const agent = new AgentHostBuilder()
        .useModel("gpt-4", "You are helpful.")
        .useApiKey(process.env.OPENAI_API_KEY!)
        .onMessage(handleCommands)
        .build();
    ```

**Key insight:** By **not calling `next()`**, you short-circuit the pipeline. The message never reaches the LLM.

### Middleware Execution Order

Middleware execute in the order you register them:

=== "Python"

    ```python
    async def log_middleware(message, thread, next):
        print("1. Before log")
        await next()
        print("4. After log")

    async def command_middleware(message, thread, next):
        print("2. Before command")
        await next()
        print("3. After command")

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[log_middleware, command_middleware]  # Execute in order
    )

    # When a message arrives:
    # 1. Before log
    # 2. Before command
    # [LLM processes]
    # 3. After command
    # 4. After log
    ```

=== "C#"

    ```csharp
    async Task LogMiddleware(IMessage msg, IThread thread, Func<Task> next, CancellationToken ct)
    {
        Console.WriteLine("1. Before log");
        await next();
        Console.WriteLine("4. After log");
    }

    async Task CommandMiddleware(IMessage msg, IThread thread, Func<Task> next, CancellationToken ct)
    {
        Console.WriteLine("2. Before command");
        await next();
        Console.WriteLine("3. After command");
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new object[]
        {
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)LogMiddleware,
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)CommandMiddleware
        }
    };

    // When a message arrives:
    // 1. Before log
    // 2. Before command
    // [LLM processes]
    // 3. After command
    // 4. After log
    ```

=== "TypeScript"

    ```typescript
    async function logMiddleware(message: IMessage, thread: IThread, next: () => Promise<void>) {
        console.log("1. Before log");
        await next();
        console.log("4. After log");
    }

    async function commandMiddleware(message: IMessage, thread: IThread, next: () => Promise<void>) {
        console.log("2. Before command");
        await next();
        console.log("3. After command");
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [logMiddleware, commandMiddleware]  // Execute in order
    };

    // When a message arrives:
    // 1. Before log
    // 2. Before command
    // [LLM processes]
    // 3. After command
    // 4. After log
    ```

**Visual:**

```
┌─────────────────┐
│  User Message   │
└────────┬────────┘
         │
    [Middleware 1] ← Before
         │
    [Middleware 2] ← Before
         │
       [LLM]
         │
    [Middleware 2] ← After
         │
    [Middleware 1] ← After
         │
┌────────▼────────┐
│    Response     │
└─────────────────┘
```

### Wrapping: Before AND After

The real power of middleware is doing something **before and after** processing:

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
        Middleware = new object[]
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

Wrap processing in try/catch to handle errors gracefully:

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
        Middleware = new object[]
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
            console.error(`❌ Error: ${error.message}`);
            const errorMsg = new AgentMessage({
                content: [new TextContent({ text: "Sorry, something went wrong." })]
            });
            thread.addMessage(errorMsg);
        }
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [errorMiddleware]  // Add first to catch all errors
    };
    ```

### Choosing Middleware Type

The Agent Protocol provides two types of middleware for different use cases:

#### Content Middleware (Recommended for Most Cases)

Use **content middleware** when processing a **single content type**:

**Benefits:**

- ✅ Simpler API - get typed content directly
- ✅ Automatic type filtering - only see `TextContent`, `FunctionCallContent`, etc.
- ✅ Clear intent - explicitly handle one type

**Use cases:**

- Log text messages
- Validate function calls
- Transform function results
- Process images

**Example:**

=== "Python"

    ```python
    async def log_text(
        content_chunks: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        complete_text = await content_chunks.wait()
        print(f"📨 Received: {complete_text.text}")

        async def process():
            yield complete_text
        await next(process())

    # Register for TextContent only
    agent = (
        AgentHostBuilder()
            .use_model("gpt-4", "You are helpful.")
            .on_content(TextContent, log_text)
            .build()
    )
    ```

=== "C#"

    ```csharp
    async Task LogText(
        IAsyncEnumerable<TextContent> contentChunks,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken ct)
    {
        var completeText = await contentChunks.WaitForCompletionAsync();
        Console.WriteLine($"📨 Received: {completeText.Text}");

        async IAsyncEnumerable<TextContent> Process()
        {
            yield return completeText;
        }
        await next(Process());
    }

    // Register for TextContent only
    var agent = new AgentHostBuilder()
        .UseModel("gpt-4", "You are helpful.")
        .OnContent<TextContent>(LogText)
        .Build();
    ```

=== "TypeScript"

    ```typescript
    async function logText(
        contentChunks: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        const completeText = await contentChunks.value;
        console.log(`📨 Received: ${completeText.text}`);

        async function* process() {
            yield completeText;
        }
        await next(process());
    }

    // Register for TextContent only
    const agent = new AgentHostBuilder()
        .useModel("gpt-4", "You are helpful.")
        .onContent(TextContent, logText)
        .build();
    ```

#### Message Middleware (Advanced)

Use **message middleware** when you need **cross-content-type logic**:

**When to use:**

- ⚠️ More complex - manual type checking required
- ⚠️ Access to full message - can see all content types
- ⚠️ Flow control - can skip/modify message processing

**Use cases:**

- Command routing (check text, then decide action)
- Rate limiting (count ALL content types)
- Error handling (wrap entire message processing)
- Metrics (track message-level statistics)

**Example:**

=== "Python"

    ```python
    async def command_router(
        message: IMessage,
        thread: IThread,
        next: Callable[[], Awaitable[None]]
    ) -> None:
        # Check text content to detect commands
        text_parts = []
        async for content in message.content:
            if isinstance(content, TextContent):
                text_parts.append(await content.wait())
        text = "".join(c.text for c in text_parts).strip()

        if text.startswith("/help"):
            # Handle command directly - skip LLM
            await thread.send_text("Available commands: /help, /status")
            return

        # Not a command - continue to LLM
        await next()

    agent = (
        AgentHostBuilder()
            .use_model("gpt-4", "You are helpful.")
            .on_message(command_router)
            .build()
    )
    ```

=== "C#"

    ```csharp
    async Task CommandRouter(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken ct)
    {
        // Check text content to detect commands
        var textParts = new List<TextContent>();
        await foreach (var content in message.Content)
        {
            if (content is TextContent textContent)
            {
                textParts.Add(await textContent.WaitForCompletionAsync());
            }
        }
        var text = string.Join("", textParts.Select(c => c.Text)).Trim();

        if (text.StartsWith("/help"))
        {
            // Handle command directly - skip LLM
            await thread.SendTextAsync("Available commands: /help, /status");
            return;
        }

        // Not a command - continue to LLM
        await next();
    }

    var agent = new AgentHostBuilder()
        .UseModel("gpt-4", "You are helpful.")
        .OnMessage(CommandRouter)
        .Build();
    ```

=== "TypeScript"

    ```typescript
    async function commandRouter(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ): Promise<void> {
        // Check text content to detect commands
        const textParts: TextContent[] = [];
        for await (const content of message.content) {
            if (content instanceof TextContent) {
                textParts.push(await content.value);
            }
        }
        const text = textParts.map(c => c.text).join("").trim();

        if (text.startsWith("/help")) {
            // Handle command directly - skip LLM
            await thread.sendText("Available commands: /help, /status");
            return;
        }

        // Not a command - continue to LLM
        await next();
    }

    const agent = new AgentHostBuilder()
        .useModel("gpt-4", "You are helpful.")
        .onMessage(commandRouter)
        .build();
    ```

**Rule of thumb:** Start with content middleware for simple, single-type operations. Only use message middleware when you need to inspect multiple content types or control message flow.

---

### Understanding the Streaming Model

The Agent Protocol uses **streaming by default**. When you call the LLM, it doesn't return a single response—it returns **chunks** as they're generated.

**Key concepts:**

1. **Streaming is the default**: All LLM responses are streamed, not returned as a single blob
2. **Content middleware**: Process chunks as they stream (not just whole messages)
3. **AsyncIterables**: Content comes as async streams you can iterate over

**Mental model:**

```
LLM generates tokens → Chunks flow through pipeline → Your middleware processes each chunk → Client receives stream
```

### Processing LLM Output

To process content as it streams from the LLM, use **content middleware** in the unified `middleware` array:

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable, Callable, Awaitable

    async def log_text_content(
        content_stream: AsyncIterable[TextContent],
        thread: IThread,
        next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
    ) -> None:
        async def process_and_forward():
            async for chunk in content_stream:
                print(f"📝 LLM generated: {chunk.text}")
                yield chunk  # Forward to next middleware

        await next(process_and_forward())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            log_middleware,                     # Message middleware (plain function)
            (TextContent, log_text_content),    # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    async Task LogTextContent(
        IAsyncEnumerable<TextContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<TextContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<TextContent> ProcessAndForward()
        {
            await foreach (var chunk in contentStream)
            {
                Console.WriteLine($"📝 LLM generated: {chunk.Text}");
                yield return chunk;  // Forward to next middleware
            }
        }

        await next(ProcessAndForward());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new object[]
        {
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)LogMiddleware,  // Message middleware
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)LogTextContent)  // Content middleware (tuple)
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import { TextContent } from '@microsoft/agents-protocol';

    async function logTextContent(
        contentStream: AsyncIterable<TextContent>,
        thread: IThread,
        next: (stream: AsyncIterable<TextContent>) => Promise<void>
    ): Promise<void> {
        async function* processAndForward() {
            for await (const chunk of contentStream) {
                console.log(`📝 LLM generated: ${chunk.text}`);
                yield chunk;  // Forward to next middleware
            }
        }

        await next(processAndForward());
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            logMiddleware,                      // Message middleware (plain function)
            [TextContent, logTextContent],      // Content middleware (array)
        ]
    };
    ```

**Key differences from message middleware:**

| Aspect | Message Middleware | Content Middleware |
|--------|-------------------|-------------------|
| **When** | Once per message | Multiple times (per chunk) |
| **Input** | Single message | Stream of content chunks |
| **Output** | None (mutates thread) | Stream of content chunks |
| **Pattern** | `await next()` | `await next(async_generator)` |
| **Registration** | Plain function | Tuple: `(ContentType, function)` |

### Message-level chunks

You can also process entire messages as they're generated (not just content):

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentMessage

    async def process_all_chunks(
        message: IMessage,
        thread: IThread,
        next: Callable[[], Awaitable[None]]
    ) -> None:
        if isinstance(message, AgentMessage):
            print(f"🤖 Agent message received")
            async for content in message.content:
                if isinstance(content, TextContent):
                    complete_text = await content.wait()
                    print(f"  Text: {complete_text.text}")

        await next()

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[process_all_chunks]  # Message middleware
    )
    ```

=== "C#"

    ```csharp
    async Task ProcessAllChunks(
        IMessage message,
        IThread thread,
        Func<Task> next,
        CancellationToken cancellationToken)
    {
        if (message is AgentMessage agentMsg)
        {
            Console.WriteLine($"🤖 Agent message received");
            await foreach (var content in agentMsg.Content)
            {
                if (content is TextContent textContent)
                {
                    var completeText = await textContent.WaitForCompletionAsync();
                    Console.WriteLine($"  Text: {completeText.Text}");
                }
            }
        }

        await next();
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new object[]
        {
            (Func<IMessage, IThread, Func<Task>, CancellationToken, Task>)ProcessAllChunks
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import { AgentMessage, TextContent } from '@microsoft/agents-protocol';

    async function processAllChunks(
        message: IMessage,
        thread: IThread,
        next: () => Promise<void>
    ): Promise<void> {
        if (message instanceof AgentMessage) {
            console.log(`🤖 Agent message received`);
            for await (const content of message.content) {
                if (content instanceof TextContent) {
                    const completeText = await content.value;
                    console.log(`  Text: ${completeText.text}`);
                }
            }
        }

        await next();
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [processAllChunks]  // Message middleware
    };
    ```

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
        Middleware = new object[]
        {
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)AddEmojis)  // Content middleware (tuple)
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
        Middleware = new object[]
        {
            (typeof(FunctionCallContent), (Func<IAsyncEnumerable<FunctionCallContent>, IThread, Func<IAsyncEnumerable<FunctionCallContent>, Task>, CancellationToken, Task>)LogFunctionCalls),     // Tuple
            (typeof(FunctionResultContent), (Func<IAsyncEnumerable<FunctionResultContent>, IThread, Func<IAsyncEnumerable<FunctionResultContent>, Task>, CancellationToken, Task>)LogFunctionResults)  // Tuple
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

## Step 5: Content Types

The Agent Protocol supports multiple content types, not just text.

### Multimodal Content

Messages can contain text, images, audio, and more:

=== "Python"

    ```python
    from microsoft.agents.protocol import (
        UserMessage,
        TextContent,
        ImageContent,
        AudioContent,
        FileContent
    )

    # Text only
    msg1 = UserMessage(content=[
        TextContent(text="Hello!")
    ])

    # Text + Image
    msg2 = UserMessage(content=[
        TextContent(text="What's in this image?"),
        ImageContent(url="https://example.com/photo.jpg")
    ])

    # Audio
    msg3 = UserMessage(content=[
        AudioContent(url="https://example.com/audio.mp3")
    ])

    # File attachment
    msg4 = UserMessage(content=[
        TextContent(text="Analyze this CSV"),
        FileContent(url="https://example.com/data.csv", mime_type="text/csv")
    ])
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    // Text only
    var msg1 = new UserMessage
    {
        Content = new IContent[]
        {
            new TextContent { Text = "Hello!" }
        }
    };

    // Text + Image
    var msg2 = new UserMessage
    {
        Content = new IContent[]
        {
            new TextContent { Text = "What's in this image?" },
            new ImageContent { Url = "https://example.com/photo.jpg" }
        }
    };

    // Audio
    var msg3 = new UserMessage
    {
        Content = new IContent[]
        {
            new AudioContent { Url = "https://example.com/audio.mp3" }
        }
    };

    // File attachment
    var msg4 = new UserMessage
    {
        Content = new IContent[]
        {
            new TextContent { Text = "Analyze this CSV" },
            new FileContent { Url = "https://example.com/data.csv", MimeType = "text/csv" }
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import {
        UserMessage,
        TextContent,
        ImageContent,
        AudioContent,
        FileContent
    } from '@microsoft/agents-protocol';

    // Text only
    const msg1 = new UserMessage({
        content: [new TextContent({ text: "Hello!" })]
    });

    // Text + Image
    const msg2 = new UserMessage({
        content: [
            new TextContent({ text: "What's in this image?" }),
            new ImageContent({ url: "https://example.com/photo.jpg" })
        ]
    });

    // Audio
    const msg3 = new UserMessage({
        content: [new AudioContent({ url: "https://example.com/audio.mp3" })]
    });

    // File attachment
    const msg4 = new UserMessage({
        content: [
            new TextContent({ text: "Analyze this CSV" }),
            new FileContent({ url: "https://example.com/data.csv", mimeType: "text/csv" })
        ]
    });
    ```

### Processing Multimodal Content in Middleware

Use content middleware to process specific content types:

=== "Python"

    ```python
    from microsoft.agents.protocol import ImageContent
    from typing import AsyncIterable, Callable, Awaitable

    async def process_images(
        content_stream: AsyncIterable[ImageContent],
        thread: IThread,
        next: Callable[[AsyncIterable[ImageContent]], Awaitable[None]]
    ) -> None:
        async def transform():
            async for image in content_stream:
                print(f"🖼️ Processing image: {image.url}")
                # Could resize, compress, add watermark, etc.
                yield image

        await next(transform())

    config = AgentConfig(
        model="gpt-4-vision",
        instructions="You can see images.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (ImageContent, process_images),  # Content middleware (tuple)
        ]
    )
    ```

=== "C#"

    ```csharp
    async Task ProcessImages(
        IAsyncEnumerable<ImageContent> contentStream,
        IThread thread,
        Func<IAsyncEnumerable<ImageContent>, Task> next,
        CancellationToken cancellationToken)
    {
        async IAsyncEnumerable<ImageContent> Transform()
        {
            await foreach (var image in contentStream)
            {
                Console.WriteLine($"🖼️ Processing image: {image.Url}");
                // Could resize, compress, add watermark, etc.
                yield return image;
            }
        }

        await next(Transform());
    }

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4-vision",
        Instructions = "You can see images.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Middleware = new object[]
        {
            (typeof(ImageContent), (Func<IAsyncEnumerable<ImageContent>, IThread, Func<IAsyncEnumerable<ImageContent>, Task>, CancellationToken, Task>)ProcessImages)  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import { ImageContent } from '@microsoft/agents-protocol';

    async function processImages(
        contentStream: AsyncIterable<ImageContent>,
        thread: IThread,
        next: (stream: AsyncIterable<ImageContent>) => Promise<void>
    ): Promise<void> {
        async function* transform() {
            for await (const image of contentStream) {
                console.log(`🖼️ Processing image: ${image.url}`);
                // Could resize, compress, add watermark, etc.
                yield image;
            }
        }

        await next(transform());
    }

    const config: AgentConfig = {
        model: "gpt-4-vision",
        instructions: "You can see images.",
        apiKey: process.env.OPENAI_API_KEY!,
        middleware: [
            [ImageContent, processImages],  // Content middleware (array)
        ]
    };
    ```

### Special Messages

The protocol includes special message types for richer interactions:

=== "Python"

    ```python
    from microsoft.agents.protocol import (
        TypingIndicatorContent,
        MessageReactionContent,
        MessageDeleteContent,
        MessageUpdateContent
    )
    from typing import AsyncIterable, Callable, Awaitable

    async def handle_reactions(
        content_stream: AsyncIterable[MessageReactionContent],
        thread: IThread,
        next: Callable[[AsyncIterable[MessageReactionContent]], Awaitable[None]]
    ) -> None:
        async def process():
            async for reaction in content_stream:
                print(f"👍 User reacted with: {reaction.emoji}")
                yield reaction

        await next(process())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middleware=[
            (MessageReactionContent, handle_reactions),  # Content middleware (tuple)
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
                Console.WriteLine($"👍 User reacted with: {reaction.Emoji}");
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
        Middleware = new object[]
        {
            (typeof(MessageReactionContent), (Func<IAsyncEnumerable<MessageReactionContent>, IThread, Func<IAsyncEnumerable<MessageReactionContent>, Task>, CancellationToken, Task>)HandleReactions)  // Tuple
        }
    };
    ```

=== "TypeScript"

    ```typescript
    import { MessageReactionContent } from '@microsoft/agents-protocol';

    async function handleReactions(
        contentStream: AsyncIterable<MessageReactionContent>,
        thread: IThread,
        next: (stream: AsyncIterable<MessageReactionContent>) => Promise<void>
    ): Promise<void> {
        async function* process() {
            for await (const reaction of contentStream) {
                console.log(`👍 User reacted with: ${reaction.emoji}`);
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
            [MessageReactionContent, handleReactions],  // Content middleware (array)
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
        Middleware = new object[]
        {
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)BatchContent)  // Tuple
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
        Middleware = new object[]
        {
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)FilterProfanity)  // Tuple
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
        Middleware = new object[]
        {
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)TeeToAnalytics)  // Tuple
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
        Middleware = new object[]
        {
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)RateLimit)  // Tuple
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
        Middleware = new object[]
        {
            (typeof(TextContent), (Func<IAsyncEnumerable<TextContent>, IThread, Func<IAsyncEnumerable<TextContent>, Task>, CancellationToken, Task>)MarkdownToHtml)  // Tuple
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
    from microsoft.agents.protocol.hosting import AgentHostBuilder
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

    # Configure agent with builder pattern
    agent = (
        AgentHostBuilder()
            .use_model("gpt-4", "You are a helpful assistant with access to weather and time information.")
            .use_api_key(os.getenv("OPENAI_API_KEY"))
            .use_storage(SqlStorageProvider(os.getenv("DATABASE_URL")))
            .use_functions([get_weather, get_time])
            .on_content(TextContent, log_text)                      # Content middleware - log incoming text
            .on_message(handle_commands)                            # Message middleware - command routing
            .on_content(TextContent, log_text_chunks)               # Content middleware - stream LLM text
            .on_content(FunctionCallContent, log_function_calls)    # Content middleware - log function calls
            .on_content(FunctionResultContent, log_function_results) # Content middleware - log function results
            .build()
    )

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

    // Configure agent with builder pattern
    var agent = new AgentHostBuilder()
        .UseModel("gpt-4", "You are a helpful assistant with access to weather and time information.")
        .UseApiKey(builder.Configuration["OpenAI:ApiKey"])
        .UseStorage(new SqlStorageProvider(builder.Configuration["DatabaseUrl"]))
        .UseFunctions(new[]
        {
            ("get_weather", "Get current weather", (Func<string, string>)GetWeather),
            ("get_time", "Get current time", (Func<string>)GetTime)
        })
        .OnContent<TextContent>(LogText)                        // Content middleware - log incoming text
        .OnMessage(HandleCommands)                              // Message middleware - command routing
        .OnContent<TextContent>(LogTextChunks)                  // Content middleware - stream LLM text
        .OnContent<FunctionCallContent>(LogFunctionCalls)       // Content middleware - log function calls
        .OnContent<FunctionResultContent>(LogFunctionResults)   // Content middleware - log function results
        .Build();

    builder.Services.AddAgentHost(agent);

    var app = builder.Build();
    app.MapAgentProtocol();
    await app.RunAsync();
    ```

=== "TypeScript"

    ```typescript
    import { AgentHostBuilder } from '@microsoft/agents-protocol-hosting';
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

    // Configure agent with builder pattern
    const agent = new AgentHostBuilder()
        .useModel("gpt-4", "You are a helpful assistant with access to weather and time information.")
        .useApiKey(process.env.OPENAI_API_KEY!)
        .useStorage(new SqlStorageProvider(process.env.DATABASE_URL!))
        .useFunctions([
            { name: "get_weather", description: "Get current weather", fn: getWeather },
            { name: "get_time", description: "Get current time", fn: getTime }
        ])
        .onContent(TextContent, logText)                        // Content middleware - log incoming text
        .onMessage(handleCommands)                              // Message middleware - command routing
        .onContent(TextContent, logTextChunks)                  // Content middleware - stream LLM text
        .onContent(FunctionCallContent, logFunctionCalls)       // Content middleware - log function calls
        .onContent(FunctionResultContent, logFunctionResults)   // Content middleware - log function results
        .build();

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

### Message Middleware

Process entire messages (once per message):

```python
async def my_middleware(message: IMessage, thread: IThread, next: Callable[[], Awaitable[None]]) -> None:
    # Before processing
    print(f"Message: {text}")

    await next()  # Continue to next middleware/LLM

    # After processing
    print("Done")

# Register as plain function
config = AgentConfig(middleware=[my_middleware])
```

### Content Middleware

Process streaming content (multiple times per message):

```python
async def my_content_middleware(
    content_stream: AsyncIterable[TextContent],
    thread: IThread,
    next: Callable[[AsyncIterable[TextContent]], Awaitable[None]]
) -> None:
    async def process():
        async for chunk in content_stream:
            print(f"Chunk: {chunk.text}")
            yield chunk  # Forward to next middleware

    await next(process())

# Register as tuple: (ContentType, function)
config = AgentConfig(middleware=[
    (TextContent, my_content_middleware)  # Tuple notation
])
```

### Unified Middleware Array

Mix both types in a single array:

```python
config = AgentConfig(
    middleware=[
        message_middleware_1,                   # Message middleware
        (TextContent, content_middleware_1),    # Content middleware (tuple)
        message_middleware_2,                   # Message middleware
        (ImageContent, content_middleware_2),   # Content middleware (tuple)
    ]
)
```

**Key points:**
- Message middleware: plain function
- Content middleware: tuple `(ContentType, function)`
- Execution order: array order
- Stop processing: don't call `next()`
- Transform content: yield modified chunks
