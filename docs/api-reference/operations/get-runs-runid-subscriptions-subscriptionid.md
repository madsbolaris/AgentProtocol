# GET /runs/{runId}/subscriptions/{subscriptionId}

Get a specific subscription.

<!-- GENERATED_START -->

## GET /runs/{runId}/subscriptions/{subscriptionId}

Get a specific subscription.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Responses

**200**: OK
Subscription details

**404**: Not Found
Run or subscription not found

REQUEST:
- GET /runs/{runId}/subscriptions/{subscriptionId}

---

<!-- GENERATED_END -->