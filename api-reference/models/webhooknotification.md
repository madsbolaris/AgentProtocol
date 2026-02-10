# WebhookNotification

Webhook Notification

<!-- GENERATED_START -->

## WebhookNotification

Webhook Notification

### Usage

Webhook payload sent to subscription webhookUrl when subscribed events occur.
Contains minimal event data - clients should fetch full details via REST API.

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `eventSeq` | `int64` | Yes |  |
| `eventType` | `string` | Yes |  |
| `kind` | `"thread.activity" | "run.activity" | "agent.activity"` | Yes |  |
| `messageId` | `string` | No |  |
| `resourceId` | `string` | Yes |  |
| `runId` | `string` | No |  |
| `sequenceNumber` | `int64` | Yes |  |
| `status` | `string` | No |  |
| `subscriptionId` | `string` | Yes |  |
| `timestamp` | `utcDateTime` | Yes |  |

### Examples

#### Thread activity notification

```json
{
"kind": "thread.activity",
"resourceId": "thread_123",
"subscriptionId": "sub_456",
"eventType": "message.created",
"sequenceNumber": 42,
"eventSeq": 10,
"timestamp": "2026-02-07T10:00:00Z",
"data": {
"messageId": "msg_789",
"runId": "run_001"
}
}
```

---
<!-- GENERATED_END -->