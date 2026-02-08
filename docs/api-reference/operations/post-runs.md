# POST /runs

Create and execute an agent run.

<!-- GENERATED_START -->

## POST /runs

Create and execute an agent run.

### Request Body

**Type:** `Run`

### Responses

**201**: Created
Run created and started

**400**: Bad Request
Invalid input

**404**: Not Found
Thread or agent not found

**500**: Internal Server Error
Execution error

REQUEST:
- POST /runs
- Body: Run with input messages, agent configuration, and options

---

<!-- GENERATED_END -->