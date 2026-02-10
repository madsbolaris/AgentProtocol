# POST {threadId}/runs

Create a run within the thread context.

<!-- GENERATED_START -->

## POST {threadId}/runs

Create a run within the thread context.

### Usage

Use Cases:
- Multi-turn conversations: POST /threads/{id}/runs for each turn
- Explicit thread context: More discoverable than threadId in body
- RESTful clients: Prefer nested resources over query params


Rationale:
- REST conventions: Resource nesting (threads → runs)
- Discoverability: Clearer API surface
- Context clarity: Explicit thread scope
- LangChain alignment: Industry standard pattern

### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `threadId` | `string` | Yes |  |

### Request Body

**Type:** `Run`

### Responses

**201**: Created
Run created in thread

**400**: Bad Request
Invalid run configuration

REQUEST:
- POST /threads/{threadId}/runs
- Body: Run with agent and input configuration

**404**: Not Found
Thread not found

---

<!-- GENERATED_END -->