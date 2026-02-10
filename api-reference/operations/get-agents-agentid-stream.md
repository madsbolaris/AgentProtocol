# GET /agents/{agentId}/stream

Stream agent events (all activity across all runs).

<!-- GENERATED_START -->

## GET /agents/{agentId}/stream

Stream agent events (all activity across all runs).

### Usage

Use Cases:
- Agent monitoring dashboard
- Debugging agent behavior across multiple threads
- Analytics and usage tracking
- Real-time agent activity feeds

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `events` | `string` | No |  |
| `since` | `utcDateTime` | No |  |
| `threadId` | `string` | No |  |
| `roles` | `string` | No |  |
| `userIds` | `string` | No |  |
| `contentTypes` | `string` | No |  |
| `audience` | `string` | No |  |

### Responses

**200**: OK
SSE stream with agent events

**404**: Not Found
Agent not found

REQUEST:
- GET /agents/{agentId}/stream

---

<!-- GENERATED_END -->