# GET {threadId}/runs

List runs within the thread.

<!-- GENERATED_START -->

## GET {threadId}/runs

List runs within the thread.

### Usage

Use Cases:
- Conversation history: View all agent interactions in thread
- Run debugging: Inspect all executions for specific thread
- Analytics: Analyze run patterns per conversation


Rationale:
- REST conventions: Resource nesting (threads → runs)
- Discoverability: Natural API navigation
- Thread-centric view: All runs for conversation in one call
- LangChain alignment: Industry standard pattern

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | `RunStatus` | No |  |
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of runs in thread

**404**: Not Found
Thread not found

REQUEST:
- GET /threads/{threadId}/runs?status={status}&after={runId}&limit={limit}

---

<!-- GENERATED_END -->