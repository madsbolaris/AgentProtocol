# GET /runs

List runs with optional filtering.

<!-- GENERATED_START -->

## GET /runs

List runs with optional filtering.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | No |  |
| `agentId` | `string` | No |  |
| `status` | `RunStatus` | No |  |
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of runs

REQUEST:
- GET /runs?threadId={threadId}&agentId={agentId}&status={status}&after={runId}&limit={limit}

---

<!-- GENERATED_END -->