# ChatMessage

Chat Message

<!-- GENERATED_START -->

## ChatMessage

Chat Message

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentId` | `string` | No | Agent that generated this message. |
| `authorName` | `string` | No | Author name for display. |
| `completedAt` | `utcDateTime` | No | Timestamp when message generation completed. |
| `completionId` | `string` | No | Run that generated this message. |
| `contents` | `AIContent[]` | Yes | Content items in this message. |
| `createdAt` | `utcDateTime` | No | Timestamp when message was created. |
| `messageId` | `string` | No | Unique message identifier. |
| `metadata` | `Record<unknown>` | No | Custom metadata. |
| `parentMessageId` | `string` | No | Parent message ID for conversation branching. |
| `rawRepresentation` | `unknown` | No | Underlying provider representation. |
| `role` | `ChatRole` | Yes | Message role. |
| `text` | `string` | No | Concatenated text from all TextContent items. |
| `threadId` | `string` | No | Thread this message belongs to. |
| `userId` | `string` | No | User who created this message. |

---
<!-- GENERATED_END -->