# GET {runId}/wait

Wait for run completion (blocking).

<!-- GENERATED_START -->

## GET {runId}/wait

Wait for run completion (blocking).

### Usage

Use Cases:
- Background runs: Create run, return runId, client waits separately
- Async workflows: Trigger run, do other work, wait for completion
- Simple clients: No SSE support, prefer blocking wait over polling


Rationale:
- Polling alternative for clients without SSE support
- Background run pattern: POST /runs → GET /runs/{id}/wait
- Simplified response (no need to poll GET /runs/{id} repeatedly)

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | `"json" | "xml"` | No |  |

### Responses

**200**: OK
RunWaitResponse with final run state

**404**: Not Found
Run not found

**408**: Request Timeout
Run exceeded time limit

REQUEST:
- GET /runs/{runId}/wait
- Query: format=xml for XML representation (pretty-printed)

**409**: Conflict
Run already completed (returns completed state)

---

<!-- GENERATED_END -->