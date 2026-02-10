# VideoContent

Video Content

<!-- GENERATED_START -->

## VideoContent

Video Content
Represents video data that can be included in messages. Supports screen recordings,
video responses, and other video scenarios. Video can be provided as raw bytes,
data URI, or external URL reference.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `data` | `bytes` | No | Raw video bytes. |
| `dataUri` | `string` | No | Data URI (base64 encoded). |
| `duration` | `int32` | No | Duration in seconds. |
| `frameRate` | `int32` | No | Frame rate (frames per second). |
| `height` | `int32` | No | Video height in pixels. |
| `kind` | `"video"` | Yes |  |
| `mimeType` | `string` | No | MIME type. |
| `uri` | `string` | No | External video URL. |
| `width` | `int32` | No | Video width in pixels. |

---
<!-- GENERATED_END -->