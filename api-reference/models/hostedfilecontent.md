# HostedFileContent

Hosted File Content

<!-- GENERATED_START -->

## HostedFileContent

Hosted File Content
XML: <hosted-file file-id="file-abc123" filename="doc.pdf" media-type="application/pdf" size-bytes="1024" />

### Usage

Rationale:
- Provider-hosted files (e.g., OpenAI file uploads, Azure blob storage)
- File processing by provider (embeddings, image analysis, transcription)
- Efficient reference without transferring file content in messages

EXAMPLES:
- OpenAI: file-abc123 (uploaded via files API)
- Azure: azure://storage.blob.core.windows.net/container/file.pdf

XML: <hosted-file file-id="file-abc123" filename="doc.pdf" media-type="application/pdf" size-bytes="1024" />

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `fileId` | `string` | Yes | Provider's file identifier. |
| `filename` | `string` | No | Original filename (optional). |
| `kind` | `"hostedFile"` | Yes |  |
| `mediaType` | `string` | No | Media type (MIME type). |
| `sizeBytes` | `int64` | No | File size in bytes (optional). |

---
<!-- GENERATED_END -->