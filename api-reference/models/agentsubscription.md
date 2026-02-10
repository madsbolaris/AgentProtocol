# AgentSubscription

Agent Subscription - Webhook Notification Registration

<!-- GENERATED_START -->

## AgentSubscription

Agent Subscription - Webhook Notification Registration

### Usage

Use Cases:
- Monitor agent activity across all threads
- Track agent configuration changes
- Build agent analytics dashboards
- Debug agent behavior in production
- Track agent errors and failures

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

### Examples

#### Subscribe to agent errors

```http
POST /agents/{agentId}/subscriptions
{
"webhookUrl": "https://example.com/webhook",
"events": ["run.failed", "agent.error"]
}
```

---
<!-- GENERATED_END -->