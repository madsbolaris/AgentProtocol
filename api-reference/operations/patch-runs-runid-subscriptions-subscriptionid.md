# PATCH /runs/{runId}/subscriptions/{subscriptionId}

<!-- GENERATED_START -->

## PATCH /runs/{runId}/subscriptions/{subscriptionId}

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Request Body

**Type:** `RunSubscription`

### Responses

**200**: OK
Subscription details

**404**: Not Found
Agent or subscription not found

### Examples

#### Example 1

```http
GET /agents/agent-123/subscriptions/sub-456
```

---

<!-- GENERATED_END -->