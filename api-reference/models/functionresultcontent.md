# FunctionResultContent

Function Result Content

<!-- GENERATED_START -->

## FunctionResultContent

Function Result Content
XML: <function-result call-id="..." name="...">{"result": "value"}</function-result>

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `callId` | `string` | No | Tool call ID this result corresponds to |
| `kind` | `"functionResult"` | Yes |  |
| `name` | `string` | No | Name of the function that was called |
| `result` | `string` | Yes | Result data as JSON string (XML serialization uses string only) |

---
<!-- GENERATED_END -->