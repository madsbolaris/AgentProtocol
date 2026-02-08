# RunRequiresActionEvent

<!-- GENERATED_START -->

## RunRequiresActionEvent

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agentId` | `string` | No |  |
| `eventSeq` | `int64` | Yes |  |
| `kind` | `"submit_tool_outputs"` | Yes |  |
| `runId` | `string` | Yes |  |
| `status` | `"requires_action"` | Yes |  |
| `threadId` | `string` | No |  |
| `timestamp` | `utcDateTime` | Yes |  |
| `tool_calls` | `FunctionCallContent[]` | Yes |  |

---
<!-- GENERATED_END -->