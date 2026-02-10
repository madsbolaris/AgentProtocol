# GET {runId}/stream

Stream run output (reconnectable).

<!-- GENERATED_START -->

## GET {runId}/stream

Stream run output (reconnectable).

### Usage

Use Cases:
- Reconnection after network failure
- Multiple observers: Dashboard + CLI both streaming same run
- Late joining: Start run, navigate away, return and stream remaining output


Rationale:
- Reconnection pattern for resilient streaming
- Background run pattern: POST /runs → GET /runs/{id}/stream
- Multiple clients can stream same run (monitoring, debugging)

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `events` | `string` | No |  |
| `since` | `utcDateTime` | No |  |

### Responses

**200**: OK
SSE stream with run events

**404**: Not Found
Run not found

REQUEST:
- GET /runs/{runId}/stream

---

<!-- GENERATED_END -->