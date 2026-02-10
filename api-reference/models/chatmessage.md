# ChatMessage

Chat Message

<!-- GENERATED_START -->

## ChatMessage

Chat Message
Key Capabilities:
- Multi-modal content via AIContent[] array
- Message branching via parentMessageId (conversation tree)
- Audit trail via userId, agentId, completionId
- Bidirectional presence (typing indicators)
- Social interactions (reactions)
M365 Integration:
- Maps to Canonical Event in Conversation Store
- Supports Entra User ID and Agent ID
- Links to Run for execution tracking

### Usage

Core message model representing a single message in a conversation thread.
Supports multi-modal content (text, images, audio, video, files) and rich metadata.
Used for both user messages and agent responses.

Key Capabilities:
- Multi-modal content via AIContent[] array
- Message branching via parentMessageId (conversation tree)
- Audit trail via userId, agentId, completionId
- Bidirectional presence (typing indicators)
- Social interactions (reactions)

M365 Integration:
- Maps to Canonical Event in Conversation Store
- Supports Entra User ID and Agent ID
- Links to Run for execution tracking

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentId` | `string` | No | Agent that generated this message. |
| `authorName` | `string` | No | Author name for display. |
| `completedAt` | `utcDateTime` | No | Timestamp when message generation completed. |
| `completionId` | `string` | No | Run that generated this message. |
| `contents` | `AIContent[]` | Yes | Content items in this message. |
| `createdAt` | `utcDateTime` | No | Timestamp when message was created. |
| `messageId` | `string` | Yes | Unique message identifier. |
| `metadata` | `Record<unknown>` | No | Custom metadata. |
| `parentMessageId` | `string` | No | Parent message ID for conversation branching. |
| `rawRepresentation` | `unknown` | No | Underlying provider representation. |
| `role` | `ChatRole` | Yes | Message role. |
| `text` | `string` | No | Concatenated text from all TextContent items. |
| `threadId` | `string` | No | Thread this message belongs to. |
| `userId` | `string` | No | User who created this message. |

### Examples

#### User text message

```json
{
"messageId": "msg_123",
"role": "user",
"contents": [
{ "kind": "text", "text": "What's the weather today?" }
],
"userId": "user_789",
"createdAt": "2026-02-07T10:00:00Z"
}
```

#### Agent response with tool call

```json
{
"messageId": "msg_124",
"role": "assistant",
"contents": [
{
"kind": "functionCall",
"callId": "call_001",
"name": "get_weather",
"arguments": "{\"location\": \"San Francisco\"}"
}
],
"agentId": "agent_001",
"completionId": "run_789",
"createdAt": "2026-02-07T10:00:01Z"
}
```

#### Multi-modal message with image

```json
{
"messageId": "msg_125",
"role": "user",
"contents": [
{ "kind": "text", "text": "What's in this image?" },
{
"kind": "image",
"uri": "https://example.com/photo.jpg",
"mimeType": "image/jpeg"
}
],
"userId": "user_789",
"createdAt": "2026-02-07T10:00:05Z"
}
```

---
<!-- GENERATED_END -->