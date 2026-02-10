# GET /threads/{threadId}/subscriptions/{subscriptionId}

Get a specific subscription.

<!-- GENERATED_START -->

## GET /threads/{threadId}/subscriptions/{subscriptionId}

Get a specific subscription.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Responses

**200**: OK
Subscription details

**404**: Not Found
Thread or subscription not found

REQUEST:
- GET /threads/{threadId}/subscriptions/{subscriptionId}

---

<!-- GENERATED_END -->