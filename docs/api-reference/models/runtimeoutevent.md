# RunTimeoutEvent

<!-- GENERATED_START -->

## RunTimeoutEvent

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentId` | `string` | No |  |
| `eventSeq` | `int64` | Yes |  |
| `output` | `ChatMessage[]` | No |  |
| `runId` | `string` | Yes |  |
| `status` | `"timeout"` | Yes |  |
| `threadId` | `string` | No |  |
| `timedOutAt` | `utcDateTime` | Yes |  |
| `usage` | `CompletionUsage` | No |  |

---
<!-- GENERATED_END -->