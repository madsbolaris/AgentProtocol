# DELETE /threads/{threadId}/watch/{agentId}

Unsubscribe agent from watching thread.

<!-- GENERATED_START -->

## DELETE /threads/{threadId}/watch/{agentId}

Unsubscribe agent from watching thread.

### Usage

Use Cases:
- Remove agent from thread
- Temporary disable agent participation
- Clean up after thread completion

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |
| `agentId` | `string` | Yes |  |

### Responses

**204**: No Content
Watch deleted (agent no longer watching)

**404**: Not Found
Thread, agent, or watch not found

REQUEST:
- DELETE /threads/{threadId}/watch/{agentId}

### Examples

#### Example 1

```http
DELETE /threads/thread-123/watch/agent-support
```

---

<!-- GENERATED_END -->