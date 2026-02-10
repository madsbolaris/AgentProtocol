# EventContent

Event Content (Programmatic Events)

<!-- GENERATED_START -->

## EventContent

Event Content (Programmatic Events)

### Usage

Use Cases:
- Programmatic notifications: token_refresh, payment_received, workflow_completed
- Thread lifecycle: participant_added, participant_removed, topic_changed
- System notifications: session_started, session_ended
- External triggers: scheduled_trigger, webhook_received, threshold_alert

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `additionalProperties` | `Record<unknown>` | No | Additional properties |
| `kind` | `"event"` | Yes |  |
| `name` | `string` | Yes | Event name |
| `text` | `string` | No | Human-readable description |
| `timestamp` | `utcDateTime` | No | Event timestamp |
| `value` | `Record<unknown>` | No | Event payload |

---
<!-- GENERATED_END -->