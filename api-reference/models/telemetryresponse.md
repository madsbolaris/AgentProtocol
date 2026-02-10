# TelemetryResponse

Telemetry Response

<!-- GENERATED_START -->

## TelemetryResponse

Telemetry Response

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `eventSeqs` | `int64[]` | Yes | Event sequence numbers after which to insert telemetry. |
| `kind` | `"telemetry"` | Yes | Response type discriminator. |
| `telemetryEvent` | `string` | Yes | Telemetry event name. |
| `telemetryProperties` | `Record<unknown>` | No | Telemetry event properties (optional). |

---
<!-- GENERATED_END -->