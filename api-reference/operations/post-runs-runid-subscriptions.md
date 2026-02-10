# POST /runs/{runId}/subscriptions

Create a webhook subscription for a run.

<!-- GENERATED_START -->

## POST /runs/{runId}/subscriptions

Create a webhook subscription for a run.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |

### Request Body

**Type:** `RunSubscription`

### Responses

**201**: Created
Subscription created

**400**: Bad Request
Invalid webhookUrl or configuration

**404**: Not Found
Run not found

REQUEST:
- POST /runs/{runId}/subscriptions
- Body: RunSubscription with webhookUrl and optional config

---

<!-- GENERATED_END -->