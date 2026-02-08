# DELETE /threads/{threadId}/subscriptions/{subscriptionId}

Delete a subscription.

<!-- GENERATED_START -->

## DELETE /threads/{threadId}/subscriptions/{subscriptionId}

Delete a subscription.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Responses

**204**: No Content
Subscription deleted

**404**: Not Found
Thread or subscription not found

REQUEST:
- DELETE /threads/{threadId}/subscriptions/{subscriptionId}

---

<!-- GENERATED_END -->