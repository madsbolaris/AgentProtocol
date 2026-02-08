# AudioContent

Audio Content

<!-- GENERATED_START -->

## AudioContent

Audio Content
Represents audio data that can be included in messages. Supports voice notes,
audio responses, and other audio scenarios. Audio can be provided as raw bytes,
data URI, or external URL reference.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `data` | `bytes` | No | Raw audio bytes. |
| `dataUri` | `string` | No | Data URI (base64 encoded). |
| `duration` | `int32` | No | Duration in seconds. |
| `kind` | `"audio"` | Yes |  |
| `mimeType` | `string` | No | MIME type. |
| `uri` | `string` | No | External audio URL. |

---
<!-- GENERATED_END -->