# POST {threadId}/watch

Subscribe agent to watch thread.

<!-- GENERATED_START -->

## POST {threadId}/watch

Subscribe agent to watch thread.

### Usage

Use Cases:
- Support agents: Watch support threads for user messages
- Monitoring agents: Watch threads for specific content types
- Multi-agent: Multiple agents watching same thread with different conditions

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Request Body

**Type:** `{ agentId: string }`

### Responses

**201**: Created
ThreadWatch created (agent now watching thread)

**400**: Bad Request
Agent missing AutoResponseConfig

**404**: Not Found
Thread or agent not found

**409**: Conflict
Agent already watching this thread

REQUEST:
- POST /threads/{threadId}/watch
- Body: { agentId: string }

### Examples

#### Example 1

```http
POST /threads/thread-123/watch
{ "agentId": "agent-support" }
```

---

<!-- GENERATED_END -->