# POST /threads/{threadId}/subscriptions

Create a webhook subscription.

<!-- GENERATED_START -->

## POST /threads/{threadId}/subscriptions

Create a webhook subscription.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Request Body

**Type:** `ThreadSubscription`

### Responses

**201**: Created
Subscription created

**400**: Bad Request
Invalid webhookUrl or configuration

**404**: Not Found
Thread not found

REQUEST:
- POST /threads/{threadId}/subscriptions
- Body: ThreadSubscription with webhookUrl and optional config

---

<!-- GENERATED_END -->