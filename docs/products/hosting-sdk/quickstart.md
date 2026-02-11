# Agent Protocol Hosting SDK - Quickstart (next() approach)

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
    pip install microsoft-agents-hosting
    pip install python-dotenv  # For loading .env
    ```

=== "C#"

    ```bash
    dotnet add package Microsoft.Agents.Protocol.Hosting
    ```

=== "TypeScript"

    ```bash
    npm install @microsoft/agents-hosting
    npm install dotenv
    ```

---

## Step 1: Hello World

Create your first agent in under 2 minutes.

=== "Python"

    ```python
    from microsoft.agents.hosting import AgentHost, AgentConfig
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
    import { AgentHost, AgentConfig } from '@microsoft/agents-hosting';
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
        # Output: "Agent: Hello! How can I help you today?"

    import asyncio
    asyncio.run(test())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");
    var response = await client.CompleteChatAsync("Hello!");
    Console.WriteLine($"Agent: {response.Text}");
    // Output: "Agent: Hello! How can I help you today?"
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol';

    const client = new AgentProtocolClient("http://localhost:5000");
    const response = await client.completeChat("Hello!");
    console.log(`Agent: ${response.text}`);
    // Output: "Agent: Hello! How can I help you today?"
    ```

🎉 **Congratulations!** You've built your first agent. The LLM automatically handles incoming messages and generates responses.

**What you get automatically:**
- ✅ REST API endpoint (`POST /v1/threads/{thread_id}/runs`)
- ✅ Streaming responses (SSE)
- ✅ Conversation history (in-memory)
- ✅ Horizontal scaling (multiple workers)
- ✅ Worker restarts without losing state
- ✅ Long-running conversations (days/weeks)
- ✅ Async processing (user doesn't wait)

---

## Understanding What Just Happened

Before going further, let's understand the architecture you just created.

### Mental Model: Client vs Host

Your agent code is a **Host** (server-side), not a **Client** (user-facing app).

**Dataflow:**

```
┌─────────────────┐
│  Client SDK     │  (Web app, mobile app, CLI)
│  (User Device)  │
└────────┬────────┘
         │ HTTP/SSE
         │
┌────────▼────────┐
│  Agent Host     │  (Your code - what you just wrote)
│  (Your Server)  │
└────┬───────┬────┘
     │       │
     │       └─────► Storage (threads, state)
     │
     ▼
┌─────────────────┐
│  LLM Provider   │  (OpenAI, Anthropic, etc.)
│  APIs           │
└─────────────────┘
```

**Processing Flow:**

```
1. Client sends message
   → Queued in Agent Host

2. Worker picks up message
   → Loads conversation history
   → Calls your middlewares
   → Calls LLM if needed
   → Generates response events
   → Saves to durable log
   → Worker exits

3. Client streams events
   → Receives response in real-time
```

**Key Differences:**

| Aspect | Client | Host |
|--------|--------|------|
| **Lifecycle** | Long-lived (minutes/hours) | Short-lived (seconds) |
| **Connects to** | Agent host (your server) | LLM APIs |
| **Processes** | One conversation | Many conversations |
| **Runs on** | User's device | Your servers |

**Why This Architecture?**

- ✅ Horizontal scaling (multiple workers)
- ✅ Worker restarts without losing state
- ✅ Long-running conversations (days/weeks)
- ✅ Async processing (user doesn't wait)

### How the Pipeline Works

When you build an agent, you're creating a **processing pipeline**:

```
User Message
    ↓
[Middleware 1]  ← Your code
    ↓
[Middleware 2]  ← Your code
    ↓
[LLM]          ← Automatic
    ↓
[Functions]    ← Your tools
    ↓
[LLM]          ← Processes function results
    ↓
Response
```

**Key insight:** The **order** matters! Components execute in the order you register them:

```python
config = AgentConfig(
    model="gpt-4",
    instructions="...",
    middlewares=[middleware1],  # Runs first
    functions=[my_function]     # Runs third (when LLM calls it)
)
agent = AgentHost(config)
```

**Function placement in particular is important:**
- **Function schemas** are always visible to the LLM (so it knows what's available)
- **Function execution** happens at the point where functions appear in the chain
- Most commonly, you'll add functions right after the model so they execute immediately

This becomes important when you want to validate, log, or transform function calls before they execute (covered later).

---

---

## Step 2: Adding Tools

Agents become powerful when they can call functions to get real-time data or take actions.

=== "Python"

    ```python
    from microsoft.agents.hosting import AgentHost, AgentConfig
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
    import { AgentHost, AgentConfig } from '@microsoft/agents-hosting';

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

---

## Step 3: Client-Provided Functions

Allow clients to provide their own function implementations that the agent can call.

### Server Configuration

**Key insight:** Clients own the function schemas. The server just controls which functions are allowed.

**Simplest approach** - Accept any function the client provides:

=== "Python"

    ```python
    from microsoft.agents.hosting import AgentHost, AgentConfig
    import os

    config = AgentConfig(
        model="gpt-4",
        instructions="You are a helpful assistant.",
        api_key=os.getenv("OPENAI_API_KEY"),
        accept_client_functions=True  # ✅ Client can provide any function
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
        AcceptClientFunctions = true  // ✅ Client can provide any function
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
        acceptClientFunctions: true  // ✅ Client can provide any function
    };

    const agent = new AgentHost(config);
    ```

**Restrict by name** - Only allow specific function names:

=== "Python"

    ```python
    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        client_functions=["get_local_file", "get_system_info"]  # Only allow these
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
        ClientFunctions = new[] { "get_local_file", "get_system_info" }  // Only allow these
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
        clientFunctions: ["get_local_file", "get_system_info"]  // Only allow these
    };

    const agent = new AgentHost(config);
    ```

### Client Implementation

The client defines function schemas and implementations. The server validates the names:

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient, ToolCollection
    import platform

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Define client-side tool implementations
        tools = ToolCollection()

        @tools.function("get_local_file")
        async def get_local_file(path: str) -> str:
            """Read a file from the user's local filesystem"""
            try:
                with open(path, 'r') as f:
                    return f.read()
            except Exception as e:
                return f"Error reading file: {str(e)}"

        @tools.function("get_system_info")
        async def get_system_info() -> str:
            """Get information about the user's system"""
            return f"OS: {platform.system()} {platform.release()}, Python: {platform.python_version()}"

        # Send message with client-provided tools
        response = await client.complete_chat(
            "What's in my config.json file and what system am I using?",
            tools=tools
        )
        print(f"Agent: {response.text}")

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
        .Add("get_local_file", "Read a file from the user's local filesystem",
            (string path) =>
            {
                try
                {
                    return File.ReadAllText(path);
                }
                catch (Exception ex)
                {
                    return $"Error reading file: {ex.Message}";
                }
            })
        .Add("get_system_info", "Get information about the user's system",
            () => $"OS: {Environment.OSVersion}, .NET: {Environment.Version}");

    // Send message with client-provided tools
    var response = await client.CompleteChatAsync(
        "What's in my config.json file and what system am I using?",
        tools: tools
    );
    Console.WriteLine($"Agent: {response.Text}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, ToolCollection } from '@microsoft/agents-protocol-client';
    import * as fs from 'fs';
    import * as os from 'os';

    const client = new AgentProtocolClient("http://localhost:5000");

    // Define client-side tool implementations
    const tools = new ToolCollection()
        .add("get_local_file", "Read a file from the user's local filesystem",
            async (path: string) => {
                try {
                    return await fs.promises.readFile(path, 'utf-8');
                } catch (error) {
                    const message = error instanceof Error ? error.message : String(error);
                    return `Error reading file: ${message}`;
                }
            })
        .add("get_system_info", "Get information about the user's system",
            () => `OS: ${os.platform()} ${os.release()}, Node: ${process.version}`);

    // Send message with client-provided tools
    const response = await client.completeChat(
        "What's in my config.json file and what system am I using?",
        { tools }
    );
    console.log(`Agent: ${response.text}`);
    ```

**How it works:**

1. **Client sends function schemas** - When starting a run, the client includes function definitions
2. **Server validates** - The server checks if the function names are allowed
3. **Functions bound to run** - Each run can have different client functions
4. **LLM sees schemas** - The model can call client functions like server-side functions
5. **Execution happens on client** - When the LLM requests a client function, the server sends it back to the client
6. **LLM generates final response** - The agent uses the function result to complete the response

!!! warning "Security Consideration"
    Client functions execute on the client side and access client resources (local files, system info, etc.). The server should only gate which function **names** are allowed, trusting clients to implement them correctly. Never accept function names that could be confused with privileged server operations.

---

## Step 4: Understanding Middleware

So far, you've let the LLM handle all messages automatically. But what if you want to:

- Log every message
- Route commands (`/help`, `/reset`)
- Add authentication
- Filter content

This is where **middleware** comes in.

### What is Middleware?

A **middleware** function processes messages before they reach the LLM:

```
Message → Middleware 1 → Middleware 2 → Middleware 3 → LLM → Response
```

Each middleware can:
1. **Inspect** the message and pass it along
2. **Modify** the message
3. **Respond** directly (skip LLM)
4. **Block** the message

### Your First Middleware

=== "Python"

    ```python
    from microsoft.agents.hosting import AgentHost, AgentConfig

    async def log_messages(message, thread, next):
        """Log every incoming message"""
        # Wait for message completion (buffers all content chunks)
        text = await message.wait()
        await thread.log(f"Received: {text}")

        # Call next() to continue the pipeline
        await next()

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middlewares=[log_messages]
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
        OnMessage = async (message, thread, next, ct) =>
        {
            // Wait for message completion (buffers all content chunks)
            var text = await message.WaitForCompletionAsync(ct);
            await thread.LogAsync($"Received: {text}", ct);

            // Call next() to continue the pipeline
            await next();
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { AgentHost, AgentConfig } from '@microsoft/agents-hosting';

    async function logMessages(message, thread, next) {
        // Wait for message completion (buffers all content chunks)
        const text = await message.wait();
        await thread.log(`Received: ${text}`);

        // Call next() to continue the pipeline
        await next();
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middlewares: [logMessages]
    };

    const agent = new AgentHost(config);
    ```

**Key concept:** Call `next()` to pass control to the next middleware or LLM. If you don't call `next()`, the pipeline stops.

### Command Routing Middleware

=== "Python"

    ```python
    async def handle_commands(message, thread, next):
        """Handle slash commands"""
        # Wait for message completion and extract text
        text = (await message.wait()).get_text()

        if text.startswith("/help"):
            await thread.send_text(
                "Available commands:\n"
                "/help - Show this message\n"
                "/reset - Start new conversation"
            )
            return  # Don't call next() - we handled it

        if text.startswith("/reset"):
            # Clear conversation history (implementation depends on storage)
            await thread.send_text("Conversation reset!")
            return  # Don't call next()

        # Not a command, pass to LLM
        await next()

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middlewares=[handle_commands]
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
        OnMessage = async (message, thread, next, ct) =>
        {
            // Wait for message completion and extract text
            var text = (await message.WaitForCompletionAsync(ct)).GetText();

            if (text.StartsWith("/help"))
            {
                await thread.SendTextAsync(
                    "Available commands:\n" +
                    "/help - Show this message\n" +
                    "/reset - Start new conversation", ct);
                return;  // Don't call next() - we handled it
            }

            if (text.StartsWith("/reset"))
            {
                await thread.SendTextAsync("Conversation reset!", ct);
                return;  // Don't call next()
            }

            // Not a command, pass to LLM
            await next();
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function handleCommands(message, thread, next) {
        const text = (await message.wait()).getText();

        if (text.startsWith("/help")) {
            await thread.sendText(
                "Available commands:\n" +
                "/help - Show this message\n" +
                "/reset - Start new conversation"
            );
            return;  // Don't call next() - we handled it
        }

        if (text.startsWith("/reset")) {
            await thread.sendText("Conversation reset!");
            return;  // Don't call next()
        }

        // Not a command, pass to LLM
        await next();
    }
    ```

### Middleware Execution Order

When you register multiple middlewares, they execute in order:

1. **Message middlewares** - run in registration order
2. **LLM** - runs if all middlewares call `next()`

=== "Python"

    ```python
    async def log_middleware(message, thread, next):
        await thread.log(f"Message: {await message.wait()}")
        await next()  # Continue to next middleware

    async def command_middleware(message, thread, next):
        text = (await message.wait()).get_text()
        if text.startswith("/"):
            await thread.send_text("Handled command")
            return  # Stop here - don't call next()
        await next()  # Continue to LLM

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        middlewares=[log_middleware, command_middleware]  # Execute in order
    )

    agent = AgentHost(config)
    ```

**Flow:**
```
Message arrives
  → log_middleware (logs, calls next())
  → command_middleware (if command: stops, else: calls next())
  → LLM (if next() was called)
```

### Wrapping: Before AND After

A key advantage of `next()` is that middleware can run code **after** downstream processing:

=== "Python"

    ```python
    import time

    async def timing_middleware(message, thread, next):
        """Measure request timing"""
        start = time.time()
        await thread.log("Request started")

        # Process downstream middlewares and LLM
        await next()

        # This runs AFTER the LLM responds!
        duration = time.time() - start
        await thread.log(f"Request completed in {duration:.2f}s")
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        OnMessage = async (message, thread, next, ct) =>
        {
            var start = DateTime.UtcNow;
            await thread.LogAsync("Request started", ct);

            // Process downstream middlewares and LLM
            await next();

            // This runs AFTER the LLM responds!
            var duration = DateTime.UtcNow - start;
            await thread.LogAsync($"Request completed in {duration.TotalSeconds:F2}s", ct);
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function timingMiddleware(message, thread, next) {
        const start = Date.now();
        await thread.log("Request started");

        // Process downstream middlewares and LLM
        await next();

        // This runs AFTER the LLM responds!
        const duration = Date.now() - start;
        await thread.log(`Request completed in ${duration}ms`);
    }
    ```

**This is the key advantage of `next()`** - you can wrap both the request and response in a single middleware.

### Error Handling

Middleware can catch and handle errors from downstream processing:

=== "Python"

    ```python
    async def error_middleware(message, thread, next):
        """Catch and handle errors gracefully"""
        try:
            await next()  # Process downstream middlewares and LLM
        except Exception as e:
            # Log the error for debugging
            await thread.log(f"Error: {str(e)}")
            # Send user-friendly message
            await thread.send_text("Sorry, something went wrong. Please try again.")
            # Error is handled - don't re-raise

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        middlewares=[error_middleware, other_middleware]  # error_middleware first
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
        OnMessage = async (message, thread, next, ct) =>
        {
            try
            {
                await next();  // Process downstream middlewares and LLM
            }
            catch (Exception e)
            {
                // Log the error for debugging
                await thread.LogAsync($"Error: {e.Message}", ct);
                // Send user-friendly message
                await thread.SendTextAsync("Sorry, something went wrong. Please try again.", ct);
                // Error is handled - don't re-throw
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function errorMiddleware(message, thread, next) {
        try {
            await next();  // Process downstream middlewares and LLM
        } catch (e) {
            // Log the error for debugging
            await thread.log(`Error: ${e.message}`);
            // Send user-friendly message
            await thread.sendText("Sorry, something went wrong. Please try again.");
            // Error is handled - don't re-throw
        }
    }
    ```

**Best practice:** Register error middleware first so it wraps all other middlewares and catches any exceptions.

### Understanding the Streaming Model

Messages in the Agent Protocol have a nested streaming structure:

```
Message
  └─> AsyncIterable<Content>  (text, image, function calls, etc.)
       └─> AsyncIterable<Chunk>  (streaming pieces of each content)
```

You can process streams at different levels depending on your needs:

1. **Message level with `message.wait()`** - Buffers all content and chunks
2. **Content-type level** - Process specific content types with dedicated middleware
3. **Message-level chunks with `message.chunks()`** - Process all chunks across all content types

**Decision Tree: Which approach should I use?**

```
Do you need to process content as it streams?
├─ No → Use message.wait()
│         └─ Example: "Get the full text and check if it contains a keyword"
│
└─ Yes → Do you need to handle different content types separately?
    ├─ No → Use message.chunks()
    │        └─ Example: "Apply the same filter to all content"
    │
    └─ Yes → Use content-specific middleware
             └─ Example: "Transform text, log images, validate function calls"
```

**Quick reference:**
- **Simple use case** (just need the complete message): `message.wait()`
- **Process all chunks the same way**: `message.chunks()`
- **Different logic per content type**: Content-specific middleware

### Processing LLM Output

You can also add middlewares **after** the model to process content generated by the LLM:

**Option 1: Transform chunks as they stream (by content type)**

=== "Python"

    ```python
    from microsoft.agents.protocol import TextContent
    from typing import AsyncIterable

    async def filter_llm_output(chunks: AsyncIterable[TextContent], thread, next):
        """Transform LLM output chunks"""
        async def transform():
            async for chunk in chunks:  # Read LLM chunks
                # Transform or filter LLM output
                filtered = chunk.text.replace("bad_word", "[filtered]")
                yield TextContent(text=filtered)

        # Pass transformed chunks downstream
        await next(transform())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middlewares=[log_middleware],
        content_middlewares={
            TextContent: [filter_llm_output]
        }
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
        MessageMiddlewares = new[] { log_middleware },
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    // Transform chunks as they stream
                    async IAsyncEnumerable<TextContent> Transform()
                    {
                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            var filtered = chunk.Text.Replace("bad_word", "[filtered]");
                            yield return new TextContent { Text = filtered };
                        }
                    }

                    // Pass transformed chunks downstream
                    await next(Transform());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { TextContent } from '@microsoft/agents-protocol';

    async function filterLlmOutput(chunks, thread, next) {
        // Transform chunks as they stream
        async function* transform() {
            for await (const chunk of chunks) {
                const filtered = chunk.text.replace("bad_word", "[filtered]");
                yield new TextContent({ text: filtered });
            }
        }

        // Pass transformed chunks downstream
        await next(transform());
    }
    ```

**Option 1b: Process chunks at message level (across all content types)**

When you need message-level logic across different content types and their chunks, use `message.chunks()` to flatten the nested structure:

=== "Python"

    ```python
    async def process_all_chunks(message, thread, next):
        """Process all chunks regardless of content type"""
        async def transform_chunks():
            async for chunk in message.chunks():
                # chunk contains metadata: content_type, content_index, etc.
                if chunk.content_type == "text":
                    # Apply message-level text filtering
                    yield chunk.with_text(chunk.text.replace("bad_word", "[filtered]"))
                elif chunk.content_type == "image":
                    # Apply message-level image processing
                    yield process_image_chunk(chunk)
                else:
                    yield chunk

        # Pass transformed chunks downstream
        # Framework routes chunks back to correct content based on metadata
        await next(transform_chunks())

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middlewares=[process_all_chunks]
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
        OnMessage = async (message, thread, next, ct) =>
        {
            async IAsyncEnumerable<IChunk> TransformChunks()
            {
                await foreach (var chunk in message.Chunks().WithCancellation(ct))
                {
                    // chunk contains metadata: ContentType, ContentIndex, etc.
                    switch (chunk)
                    {
                        case TextChunk textChunk:
                            yield return textChunk with {
                                Text = textChunk.Text.Replace("bad_word", "[filtered]")
                            };
                            break;
                        case ImageChunk imageChunk:
                            yield return ProcessImageChunk(imageChunk);
                            break;
                        default:
                            yield return chunk;
                            break;
                    }
                }
            }

            // Framework routes chunks back to correct content based on metadata
            await next(TransformChunks());
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function processAllChunks(message, thread, next) {
        async function* transformChunks() {
            for await (const chunk of message.chunks()) {
                // chunk contains metadata: contentType, contentIndex, etc.
                if (chunk.contentType === "text") {
                    yield chunk.withText(chunk.text.replace("bad_word", "[filtered]"));
                } else if (chunk.contentType === "image") {
                    yield processImageChunk(chunk);
                } else {
                    yield chunk;
                }
            }
        }

        // Framework routes chunks back to correct content based on metadata
        await next(transformChunks());
    }
    ```

**Option 2: Post-process after LLM completes**

=== "Python"

    ```python
    async def after_llm_middleware(chunks: AsyncIterable[TextContent], thread, next):
        """Do something after LLM finishes"""
        # First, pass chunks through to downstream/client
        await next(chunks)

        # Now this runs AFTER all chunks have been sent
        await thread.log("LLM finished responding")
        await metrics.record_completion()
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    // First, pass chunks through to downstream/client
                    await next(chunks);

                    // Now this runs AFTER all chunks have been sent
                    await thread.LogAsync("LLM finished responding", ct);
                    await metrics.RecordCompletionAsync(ct);
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function afterLlmMiddleware(chunks, thread, next) {
        // First, pass chunks through to downstream/client
        await next(chunks);

        // Now this runs AFTER all chunks have been sent
        await thread.log("LLM finished responding");
        await metrics.recordCompletion();
    }
    ```

**Key insights:**
- The pipeline flows through `next()` calls - position in the config determines when components register, but `next()` determines execution flow
- To process LLM output chunks:
  - Transform chunks: read from `chunks`, yield transformed, pass to `next()`
  - Post-process: call `next(chunks)` first, then run cleanup code
- **Chunk routing:** When you transform chunks using `message.chunks()`, each chunk contains metadata (content_type, content_index, etc.). The framework uses this metadata to route chunks back into the correct content structure when sending to downstream middlewares or clients

!!! note "Middleware Content Attribution"
    When a middleware sends new content using `thread.send_text()` or similar methods, that content is always attributed to a message from the current agent role. The LLM will not reason over or respond to content it generated that was then modified by other middlewares - it only sees the final output as agent messages in the conversation history.


### Intercepting Function Calls

**Function calls are just content types** - they flow through the same pipeline as text, images, or any other content. This means you can intercept, validate, or transform them using content-specific middleware:

=== "Python"

    ```python
    from microsoft.agents.protocol import FunctionCallContent, FunctionResultContent

    async def validate_function_calls(chunks: AsyncIterable[FunctionCallContent], thread, next):
        """Validate and log function calls before execution"""
        async def validated():
            async for chunk in chunks:
                # Log the function call
                await thread.log(f"Function call: {chunk.name}({chunk.arguments})")

                # Validate permissions
                if chunk.name == "delete_data" and not thread.user.is_admin:
                    # Return error instead of executing
                    yield FunctionResultContent(
                        call_id=chunk.id,
                        error="Permission denied: admin access required"
                    )
                else:
                    # Pass through for execution
                    yield chunk

        await next(validated())

    async def transform_function_results(chunks: AsyncIterable[FunctionResultContent], thread, next):
        """Transform function results after execution"""
        async def transformed():
            async for chunk in chunks:
                # Cache the result
                await cache.set(chunk.call_id, chunk.result)

                # Transform or filter result
                yield chunk

        await next(transformed())

    def get_weather(location: str) -> str:
        return f"Weather in {location}: sunny, 72°F"

    def delete_data(id: str) -> str:
        return f"Deleted data {id}"

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        functions=[get_weather, delete_data],
        content_middlewares={
            FunctionCallContent: [validate_function_calls],
            FunctionResultContent: [transform_function_results]
        }
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Functions = new[]
        {
            ("get_weather", "Get weather", (Func<string, string>)GetWeather),
            ("delete_data", "Delete data", (Func<string, string>)DeleteData)
        },
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(FunctionCallContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<FunctionCallContent> chunks, IThread thread, Func<IAsyncEnumerable<IContent>, Task> next, CancellationToken ct) =>
                {
                    async IAsyncEnumerable<IContent> Validated()
                    {
                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            await thread.LogAsync($"Function call: {chunk.Name}({chunk.Arguments})", ct);

                            if (chunk.Name == "delete_data" && !thread.User.IsAdmin)
                            {
                                yield return new FunctionResultContent
                                {
                                    CallId = chunk.Id,
                                    Error = "Permission denied: admin access required"
                                };
                            }
                            else
                            {
                                yield return chunk;
                            }
                        }
                    }

                    await next(Validated());
                }
            },
            [typeof(FunctionResultContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<FunctionResultContent> chunks, IThread thread, Func<IAsyncEnumerable<FunctionResultContent>, Task> next, CancellationToken ct) =>
                {
                    async IAsyncEnumerable<FunctionResultContent> Transformed()
                    {
                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            await cache.SetAsync(chunk.CallId, chunk.Result, ct);
                            yield return chunk;
                        }
                    }

                    await next(Transformed());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { FunctionCallContent, FunctionResultContent } from '@microsoft/agents-protocol';

    async function validateFunctionCalls(chunks, thread, next) {
        async function* validated() {
            for await (const chunk of chunks) {
                await thread.log(`Function call: ${chunk.name}(${chunk.arguments})`);

                if (chunk.name === "delete_data" && !thread.user.isAdmin) {
                    yield new FunctionResultContent({
                        callId: chunk.id,
                        error: "Permission denied: admin access required"
                    });
                } else {
                    yield chunk;
                }
            }
        }

        await next(validated());
    }

    async function transformFunctionResults(chunks, thread, next) {
        async function* transformed() {
            for await (const chunk of chunks) {
                await cache.set(chunk.callId, chunk.result);
                yield chunk;
            }
        }

        await next(transformed());
    }

    function getWeather(location: string): string {
        return `Weather in ${location}: sunny, 72°F`;
    }

    function deleteData(id: string): string {
        return `Deleted data ${id}`;
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        functions: [
            { name: "get_weather", description: "Get weather", fn: getWeather },
            { name: "delete_data", description: "Delete data", fn: deleteData }
        ],
        contentMiddlewares: {
            [FunctionCallContent.name]: [validateFunctionCalls],
            [FunctionResultContent.name]: [transformFunctionResults]
        }
    };

    const agent = new AgentHost(config);
    ```

**Key insight:** Function calls and results are just content types that stream through the pipeline. You don't need special methods - use the same middleware pattern you use for text, images, or any other content.

---

## Step 5: Content Types

The Agent Protocol supports multiple content types beyond simple text. Learn how to handle images, audio, reactions, and other message types.

### Multimodal Content

Handle images, audio, files, and other media from users.

=== "Python"

    ```python
    config = AgentConfig(
        model="gpt-4-vision",
        instructions="You can analyze images.",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4-vision",
        Instructions = "You can analyze images.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"]
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    const config: AgentConfig = {
        model: "gpt-4-vision",
        instructions: "You can analyze images.",
        apiKey: process.env.OPENAI_API_KEY!
    };

    const agent = new AgentHost(config);
    ```

**What this does:**
- LLM automatically receives all content types (text, images, audio, etc.)
- No special handling needed for basic multimodal input

!!! note "Automatic Model Capability Detection"
    The SDK detects model capabilities and only sends supported content:
    - GPT-4 Vision → Receives text + images
    - GPT-4 (non-vision) → Text only (images converted to descriptions)
    - Claude 3.5 → Text + images + documents

### Processing Multimodal Content in Middlewares

If you need to process different content types:

=== "Python"

    ```python
    from microsoft.agents.protocol import ImageContent

    async def log_images(chunks: AsyncIterable[ImageContent], thread, next):
        """Log image metadata"""
        async def process():
            async for chunk in chunks:
                await thread.log(f"Image received: {chunk.uri}")
                yield chunk  # Forward unchanged

        await next(process())

    config = AgentConfig(
        model="gpt-4-vision",
        instructions="You can analyze images.",
        api_key=os.getenv("OPENAI_API_KEY"),
        content_middlewares={
            ImageContent: [log_images]
        }
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4-vision",
        Instructions = "You can analyze images.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(ImageContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<ImageContent> chunks, IThread thread, Func<IAsyncEnumerable<ImageContent>, Task> next, CancellationToken ct) =>
                {
                    async IAsyncEnumerable<ImageContent> Process()
                    {
                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            await thread.LogAsync($"Image received: {chunk.Uri}", ct);
                            yield return chunk;  // Forward unchanged
                        }
                    }

                    await next(Process());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { ImageContent } from '@microsoft/agents-protocol';

    async function logImages(chunks, thread, next) {
        async function* process() {
            for await (const chunk of chunks) {
                await thread.log(`Image received: ${chunk.uri}`);
                yield chunk;  // Forward unchanged
            }
        }

        await next(process());
    }
    ```

### Special Messages

Handle reactions, typing indicators, and other events using the same `next()` pattern:

=== "Python"

    ```python
    from microsoft.agents.protocol import MessageReactionContent, TypingIndicatorContent

    async def on_reaction(chunks: AsyncIterable[MessageReactionContent], thread, next):
        """Handle emoji reactions"""
        async for chunk in chunks:
            if chunk.reaction == "👍":
                await thread.send_text("Thanks for the feedback!")
                return  # Don't call next() - we handled it

        # Acknowledged, no response needed
        return

    async def on_typing(chunks: AsyncIterable[TypingIndicatorContent], thread, next):
        """Handle typing indicators"""
        # Just acknowledge silently (don't call next)
        return

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        content_middlewares={
            MessageReactionContent: [on_reaction],
            TypingIndicatorContent: [on_typing]
        }
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
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(MessageReactionContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<MessageReactionContent> chunks, IThread thread, Func<IAsyncEnumerable<MessageReactionContent>, Task> next, CancellationToken ct) =>
                {
                    await foreach (var chunk in chunks.WithCancellation(ct))
                    {
                        if (chunk.Reaction == "👍")
                        {
                            await thread.SendTextAsync("Thanks for the feedback!", ct);
                            return;  // Don't call next()
                        }
                    }
                    // Acknowledged
                }
            },
            [typeof(TypingIndicatorContent)] = new Delegate[]
            {
                (IAsyncEnumerable<TypingIndicatorContent> chunks, IThread thread, Func<IAsyncEnumerable<TypingIndicatorContent>, Task> next, CancellationToken ct) =>
                {
                    // Just acknowledge silently
                    return Task.CompletedTask;
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    import { MessageReactionContent, TypingIndicatorContent } from '@microsoft/agents-protocol';

    async function onReaction(chunks, thread, next) {
        for await (const chunk of chunks) {
            if (chunk.reaction === "👍") {
                await thread.sendText("Thanks for the feedback!");
                return;  // Don't call next()
            }
        }
        // Acknowledged
    }

    async function onTyping(chunks, thread, next) {
        // Just acknowledge silently
        return;
    }

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        contentMiddlewares: {
            [MessageReactionContent.name]: [onReaction],
            [TypingIndicatorContent.name]: [onTyping]
        }
    };

    const agent = new AgentHost(config);
    ```

**Note:** Content-specific middlewares handle specific content types, while message middlewares handle all messages. Not calling `next()` stops the pipeline.

---


## Step 6: Persistent Conversations

Maintain context across multiple messages automatically.

**Key Insight:** Unlike the client SDK where you explicitly create a `Conversation`, the hosting SDK **automatically manages threads**. Each message includes a `thread_id`, and the SDK maintains conversation history.

=== "Python"

    ```python
    # That's it! The host automatically:
    # - Creates threads when needed
    # - Maintains conversation history
    # - Passes full context to the LLM
    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY")
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    // Threads are managed automatically!
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"]
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    // Threads are managed automatically!
    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!
    };

    const agent = new AgentHost(config);
    ```

**Test multi-turn conversation:**

=== "Python"

    ```python
    from microsoft.agents.client import AgentProtocolClient

    async def test():
        client = AgentProtocolClient("http://localhost:5000")

        # Create a conversation
        conversation = client.create_conversation()

        msg1 = await conversation.send("Hi, I'm Alice")
        print(f"Agent: {msg1.text}")
        # Output: "Nice to meet you, Alice!"

        msg2 = await conversation.send("What's my name?")
        print(f"Agent: {msg2.text}")
        # Output: "Your name is Alice."

        # Thread ID for resuming later
        print(f"Thread: {conversation.thread_id}")

    import asyncio
    asyncio.run(test())
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    // Create a conversation
    var conversation = client.CreateConversation();

    var msg1 = await conversation.SendAsync("Hi, I'm Alice");
    Console.WriteLine($"Agent: {msg1.Text}");
    // Output: "Nice to meet you, Alice!"

    var msg2 = await conversation.SendAsync("What's my name?");
    Console.WriteLine($"Agent: {msg2.Text}");
    // Output: "Your name is Alice."

    // Thread ID for resuming later
    Console.WriteLine($"Thread: {conversation.ThreadId}");
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol';

    const client = new AgentProtocolClient("http://localhost:5000");

    // Create a conversation
    const conversation = client.createConversation();

    const msg1 = await conversation.send("Hi, I'm Alice");
    console.log(`Agent: ${msg1.text}`);
    // Output: "Nice to meet you, Alice!"

    const msg2 = await conversation.send("What's my name?");
    console.log(`Agent: ${msg2.text}`);
    // Output: "Your name is Alice."

    // Thread ID for resuming later
    console.log(`Thread: ${conversation.threadId}`);
    ```

⚠️ **Important**: By default, threads are stored **in-memory** and lost on restart. For production, configure durable storage (covered later).

---


## Production Deployment

### Durable Storage

By default, conversations are in-memory (lost on restart). For production:

=== "Python"

    ```python
    from microsoft.agents.hosting import AgentHost, AgentConfig, SqlStorageProvider

    storage = SqlStorageProvider(
        connection_string="Server=localhost;Database=AgentProtocol;..."
    )

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        storage=storage
    )

    agent = AgentHost(config)
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting.Storage;

    var storage = new SqlStorageProvider(
        builder.Configuration.GetConnectionString("AgentProtocol")
    );

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Storage = storage
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

### Production Defaults

One-line production configuration:

=== "Python"

    ```python
    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        production=True  # Enables: durable storage, queues, retries, observability
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
        Production = true  // Enables: durable storage, queues, retries, observability
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

This enables:
- ✅ Durable state (SQL/Redis)
- ✅ Queue-based workers (horizontal scaling)
- ✅ Automatic retries with backoff
- ✅ Dead letter queue
- ✅ OpenTelemetry observability

### Resource Management

Earlier examples created resources like `HttpClient` inline for simplicity. In production, follow these patterns:

=== "C#"

    **Problem:** Creating `HttpClient` instances directly causes socket exhaustion:

    ```csharp
    // ❌ DON'T DO THIS IN PRODUCTION
    .AddFunction("weather", "Get weather", async (string city) =>
    {
        using var client = new HttpClient();  // Creates new socket each time
        var response = await client.GetStringAsync($"https://api.weather.com/{city}");
        return response;
    })
    ```

    **Solution:** Use dependency injection with `IHttpClientFactory`:

    ```csharp
    // Register in Program.cs
    builder.Services.AddHttpClient();

    // Access from service provider
    var sp = builder.Services.BuildServiceProvider();
    var httpClientFactory = sp.GetRequiredService<IHttpClientFactory>();

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        Functions = new[]
        {
            ("weather", "Get weather", (Func<string, Task<string>>)(async (string city) =>
            {
                var client = httpClientFactory.CreateClient();
                var response = await client.GetStringAsync($"https://api.weather.com/{city}");
                return response;
            }))
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "Python"

    **Problem:** Creating `ClientSession` instances per request:

    ```python
    # ❌ DON'T DO THIS IN PRODUCTION
    async def get_weather(city: str) -> str:
        async with aiohttp.ClientSession() as session:  # New session each time
            async with session.get(f"https://api.weather.com/{city}") as resp:
                return await resp.text()
    ```

    **Solution:** Reuse sessions across requests:

    ```python
    import aiohttp
    from contextlib import asynccontextmanager

    # Create reusable session
    http_session: aiohttp.ClientSession | None = None

    @asynccontextmanager
    async def lifespan(app):
        global http_session
        http_session = aiohttp.ClientSession()
        yield
        await http_session.close()

    async def get_weather(city: str) -> str:
        async with http_session.get(f"https://api.weather.com/{city}") as resp:
            return await resp.text()

    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        functions=[get_weather]
    )

    agent = AgentHost(config)
    ```

=== "TypeScript"

    **Problem:** Creating new fetch instances or not reusing connections:

    ```typescript
    // ❌ DON'T DO THIS IN PRODUCTION (depending on fetch implementation)
    .add("weather", "Get weather", async (city: string) => {
        const response = await fetch(`https://api.weather.com/${city}`);
        return await response.text();
    })
    ```

    **Solution:** For Node.js 18+, built-in `fetch` handles connection pooling. For earlier versions or custom needs:

    ```typescript
    import { Agent } from 'https';

    // Create reusable agent with connection pooling
    const httpsAgent = new Agent({
        keepAlive: true,
        maxSockets: 50
    });

    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        functions: [{
            name: "weather",
            description: "Get weather",
            fn: async (city: string) => {
                const response = await fetch(`https://api.weather.com/${city}`, {
                    // @ts-ignore - agent option for node-fetch compatibility
                    agent: httpsAgent
                });
                return await response.text();
            }
        }]
    };

    const agent = new AgentHost(config);
    ```

**Key principle:** Create expensive resources (HTTP clients, DB connections) once and reuse them. Don't create them per-request.

---

## Advanced: Stream Flow Control with next()

**When to read this section:** After you're comfortable with basic middlewares and want fine-grained control over streaming content chunk-by-chunk.

### The Challenge

When content streams (LLM responses, user audio, function results), middlewares see chunks arrive in real-time. You need to decide:
- Pass through without reading?
- Read and forward unchanged?
- Transform each chunk?
- Buffer at natural boundaries (sentences, paragraphs)?

The `next()` pattern gives you complete control while keeping code clean and composable.

### Core Patterns

**Pattern 1: Pass-Through (Don't Read Chunks)**

If you don't need to read chunks, just pass them through to the next middleware:

=== "Python"

    ```python
    async def log_middleware(chunks: AsyncIterable[TextContent], thread, next):
        """Log that we saw a text stream, but don't read chunks"""
        await thread.log("Received text stream")

        # Pass chunks through unread
        await next(chunks)
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    await thread.LogAsync("Received text stream", ct);

                    // Pass chunks through unread
                    await next(chunks);
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function logMiddleware(chunks, thread, next) {
        await thread.log("Received text stream");

        // Pass chunks through unread
        await next(chunks);
    }
    ```

**Pattern 2: Inspect and Forward Unchanged**

Read chunks for logging/monitoring while forwarding them unchanged:

=== "Python"

    ```python
    async def inspect_chunks(chunks: AsyncIterable[TextContent], thread, next):
        """Inspect each chunk while forwarding unchanged"""
        async def forward_with_logging():
            async for chunk in chunks:
                await thread.log(f"Chunk: {chunk.text}")
                yield chunk  # Forward unchanged

        await next(forward_with_logging())
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    async IAsyncEnumerable<TextContent> ForwardWithLogging()
                    {
                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            await thread.LogAsync($"Chunk: {chunk.Text}", ct);
                            yield return chunk;  // Forward unchanged
                        }
                    }

                    await next(ForwardWithLogging());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function inspectChunks(chunks, thread, next) {
        async function* forwardWithLogging() {
            for await (const chunk of chunks) {
                await thread.log(`Chunk: ${chunk.text}`);
                yield chunk;  // Forward unchanged
            }
        }

        await next(forwardWithLogging());
    }
    ```

**Pattern 3: Transform Per-Chunk**

Transform each chunk as it arrives:

=== "Python"

    ```python
    async def uppercase_transform(chunks: AsyncIterable[TextContent], thread, next):
        """Transform each chunk to uppercase"""
        async def transform():
            async for chunk in chunks:
                # Transform and forward
                yield TextContent(text=chunk.text.upper())

        await next(transform())
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    async IAsyncEnumerable<TextContent> Transform()
                    {
                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            yield return new TextContent { Text = chunk.Text.ToUpper() };
                        }
                    }

                    await next(Transform());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function uppercaseTransform(chunks, thread, next) {
        async function* transform() {
            for await (const chunk of chunks) {
                yield new TextContent({ text: chunk.text.toUpperCase() });
            }
        }

        await next(transform());
    }
    ```

**Pattern 4: Windowed Buffering (Sentence Boundaries)**

Buffer and process at natural boundaries like sentences:

=== "Python"

    ```python
    async def sentence_filter(chunks: AsyncIterable[TextContent], thread, next):
        """Filter content sentence by sentence"""
        async def filter_by_sentence():
            buffer = ""

            async for chunk in chunks:
                buffer += chunk.text

                # Process complete sentences
                while ". " in buffer:
                    sentence, buffer = buffer.split(". ", 1)
                    sentence += ". "

                    # Filter inappropriate content
                    if not contains_profanity(sentence):
                        yield TextContent(text=sentence)
                    else:
                        yield TextContent(text="[filtered]. ")

            # Flush remaining buffer
            if buffer.strip():
                cleaned = "[filtered]" if contains_profanity(buffer) else buffer
                yield TextContent(text=cleaned)

        await next(filter_by_sentence())
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    async IAsyncEnumerable<TextContent> FilterBySentence()
                    {
                        var buffer = "";

                        await foreach (var chunk in chunks.WithCancellation(ct))
                        {
                            buffer += chunk.Text;

                            // Process complete sentences
                            while (buffer.Contains(". "))
                            {
                                var parts = buffer.Split(new[] { ". " }, 2, StringSplitOptions.None);
                                var sentence = parts[0] + ". ";
                                buffer = parts[1];

                                var filtered = ContainsProfanity(sentence)
                                    ? "[filtered]. "
                                    : sentence;
                                yield return new TextContent { Text = filtered };
                            }
                        }

                        // Flush remaining buffer
                        if (!string.IsNullOrWhiteSpace(buffer))
                        {
                            var cleaned = ContainsProfanity(buffer) ? "[filtered]" : buffer;
                            yield return new TextContent { Text = cleaned };
                        }
                    }

                    await next(FilterBySentence());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function sentenceFilter(chunks, thread, next) {
        async function* filterBySentence() {
            let buffer = "";

            for await (const chunk of chunks) {
                buffer += chunk.text;

                // Process complete sentences
                while (buffer.includes(". ")) {
                    const idx = buffer.indexOf(". ");
                    let sentence = buffer.substring(0, idx + 2);
                    buffer = buffer.substring(idx + 2);

                    if (!containsProfanity(sentence)) {
                        yield new TextContent({ text: sentence });
                    } else {
                        yield new TextContent({ text: "[filtered]. " });
                    }
                }
            }

            // Flush remaining buffer
            if (buffer.trim()) {
                const cleaned = containsProfanity(buffer) ? "[filtered]" : buffer;
                yield new TextContent({ text: cleaned });
            }
        }

        await next(filterBySentence());
    }
    ```

**Pattern 5: Buffer Complete Content**

Sometimes you need all chunks before deciding how to proceed:

=== "Python"

    ```python
    async def content_filter(chunks: AsyncIterable[TextContent], thread, next):
        """Filter based on complete content"""
        # Collect all chunks
        full_text = ""
        async for chunk in chunks:
            full_text += chunk.text

        # Make decision based on complete content
        if is_inappropriate(full_text):
            # Replace entire content
            async def filtered():
                yield TextContent(text="[Content filtered by policy]")
            await next(filtered())
        else:
            # Recreate original stream
            async def passthrough():
                yield TextContent(text=full_text)
            await next(passthrough())
    ```

=== "C#"

    ```csharp
    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(TextContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<TextContent> chunks, IThread thread, Func<IAsyncEnumerable<TextContent>, Task> next, CancellationToken ct) =>
                {
                    // Collect all chunks
                    var fullText = "";
                    await foreach (var chunk in chunks.WithCancellation(ct))
                    {
                        fullText += chunk.Text;
                    }

                    // Make decision based on complete content
                    async IAsyncEnumerable<TextContent> Result()
                    {
                        if (IsInappropriate(fullText))
                        {
                            yield return new TextContent { Text = "[Content filtered by policy]" };
                        }
                        else
                        {
                            yield return new TextContent { Text = fullText };
                        }
                    }

                    await next(Result());
                }
            }
        }
    };

    builder.Services
        .AddAgentHost()
        .AddDefaultAgent(agentOptions);
    ```

=== "TypeScript"

    ```typescript
    async function contentFilter(chunks, thread, next) {
        // Collect all chunks
        let fullText = "";
        for await (const chunk of chunks) {
            fullText += chunk.text;
        }

        // Make decision based on complete content
        async function* result() {
            if (isInappropriate(fullText)) {
                yield new TextContent({ text: "[Content filtered by policy]" });
            } else {
                yield new TextContent({ text: fullText });
            }
        }

        await next(result());
    }
    ```


---

## Complete Example

Here's a full agent with all concepts using the `next()` pattern:

=== "Python"

    ```python
    from microsoft.agents.hosting import AgentHost, AgentConfig
    from microsoft.agents.protocol import MessageReactionContent
    from typing import AsyncIterable
    import os
    from datetime import datetime, timezone

    # Tools
    def get_weather(location: str) -> str:
        """Get current weather for a location"""
        return f"Weather in {location}: sunny, 72°F"

    def get_time() -> str:
        """Get current time in UTC"""
        return datetime.now(timezone.utc).isoformat()

    # Middlewares
    async def log_messages(message, thread, next):
        text = (await message.wait()).get_text()
        await thread.log(f"Thread {thread.thread_id}: {text}")
        await next()

    async def handle_commands(message, thread, next):
        text = (await message.wait()).get_text()
        if text == "/help":
            await thread.send_text("Ask me about weather or time!")
            return  # Don't call next() - we handled it
        await next()

    async def on_reaction(chunks: AsyncIterable[MessageReactionContent], thread, next):
        async for chunk in chunks:
            if chunk.reaction == "👍":
                await thread.send_text("Glad you liked it!")
                return  # Don't call next()
        # Acknowledged, no response

    # Build agent
    config = AgentConfig(
        model="gpt-4",
        instructions="You are helpful.",
        api_key=os.getenv("OPENAI_API_KEY"),
        middlewares=[log_messages, handle_commands],
        functions=[get_weather, get_time],
        content_middlewares={
            MessageReactionContent: [on_reaction]
        }
    )

    agent = AgentHost(config)

    if __name__ == "__main__":
        agent.run()
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Hosting;
    using Microsoft.Agents.Protocol;

    var builder = WebApplication.CreateBuilder(args);

    // Define middleware functions
    async Task LogMessages(IMessage message, IThread thread, Func<Task> next, CancellationToken ct)
    {
        var text = (await message.WaitForCompletionAsync(ct)).GetText();
        await thread.LogAsync($"Thread {thread.ThreadId}: {text}", ct);
        await next();
    }

    async Task HandleCommands(IMessage message, IThread thread, Func<Task> next, CancellationToken ct)
    {
        var text = (await message.WaitForCompletionAsync(ct)).GetText();
        if (text == "/help")
        {
            await thread.SendTextAsync("Ask me about weather or time!", ct);
            return;  // Don't call next()
        }
        await next();
    }

    // Tools
    string GetWeather(string location) => $"Weather in {location}: sunny, 72°F";
    string GetTime() => DateTime.UtcNow.ToString("O");

    var agentOptions = new AgentOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        ApiKey = builder.Configuration["OpenAI:ApiKey"],
        MessageMiddlewares = new[] { LogMessages, HandleCommands },
        Functions = new[]
        {
            ("get_weather", "Get current weather", (Func<string, string>)GetWeather),
            ("get_time", "Get current time", (Func<string>)GetTime)
        },
        ContentMiddlewares = new Dictionary<Type, Delegate[]>
        {
            [typeof(MessageReactionContent)] = new Delegate[]
            {
                async (IAsyncEnumerable<MessageReactionContent> chunks, IThread thread, Func<IAsyncEnumerable<MessageReactionContent>, Task> next, CancellationToken ct) =>
                {
                    await foreach (var chunk in chunks.WithCancellation(ct))
                    {
                        if (chunk.Reaction == "👍")
                        {
                            await thread.SendTextAsync("Glad you liked it!", ct);
                            return;
                        }
                    }
                }
            }
        }
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
    import { AgentHost, AgentConfig } from '@microsoft/agents-hosting';
    import { MessageReactionContent } from '@microsoft/agents-protocol';
    import 'dotenv/config';

    // Tools
    function getWeather(location: string): string {
        return `Weather in ${location}: sunny, 72°F`;
    }

    function getTime(): string {
        return new Date().toISOString();
    }

    // Middlewares
    async function logMessages(message, thread, next) {
        const text = (await message.wait()).getText();
        await thread.log(`Thread ${thread.threadId}: ${text}`);
        await next();
    }

    async function handleCommands(message, thread, next) {
        const text = (await message.wait()).getText();
        if (text === "/help") {
            await thread.sendText("Ask me about weather or time!");
            return;  // Don't call next()
        }
        await next();
    }

    async function onReaction(chunks, thread, next) {
        for await (const chunk of chunks) {
            if (chunk.reaction === "👍") {
                await thread.sendText("Glad you liked it!");
                return;
            }
        }
    }

    // Build agent
    const config: AgentConfig = {
        model: "gpt-4",
        instructions: "You are helpful.",
        apiKey: process.env.OPENAI_API_KEY!,
        middlewares: [logMessages, handleCommands],
        functions: [
            { name: "get_weather", description: "Get current weather", fn: getWeather },
            { name: "get_time", description: "Get current time", fn: getTime }
        ],
        contentMiddlewares: {
            [MessageReactionContent.name]: [onReaction]
        }
    };

    const agent = new AgentHost(config);
    agent.listen(5000);
    ```

---

## Next Steps

Now that you've mastered the basics with the `next()` pattern:

- **Multimodal Deep Dive**: Process images, audio, video in detail
- **Advanced Middleware Patterns**: Authentication, rate limiting, approval workflows
- **Production Guide**: Scaling, monitoring, deployment strategies
- **Storage Options**: SQL, Redis, Cosmos DB configuration
- **Security**: Authentication, authorization, content filtering

**Keep exploring!** The `next()` pattern gives you full control over the agent pipeline while keeping code clean and composable.
