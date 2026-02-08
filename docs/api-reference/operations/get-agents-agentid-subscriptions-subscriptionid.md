# GET /agents/{agentId}/subscriptions/{subscriptionId}

Get a specific subscription.

<!-- GENERATED_START -->

## GET /agents/{agentId}/subscriptions/{subscriptionId}

Get a specific subscription.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Responses

**200**: OK
Subscription details

**404**: Not Found
Agent or subscription not found

REQUEST:
- GET /agents/{agentId}/subscriptions/{subscriptionId}

---

<!-- GENERATED_END -->