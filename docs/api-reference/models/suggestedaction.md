# SuggestedAction

Suggested Action

<!-- GENERATED_START -->

## SuggestedAction

Suggested Action
Represents a single quick reply button/action

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `actionType` | `"message" | "call" | "openUrl" | "openApp"` | Yes | Type of action |
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `image` | `string` | No | Optional icon URI |
| `text` | `string` | No | Text to send when clicked (for actionType="message") |
| `title` | `string` | Yes | Display text on the button |
| `value` | `string` | No | Action payload (URL for openUrl, phone for call, data for message) |

---
<!-- GENERATED_END -->