# HostedVectorStoreContent

Hosted Vector Store Content

<!-- GENERATED_START -->

## HostedVectorStoreContent

Hosted Vector Store Content

### Usage

Rationale:
- Provider-hosted vector stores (e.g., OpenAI Assistants vector stores)
- RAG (Retrieval-Augmented Generation) with provider-managed embeddings
- Efficient reference without transferring embeddings in messages

EXAMPLES:
- OpenAI: vs_abc123 (created via vector stores API)
- Azure: Reference to Azure AI Search index

M365: Supports BYOM (Bring Your Own Memory) pattern via vector store references

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `documentCount` | `int32` | No | Number of vectors/documents in store (optional). |
| `kind` | `"hostedVectorStore"` | Yes |  |
| `name` | `string` | No | Vector store name (optional). |
| `vectorStoreId` | `string` | Yes | Provider's vector store identifier. |

---
<!-- GENERATED_END -->