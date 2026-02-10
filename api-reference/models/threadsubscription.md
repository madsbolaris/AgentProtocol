# ThreadSubscription

Thread Subscription - Webhook Notification Registration

<!-- GENERATED_START -->

## ThreadSubscription

Thread Subscription - Webhook Notification Registration

### Usage

Use Cases:
- Real-time conversation monitoring
- Message notification delivery
- Thread status tracking (archived, closed)
- Participant changes (joined, left)
- Build messaging app UIs

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `active` | `boolean = true` | No | Whether subscription is currently active. |
| `createdAt` | `utcDateTime` | Yes | Timestamp when subscription was created. |
| `events` | `string[]` | No | Event types to subscribe to. |
| `expiresAt` | `utcDateTime` | No | Subscription expiration time. |
| `failureCount` | `int32 = 0` | No | Number of consecutive failed delivery attempts. |
| `lastDeliveredAt` | `utcDateTime` | No | Timestamp of last successful webhook delivery. |
| `messageFilters` | `MessageFilters` | No | Message filters for webhook subscriptions. |
| `metadata` | `Record<unknown>` | No | Custom metadata for subscription. |
| `subscriptionId` | `string` | Yes | Unique subscription identifier. |
| `threadId` | `string` | Yes | Thread being subscribed to. |
| `webhookSecret` | `string` | No | Secret for webhook signature validation. |
| `webhookUrl` | `url` | Yes | Webhook URL to POST notifications to. |

### Examples

#### Subscribe to all thread activity

```http
POST /threads/{threadId}/subscriptions
{
"webhookUrl": "https://example.com/webhook",
"webhookSecret": "secret_xyz"
}
```

#### Subscribe to user messages only

```http
POST /threads/{threadId}/subscriptions
{
"webhookUrl": "https://example.com/webhook",
"events": ["message.created", "message.completed"],
"messageFilters": {
"roles": ["user"]
}
}
```

---
<!-- GENERATED_END -->