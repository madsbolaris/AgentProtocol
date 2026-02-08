# TelemetryHook

Telemetry Hook

<!-- GENERATED_START -->

## TelemetryHook

Telemetry Hook

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `condition` | `HookCondition` | No | Condition for when to emit telemetry. |
| `event` | `string` | Yes | Telemetry event name. |
| `kind` | `"telemetry"` | Yes | Hook type discriminator. |
| `name` | `string` | Yes | Hook name (unique per run). |
| `properties` | `Record<string>` | No | Telemetry event properties. |

---
<!-- GENERATED_END -->