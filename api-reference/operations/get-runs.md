# GET /runs

List runs with optional filtering.

<!-- GENERATED_START -->

## GET /runs

List runs with optional filtering.

### Usage

Retrieve a paginated list of runs with optional filters.
Use for monitoring run history, filtering by thread/agent/status, or pagination.

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

### Examples

#### List all runs

```http
GET /runs
```

#### Filter by thread

```http
GET /runs?threadId=thread_123&limit=10
```

---

<!-- GENERATED_END -->