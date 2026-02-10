# POST {threadId}/copy

RESTful resource nesting for thread-scoped run listing

<!-- GENERATED_START -->

## POST {threadId}/copy

RESTful resource nesting for thread-scoped run listing

### Usage

RESTful resource nesting for thread-scoped run listing.

Use Cases:
- View conversation history (all runs in thread)
- Run debugging and analytics for specific thread
- Natural API navigation (threads → runs)

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Request Body

**Type:** `ThreadCopyRequest`

### Responses

**200**: OK
Array of runs in thread

**404**: Not Found
Thread not found

### Examples

#### Example 1

```http
GET /threads/thread-123/runs?limit=50
```

#### ```http

```json
[
{
"runId": "run-abc123",
"threadId": "thread-123",
"status": "completed",
"createdAt": "2026-02-06T10:00:00Z",
"completedAt": "2026-02-06T10:00:05Z"
},
{
"runId": "run-def456",
"threadId": "thread-123",
"status": "completed",
"createdAt": "2026-02-06T10:01:00Z",
"completedAt": "2026-02-06T10:01:03Z"
}
]
```

#### Example 3

```http
GET /threads/thread-123/runs?status=completed&limit=100
```

#### ```http

```http
# Page 1
GET /threads/thread-123/runs?limit=100

# Page 2
GET /threads/thread-123/runs?after=run-abc123&limit=100
```

---

<!-- GENERATED_END -->