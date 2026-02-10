# SendMessageHook

Send Message Hook

<!-- GENERATED_START -->

## SendMessageHook

Send Message Hook

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `condition` | `RunCondition` | No | Condition for when to send message. |
| `kind` | `"sendMessage"` | Yes | Hook type discriminator. |
| `message` | `ChatMessage` | Yes | Message to inject (for LLM regeneration). |
| `name` | `string` | Yes | Hook name (unique per run). |

---
<!-- GENERATED_END -->