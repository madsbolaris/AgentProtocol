# HostedFileContent

Hosted File Content

<!-- GENERATED_START -->

## HostedFileContent

Hosted File Content

### Usage

Rationale:
- Provider-hosted files (e.g., OpenAI file uploads, Azure blob storage)
- File processing by provider (embeddings, image analysis, transcription)
- Efficient reference without transferring file content in messages

EXAMPLES:
- OpenAI: file-abc123 (uploaded via files API)
- Azure: azure://storage.blob.core.windows.net/container/file.pdf

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `fileId` | `string` | Yes | Provider's file identifier. |
| `filename` | `string` | No | Original filename (optional). |
| `kind` | `"hostedFile"` | Yes |  |
| `mediaType` | `string` | No | Media type (MIME type). |
| `sizeBytes` | `int64` | No | File size in bytes (optional). |

---
<!-- GENERATED_END -->