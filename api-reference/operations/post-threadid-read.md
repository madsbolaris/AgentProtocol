# POST {threadId}/read

Mark thread as read.

<!-- GENERATED_START -->

## POST {threadId}/read

Mark thread as read.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Responses

**200**: OK
Thread with unreadCount reset to 0

**404**: Not Found
Thread not found

REQUEST:
- POST /threads/{threadId}/read

---

<!-- GENERATED_END -->