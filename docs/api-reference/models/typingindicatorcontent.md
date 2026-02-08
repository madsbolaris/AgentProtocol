# TypingIndicatorContent

Typing Indicator Content (Bidirectional Presence)

<!-- GENERATED_START -->

## TypingIndicatorContent

Typing Indicator Content (Bidirectional Presence)
BIDIRECTIONAL: Can be sent by either party
- User sends: "I'm typing a message"
- Agent sends: "I'm generating a response"
EPHEMERAL: Not persisted in message history
- Temporary presence indicator
- Cleared when actual content arrives

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `from` | `string` | Yes | Who is typing (user ID or agent ID) |
| `kind` | `"typingIndicator"` | Yes |  |
| `status` | `"typing" | "thinking" | "processing"` | Yes | Indicator status |
| `timestamp` | `utcDateTime` | No | Optional timestamp |

---
<!-- GENERATED_END -->