# SendMessageResponse

Send Message Response

<!-- GENERATED_START -->

## SendMessageResponse

Send Message Response

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `eventSeqs` | `int64[]` | Yes | Event sequence numbers after which to insert message. |
| `injectedMessage` | `ChatMessage` | Yes | Message to inject. |
| `kind` | `"sendMessage"` | Yes | Response type discriminator. |

---
<!-- GENERATED_END -->