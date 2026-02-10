# ChatHistoryProviderConfig

Chat History Provider Configuration

<!-- GENERATED_START -->

## ChatHistoryProviderConfig

Chat History Provider Configuration

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `config` | `Record<unknown>` | No | Custom provider configuration. |
| `connection` | `Connection` | No | Connection configuration (for database/service providers). |
| `providerType` | `"inMemory" | "cosmosDb" | "sqlServer" | "serviceApi" | "custom"` | Yes | Provider type. |
| `retrievalOptions` | `HistoryRetrievalOptions` | No | History retrieval options. |

---
<!-- GENERATED_END -->