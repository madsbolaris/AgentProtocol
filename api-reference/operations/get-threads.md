# GET /threads

List threads with optional filtering.

<!-- GENERATED_START -->

## GET /threads

List threads with optional filtering.

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `updatedSince` | `utcDateTime` | No |  |
| `status` | `ThreadStatus` | No |  |
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of threads

REQUEST:
- GET /threads?updatedSince={timestamp}&status={status}&after={threadId}&limit={limit}

---

<!-- GENERATED_END -->