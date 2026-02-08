# GET /threads/{threadId}/watch

List agents watching thread.

<!-- GENERATED_START -->

## GET /threads/{threadId}/watch

List agents watching thread.

### Usage

Use Cases:
- View which agents are watching thread
- Check agent participation status
- Monitor auto-response activity

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Responses

**200**: OK
Array of ThreadWatch records

**404**: Not Found
Thread not found

REQUEST:
- GET /threads/{threadId}/watch

### Examples

#### Example 1

```http
GET /threads/thread-123/watch
// Returns: [
//   { "watchId": "watch-456", "agentId": "agent-support", "active": true, ... },
//   { "watchId": "watch-789", "agentId": "agent-monitor", "active": true, ... }
// ]
```

---

<!-- GENERATED_END -->