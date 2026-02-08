# DELETE /agents/{agentId}/subscriptions/{subscriptionId}

{

<!-- GENERATED_START -->

## DELETE /agents/{agentId}/subscriptions/{subscriptionId}

{ "status": "closed" } ```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `agentId` | `string` | Yes |  |
| `subscriptionId` | `string` | Yes |  |

### Responses

**200**: OK
Updated thread

**404**: Not Found
Thread not found

**409**: Conflict
Update conflict

### Examples

#### Example 1

```http
PATCH /threads/thread-123
Content-Type: application/json

{
"status": "closed"
}
```

---

<!-- GENERATED_END -->