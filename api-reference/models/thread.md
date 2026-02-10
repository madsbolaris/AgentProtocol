# Thread

Thread - Conversation

<!-- GENERATED_START -->

## Thread

Thread - Conversation
M365 REQUIREMENT: Maps to Conversation in Conversation Store
Key Capabilities:
- Persistent message history with participants
- Lifecycle management (active, closed, archived)
- Multi-channel support via channelInfo
- Unread count tracking for notifications
- Proactive messaging support (webhooks, polling, SSE)
Conversation Patterns:
- 1:1 conversations (2 participants)
- Group chats (multiple participants)
- Channel-based routing (Teams, Slack, etc.)
- Cross-channel conversations (same thread, multiple channels)
M365 Integration:
- Maps to Conversation in Conversation Store
- Links to Agent Journal for cross-conversation memory
- Supports Teams/Outlook participant mapping

### Usage

Core conversation model representing a persistent message thread.
Manages conversation lifecycle, participants, messages, and metadata.
Supports multi-turn conversations, group chats, and channel-based routing.

Key Capabilities:
- Persistent message history with participants
- Lifecycle management (active, closed, archived)
- Multi-channel support via channelInfo
- Unread count tracking for notifications
- Proactive messaging support (webhooks, polling, SSE)

Conversation Patterns:
- 1:1 conversations (2 participants)
- Group chats (multiple participants)
- Channel-based routing (Teams, Slack, etc.)
- Cross-channel conversations (same thread, multiple channels)

M365 Integration:
- Maps to Conversation in Conversation Store
- Links to Agent Journal for cross-conversation memory
- Supports Teams/Outlook participant mapping

**Extends:** `ThreadBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `channelInfo` | `ChannelInfo` | No | Channel information for multi-channel routing. |
| `lastActivityAt` | `utcDateTime` | No | Timestamp of last activity (message, event, or status change). |
| `lastMessageAt` | `utcDateTime` | No | Timestamp of last message. |
| `messages` | `ChatMessage[]` | Yes | Messages in this thread. |
| `participants` | `Participant[]` | Yes | Participants in this thread. |
| `unreadCount` | `int32 = 0` | No | Number of unread messages/events for subscribed clients. |

### Examples

#### 1:1 conversation thread

```json
{
"threadId": "thread_123",
"status": "active",
"participants": [
{ "userId": "user_001", "role": "user" },
{ "agentId": "agent_001", "role": "assistant" }
],
"messages": [
{
"messageId": "msg_001",
"role": "user",
"contents": [{ "kind": "text", "text": "Hello!" }],
"createdAt": "2026-02-07T10:00:00Z"
}
],
"createdAt": "2026-02-07T10:00:00Z",
"lastActivityAt": "2026-02-07T10:00:00Z",
"unreadCount": 0
}
```

#### Group chat thread

```json
{
"threadId": "thread_456",
"status": "active",
"participants": [
{ "userId": "user_001", "role": "user" },
{ "userId": "user_002", "role": "user" },
{ "agentId": "agent_001", "role": "assistant" }
],
"messages": [],
"metadata": {
"topic": "Project Planning",
"department": "Engineering"
},
"createdAt": "2026-02-07T10:00:00Z"
}
```

#### Multi-channel thread

```json
{
"threadId": "thread_789",
"status": "active",
"channelInfo": {
"channelId": "teams",
"channelConversationId": "19:abc123@thread.skype"
},
"participants": [
{ "userId": "user_001", "role": "user" },
{ "agentId": "agent_001", "role": "assistant" }
],
"messages": [],
"createdAt": "2026-02-07T10:00:00Z"
}
```

#### XML Output with thread wrapper

```xml
<thread thread-id="thread_123" status="active" created-at="2026-02-07T10:00:00Z">
<user message-id="msg_001" user-id="user_001" created-at="2026-02-07T10:00:00Z">
<text>Hello!</text>
</user>
<agent message-id="msg_002" agent-id="agent_001" created-at="2026-02-07T10:00:01Z">
<text>Hi there!</text>
</agent>
</thread>
```

---
<!-- GENERATED_END -->