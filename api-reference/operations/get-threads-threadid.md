# GET /threads/{threadId}

Get a specific thread by ID.

<!-- GENERATED_START -->

## GET /threads/{threadId}

Get a specific thread by ID.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | `"json" | "xml"` | No |  |

### Responses

**200**: OK
Thread details with messages

**404**: Not Found
Thread not found

REQUEST:
- GET /threads/{threadId}
- Query: format=xml for XML representation (pretty-printed)

---

<!-- GENERATED_END -->