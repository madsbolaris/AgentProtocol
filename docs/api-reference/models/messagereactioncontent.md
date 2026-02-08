# MessageReactionContent

Message Reaction Content (Social Interactions)

<!-- GENERATED_START -->

## MessageReactionContent

Message Reaction Content (Social Interactions)
LIGHTWEIGHT: Doesn't interrupt conversation flow
- Simple social acknowledgment
- Multiple reactions can exist on one message

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `kind` | `"messageReaction"` | Yes |  |
| `reactionsAdded` | `MessageReaction[]` | No | Reactions added |
| `reactionsRemoved` | `MessageReaction[]` | No | Reactions removed |
| `referencedMessageId` | `string` | Yes | Message ID being reacted to |

---
<!-- GENERATED_END -->