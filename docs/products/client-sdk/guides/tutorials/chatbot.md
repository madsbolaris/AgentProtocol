# Building a Chatbot

Build a conversational AI chatbot from scratch in 30 minutes.

## What You'll Build

A fully-functional chatbot that:

- Maintains conversation context across multiple turns
- Streams responses in real-time for better UX
- Handles errors gracefully
- Persists conversations for later resumption

**Time Required:** 30 minutes
**Difficulty:** Beginner

---

## Prerequisites

- Python 3.9+, Node.js 18+, or .NET 8+
- A running Agent Protocol server ([setup guide](../../quickstart.md#before-you-start))
- Basic programming knowledge in your chosen language

---

## Step 1: Project Setup

Create a new project directory and install the Client SDK.

=== "Python"

    ```bash
    # Create project directory
    mkdir my-chatbot
    cd my-chatbot

    # Create virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate

    # Install Client SDK
    pip install microsoft-agents-protocol

    # Create main file
    touch chatbot.py
    ```

=== "TypeScript"

    ```bash
    # Create project directory
    mkdir my-chatbot
    cd my-chatbot

    # Initialize project
    npm init -y

    # Install Client SDK
    npm install @microsoft/agents-protocol-client
    npm install --save-dev @types/node typescript

    # Create TypeScript config
    npx tsc --init

    # Create main file
    touch chatbot.ts
    ```

=== "C#"

    ```bash
    # Create project
    dotnet new console -n MyChatbot
    cd MyChatbot

    # Install Client SDK
    dotnet add package Microsoft.Agents.Protocol.Client

    # Project is ready - edit Program.cs
    ```

---

## Step 2: Basic Chat Loop

Let's start with a simple command-line chat interface.

=== "Python"

    ```python
    # chatbot.py
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        # Initialize client
        client = AgentProtocolClient("http://localhost:5000")

        print("Chatbot ready! Type 'quit' to exit.")

        while True:
            # Get user input
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            # Get agent response
            response = await client.complete_chat(user_input)
            print(f"Bot: {response}\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

    **Run it:**
    ```bash
    python chatbot.py
    ```

=== "TypeScript"

    ```typescript
    // chatbot.ts
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
    import * as readline from 'readline';

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function question(prompt: string): Promise<string> {
        return new Promise((resolve) => {
            rl.question(prompt, resolve);
        });
    }

    async function main() {
        // Initialize client
        const client = new AgentProtocolClient("http://localhost:5000");

        console.log("Chatbot ready! Type 'quit' to exit.\n");

        while (true) {
            // Get user input
            const userInput = await question("You: ");

            if (userInput.toLowerCase() === 'quit' || userInput.toLowerCase() === 'exit') {
                console.log("Goodbye!");
                rl.close();
                break;
            }

            // Get agent response
            const response = await client.completeChat(userInput);
            console.log(`Bot: ${response}\n`);
        }
    }

    main();
    ```

    **Run it:**
    ```bash
    npx ts-node chatbot.ts
    ```

=== "C#"

    ```csharp
    // Program.cs
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        static async Task Main()
        {
            // Initialize client
            var client = new AgentProtocolClient("http://localhost:5000");

            Console.WriteLine("Chatbot ready! Type 'quit' to exit.\n");

            while (true)
            {
                // Get user input
                Console.Write("You: ");
                var userInput = Console.ReadLine();

                if (userInput?.ToLower() is "quit" or "exit")
                {
                    Console.WriteLine("Goodbye!");
                    break;
                }

                // Get agent response
                var response = await client.CompleteChatAsync(userInput);
                Console.WriteLine($"Bot: {response}\n");
            }
        }
    }
    ```

    **Run it:**
    ```bash
    dotnet run
    ```

**Try it out:**
```
Chatbot ready! Type 'quit' to exit.

You: Hello!
Bot: Hello! How can I help you today?

You: What's the weather like?
Bot: I don't have access to current weather data, but I'd be happy to help you with something else!

You: quit
Goodbye!
```

**Problem:** The bot doesn't remember previous messages. Each interaction is isolated.

---

## Step 3: Add Conversation Memory

Let's make the bot remember the conversation using persistent threads.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Create persistent conversation
        conversation = client.create_conversation()

        print("Chatbot ready! Type 'quit' to exit.")
        print(f"Conversation ID: {conversation.thread_id}\n")

        while True:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            # Send message in conversation (context preserved)
            response = await conversation.send(user_input)
            print(f"Bot: {response}\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
    import * as readline from 'readline';

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function question(prompt: string): Promise<string> {
        return new Promise((resolve) => {
            rl.question(prompt, resolve);
        });
    }

    async function main() {
        const client = new AgentProtocolClient("http://localhost:5000");

        // Create persistent conversation
        const conversation = client.createConversation();

        console.log("Chatbot ready! Type 'quit' to exit.");
        console.log(`Conversation ID: ${conversation.threadId}\n`);

        while (true) {
            const userInput = await question("You: ");

            if (userInput.toLowerCase() === 'quit' || userInput.toLowerCase() === 'exit') {
                console.log("Goodbye!");
                rl.close();
                break;
            }

            // Send message in conversation (context preserved)
            const response = await conversation.send(userInput);
            console.log(`Bot: ${response}\n`);
        }
    }

    main();
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        static async Task Main()
        {
            var client = new AgentProtocolClient("http://localhost:5000");

            // Create persistent conversation
            var conversation = client.CreateConversation();

            Console.WriteLine("Chatbot ready! Type 'quit' to exit.");
            Console.WriteLine($"Conversation ID: {conversation.ThreadId}\n");

            while (true)
            {
                Console.Write("You: ");
                var userInput = Console.ReadLine();

                if (userInput?.ToLower() is "quit" or "exit")
                {
                    Console.WriteLine("Goodbye!");
                    break;
                }

                // Send message in conversation (context preserved)
                var response = await conversation.SendAsync(userInput);
                Console.WriteLine($"Bot: {response}\n");
            }
        }
    }
    ```

**Try it out:**
```
Chatbot ready! Type 'quit' to exit.
Conversation ID: thread_abc123

You: My name is Alice
Bot: Nice to meet you, Alice! How can I help you today?

You: What's my name?
Bot: Your name is Alice!

You: quit
Goodbye!
```

**Much better!** The bot now remembers context across multiple turns.

---

## Step 4: Add Streaming for Real-Time Responses

Make responses appear instantly as they're generated.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import AgentProtocolClient

    async def main():
        client = AgentProtocolClient("http://localhost:5000")
        conversation = client.create_conversation()

        print("Chatbot ready! Type 'quit' to exit.")
        print(f"Conversation ID: {conversation.thread_id}\n")

        while True:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            # Stream response token-by-token
            print("Bot: ", end="", flush=True)
            await conversation.send_stream(
                user_input,
                on_text_chunk=lambda text: print(text, end="", flush=True)
            )
            print("\n")  # New line after response

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
    import * as readline from 'readline';

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function question(prompt: string): Promise<string> {
        return new Promise((resolve) => {
            rl.question(prompt, resolve);
        });
    }

    async function main() {
        const client = new AgentProtocolClient("http://localhost:5000");
        const conversation = client.createConversation();

        console.log("Chatbot ready! Type 'quit' to exit.");
        console.log(`Conversation ID: ${conversation.threadId}\n`);

        while (true) {
            const userInput = await question("You: ");

            if (userInput.toLowerCase() === 'quit' || userInput.toLowerCase() === 'exit') {
                console.log("Goodbye!");
                rl.close();
                break;
            }

            // Stream response token-by-token
            process.stdout.write("Bot: ");
            await conversation.sendStream(
                userInput,
                { onTextChunk: (text) => process.stdout.write(text) }
            );
            console.log("\n");
        }
    }

    main();
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        static async Task Main()
        {
            var client = new AgentProtocolClient("http://localhost:5000");
            var conversation = client.CreateConversation();

            Console.WriteLine("Chatbot ready! Type 'quit' to exit.");
            Console.WriteLine($"Conversation ID: {conversation.ThreadId}\n");

            while (true)
            {
                Console.Write("You: ");
                var userInput = Console.ReadLine();

                if (userInput?.ToLower() is "quit" or "exit")
                {
                    Console.WriteLine("Goodbye!");
                    break;
                }

                // Stream response token-by-token
                Console.Write("Bot: ");
                await conversation.SendStreamAsync(
                    userInput,
                    onTextChunk: text => Console.Write(text)
                );
                Console.WriteLine("\n");
            }
        }
    }
    ```

**Try it out - responses now appear instantly:**
```
You: Tell me a story
Bot: Once upon a time, there was a curious robot...
```

Instead of waiting for the complete response, you see text appearing in real-time!

---

## Step 5: Add Error Handling

Make the chatbot robust to network errors and timeouts.

=== "Python"

    ```python
    import asyncio
    from microsoft.agents.protocol import (
        AgentProtocolClient,
        AgentProtocolException,
        AgentTimeoutException,
        AgentNetworkException
    )

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        try:
            conversation = client.create_conversation()
            print("Chatbot ready! Type 'quit' to exit.")
            print(f"Conversation ID: {conversation.thread_id}\n")
        except AgentNetworkException:
            print("Error: Cannot connect to agent server.")
            print("Make sure the server is running at http://localhost:5000")
            return

        while True:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            try:
                print("Bot: ", end="", flush=True)
                await conversation.send_stream(
                    user_input,
                    on_text_chunk=lambda text: print(text, end="", flush=True)
                )
                print("\n")

            except AgentTimeoutException:
                print("\n[Request timed out. Please try again.]\n")

            except AgentNetworkException:
                print("\n[Network error. Check your connection.]\n")

            except AgentProtocolException as e:
                print(f"\n[Error: {e.message}]\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import {
        AgentProtocolClient,
        AgentProtocolException,
        AgentTimeoutException,
        AgentNetworkException
    } from '@microsoft/agents-protocol-client';
    import * as readline from 'readline';

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function question(prompt: string): Promise<string> {
        return new Promise((resolve) => {
            rl.question(prompt, resolve);
        });
    }

    async function main() {
        const client = new AgentProtocolClient("http://localhost:5000");
        let conversation;

        try {
            conversation = client.createConversation();
            console.log("Chatbot ready! Type 'quit' to exit.");
            console.log(`Conversation ID: ${conversation.threadId}\n`);
        } catch (error) {
            if (error instanceof AgentNetworkException) {
                console.error("Error: Cannot connect to agent server.");
                console.error("Make sure the server is running at http://localhost:5000");
                return;
            }
            throw error;
        }

        while (true) {
            const userInput = await question("You: ");

            if (userInput.toLowerCase() === 'quit' || userInput.toLowerCase() === 'exit') {
                console.log("Goodbye!");
                rl.close();
                break;
            }

            try {
                process.stdout.write("Bot: ");
                await conversation.sendStream(
                    userInput,
                    { onTextChunk: (text) => process.stdout.write(text) }
                );
                console.log("\n");

            } catch (error) {
                if (error instanceof AgentTimeoutException) {
                    console.log("\n[Request timed out. Please try again.]\n");
                } else if (error instanceof AgentNetworkException) {
                    console.log("\n[Network error. Check your connection.]\n");
                } else if (error instanceof AgentProtocolException) {
                    console.log(`\n[Error: ${error.message}]\n`);
                } else {
                    throw error;
                }
            }
        }
    }

    main();
    ```

=== "C#"

    ```csharp
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        static async Task Main()
        {
            var client = new AgentProtocolClient("http://localhost:5000");
            Conversation conversation;

            try
            {
                conversation = client.CreateConversation();
                Console.WriteLine("Chatbot ready! Type 'quit' to exit.");
                Console.WriteLine($"Conversation ID: {conversation.ThreadId}\n");
            }
            catch (AgentNetworkException)
            {
                Console.WriteLine("Error: Cannot connect to agent server.");
                Console.WriteLine("Make sure the server is running at http://localhost:5000");
                return;
            }

            while (true)
            {
                Console.Write("You: ");
                var userInput = Console.ReadLine();

                if (userInput?.ToLower() is "quit" or "exit")
                {
                    Console.WriteLine("Goodbye!");
                    break;
                }

                try
                {
                    Console.Write("Bot: ");
                    await conversation.SendStreamAsync(
                        userInput,
                        onTextChunk: text => Console.Write(text)
                    );
                    Console.WriteLine("\n");
                }
                catch (AgentTimeoutException)
                {
                    Console.WriteLine("\n[Request timed out. Please try again.]\n");
                }
                catch (AgentNetworkException)
                {
                    Console.WriteLine("\n[Network error. Check your connection.]\n");
                }
                catch (AgentProtocolException ex)
                {
                    Console.WriteLine($"\n[Error: {ex.Message}]\n");
                }
            }
        }
    }
    ```

---

## Step 6: Save and Resume Conversations

Allow users to save and resume conversations later.

=== "Python"

    ```python
    import asyncio
    import json
    from pathlib import Path
    from microsoft.agents.protocol import AgentProtocolClient

    SAVE_FILE = Path("conversation.json")

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Load existing conversation or create new one
        if SAVE_FILE.exists():
            data = json.loads(SAVE_FILE.read_text())
            thread_id = data["thread_id"]
            conversation = client.resume_conversation(thread_id)
            print(f"Resumed conversation: {thread_id}")
        else:
            conversation = client.create_conversation()
            print(f"New conversation: {conversation.thread_id}")

            # Save thread ID
            SAVE_FILE.write_text(json.dumps({
                "thread_id": conversation.thread_id
            }))

        print("Type 'quit' to exit, 'clear' to start new conversation.\n")

        while True:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            if user_input.lower() == 'clear':
                # Start new conversation
                conversation = client.create_conversation()
                SAVE_FILE.write_text(json.dumps({
                    "thread_id": conversation.thread_id
                }))
                print(f"Started new conversation: {conversation.thread_id}\n")
                continue

            print("Bot: ", end="", flush=True)
            await conversation.send_stream(
                user_input,
                on_text_chunk=lambda text: print(text, end="", flush=True)
            )
            print("\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

=== "TypeScript"

    ```typescript
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
    import * as readline from 'readline';
    import * as fs from 'fs';

    const SAVE_FILE = 'conversation.json';

    const rl = readline.createInterface({
        input: process.stdin,
        output: process.stdout
    });

    function question(prompt: string): Promise<string> {
        return new Promise((resolve) => {
            rl.question(prompt, resolve);
        });
    }

    async function main() {
        const client = new AgentProtocolClient("http://localhost:5000");
        let conversation;

        // Load existing conversation or create new one
        if (fs.existsSync(SAVE_FILE)) {
            const data = JSON.parse(fs.readFileSync(SAVE_FILE, 'utf-8'));
            const threadId = data.thread_id;
            conversation = client.resumeConversation(threadId);
            console.log(`Resumed conversation: ${threadId}`);
        } else {
            conversation = client.createConversation();
            console.log(`New conversation: ${conversation.threadId}`);

            // Save thread ID
            fs.writeFileSync(SAVE_FILE, JSON.stringify({
                thread_id: conversation.threadId
            }));
        }

        console.log("Type 'quit' to exit, 'clear' to start new conversation.\n");

        while (true) {
            const userInput = await question("You: ");

            if (userInput.toLowerCase() === 'quit' || userInput.toLowerCase() === 'exit') {
                console.log("Goodbye!");
                rl.close();
                break;
            }

            if (userInput.toLowerCase() === 'clear') {
                conversation = client.createConversation();
                fs.writeFileSync(SAVE_FILE, JSON.stringify({
                    thread_id: conversation.threadId
                }));
                console.log(`Started new conversation: ${conversation.threadId}\n`);
                continue;
            }

            process.stdout.write("Bot: ");
            await conversation.sendStream(
                userInput,
                { onTextChunk: (text) => process.stdout.write(text) }
            );
            console.log("\n");
        }
    }

    main();
    ```

=== "C#"

    ```csharp
    using System.Text.Json;
    using Microsoft.Agents.Protocol.Client;

    class Program
    {
        const string SaveFile = "conversation.json";

        static async Task Main()
        {
            var client = new AgentProtocolClient("http://localhost:5000");
            Conversation conversation;

            // Load existing conversation or create new one
            if (File.Exists(SaveFile))
            {
                var json = await File.ReadAllTextAsync(SaveFile);
                var data = JsonSerializer.Deserialize<Dictionary<string, string>>(json);
                var threadId = data["thread_id"];
                conversation = client.ResumeConversation(threadId);
                Console.WriteLine($"Resumed conversation: {threadId}");
            }
            else
            {
                conversation = client.CreateConversation();
                Console.WriteLine($"New conversation: {conversation.ThreadId}");

                // Save thread ID
                var data = new Dictionary<string, string>
                {
                    ["thread_id"] = conversation.ThreadId
                };
                await File.WriteAllTextAsync(SaveFile, JsonSerializer.Serialize(data));
            }

            Console.WriteLine("Type 'quit' to exit, 'clear' to start new conversation.\n");

            while (true)
            {
                Console.Write("You: ");
                var userInput = Console.ReadLine();

                if (userInput?.ToLower() is "quit" or "exit")
                {
                    Console.WriteLine("Goodbye!");
                    break;
                }

                if (userInput?.ToLower() == "clear")
                {
                    conversation = client.CreateConversation();
                    var data = new Dictionary<string, string>
                    {
                        ["thread_id"] = conversation.ThreadId
                    };
                    await File.WriteAllTextAsync(SaveFile, JsonSerializer.Serialize(data));
                    Console.WriteLine($"Started new conversation: {conversation.ThreadId}\n");
                    continue;
                }

                Console.Write("Bot: ");
                await conversation.SendStreamAsync(
                    userInput,
                    onTextChunk: text => Console.Write(text)
                );
                Console.WriteLine("\n");
            }
        }
    }
    ```

**Now you can resume conversations across sessions!**

---

## Complete Code

Here's the final, complete chatbot with all features:

??? example "Python - Complete Chatbot"
    ```python
    import asyncio
    import json
    from pathlib import Path
    from microsoft.agents.protocol import (
        AgentProtocolClient,
        AgentProtocolException,
        AgentTimeoutException,
        AgentNetworkException
    )

    SAVE_FILE = Path("conversation.json")

    async def main():
        client = AgentProtocolClient("http://localhost:5000")

        # Load or create conversation
        try:
            if SAVE_FILE.exists():
                data = json.loads(SAVE_FILE.read_text())
                conversation = client.resume_conversation(data["thread_id"])
                print(f"Resumed: {data['thread_id']}")
            else:
                conversation = client.create_conversation()
                print(f"New conversation: {conversation.thread_id}")
                SAVE_FILE.write_text(json.dumps({"thread_id": conversation.thread_id}))
        except AgentNetworkException:
            print("Error: Cannot connect to server at http://localhost:5000")
            return

        print("Commands: 'quit' to exit, 'clear' for new conversation\n")

        while True:
            user_input = input("You: ")

            if user_input.lower() in ['quit', 'exit']:
                print("Goodbye!")
                break

            if user_input.lower() == 'clear':
                conversation = client.create_conversation()
                SAVE_FILE.write_text(json.dumps({"thread_id": conversation.thread_id}))
                print(f"New conversation: {conversation.thread_id}\n")
                continue

            try:
                print("Bot: ", end="", flush=True)
                await conversation.send_stream(
                    user_input,
                    on_text_chunk=lambda text: print(text, end="", flush=True)
                )
                print("\n")
            except AgentTimeoutException:
                print("\n[Timeout - try again]\n")
            except AgentNetworkException:
                print("\n[Network error]\n")
            except AgentProtocolException as e:
                print(f"\n[Error: {e.message}]\n")

    if __name__ == "__main__":
        asyncio.run(main())
    ```

---

## What You've Learned

✅ **Conversation Management** - Create and maintain conversation context
✅ **Real-Time Streaming** - Display responses as they're generated
✅ **Error Handling** - Handle timeouts and network errors gracefully
✅ **State Persistence** - Save and resume conversations

---

## Next Steps

<div class="grid cards" markdown>

- **:material-tools: Add Tools**

    Enable function calling

    [:octicons-arrow-right-24: Tools Tutorial](tools-tutorial.md)

- **:material-image: Multimodal**

    Add image and audio support

    [:octicons-arrow-right-24: Multimodal Tutorial](multimodal-assistant.md)

- **:material-rocket-launch: Deploy**

    Take your chatbot to production

    [:octicons-arrow-right-24: Deployment Tutorial](production-deployment.md)

</div>

---

## Troubleshooting

**Bot doesn't remember context:**
- Ensure you're using `conversation.send()` not `client.complete_chat()`
- Check that you're using the same conversation object

**Streaming doesn't work:**
- Make sure you're using `send_stream()` with `on_text_chunk` callback
- Check that you're flushing output buffers (`flush=True` in Python)

**Connection errors:**
- Verify agent server is running: `curl http://localhost:5000/health`
- Check firewall settings
- Ensure correct port in client URL
