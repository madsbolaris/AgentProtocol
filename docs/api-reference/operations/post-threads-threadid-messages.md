# POST /threads/{threadId}/messages

Add a message to a thread.

<!-- GENERATED_START -->

## POST /threads/{threadId}/messages

Add a message to a thread.

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Request Body

**Type:** `ChatMessage`

### Responses

**201**: Created
Message added

**400**: Bad Request
Invalid message

**404**: Not Found
Thread not found

**409**: Conflict
Message ID already exists (if client-provided)

REQUEST:
- POST /threads/{threadId}/messages
- Body: ChatMessage to add to thread

---

<!-- GENERATED_END -->