# FunctionCallContent

Function Call Content

<!-- GENERATED_START -->

## FunctionCallContent

Function Call Content

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `arguments` | `string | Record<unknown>` | No | Arguments as JSON string or dictionary |
| `callId` | `string` | Yes | Unique identifier for this tool call |
| `kind` | `"functionCall"` | Yes |  |
| `name` | `string` | Yes | Name of the function to call |

---
<!-- GENERATED_END -->