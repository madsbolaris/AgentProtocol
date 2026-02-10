# SearchResultContent

Search Result Content

<!-- GENERATED_START -->

## SearchResultContent

Search Result Content

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `citations` | `Citation[]` | No | Citations to specific parts of content |
| `kind` | `"searchResult"` | Yes |  |
| `mimeType` | `string` | No | MIME type of source content |
| `score` | `float32` | No | Relevance score (0.0-1.0) |
| `snippet` | `string` | Yes | Snippet/summary |
| `title` | `string` | Yes | Search result title |
| `url` | `string` | Yes | Source URL |

---
<!-- GENERATED_END -->