# JSONSchema

JSON Schema

<!-- GENERATED_START -->

## JSONSchema

JSON Schema
UNIVERSAL STANDARD: Used by OpenAI, Anthropic, Azure, etc.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `JSONSchema | boolean` | No | Additional properties |
| `description` | `string` | No | Property description |
| `format` | `string` | No | Format hint |
| `items` | `JSONSchema` | No | Array item schema |
| `maxItems` | `int32` | No | Maximum array length |
| `maximum` | `float64` | No | Maximum value |
| `minItems` | `int32` | No | Minimum array length |
| `minimum` | `float64` | No | Minimum value |
| `pattern` | `string` | No | Pattern (regex) |
| `properties` | `Record<JSONSchema>` | No | Object properties |
| `required` | `string[]` | No | Required properties |
| `type` | `"object" | "string" | "number" | "integer" | "boolean" | "array" | "null"` | No | Schema type |

---
<!-- GENERATED_END -->