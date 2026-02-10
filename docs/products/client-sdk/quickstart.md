# Client SDK Quickstart

!!! tip "New to Agent Protocol?"
    This quickstart focuses on the Client SDK specifically. If you want a unified 30-minute guide that shows all SDKs working together, start with the [Getting Started Guide](../../getting-started.md).

**Get started in 30 minutes**

This quickstart walks you through the simplest ways to interact with agents: simple completions, streaming responses, persistent conversations, and tool usage across Python, TypeScript, and C#.

---

## Before You Start

You need a running Agent Protocol server to connect to. Choose one of these options:

### Option 1: Run the Echo Sample (Recommended for Testing)

The echo-m365 agent is perfect for testing the Client SDK:

=== "Python"

    ```bash
    # Clone the repository
    git clone https://github.com/madsbolaris/AgentProtocol.git
    cd AgentProtocol/python/samples/agents/echo-m365

    # Install dependencies
    pip install -r requirements.txt

    # Run the agent
    python src/start_server.py
    ```

    Server will start at `http://localhost:3978`

=== "TypeScript"

    ```bash
    # Clone the repository
    git clone https://github.com/madsbolaris/AgentProtocol.git
    cd AgentProtocol/javascript/samples/echo-m365

    # Install and run
    npm install
    npm run start
    ```

    Server will start at `http://localhost:3978`

=== "C#"

    ```bash
    # Clone the repository
    git clone https://github.com/madsbolaris/AgentProtocol.git
    cd AgentProtocol/dotnet/samples/agents/EchoM365

    # Run the agent
    dotnet run
    ```

    Server will start at `http://localhost:5000`

!!! note "Port Configuration"
    The Python and TypeScript echo agents run on port **3978**, while the C# version runs on port **5000**. Make sure to use the correct port in your client code, or configure the agent to run on a specific port.

### Option 2: Use Your Own Agent

If you have a production Agent Protocol endpoint:

- **Base URL**: Your agent's URL (e.g., `https://agents.company.com`)
- **API Key**: Obtain from your agent administrator
- **Agent ID** (optional): Specific agent to use

---

## Prerequisites

- **Runtime**: Python 3.9+, Node.js 18+, or .NET 8+
- **Agent Server**: Running locally (see "Before You Start" above) or production endpoint
- **API Credentials** (for production): API key or OAuth2 token

---

## Installation

=== "Python"

    ```bash
    pip install microsoft-agents-protocol
    ```

=== "TypeScript"

    ```bash
    npm install @microsoft/agents-protocol-client
    ```

=== "C#"

    ```bash
    dotnet add package Microsoft.Agents.Protocol.Client
    ```

---

## Step 1: Simple Completion

The absolute simplest interaction - one line to get a response.

!!! tip "About Code Examples"
    Examples use snippet includes for maintainability. When rendered, you'll see complete, runnable code. Python examples require running inside an `async def main()` function with `asyncio.run(main())` - see the Complete Example section for the full pattern.

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    // Create client with your endpoint
    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-simple-completion_main.cs"
    ```

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient
    import asyncio

    async def main():
        # Create client with your endpoint (adjust port if needed)
        client = AgentProtocolClient("http://localhost:3978")

        --8<-- "docs/snippets/python/client-simple-completion_main.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    // Create client with your endpoint
    const client = new AgentProtocolClient("http://localhost:3978");

    --8<-- "docs/snippets/typescript/client-simple-completion_main.ts"
    ```

**Expected Output:**

```text
I can help you with analysis, writing, coding, research, and problem-solving tasks.
```

!!! tip "What this does"
    - Uses the server's default agent
    - Creates an ephemeral thread (no state persisted)
    - Returns the complete response when finished

---

## Step 2: Streaming Responses

Get tokens as they're generated for a better user experience (typewriter effect).

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-streaming_main.cs"
    ```

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient
    import asyncio

    async def main():
        client = AgentProtocolClient("http://localhost:3978")

        --8<-- "docs/snippets/python/client-streaming_main.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:3978");

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

---

## Step 3: Persistent Conversations

Maintain conversation context across multiple turns automatically.

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-conversation_main.cs"

    // Save thread ID to resume later
    Console.WriteLine($"Thread ID: {conversation.ThreadId}");
    ```

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient
    import asyncio

    async def main():
        client = AgentProtocolClient("http://localhost:3978")

        --8<-- "docs/snippets/python/client-conversation_main.py"

        # Save thread ID to resume later
        print(f"Thread ID: {conversation.thread_id}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:3978");

    --8<-- "docs/snippets/typescript/client-conversation_main.ts"
    ```

**Output:**

```text
Agent: The capital of France is Paris.
Agent: Paris has a population of approximately 2.1 million people in the city proper.
Thread ID: thread_abc123
```

!!! tip "What this does"
    - Creates a persistent thread on the server
    - Maintains full conversation history automatically
    - No manual thread management required

**Resume later:**

=== "C#"

    ```csharp
    --8<-- "docs/snippets/csharp/client-resume-conversation_main.cs"
    ```

=== "Python"

    ```python
    --8<-- "docs/snippets/python/client-resume-conversation_main.py"
    ```

=== "TypeScript"

    ```typescript
    --8<-- "docs/snippets/typescript/client-resume-conversation_main.ts"
    ```

---

## Step 4: Tools/Functions

Register tools that agents can call automatically.

!!! warning "Security Notice"
    Tool execution can be dangerous if not properly validated. Always validate and sanitize tool inputs in production. See the security section below for secure implementation patterns.

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var client = new AgentProtocolClient("http://localhost:5000");

    --8<-- "docs/snippets/csharp/client-tools_main.cs"
    ```

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient, ToolCollection
    import asyncio

    async def main():
        client = AgentProtocolClient("http://localhost:3978")

        --8<-- "docs/snippets/python/client-tools_main.py"

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, ToolCollection } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient("http://localhost:3978");

    --8<-- "docs/snippets/typescript/client-tools_main.ts"
    ```

**Output:**

```text
The weather in San Francisco is 72°F and sunny!
```

!!! tip "What this does"
    - Registers tools with simple lambda functions
    - SDK automatically executes when agent requests
    - Returns final response with tool results incorporated

---

## 🔒 Security Best Practices

!!! danger "Production Security Requirements"
    **⚠️ CRITICAL**: All examples use `http://localhost` for **local development only**. Production deployments require additional security measures.

### Security Checklist

Before deploying to production, ensure you have implemented:

| Requirement | Why | Priority |
| ----------- | --- | -------- |
| ✅ Use HTTPS (TLS 1.3+) | Prevents network interception and man-in-the-middle attacks | 🔴 Critical |
| ✅ Validate all tool inputs | Prevents injection attacks (SQL, command, code injection) | 🔴 Critical |
| ✅ Sanitize tool parameters | Prevents code execution and path traversal | 🔴 Critical |
| ✅ Store secrets securely | Use Vault/Key Vault, never hardcode or use plain env vars | 🔴 Critical |
| ✅ Rate limit requests | Prevents denial-of-service attacks | 🟠 High |
| ✅ Sanitize error messages | Prevents information leakage of internal details | 🟠 High |
| ✅ Implement proper auth | Use API keys with rotation or OAuth2 with short-lived tokens | 🟠 High |
| ✅ Log security events | Audit tool execution, failed auth, unusual patterns | 🟡 Medium |

### Secure Tool Implementation Example

=== "Python"

    ```python
    import re
    from typing import Optional

    def get_weather(location: str) -> str:
        """
        Get weather for a location with input validation.

        Security measures:
        - Input validation with regex
        - Length limits
        - No system command execution
        """
        # Validate input - only allow letters, spaces, commas
        if not re.match(r'^[a-zA-Z\s,]+$', location):
            raise ValueError("Invalid location format: only letters, spaces, and commas allowed")

        # Length validation
        if len(location) > 100:
            raise ValueError("Location name too long (max 100 characters)")

        # Safe to use validated input
        # In production, call a safe weather API here
        return f"Weather in {location}: 72°F, sunny"

    # Register with validation
    tools = ToolCollection()
    tools.add("get_weather", get_weather)
    ```

=== "C#"

    ```csharp
    using System.Text.RegularExpressions;

    string GetWeather(string location)
    {
        // Validate input - only allow letters, spaces, commas
        if (!Regex.IsMatch(location, @"^[a-zA-Z\s,]+$"))
        {
            throw new ArgumentException("Invalid location format");
        }

        // Length validation
        if (location.Length > 100)
        {
            throw new ArgumentException("Location name too long");
        }

        // Safe to use validated input
        return $"Weather in {location}: 72°F, sunny";
    }

    var tools = new ToolCollection
    {
        ["get_weather"] = GetWeather
    };
    ```

=== "TypeScript"

    ```typescript
    function getWeather(location: string): string {
        // Validate input - only allow letters, spaces, commas
        if (!/^[a-zA-Z\s,]+$/.test(location)) {
            throw new Error("Invalid location format");
        }

        // Length validation
        if (location.length > 100) {
            throw new Error("Location name too long");
        }

        // Safe to use validated input
        return `Weather in ${location}: 72°F, sunny`;
    }

    const tools: ToolCollection = {
        get_weather: getWeather
    };
    ```

### Additional Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/) - Common web application security risks
- [Prompt Injection Mitigation](../security/prompt-injection.md) - Protecting against prompt attacks
- [Secrets Management Guide](../security/secrets.md) - Secure credential handling

---

## Production Configuration

Configure for production use with authentication, timeouts, and secure connections.

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    var options = new AgentProtocolClientOptions
    {
        BaseUrl = "https://agents.company.com",  // HTTPS required
        ApiKey = Environment.GetEnvironmentVariable("AGENT_API_KEY"),
        DefaultAgentId = "production-assistant",
        Timeout = TimeSpan.FromSeconds(30)
    };

    var client = new AgentProtocolClient(options);
    ```

=== "Python"

    ```python
    import os
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

    options = AgentProtocolClientOptions(
        base_url="https://agents.company.com",  # HTTPS required
        api_key=os.getenv("AGENT_API_KEY"),
        default_agent_id="production-assistant",
        timeout=30.0  # seconds
    )

    client = AgentProtocolClient(options)
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const options = {
        baseUrl: "https://agents.company.com",  // HTTPS required
        apiKey: process.env.AGENT_API_KEY,
        defaultAgentId: "production-assistant",
        timeout: 30000  // milliseconds
    };

    const client = new AgentProtocolClient(options);
    ```

!!! tip "Production Configuration Best Practices"
    - Always use HTTPS in production (never HTTP)
    - Store API keys in secure secret management systems
    - Use environment-specific configuration files
    - Set appropriate timeouts for your use case
    - Enable request retry with exponential backoff
    - Implement circuit breakers for resilience

---

## Complete Example

Here's a full example combining all concepts with proper error handling:

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        static async Task Main()
        {
            var client = new AgentProtocolClient("http://localhost:5000");

            try
            {
                // Simple completion
                Console.WriteLine("=== Simple Completion ===");
                var simple = await client.CompleteChatAsync("Hello!");
                Console.WriteLine($"Agent: {simple}\n");

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
                Console.WriteLine($"Agent: {msg1}");

                var msg2 = await conversation.SendAsync("Tell me about Mars");
                Console.WriteLine($"Agent: {msg2}");

                Console.WriteLine($"Thread: {conversation.ThreadId}");
            }
            catch (AgentProtocolException ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
            }
        }
    }
    ```

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolException

    async def main():
        client = AgentProtocolClient("http://localhost:3978")

        try:
            # Simple completion
            print("=== Simple Completion ===")
            simple = await client.complete_chat("Hello!")
            print(f"Agent: {simple}\n")

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
            print(f"Agent: {msg1}")

            msg2 = await conversation.send("Tell me about Mars")
            print(f"Agent: {msg2}")

            print(f"Thread: {conversation.thread_id}")

        except AgentProtocolException as ex:
            print(f"Error: {ex.message}")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient, AgentProtocolException } from '@microsoft/agents-protocol-client';

    async function main() {
        const client = new AgentProtocolClient("http://localhost:3978");

        try {
            // Simple completion
            console.log("=== Simple Completion ===");
            const simple = await client.completeChat("Hello!");
            console.log(`Agent: ${simple}\n`);

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
            console.log(`Agent: ${msg1}`);

            const msg2 = await conversation.send("Tell me about Mars");
            console.log(`Agent: ${msg2}`);

            console.log(`Thread: ${conversation.threadId}`);
        } catch (error) {
            if (error instanceof AgentProtocolException) {
                console.log(`Error: ${error.message}`);
            } else {
                throw error;
            }
        }
    }

    main();
    ```

---

## Error Handling

Handle common errors gracefully:

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    try
    {
        var response = await client.CompleteChatAsync("Hello");
        Console.WriteLine(response);
    }
    catch (AgentNotFoundException ex)
    {
        Console.WriteLine($"Agent '{ex.AgentId}' not found");
    }
    catch (AgentAuthenticationException)
    {
        Console.WriteLine("Invalid API key");
    }
    catch (AgentTimeoutException ex)
    {
        Console.WriteLine($"Request timed out after {ex.Timeout}");
    }
    catch (AgentProtocolException ex)
    {
        Console.WriteLine($"Protocol error: {ex.Message}");
        // Log full details for debugging (don't expose to end users)
    }
    ```

=== "Python"

    ```python
    from microsoft.agents.protocol import (
        AgentProtocolClient,
        AgentNotFoundException,
        AgentAuthenticationException,
        AgentTimeoutException,
        AgentProtocolException
    )

    try:
        response = await client.complete_chat("Hello")
        print(response)
    except AgentNotFoundException as ex:
        print(f"Agent '{ex.agent_id}' not found")
    except AgentAuthenticationException:
        print("Invalid API key")
    except AgentTimeoutException as ex:
        print(f"Request timed out after {ex.timeout} seconds")
    except AgentProtocolException as ex:
        print(f"Protocol error: {ex.message}")
        # Log full details for debugging (don't expose to end users)
    ```

=== "TypeScript"

    ```typescript
    import {
        AgentProtocolClient,
        AgentNotFoundException,
        AgentAuthenticationException,
        AgentTimeoutException,
        AgentProtocolException
    } from '@microsoft/agents-protocol-client';

    try {
        const response = await client.completeChat("Hello");
        console.log(response);
    } catch (error) {
        if (error instanceof AgentNotFoundException) {
            console.log(`Agent '${error.agentId}' not found`);
        } else if (error instanceof AgentAuthenticationException) {
            console.log("Invalid API key");
        } else if (error instanceof AgentTimeoutException) {
            console.log(`Request timed out after ${error.timeout}ms`);
        } else if (error instanceof AgentProtocolException) {
            console.log(`Protocol error: ${error.message}`);
            // Log full details for debugging (don't expose to end users)
        } else {
            throw error;
        }
    }
    ```

!!! warning "Security: Error Message Sanitization"
    Never expose internal error details (stack traces, database queries, file paths) to end users. Log detailed errors server-side for debugging, but return generic messages to clients.

---

## Troubleshooting

### Connection Refused Error

**Problem**: `ECONNREFUSED` or "connection refused" when calling the client

**Solution**:

1. Verify the agent server is running:
   ```bash
   # Check if process is listening
   netstat -an | grep LISTEN | grep 3978  # or 5000
   ```

2. Check the port matches your configuration:
   - Python/TypeScript echo agents: `http://localhost:3978`
   - C# echo agent: `http://localhost:5000`

3. Verify network connectivity:
   ```bash
   curl http://localhost:3978/health
   ```

### Agent Not Found Error

**Problem**: `AgentNotFoundException` - specified agent doesn't exist

**Solution**:

- Let the server use its default agent (don't specify `defaultAgentId`)
- Or verify the agent ID exists on the server
- Check server logs for available agents

### Authentication Failures

**Problem**: `AgentAuthenticationException` - invalid credentials

**Solution**:

1. Verify API key is correct
2. Check environment variable is set: `echo $AGENT_API_KEY`
3. Ensure API key has necessary permissions
4. For OAuth2, verify token hasn't expired

### Timeout Errors

**Problem**: `AgentTimeoutException` - request takes too long

**Solution**:

1. Increase timeout in client options:
   ```python
   options = AgentProtocolClientOptions(
       base_url="...",
       timeout=60.0  # Increase to 60 seconds
   )
   ```

2. Check network latency
3. Verify agent server is responding (check server logs)
4. Consider using streaming for long-running operations

### Tools Not Being Called

**Problem**: Agent doesn't call your registered tools

**Solution**:

1. Verify tools are registered with correct names
2. Check tool signatures match expected parameters
3. Ensure agent supports tool calling (not all models do)
4. Review agent logs for tool execution errors

---

## Next Steps

Now that you've completed the quickstart, explore these topics:

<div class="grid cards" markdown>

- **:material-brain: Core Concepts**

    Understand runs, threads, and streaming

    [:octicons-arrow-right-24: Learn Concepts](concepts/)

- **:material-book-open: How-To Guides**

    Authentication, error handling, multimodal content

    [:octicons-arrow-right-24: How-To Guides](how-to/)

- **:material-shield-lock: Security**

    Production security, secrets management, prompt injection

    [:octicons-arrow-right-24: Security Guide](../security/)

- **:material-image: Multimodal Content**

    Send images, audio, files to agents

    [:octicons-arrow-right-24: Multimodal Guide](how-to/multimodal/)

- **:material-cog: Advanced Tools**

    Complex tool patterns and orchestration

    [:octicons-arrow-right-24: Tools Guide](how-to/tools/)

- **:material-cloud-upload: Production Deployment**

    Docker, Kubernetes, observability, resilience

    [:octicons-arrow-right-24: Deployment Guide](../deployment/)

</div>

---

## Quick API Reference

### Client Creation

```csharp
var client = new AgentProtocolClient(baseUrl);
var client = new AgentProtocolClient(options);
```

### Simple Completions

```csharp
string response = await client.CompleteChatAsync(message);
string response = await client.CompleteChatAsync(message, cancellationToken: ct);
```

### Streaming

```csharp
await client.StreamChatAsync(message, onTextChunk: text => Console.Write(text));
```

### Conversations

```csharp
var conversation = client.CreateConversation();
var response = await conversation.SendAsync(message);
var threadId = conversation.ThreadId;

var resumed = client.ResumeConversation(threadId);
```

### Tools

```csharp
var tools = new ToolCollection
{
    ["tool_name"] = (string arg) => "result"
};
await client.CompleteChatAsync(message, tools: tools);
```

---

**Questions?** Check the [FAQ](../../community/#faq) or [open a discussion](https://github.com/madsbolaris/AgentProtocol/discussions).
