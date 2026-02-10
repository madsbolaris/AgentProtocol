# ImageContent

Image Content

<!-- GENERATED_START -->

## ImageContent

Image Content
Provides three delivery methods: uri, dataUri, or raw data bytes.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `data` | `bytes` | No | Raw image bytes |
| `dataUri` | `string` | No | Data URI (base64 encoded) |
| `height` | `int32` | No | Image height in pixels |
| `kind` | `"image"` | Yes |  |
| `mimeType` | `string` | No | MIME type (e.g., "image/png") |
| `uri` | `string` | No | External image URL |
| `width` | `int32` | No | Image width in pixels |

---
<!-- GENERATED_END -->