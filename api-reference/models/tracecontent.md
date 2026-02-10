# TraceContent

XML: <trace name="..." label="..." severity="information" timestamp="...">{value}</trace>

<!-- GENERATED_START -->

## TraceContent

XML: <trace name="..." label="..." severity="information" timestamp="...">{value}</trace>

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `kind` | `"trace"` | Yes |  |
| `label` | `string` | No | Human-readable label |
| `name` | `string` | Yes | Trace name (identifies the component/operation) |
| `severity` | `string` | No | Severity level |
| `timestamp` | `utcDateTime` | No | Trace timestamp |
| `value` | `string` | No | Trace data/payload (as text/JSON) |

---
<!-- GENERATED_END -->