# GET /runs/{runId}

Get a specific run by ID.

<!-- GENERATED_START -->

## GET /runs/{runId}

Get a specific run by ID.

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
Run details

**404**: Not Found
Run not found

REQUEST:
- GET /runs/{runId}
- Query: format=xml for XML representation (pretty-printed)

---

<!-- GENERATED_END -->