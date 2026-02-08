# RunWaitResponse

Run Wait Response

<!-- GENERATED_START -->

## RunWaitResponse

Run Wait Response
Response model for POST /runs/wait and GET /runs/{runId}/wait
Returns final run state after completion (blocking until done).
WAIT PATTERN:
- POST /runs/wait: Create ephemeral run and wait for completion
- GET /runs/{runId}/wait: Wait for existing run to complete
- Both return this response model when run finishes
DIFFERENCE FROM Run:
- Run: Full model with create/read visibility annotations
- RunWaitResponse: Simplified read-only completion state

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `completedAt` | `utcDateTime` | No | Timestamp when run finished. |
| `createdAt` | `utcDateTime` | Yes | Timestamp when run was created. |
| `error` | `RunError` | No | Error details if run failed or completed incompletely. |
| `output` | `ChatMessage[]` | Yes | Messages generated during the run. |
| `runId` | `string` | Yes | Unique identifier for the completed run. |
| `status` | `RunStatus` | Yes | Final run status (completed, failed, cancelled, timeout, incomplete). |
| `threadId` | `string` | No | Thread ID if run was stateful (null for ephemeral runs). |
| `usage` | `CompletionUsage` | No | Token usage statistics. |

---
<!-- GENERATED_END -->