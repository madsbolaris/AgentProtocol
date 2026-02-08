# ActionContent

Action Content (Interactive Actions Requiring Response)

<!-- GENERATED_START -->

## ActionContent

Action Content (Interactive Actions Requiring Response)

### Usage

Use Cases:
- Card button clicks: card_action_submit, adaptive_card_action
- Interactive elements: button_clicked, menu_selected
- Form submissions: form_submitted, input_provided

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `kind` | `"action"` | Yes |  |
| `name` | `string` | Yes | Action name/type |
| `text` | `string` | No | Display text for the action |
| `timestamp` | `utcDateTime` | No | Action timestamp |
| `value` | `Record<unknown>` | No | Action payload/data |

---
<!-- GENERATED_END -->