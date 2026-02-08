# Thread

<!-- GENERATED_START -->

## Thread

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `channelInfo` | `ChannelInfo` | No | Channel information for multi-channel routing. |
| `createdAt` | `utcDateTime` | Yes | Timestamp when thread was created. |
| `lastActivityAt` | `utcDateTime` | No | Timestamp of last activity (message, event, or status change). |
| `lastMessageAt` | `utcDateTime` | No | Timestamp of last message. |
| `messages` | `ChatMessage[]` | Yes | Messages in this thread. |
| `metadata` | `Record<unknown>` | No | Custom metadata for the thread. |
| `participants` | `Participant[]` | Yes | Participants in this thread. |
| `status` | `ThreadStatus = ThreadStatus.active` | No | Thread lifecycle status. |
| `threadId` | `string` | Yes | Unique thread identifier. |
| `unreadCount` | `int32 = 0` | No | Number of unread messages/events for subscribed clients. |

---
<!-- GENERATED_END -->