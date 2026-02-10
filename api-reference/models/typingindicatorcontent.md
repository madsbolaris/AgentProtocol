# TypingIndicatorContent

XML: <typing-indicator from="user_123" status="typing" timestamp="..." />

<!-- GENERATED_START -->

## TypingIndicatorContent

XML: <typing-indicator from="user_123" status="typing" timestamp="..." />

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `from` | `string` | Yes | Who is typing (user ID or agent ID) |
| `kind` | `"typingIndicator"` | Yes |  |
| `status` | `"typing" | "thinking" | "processing"` | Yes | Indicator status |
| `timestamp` | `utcDateTime` | No | Optional timestamp |

---
<!-- GENERATED_END -->