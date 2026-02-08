# 5-Minute Quickstart

**Get your first agent running in 5 minutes!**

This guide walks you through the three fundamental operations: sending a message, streaming responses, and managing conversation threads.

---

## Step 1: Basic Request/Response

The simplest way to interact with an agent - send a message and get a response.

### Your First Agent Call

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

    # Create client
    client = AgentProtocolClient(AgentProtocolClientOptions(
        base_url="https://agents.example.com/v1",
        api_key="your-api-key"
    ))

    # Create a simple run
    async with client:
        result = await client.runs.create({
            "agent": {
                "name": "HelloAgent",
                "kind": "prompt",
                "model": "gpt-4o",
                "instructions": "You are a helpful assistant. Keep responses concise."
            },
            "input": [{
                "role": "user",
                "contents": [{
                    "kind": "text",
                    "text": "What is the capital of France?"
                }]
            }],
            "threadCleanup": "delete"  # Auto-cleanup for quickstart
        })

        print(f"Status: {result['status']}")
        print(f"Response: {result['output'][0]['contents'][0]['text']}")
    ```

=== "JavaScript/TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    // Create client
    const client = new AgentProtocolClient({
        baseUrl: "https://agents.example.com/v1",
        apiKey: "your-api-key"
    });

    async function createRun() {
        const result = await client.runs.create({
            agent: {
                name: "HelloAgent",
                kind: "prompt",
                model: "gpt-4o",
                instructions: "You are a helpful assistant. Keep responses concise."
            },
            input: [{
                role: "user",
                contents: [{
                    kind: "text",
                    text: "What is the capital of France?"
                }]
            }],
            threadCleanup: "delete"  // Auto-cleanup for quickstart
        });

        console.log(`Status: ${result.status}`);
        console.log(`Response: ${result.output[0].contents[0].text}`);
    }

    createRun();
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    // Create client
    var client = new AgentProtocolClient(new AgentProtocolClientOptions
    {
        BaseUrl = "https://agents.example.com/v1",
        ApiKey = "your-api-key"
    });

    // Create a simple run
    var result = await client.Runs.CreateAsync(new
    {
        agent = new
        {
            name = "HelloAgent",
            kind = "prompt",
            model = "gpt-4o",
            instructions = "You are a helpful assistant. Keep responses concise."
        },
        input = new[]
        {
            new
            {
                role = "user",
                contents = new[]
                {
                    new { kind = "text", text = "What is the capital of France?" }
                }
            }
        },
        threadCleanup = "delete"  // Auto-cleanup for quickstart
    });

    Console.WriteLine($"Status: {result.Status}");
    Console.WriteLine($"Response: {result.Output[0].Contents[0].Text}");
    ```

**Expected Output:**

```json
{
  "runId": "run_abc123",
  "status": "completed",
  "output": [{
    "role": "assistant",
    "contents": [{
      "kind": "text",
      "text": "The capital of France is Paris."
    }]
  }],
  "usage": {
    "inputTokens": 15,
    "outputTokens": 8,
    "totalTokens": 23
  }
}
```

!!! success "Congratulations!"
    You just made your first agent call! The agent received your message, processed it, and sent back a response.

---

## Step 2: Streaming Responses

For real-time responses, use streaming to get tokens as they're generated.

### Server-Sent Events (SSE)

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

    client = AgentProtocolClient(AgentProtocolClientOptions(
        base_url="https://agents.example.com/v1",
        api_key="your-api-key"
    ))

    async def stream_run(prompt: str):
        """Stream agent response token by token"""
        async with client:
            async for chunk in client.runs.create_stream({
                "agent": {
                    "name": "StreamingAgent",
                    "kind": "prompt",
                    "model": "gpt-4o",
                    "instructions": "You are a helpful assistant.",
                    "options": {"stream": True}
                },
                "input": [{
                    "role": "user",
                    "contents": [{"kind": "text", "text": prompt}]
                }],
                "threadCleanup": "delete"
            }):
                if chunk.get("text"):
                    print(chunk["text"], end="", flush=True)

        print("\n[Stream complete]")

    # Example usage
    await stream_run("Explain quantum computing in simple terms")
    ```

=== "JavaScript/TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    const client = new AgentProtocolClient({
        baseUrl: "https://agents.example.com/v1",
        apiKey: "your-api-key"
    });

    async function streamRun(prompt: string) {
        const stream = await client.runs.createStream({
            agent: {
                name: "StreamingAgent",
                kind: "prompt",
                model: "gpt-4o",
                instructions: "You are a helpful assistant.",
                options: { stream: true }
            },
            input: [{
                role: "user",
                contents: [{ kind: "text", text: prompt }]
            }],
            threadCleanup: "delete"
        });

        process.stdout.write("Streaming response: ");
        for await (const chunk of stream) {
            if (chunk.text) {
                process.stdout.write(chunk.text);
            }
        }
        console.log("\n[Stream complete]");
    }

    // Example usage
    streamRun("Explain quantum computing in simple terms");
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    var client = new AgentProtocolClient(new AgentProtocolClientOptions
    {
        BaseUrl = "https://agents.example.com/v1",
        ApiKey = "your-api-key"
    });

    async Task StreamRun(string prompt)
    {
        Console.Write("Streaming response: ");

        await foreach (var chunk in client.Runs.CreateStreamAsync(new
        {
            agent = new
            {
                name = "StreamingAgent",
                kind = "prompt",
                model = "gpt-4o",
                instructions = "You are a helpful assistant.",
                options = new { stream = true }
            },
            input = new[]
            {
                new
                {
                    role = "user",
                    contents = new[] { new { kind = "text", text = prompt } }
                }
            },
            threadCleanup = "delete"
        }))
        {
            if (chunk.Text != null)
            {
                Console.Write(chunk.Text);
            }
        }

        Console.WriteLine("\n[Stream complete]");
    }

    // Example usage
    await StreamRun("Explain quantum computing in simple terms");
    ```

**Output:**

```
Streaming response:
Quantum computing uses quantum bits (qubits) that can be 0, 1, or both simultaneously...
[Stream complete]
```

!!! tip "Why Streaming?"
    Streaming provides immediate feedback to users, making your application feel more responsive. Perfect for chatbots and interactive applications!

---

## Step 3: Conversation Threads

Maintain context across multiple turns with conversation threads.

### Multi-Turn Conversation

=== "Python"

    ```python
    from microsoft.agents.protocol import AgentProtocolClient, AgentProtocolClientOptions

    class ConversationClient:
        def __init__(self, base_url: str, api_key: str, agent_id: str):
            self.client = AgentProtocolClient(AgentProtocolClientOptions(
                base_url=base_url,
                api_key=api_key
            ))
            self.agent_id = agent_id
            self.thread_id = None

        async def create_thread(self):
            """Create a new conversation thread"""
            async with self.client:
                result = await self.client.threads.create({
                    "metadata": {"source": "quickstart"}
                })
                self.thread_id = result['threadId']
                print(f"Created thread: {self.thread_id}")
                return self.thread_id

        async def send_message(self, text: str):
            """Send message and get response"""
            if not self.thread_id:
                await self.create_thread()

            async with self.client:
                result = await self.client.runs.create({
                    "agentId": self.agent_id,
                    "threadId": self.thread_id,
                    "input": [{
                        "role": "user",
                        "contents": [{"kind": "text", "text": text}]
                    }]
                })

                if result['status'] == 'completed':
                    return result['output'][0]['contents'][0]['text']
                else:
                    raise Exception(f"Run failed: {result.get('error')}")

        async def get_history(self):
            """Get conversation history"""
            async with self.client:
                return await self.client.messages.list(self.thread_id)

    # Example: Multi-turn conversation
    async def main():
        client = ConversationClient(
            "https://agents.example.com/v1",
            "your-api-key",
            "agent_123"
        )

        # Turn 1
        print("User: Tell me about Paris")
        response = await client.send_message("Tell me about Paris")
        print(f"Assistant: {response}")

        # Turn 2 (maintains context)
        print("\nUser: What's the population?")
        response = await client.send_message("What's the population?")
        print(f"Assistant: {response}")

        # Turn 3
        print("\nUser: And the famous landmarks?")
        response = await client.send_message("And the famous landmarks?")
        print(f"Assistant: {response}")

        # View full history
        history = await client.get_history()
        print(f"\nTotal messages in thread: {len(history['data'])}")

    await main()
    ```

=== "JavaScript/TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    class ConversationClient {
        private client: AgentProtocolClient;
        private agentId: string;
        private threadId?: string;

        constructor(baseUrl: string, apiKey: string, agentId: string) {
            this.client = new AgentProtocolClient({
                baseUrl: baseUrl,
                apiKey: apiKey
            });
            this.agentId = agentId;
        }

        async createThread() {
            const result = await this.client.threads.create({
                metadata: { source: "quickstart" }
            });
            this.threadId = result.threadId;
            console.log(`Created thread: ${this.threadId}`);
            return this.threadId;
        }

        async sendMessage(text: string) {
            if (!this.threadId) {
                await this.createThread();
            }

            const result = await this.client.runs.create({
                agentId: this.agentId,
                threadId: this.threadId,
                input: [{
                    role: "user",
                    contents: [{ kind: "text", text: text }]
                }]
            });

            if (result.status === 'completed') {
                return result.output[0].contents[0].text;
            } else {
                throw new Error(`Run failed: ${result.error}`);
            }
        }

        async getHistory() {
            return await this.client.messages.list(this.threadId!);
        }
    }

    // Example: Multi-turn conversation
    async function main() {
        const client = new ConversationClient(
            "https://agents.example.com/v1",
            "your-api-key",
            "agent_123"
        );

        // Turn 1
        console.log("User: Tell me about Paris");
        let response = await client.sendMessage("Tell me about Paris");
        console.log(`Assistant: ${response}`);

        // Turn 2 (maintains context)
        console.log("\nUser: What's the population?");
        response = await client.sendMessage("What's the population?");
        console.log(`Assistant: ${response}`);

        // Turn 3
        console.log("\nUser: And the famous landmarks?");
        response = await client.sendMessage("And the famous landmarks?");
        console.log(`Assistant: ${response}`);

        // View full history
        const history = await client.getHistory();
        console.log(`\nTotal messages in thread: ${history.data.length}`);
    }

    main();
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol;

    public class ConversationClient
    {
        private readonly AgentProtocolClient _client;
        private readonly string _agentId;
        private string? _threadId;

        public ConversationClient(string baseUrl, string apiKey, string agentId)
        {
            _client = new AgentProtocolClient(new AgentProtocolClientOptions
            {
                BaseUrl = baseUrl,
                ApiKey = apiKey
            });
            _agentId = agentId;
        }

        public async Task<string> CreateThreadAsync()
        {
            var result = await _client.Threads.CreateAsync(new
            {
                metadata = new { source = "quickstart" }
            });
            _threadId = result.ThreadId;
            Console.WriteLine($"Created thread: {_threadId}");
            return _threadId;
        }

        public async Task<string> SendMessageAsync(string text)
        {
            if (_threadId == null)
            {
                await CreateThreadAsync();
            }

            var result = await _client.Runs.CreateAsync(new
            {
                agentId = _agentId,
                threadId = _threadId,
                input = new[]
                {
                    new
                    {
                        role = "user",
                        contents = new[] { new { kind = "text", text = text } }
                    }
                }
            });

            if (result.Status == "completed")
            {
                return result.Output[0].Contents[0].Text;
            }
            else
            {
                throw new Exception($"Run failed: {result.Error}");
            }
        }

        public async Task<dynamic> GetHistoryAsync()
        {
            return await _client.Messages.ListAsync(_threadId!);
        }
    }

    // Example: Multi-turn conversation
    async Task Main()
    {
        var client = new ConversationClient(
            "https://agents.example.com/v1",
            "your-api-key",
            "agent_123"
        );

        // Turn 1
        Console.WriteLine("User: Tell me about Paris");
        var response = await client.SendMessageAsync("Tell me about Paris");
        Console.WriteLine($"Assistant: {response}");

        // Turn 2 (maintains context)
        Console.WriteLine("\nUser: What's the population?");
        response = await client.SendMessageAsync("What's the population?");
        Console.WriteLine($"Assistant: {response}");

        // Turn 3
        Console.WriteLine("\nUser: And the famous landmarks?");
        response = await client.SendMessageAsync("And the famous landmarks?");
        Console.WriteLine($"Assistant: {response}");

        // View full history
        var history = await client.GetHistoryAsync();
        Console.WriteLine($"\nTotal messages in thread: {history.data.Length}");
    }

    await Main();
    ```

**Output:**

```
User: Tell me about Paris
Assistant: Paris is the capital of France, known for its art, culture, and history...

User: What's the population?
Assistant: Paris has a population of approximately 2.2 million people within the city limits...

User: And the famous landmarks?
Assistant: The top tourist attractions in Paris include: 1) Eiffel Tower, 2) Louvre Museum...

Total messages in thread: 6
```

!!! info "Thread Benefits"
    Threads automatically maintain conversation context. The agent remembers previous messages, enabling natural multi-turn conversations.

---

## Next Steps

Now that you've mastered the basics:

<div class="grid cards" markdown>

-   :material-tools:{ .lg .middle } **Tool Execution**

    Learn how agents can call your functions to access data and perform actions.

    [:octicons-arrow-right-24: Tool Guide](tools.md)

-   :material-code-braces:{ .lg .middle } **Code Examples**

    Explore practical examples: retries, batch processing, image analysis, and more.

    [:octicons-arrow-right-24: Examples](examples.md)

-   :material-rocket-launch:{ .lg .middle } **Advanced Patterns**

    Master ephemeral runs, background execution, and stream reconnection.

    [:octicons-arrow-right-24: Advanced Patterns](advanced-patterns.md)

</div>

---

## Common Questions

??? question "How do I handle errors?"

    Always check the `status` field in responses. Implement retry logic with exponential backoff for transient errors. See the [Error Handling Guide](../guides/error-handling.md).

??? question "What's the difference between `POST /runs` and `POST /runs/wait`?"

    - `POST /runs` - Starts a run and returns immediately. Poll `/runs/{id}` for status.
    - `POST /runs/wait` - Blocks until the run completes. Simpler for quick queries.

??? question "Can I use this in production?"

    Yes! But add proper error handling, rate limiting, and monitoring. See the [Production Deployment Guide](../guides/production-deployment.md).

---

**Need Help?** Check the [Troubleshooting Guide](troubleshooting.md) or [open an issue](https://github.com/madsbolaris/AgentProtocol/issues).
