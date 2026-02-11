# Runs, Threads, and Messages

Understanding the core data model of the Agent Protocol is essential for building robust agent applications.

## Overview

The Agent Protocol organizes conversations using three core concepts:

- **Thread**: A conversation session with persistent message history
- **Message**: Individual pieces of content (user input, agent responses, tool results)
- **Run**: A single execution of the agent to process messages

### Conceptual Model

```
Thread (Conversation Session)
  ├── Message 1 (User: "Hello")
  ├── Run 1 (Agent processes message)
  ├── Message 2 (Agent: "Hi! How can I help?")
  ├── Message 3 (User: "What's the weather?")
  ├── Run 2 (Agent calls weather tool)
  ├── Message 4 (Tool: "72°F, sunny")
  └── Message 5 (Agent: "It's 72°F and sunny today")
```

## Threads

A **thread** represents a conversation session with persistent message history.

### Creating Threads

=== "Python"
    ```python
    # Create a new thread
    thread = await client.threads.create()
    print(f"Thread ID: {thread.id}")
    ```

=== "TypeScript"
    ```typescript
    // Create a new thread
    const thread = await client.threads.create();
    console.log(`Thread ID: ${thread.id}`);
    ```

=== "C#"
    ```csharp
    // Create a new thread
    var thread = await client.Threads.CreateAsync();
    Console.WriteLine($"Thread ID: {thread.Id}");
    ```

### Thread Lifecycle

Threads persist until explicitly deleted and can be in different states:

- **Active**: Currently being used for conversations
- **Archived**: Conversation ended, preserved for history
- **Deleted**: Permanently removed

### Best Practices

✅ **Do:**
- Create one thread per user conversation/session
- Reuse threads for multi-turn conversations
- Store thread IDs in your database for session management
- Use metadata to track application-specific context

❌ **Don't:**
- Create a new thread for every message
- Keep unlimited threads without cleanup policies
- Store sensitive data in thread metadata without encryption

## Messages

**Messages** are the content exchanged within a thread between users, agents, and tools.

### Message Roles

| Role | Description | Who Creates It |
|------|-------------|----------------|
| `user` | Input from the application user | Your application |
| `agent` | Responses from the AI agent | Agent server |
| `tool` | Results from function executions | Agent server |
| `system` | System-level instructions | Your application |

### Adding Messages

=== "Python"
    ```python
    # Add a user message
    await client.threads.add_message(
        thread_id=thread.id,
        role="user",
        content="What's the capital of France?"
    )
    ```

=== "TypeScript"
    ```typescript
    // Add a user message
    await client.threads.addMessage(
        thread.id,
        "user",
        "What's the capital of France?"
    );
    ```

=== "C#"
    ```csharp
    // Add a user message
    await client.Threads.AddMessageAsync(
        thread.Id,
        "user",
        "What's the capital of France?"
    );
    ```

### Retrieving Messages

=== "Python"
    ```python
    # Get all messages in a thread
    messages = await client.threads.get_messages(thread_id=thread.id)

    # Get messages with pagination
    messages = await client.threads.get_messages(
        thread_id=thread.id,
        limit=20,
        order="desc"  # Most recent first
    )
    ```

=== "TypeScript"
    ```typescript
    // Get all messages
    const messages = await client.threads.getMessages(thread.id);

    // With pagination
    const messages = await client.threads.getMessages(thread.id, {
        limit: 20,
        order: "desc"
    });
    ```

=== "C#"
    ```csharp
    // Get all messages
    var messages = await client.Threads.GetMessagesAsync(thread.Id);

    // With pagination
    var messages = await client.Threads.GetMessagesAsync(
        thread.Id,
        limit: 20,
        order: "desc"
    );
    ```

## Runs

A **run** is a single execution of the agent within a thread to process messages and generate responses.

### Run Status Lifecycle

```
Created → Queued → In Progress → Completed
                              ├→ Failed
                              ├→ Requires Action (tool call needed)
                              └→ Cancelled
```

### Creating and Waiting for Runs

=== "Python"
    ```python
    # Create a run and wait for completion
    run = await client.runs.create_and_wait(
        thread_id=thread.id,
        message="What's 2+2?"
    )

    if run.status == "completed":
        print(f"Response: {run.output}")
    ```

=== "TypeScript"
    ```typescript
    // Create a run and wait for completion
    const run = await client.runs.createAndWait(
        thread.id,
        "What's 2+2?"
    );

    if (run.status === "completed") {
        console.log(`Response: ${run.output}`);
    }
    ```

=== "C#"
    ```csharp
    // Create a run and wait for completion
    var run = await client.Runs.CreateAndWaitAsync(
        thread.Id,
        "What's 2+2?"
    );

    if (run.Status == "completed")
    {
        Console.WriteLine($"Response: {run.Output}");
    }
    ```

### Manual Run Polling

For more control over the polling process:

=== "Python"
    ```python
    # Create run without waiting
    run = await client.runs.create(thread_id=thread.id)

    # Poll until complete
    while run.status in ["queued", "in_progress"]:
        await asyncio.sleep(0.5)
        run = await client.runs.get(run.id)

    # Handle result
    if run.status == "completed":
        print("Success!")
    elif run.status == "failed":
        print(f"Error: {run.error}")
    ```

=== "TypeScript"
    ```typescript
    // Create run without waiting
    let run = await client.runs.create(thread.id);

    // Poll until complete
    while (run.status === "queued" || run.status === "in_progress") {
        await new Promise(resolve => setTimeout(resolve, 500));
        run = await client.runs.get(run.id);
    }

    // Handle result
    if (run.status === "completed") {
        console.log("Success!");
    }
    ```

=== "C#"
    ```csharp
    // Create run without waiting
    var run = await client.Runs.CreateAsync(thread.Id);

    // Poll until complete
    while (run.Status == "queued" || run.Status == "in_progress")
    {
        await Task.Delay(500);
        run = await client.Runs.GetAsync(run.Id);
    }

    // Handle result
    if (run.Status == "completed")
    {
        Console.WriteLine("Success!");
    }
    ```

## Putting It All Together

Here's a complete example showing how threads, messages, and runs work together:

=== "Python"
    ```python
    async def have_conversation():
        # 1. Create thread
        thread = await client.threads.create()

        # 2. Add user message
        await client.threads.add_message(
            thread_id=thread.id,
            role="user",
            content="What's the capital of France?"
        )

        # 3. Create and wait for run
        run = await client.runs.create_and_wait(thread_id=thread.id)

        # 4. Get agent response
        if run.status == "completed":
            messages = await client.threads.get_messages(thread_id=thread.id)
            latest = messages[0]  # Most recent message
            # Extract first text content
            async for content in latest.content:
                if content.type == "text":
                    complete_text = await content.wait()
                    print(f"Agent: {complete_text.text}")
                    break

        # 5. Continue conversation
        await client.threads.add_message(
            thread_id=thread.id,
            role="user",
            content="What about Spain?"
        )

        run = await client.runs.create_and_wait(thread_id=thread.id)
        # ... handle response
    ```

=== "TypeScript"
    ```typescript
    async function haveConversation() {
        // 1. Create thread
        const thread = await client.threads.create();

        // 2. Add user message
        await client.threads.addMessage(
            thread.id,
            "user",
            "What's the capital of France?"
        );

        // 3. Create and wait for run
        let run = await client.runs.createAndWait(thread.id);

        // 4. Get agent response
        if (run.status === "completed") {
            const messages = await client.threads.getMessages(thread.id);
            const latest = messages[0];
            // Extract first text content
            for await (const content of latest.content) {
                if (content.type === "text") {
                    const completeText = await content.value;
                    console.log(`Agent: ${completeText.text}`);
                    break;
                }
            }
        }

        // 5. Continue conversation
        await client.threads.addMessage(thread.id, "user", "What about Spain?");
        run = await client.runs.createAndWait(thread.id);
    }
    ```

=== "C#"
    ```csharp
    async Task HaveConversation()
    {
        // 1. Create thread
        var thread = await client.Threads.CreateAsync();

        // 2. Add user message
        await client.Threads.AddMessageAsync(
            thread.Id,
            "user",
            "What's the capital of France?"
        );

        // 3. Create and wait for run
        var run = await client.Runs.CreateAndWaitAsync(thread.Id);

        // 4. Get agent response
        if (run.Status == "completed")
        {
            var messages = await client.Threads.GetMessagesAsync(thread.Id);
            var latest = messages.First();
            // Extract first text content
            await foreach (var content in latest.Content)
            {
                if (content is TextContent textContent)
                {
                    var completeText = await textContent.WaitForCompletionAsync();
                    Console.WriteLine($"Agent: {completeText.Text}");
                    break;
                }
            }
        }

        // 5. Continue conversation
        await client.Threads.AddMessageAsync(thread.Id, "user", "What about Spain?");
        run = await client.Runs.CreateAndWaitAsync(thread.Id);
    }
    ```

## Using the Conversation Helper

The SDK provides a higher-level abstraction that manages threads and runs automatically:

=== "Python"
    ```python
    # High-level API (recommended for most use cases)
    conversation = client.create_conversation()
    response1 = await conversation.add_user_message("Hello!")
    response2 = await conversation.add_user_message("Tell me more")

    # Get conversation history
    history = await conversation.get_messages()
    ```

=== "TypeScript"
    ```typescript
    // High-level API
    const conversation = client.createConversation();
    const response1 = await conversation.addUserMessage("Hello!");
    const response2 = await conversation.addUserMessage("Tell me more");
    ```

=== "C#"
    ```csharp
    // High-level API
    var conversation = client.CreateConversation();
    var response1 = await conversation.AddUserMessageAsync("Hello!");
    var response2 = await conversation.AddUserMessageAsync("Tell me more");
    ```

## Next Steps

- [Streaming](streaming.md) - Real-time responses without waiting
- [Tool Execution](tools.md) - How agents use tools during runs
- [Error Handling](error-handling.md) - Handling failures in threads and runs
- [API Reference](../../api-reference/index.md) - Complete API documentation
