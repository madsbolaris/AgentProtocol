# FileContent

File Content

<!-- GENERATED_START -->

## FileContent

File Content

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `data` | `bytes` | No | Raw file bytes |
| `dataUri` | `string` | No | Data URI (base64 encoded) |
| `filename` | `string` | No | File name |
| `kind` | `"file"` | Yes |  |
| `mimeType` | `string` | No | MIME type |
| `sizeBytes` | `int64` | No | File size in bytes (for token estimation) |
| `uri` | `string` | No | External file URL |

---
<!-- GENERATED_END -->