# UserInputRequestContent

XML: <user-input-request request-id="..." prompt="..." input-type="choice" required="true" />

<!-- GENERATED_START -->

## UserInputRequestContent

XML: <user-input-request request-id="..." prompt="..." input-type="choice" required="true" />

**Extends:** `AIContentBase`

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `inputType` | `string` | No | Input type |
| `kind` | `"userInputRequest"` | Yes |  |
| `prompt` | `string` | Yes | Prompt for user |
| `requestId` | `string` | Yes | Unique identifier for this input request |
| `required` | `boolean` | No | Whether input is required |

---
<!-- GENERATED_END -->