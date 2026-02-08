# GET /agents/{agentId}/subscriptions

List subscriptions for an agent.

<!-- GENERATED_START -->

## GET /agents/{agentId}/subscriptions

List subscriptions for an agent.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of subscriptions

**404**: Not Found
Agent not found

REQUEST:
- GET /agents/{agentId}/subscriptions?after={subscriptionId}&limit={limit}

---

<!-- GENERATED_END -->