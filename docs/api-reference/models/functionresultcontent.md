# FunctionResultContent

Function Result Content

<!-- GENERATED_START -->

## FunctionResultContent

Function Result Content

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `audience` | `string` | No | (Inherited from AIContentBase) Target audience filter (comma-separated roles). Controls which roles should see this content. |
| `encryption` | `string` | No | (Inherited from AIContentBase) Encryption metadata (key reference). Contains encryption key reference. |
| `additionalProperties` | `Record<unknown>` | No | (Inherited from AIContentBase) Client-side extensibility metadata. NOT SERIALIZED to XML. |
| `callId` | `string` | Yes | Tool call ID this result corresponds to |
| `exception` | `ErrorContent` | No | Exception if tool execution failed |
| `kind` | `"functionResult"` | Yes |  |
| `name` | `string` | Yes | Name of the function that was called |
| `result` | `string | AIContent[]` | No | Result data (can be multi-modal) |

---
<!-- GENERATED_END -->