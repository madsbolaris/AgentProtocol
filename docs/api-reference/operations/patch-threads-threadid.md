# PATCH /threads/{threadId}

<!-- GENERATED_START -->

## PATCH /threads/{threadId}

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Request Body

**Type:** `Thread`

### Responses

**200**: OK
Array of messages

**404**: Not Found
Thread not found

### Examples

#### Example 1

```http
GET /threads/thread-123/messages
```

#### Example 2

```http
GET /threads/thread-123/messages?branch=msg-2b
```

---

<!-- GENERATED_END -->