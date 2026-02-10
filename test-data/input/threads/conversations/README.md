# Conversation Test Files

This directory contains test files for multi-message conversation flows and thread management.

## Subdirectories

### single-turn/
Tests for single-turn conversations (one exchange):
- `27-thread-single-system.xml` - Thread with single system message

**Total**: 1 file

### multi-turn/
Tests for multi-turn conversations (multiple exchanges):
- `28-thread-conversation.xml` - Basic multi-turn conversation
- `38-full-conversation.xml` - Complete conversation with system, user, and agent messages
- `43-long-conversation.xml` - Extended conversation with many turns

**Total**: 3 files

### multi-user/
Tests for conversations with multiple users:
- `33-multi-user-conversation.xml` - Conversation with multiple user participants
- `34-user-to-user-with-agent.xml` - User-to-user communication facilitated by agent
- `35-multiple-user-messages.xml` - Multiple messages from different users

**Total**: 3 files

### tool-use/
Tests for conversations involving tool/function use:
- `29-thread-with-tool-use.xml` - Conversation with tool calling
- `30-thread-multimodal.xml` - Multimodal conversation (may include tool use)
- `48-tools-between-users.xml` - Tool calls in multi-user conversation

**Total**: 3 files

## Purpose

These files validate:
- Thread creation and management
- Message ordering and chronology
- Turn-taking between participants
- Context preservation across messages
- Tool/function integration in conversations
- Multi-user coordination

## Testing Focus

### Thread Management
- Thread ID generation and tracking
- Message sequencing
- Timestamp ordering
- Thread lifecycle

### Conversation Flow
- **Single-turn**: System instructions, one-shot queries
- **Multi-turn**: Back-and-forth exchanges, context retention
- **Multi-user**: User identification, role separation
- **Tool-use**: Function calls mid-conversation, result integration

### Complexity Levels

1. **Simple** - Single message or basic exchange
2. **Moderate** - Multi-turn with 3-5 messages
3. **Complex** - Long conversations, multiple users, tool use
4. **Advanced** - Combined scenarios (multi-user + tool-use)

## Conversation Patterns

### System → User → Agent
```xml
<thread>
  <system>You are a helpful assistant</system>
  <user>Hello</user>
  <agent>Hi there!</agent>
</thread>
```

### User → Agent → Tool → Agent
```xml
<thread>
  <user>What's the weather?</user>
  <agent><function-call name="get_weather"/></agent>
  <tool><function-result>72°F, Sunny</function-result></tool>
  <agent>It's 72°F and sunny!</agent>
</thread>
```

### Multi-User
```xml
<thread>
  <user user-id="user1">Hi everyone</user>
  <user user-id="user2">Hello!</user>
  <agent>Welcome to the conversation</agent>
</thread>
```

## Validation Rules

These test files ensure compliance with:
- Messages must have chronological `created-at` timestamps
- Message IDs must be unique within thread
- Tool results must reference preceding function calls
- User IDs must be consistent for same user
- Thread context must be preserved

## Total Files

**10 files** across 4 subdirectories, covering all conversation patterns in the Agent Protocol.

## Usage Example

```python
# Python - Test multi-turn conversation
thread = parse_thread_xml("conversations/multi-turn/28-thread-conversation.xml")
assert len(thread.messages) >= 3
assert thread.messages[0].role == "system"
assert thread.messages[1].role == "user"
assert thread.messages[2].role == "agent"
```

## Related Directories

- See `../basic/` for individual message types used in conversations
- See `../roles/` for role-based thread organization
- See `../scenarios/` for real-world conversation patterns
