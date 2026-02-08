# GET /threads/{threadId}/stream

<!-- GENERATED_START -->

## GET /threads/{threadId}/stream

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `events` | `string` | No |  |
| `since` | `utcDateTime` | No |  |
| `roles` | `string` | No |  |
| `userIds` | `string` | No |  |
| `agentIds` | `string` | No |  |
| `contentTypes` | `string` | No |  |
| `audience` | `string` | No |  |

### Response

- **200 OK:** Operation completed successfully
- **404 Not Found:** Resource not found

### Examples

#### Example 1

```http
GET /threads/thread-123/subscriptions?limit=50
```

---

<!-- GENERATED_END -->