# FunctionCallContent

Function Call Content

<!-- GENERATED_START -->

## FunctionCallContent

Function Call Content
XML: <function-call call-id="..." name="...">{"arg": "value"}</function-call>

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `arguments` | `string` | Yes | Arguments as JSON string (XML serialization uses string only) |
| `callId` | `string` | Yes | Unique identifier for this tool call |
| `kind` | `"functionCall"` | Yes |  |
| `name` | `string` | Yes | Name of the function to call |

---
<!-- GENERATED_END -->