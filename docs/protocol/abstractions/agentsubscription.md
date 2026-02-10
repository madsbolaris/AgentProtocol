# AgentSubscription

<!-- GENERATED_START -->

## AgentSubscription

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `active` | `boolean = true` | No | Whether subscription is currently active. |
| `agentId` | `string` | Yes | Agent being subscribed to. |
| `createdAt` | `utcDateTime` | Yes | Timestamp when subscription was created. |
| `events` | `string[]` | No | Event types to subscribe to. |
| `expiresAt` | `utcDateTime` | No | Subscription expiration time. |
| `failureCount` | `int32 = 0` | No | Number of consecutive failed delivery attempts. |
| `lastDeliveredAt` | `utcDateTime` | No | Timestamp of last successful webhook delivery. |
| `messageFilters` | `MessageFilters` | No | Message filters for webhook subscriptions. |
| `metadata` | `Record<unknown>` | No | Custom metadata for subscription. |
| `subscriptionId` | `string` | Yes | Unique subscription identifier. |
| `threadId` | `string` | No | Filter by specific thread. |
| `webhookSecret` | `string` | No | Secret for webhook signature validation. |
| `webhookUrl` | `url` | Yes | Webhook URL to POST notifications to. |

---
<!-- GENERATED_END -->