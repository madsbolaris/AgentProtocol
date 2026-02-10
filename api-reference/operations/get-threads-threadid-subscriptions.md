# GET /threads/{threadId}/subscriptions

List subscriptions for a thread.

<!-- GENERATED_START -->

## GET /threads/{threadId}/subscriptions

List subscriptions for a thread.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of subscriptions

**404**: Not Found
Thread not found

REQUEST:
- GET /threads/{threadId}/subscriptions?after={subscriptionId}&limit={limit}

---

<!-- GENERATED_END -->