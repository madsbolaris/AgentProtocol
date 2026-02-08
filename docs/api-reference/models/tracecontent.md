# TraceContent

Trace Content (Debugging/Telemetry)

<!-- GENERATED_START -->

## TraceContent

Trace Content (Debugging/Telemetry)

### Usage

Use Cases:
- Observability: luis_recognizer, qna_maker, dialog_state
- Debug traces: turn_context, middleware_executed
- Performance metrics: latency_measured, tokens_consumed

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `kind` | `"trace"` | Yes |  |
| `label` | `string` | No | Human-readable label |
| `name` | `string` | Yes | Trace name (identifies the component/operation) |
| `relatedActivityId` | `string` | No | Related activity ID (for correlation) |
| `severity` | `"verbose" | "information" | "warning" | "error"` | No | Severity level |
| `timestamp` | `utcDateTime` | No | Trace timestamp |
| `value` | `Record<unknown>` | No | Trace data/payload |
| `valueType` | `string` | No | Value type URI (e.g., "https://www.luis.ai/schemas/trace") |

---
<!-- GENERATED_END -->