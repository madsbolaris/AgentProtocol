# RunSubscription

Run Subscription - Webhook Notification Registration

<!-- GENERATED_START -->

## RunSubscription

Run Subscription - Webhook Notification Registration

### Usage

Use Cases:
- Monitor long-running executions
- Track run lifecycle for orchestration
- Get notified when specific runs complete
- Build run activity dashboards

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
| `runId` | `string` | Yes | Run being subscribed to. |
| `subscriptionId` | `string` | Yes | Unique subscription identifier. |
| `webhookSecret` | `string` | No | Secret for webhook signature validation. |
| `webhookUrl` | `url` | Yes | Webhook URL to POST notifications to. |

### Examples

#### Subscribe to run completion

```http
POST /runs/{runId}/subscriptions
{
"webhookUrl": "https://example.com/webhook",
"events": ["run.completed", "run.failed"]
}
```

---
<!-- GENERATED_END -->