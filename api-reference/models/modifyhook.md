# ModifyHook

Modify Hook

<!-- GENERATED_START -->

## ModifyHook

Modify Hook

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `condition` | `RunCondition` | No | Condition for when to modify. |
| `kind` | `"modify"` | Yes | Hook type discriminator. |
| `name` | `string` | Yes | Hook name (unique per run). |
| `predefinedPatterns` | `string[]` | No | Predefined redaction patterns. |
| `regexPatterns` | `string[]` | No | Custom regex patterns for redaction. |
| `replacement` | `string = "[REDACTED]"` | No | Replacement text for redacted content. |

---
<!-- GENERATED_END -->