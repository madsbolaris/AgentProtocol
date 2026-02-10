# GET {threadId}/messages/{messageId}

<!-- GENERATED_START -->

## GET {threadId}/messages/{messageId}

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |
| `messageId` | `string` | Yes |  |

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `format` | `"json" | "xml"` | No |  |

### Responses

**200**: OK
Message details

**404**: Not Found
Thread or message not found

### Examples

#### Example 1

```http
GET /threads/thread-123/messages/msg-456
```

#### ```http

```json
{
"messageId": "msg-456",
"role": "assistant",
"contents": [
{
"kind": "text",
"text": "Here's the analysis you requested..."
}
],
"createdAt": "2026-02-07T10:00:00Z"
}
```

---

<!-- GENERATED_END -->