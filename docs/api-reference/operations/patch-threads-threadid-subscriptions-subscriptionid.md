# PATCH /threads/{threadId}/subscriptions/{subscriptionId}

Update a subscription.

<!-- GENERATED_START -->

## PATCH /threads/{threadId}/subscriptions/{subscriptionId}

Update a subscription.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Request Body

**Type:** `ThreadSubscription`

### Responses

**200**: OK
Updated subscription

**404**: Not Found
Thread or subscription not found

REQUEST:
- PATCH /threads/{threadId}/subscriptions/{subscriptionId}
- Body: Partial ThreadSubscription with fields to update

---

<!-- GENERATED_END -->