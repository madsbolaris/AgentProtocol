# DELETE /runs/{runId}/subscriptions/{subscriptionId}

{

<!-- GENERATED_START -->

## DELETE /runs/{runId}/subscriptions/{subscriptionId}

{ "active": false } ```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `runId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Responses

**200**: OK
Updated subscription

**404**: Not Found
Agent or subscription not found

### Examples

#### Example 1

```http
PATCH /agents/agent-123/subscriptions/sub-456
Content-Type: application/json

{
"active": false
}
```

---

<!-- GENERATED_END -->