# PATCH /agents/{agentId}/subscriptions/{subscriptionId}

<!-- GENERATED_START -->

## PATCH /agents/{agentId}/subscriptions/{subscriptionId}

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Request Body

**Type:** `AgentSubscription`

### Responses

**200**: OK
Thread details with messages

**404**: Not Found
Thread not found

### Examples

#### Example 1

```http
GET /threads/thread-123
```

---

<!-- GENERATED_END -->