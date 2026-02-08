# Run Operations

Run operations for creating, managing, and monitoring agent executions.

## Overview

Runs represent individual agent execution instances. Each run has a lifecycle with states like `queued`, `in_progress`, `requires_action`, `completed`, `failed`, etc.

The Run API provides operations for:

- **Run Creation**: Create runs with agent configuration and input
- **Run Monitoring**: Wait for completion or stream events
- **Run Control**: Cancel, submit tool outputs, submit user input, submit auth
- **Run Subscriptions**: Subscribe to run-level events via webhooks

**TypeSpec Source**: [execution.tsp](../../typespec/execution.tsp), [routes.tsp](../../typespec/routes.tsp)

---

## Core Operations

### POST /runs

Create a new run (async).

**Request Body**: [Run](../models/Run.md)

**Response**: Created run with `runId` and initial status

**Example**:
```http
POST /runs
Content-Type: application/json

{
  "agentId": "agent-123",
  "threadId": "thread-456",
  "input": [{
    "role": "user",
    "contents": [{"kind": "text", "text": "Hello!"}]
  }]
}
```

**See**: [post-runs.md](./post-runs.md)

---

### POST /runs/wait

Create run and wait for completion (blocking).

**Request Body**: [Run](../models/Run.md)

**Response**: [RunWaitResponse](../models/RunWaitResponse.md) with completion status

**Example**:
```http
POST /runs/wait
Content-Type: application/json

{
  "agentId": "agent-123",
  "input": [{
    "role": "user",
    "contents": [{"kind": "text", "text": "What is 2+2?"}]
  }],
  "threadCleanup": "delete"
}
```

**See**: [post-runs-wait.md](./post-runs-wait.md)

---

### GET /runs/{runId}

Get run details.

**Response**: [Run](../models/Run.md)

**See**: [get-runs-runid.md](./get-runs-runid.md)

---

### GET /runs/{runId}/wait

Wait for existing run to complete (blocking).

**Response**: [RunWaitResponse](../models/RunWaitResponse.md)

**See**: [get-runs-runid-wait.md](./get-runs-runid-wait.md)

---

### GET /runs/{runId}/stream

Stream run events (reconnectable).

**Query Parameters**:
- `events?: string` - Event types to include
- `since?: utcDateTime` - Only events after timestamp

**Response**: Server-Sent Events (SSE) stream

**See**: [get-runs-runid-stream.md](./get-runs-runid-stream.md)

---

## Control Operations

### POST /runs/{runId}/cancel

Cancel a running execution.

**Request Body** (optional):
```json
{
  "action": "interrupt" | "rollback",
  "reason": "User requested cancellation"
}
```

**Response**: Updated [Run](../models/Run.md) with `cancelled` status

**See**: [post-runs-runid-cancel.md](./post-runs-runid-cancel.md)

---

### POST /runs/{runId}/submit_tool_outputs

Submit tool execution results (HITL - tool approval).

**Request Body**:
```json
{
  "tool_outputs": [{
    "callId": "call_123",
    "result": "Search results..."
  }]
}
```

**Response**: Updated [Run](../models/Run.md) resuming execution

**See**: [post-runs-runid-submit-tool-outputs.md](./post-runs-runid-submit-tool-outputs.md)

---

### POST /runs/{runId}/submit_input

Submit user input (HITL - input collection).

**Request Body**:
```json
{
  "input": [{
    "role": "user",
    "contents": [{"kind": "text", "text": "User response"}]
  }]
}
```

**Response**: Updated [Run](../models/Run.md) resuming execution

**See**: [post-runs-runid-submit-input.md](./post-runs-runid-submit-input.md)

---

### POST /runs/{runId}/submit_auth

Submit authentication credentials (HITL - authentication).

**Request Body**:
```json
{
  "connection": {
    "kind": "reference",
    "connectionId": "conn-gmail-user1"
  }
}
```

**Response**: Updated [Run](../models/Run.md) resuming execution

**See**: [post-runs-runid-submit-auth.md](./post-runs-runid-submit-auth.md)

---

## Subscription Operations

### GET /runs/{runId}/subscriptions

List webhook subscriptions for run events.

**See**: [get-runs-runid-subscriptions.md](./get-runs-runid-subscriptions.md)

---

### POST /runs/{runId}/subscriptions

Create webhook subscription for run events.

**Request Body**: [RunSubscription](../models/RunSubscription.md)

**See**: [post-runs-runid-subscriptions.md](./post-runs-runid-subscriptions.md)

---

### GET /runs/{runId}/subscriptions/{subscriptionId}

Get specific run subscription.

**See**: [get-runs-runid-subscriptions-subscriptionid.md](./get-runs-runid-subscriptions-subscriptionid.md)

---

### DELETE /runs/{runId}/subscriptions/{subscriptionId}

Delete run subscription.

**See**: [delete-runs-runid-subscriptions-subscriptionid.md](./delete-runs-runid-subscriptions-subscriptionid.md)

---

## Related Resources

- [Run Model](../models/Run.md)
- [RunStatus Enum](../models/RunStatus.md)
- [RunWaitResponse Model](../models/RunWaitResponse.md)
- [Thread Operations](./threads.md)
- [Agent Operations](./agents.md)

## Related Specifications

- [Run Lifecycle Specification](../../specifications/run-lifecycle.md)
- [Tool Execution Specification](../../specifications/tool-execution.md)
- [Human-in-the-Loop Guide](../../guides/human-in-loop.md)
