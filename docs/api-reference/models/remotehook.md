# RemoteHook

Remote Hook

<!-- GENERATED_START -->

## RemoteHook

Remote Hook

### Usage

Use Cases:
- Content moderation and filtering
- Dynamic guardrails
- Custom logging and telemetry
- Integration with external systems

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `condition` | `HookCondition` | No | Optional client-side filtering before remote call. |
| `config` | `Record<unknown>` | No | Hook-specific configuration sent in handshake. |
| `connection` | `Connection` | No | Authentication for remote endpoint. |
| `endpoint` | `string` | Yes | Remote endpoint URL. |
| `kind` | `"remote"` | Yes | Hook type discriminator. |
| `name` | `string` | Yes | Hook name (unique per run). |

---
<!-- GENERATED_END -->