# DELETE /threads/{threadId}

{

<!-- GENERATED_START -->

## DELETE /threads/{threadId}

{ "active": false } ```

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Response

- **204 No Content:** Resource deleted successfully
- **404 Not Found:** Resource not found
- **409 Conflict:** Resource conflict

### Examples

#### Example 1

```http
PATCH /threads/thread-123/subscriptions/sub-456
Content-Type: application/json

{
"active": false
}
```

---

<!-- GENERATED_END -->