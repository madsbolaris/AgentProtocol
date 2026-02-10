# VideoContent

Video Content

<!-- GENERATED_START -->

## VideoContent

Video Content
Represents video data that can be included in messages.
XML: <video uri="..." mime-type="..." width="1920" height="1080" duration="120" frame-rate="30" />

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `duration` | `int32` | No | Duration in seconds |
| `frameRate` | `int32` | No | Frame rate (frames per second) |
| `height` | `int32` | No | Video height in pixels |
| `kind` | `"video"` | Yes |  |
| `mimeType` | `string` | No | MIME type |
| `uri` | `string` | No | External video URL |
| `width` | `int32` | No | Video width in pixels |

---
<!-- GENERATED_END -->