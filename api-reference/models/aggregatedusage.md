# AggregatedUsage

Usage Aggregation

<!-- GENERATED_START -->

## AggregatedUsage

Usage Aggregation

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `inputTokenDetails` | `InputTokenDetails` | No | Input token details (aggregated) |
| `inputTokens` | `int64 = 0` | Yes | Total input tokens across all requests |
| `outputTokenDetails` | `OutputTokenDetails` | No | Output token details (aggregated) |
| `outputTokens` | `int64 = 0` | Yes | Total output tokens across all requests |
| `requestUsageEntries` | `RequestUsage[]` | No | Per-request usage entries (for detailed cost calculation) |
| `requests` | `int32 = 0` | Yes | Total number of requests made |
| `totalTokens` | `int64 = 0` | Yes | Total tokens (input + output) |

---
<!-- GENERATED_END -->