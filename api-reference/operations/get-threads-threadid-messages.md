# GET /threads/{threadId}/messages

Get messages from a thread.

<!-- GENERATED_START -->

## GET /threads/{threadId}/messages

Get messages from a thread.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `branch` | `string` | No |  |
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of messages

**404**: Not Found
Thread not found

REQUEST:
- GET /threads/{threadId}/messages?branch={messageId}&after={messageId}&limit={limit}

---

<!-- GENERATED_END -->