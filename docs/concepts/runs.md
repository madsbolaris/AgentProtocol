# Runs

A **run** is a single execution of an agent on a thread. When you want an agent to process messages and generate responses, you create a run.

## What is a Run?

Think of a run like pressing "send" in a chat application:
1. You provide input messages
2. The agent processes them
3. The run completes with output messages

Each run is independent but operates within a thread's context.

## Key Characteristics

### Stateful Execution
Runs have access to the full thread history. The agent can see all previous messages when processing.

### Lifecycle-driven
Runs progress through distinct states from creation to completion.

### Result-oriented
Every run produces a result: success, failure, or requiring action.

## Run Lifecycle

```
queued → in_progress → completed
                    → failed
                    → requires_action
                    → cancelled
```

### States Explained

- **queued** - Waiting to start
- **in_progress** - Agent is processing
- **requires_action** - Needs user input (e.g., tool approval)
- **completed** - Successfully finished
- **failed** - Error occurred
- **cancelled** - User stopped the run

## Execution Modes

### Synchronous (Blocking)
Wait for the run to complete before continuing:
```
create_run() → wait → get result
```

### Asynchronous (Polling)
Start the run and check status later:
```
create_run() → do other work → poll status → get result
```

### Streaming
Receive output as it's generated:
```
create_run() → stream chunks → final result
```

## Run Properties

- **ID** - Unique identifier
- **Thread ID** - Which conversation
- **Agent ID** - Which agent to run
- **Status** - Current lifecycle state
- **Input messages** - What to process
- **Output messages** - Generated responses
- **Metadata** - Custom context
- **Created/Started/Completed timestamps**
- **Error info** - If failed

## Common Patterns

### Simple Request-Response
```
1. Create thread
2. Create run with user message
3. Wait for completion
4. Read agent response
```

### Multi-turn Conversation
```
1. Create thread
2. Run 1: User asks question
3. Run 2: User asks follow-up (has context from Run 1)
4. Run 3: User asks clarification (has context from Runs 1-2)
```

### Tool Execution
```
1. Create run
2. Agent decides to use tool → status: requires_action
3. User approves/executes tool
4. Submit tool result
5. Run continues → status: completed
```

## Run Options

Customize run behavior:
- **Temperature** - Response randomness
- **Max tokens** - Response length limit
- **Tool choice** - Which tools to allow
- **Instructions** - Override agent instructions
- **Metadata** - Custom tracking data

## Related Concepts

- **[Threads](threads.md)** - Where runs execute
- **[Messages](messages.md)** - Input and output of runs
- **[Agents](agents.md)** - What runs execute
- **[Streaming](streaming.md)** - Real-time run output
- **[Tools](tools.md)** - Functions agents can call during runs

## Best Practices

✅ **Do:**
- Handle all run states (not just completed)
- Set appropriate timeouts
- Use streaming for long responses
- Preserve run IDs for debugging

❌ **Don't:**
- Create multiple concurrent runs on same thread
- Ignore requires_action state
- Poll too frequently (use webhooks or streaming)
- Forget to handle failures

## Next Steps

- Learn about [Streaming](streaming.md) for real-time output
- Understand [Tools](tools.md) for agent capabilities
- Explore the [Client SDK](../products/client-sdk/) to create runs
