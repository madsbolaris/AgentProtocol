# POST stream

Create and stream agent run (non-blocking with SSE).

<!-- GENERATED_START -->

## POST stream

Create and stream agent run (non-blocking with SSE).

### Usage

Use Cases:
- Chat UI with streaming text
- Interactive agents with real-time responses
- Simple streaming without managing runId


Rationale:
- Single request for create + stream (simpler client code)
- No need to track runId separately for simple streaming scenarios
- Common pattern for chat UIs with streaming responses

### Query Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `events` | `string` | No |  |
| `since` | `utcDateTime` | No |  |

### Request Body

**Type:** `Run`

### Responses

**200**: OK
SSE stream with run events

**400**: Bad Request
Invalid input

**404**: Not Found
Thread or agent not found

**500**: Internal Server Error
Execution error

REQUEST:
- POST /runs/stream
- Body: Run with input messages and agent configuration

---

<!-- GENERATED_END -->