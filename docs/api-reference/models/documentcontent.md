# DocumentContent

Document Content

<!-- GENERATED_START -->

## DocumentContent

Document Content

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `citations` | `Citation[]` | No | Citations to specific parts of document |
| `content` | `string` | No | Document content or excerpt |
| `documentId` | `string` | Yes | Document ID |
| `kind` | `"document"` | Yes |  |
| `mimeType` | `string` | No | MIME type of document |
| `sizeBytes` | `int64` | No | Document size in bytes (for token estimation) |
| `source` | `string` | Yes | Source URL or path |
| `title` | `string` | Yes | Document title |

---
<!-- GENERATED_END -->