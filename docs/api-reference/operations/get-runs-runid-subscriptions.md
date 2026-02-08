# GET /runs/{runId}/subscriptions

List subscriptions for a run.

<!-- GENERATED_START -->

## GET /runs/{runId}/subscriptions

List subscriptions for a run.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `after` | `string` | No |  |
| `limit` | `int32 = 100` | No |  |

### Responses

**200**: OK
Array of subscriptions

**404**: Not Found
Run not found

REQUEST:
- GET /runs/{runId}/subscriptions?after={subscriptionId}&limit={limit}

---

<!-- GENERATED_END -->