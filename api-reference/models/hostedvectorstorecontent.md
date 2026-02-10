# HostedVectorStoreContent

Hosted Vector Store Content

<!-- GENERATED_START -->

## HostedVectorStoreContent

Hosted Vector Store Content
XML: <hosted-vector-store vector-store-id="vs_abc123" name="my-vectors" document-count="1000" />

### Usage

Rationale:
- Provider-hosted vector stores (e.g., OpenAI Assistants vector stores)
- RAG (Retrieval-Augmented Generation) with provider-managed embeddings
- Efficient reference without transferring embeddings in messages

EXAMPLES:
- OpenAI: vs_abc123 (created via vector stores API)
- Azure: Reference to Azure AI Search index

M365: Supports BYOM (Bring Your Own Memory) pattern via vector store references

XML: <hosted-vector-store vector-store-id="vs_abc123" name="my-vectors" document-count="1000" />

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `documentCount` | `int32` | No | Number of vectors/documents in store (optional). |
| `kind` | `"hostedVectorStore"` | Yes |  |
| `name` | `string` | No | Vector store name (optional). |
| `vectorStoreId` | `string` | Yes | Provider's vector store identifier. |

---
<!-- GENERATED_END -->