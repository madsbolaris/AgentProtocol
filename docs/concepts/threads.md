# Threads

A **thread** represents a conversation context in the Agent Protocol. Think of it like a chat session that maintains history and state across multiple messages and runs.

## What is a Thread?

A thread is a container for:
- **Message history** - All messages exchanged between participants
- **Participant information** - Who's involved in the conversation
- **Metadata** - Custom data and context
- **State** - Conversation lifecycle and status

## Key Characteristics

### Persistent
Threads persist across multiple runs. Once created, a thread maintains its history until explicitly deleted or archived.

### Multi-turn
Threads support ongoing conversations with context preservation. Each new message has access to the full conversation history.

### Multi-participant
Threads can include multiple participants (users, agents, systems) all contributing to the same conversation.

## Thread Lifecycle

1. **Created** - New thread initialized
2. **Active** - Accepting messages and runs
3. **Archived** - No longer active but preserved
4. **Deleted** - Permanently removed

## Common Use Cases

### Chat Sessions
```
User creates thread
├─ User: "Hello, I need help"
├─ Agent: "I'm here to help!"
├─ User: "Tell me about threads"
└─ Agent: [explains threads with full context]
```

### Long-running Workflows
```
Thread tracks multi-step process
├─ Day 1: Initial request
├─ Day 2: Follow-up questions
├─ Day 3: Final resolution
└─ All context preserved
```

### Multi-agent Collaboration
```
Thread coordinates multiple agents
├─ User asks question
├─ Research agent gathers info
├─ Analysis agent processes data
└─ Response agent replies to user
```

## Thread Properties

- **ID** - Unique identifier
- **Created timestamp** - When thread was created
- **Metadata** - Custom key-value data
- **Participants** - List of participants
- **Status** - Current lifecycle state
- **Message count** - Number of messages

## Related Concepts

- **[Runs](runs.md)** - Executions that happen within a thread
- **[Messages](messages.md)** - Content exchanged in a thread
- **[Agents](agents.md)** - Entities that process thread messages

## Best Practices

✅ **Do:**
- Use one thread per conversation topic
- Set meaningful metadata for context
- Archive old threads instead of deleting
- Resume existing threads when appropriate

❌ **Don't:**
- Share threads across unrelated conversations
- Store sensitive data in thread metadata
- Create new threads for every message
- Keep threads active indefinitely

## Next Steps

- Learn about [Runs](runs.md) to execute agents on threads
- Understand [Messages](messages.md) to communicate within threads
- Explore the [Client SDK](../products/client-sdk/) to work with threads
