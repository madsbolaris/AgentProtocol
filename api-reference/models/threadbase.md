# ThreadBase

Thread Base

<!-- GENERATED_START -->

## ThreadBase

Thread Base
Common properties shared by all thread types.
SHARED BY:
- Thread: Runtime conversation threads
- EvalThread: Evaluation test threads
PROPERTIES:
- threadId: Unique identifier
- status: Lifecycle state (active, closed, archived)
- createdAt: Creation timestamp
- metadata: Custom key-value data

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `createdAt` | `utcDateTime` | Yes | Timestamp when thread was created. |
| `metadata` | `Record<unknown>` | No | Custom metadata for the thread. |
| `status` | `ThreadStatus` | No | Thread lifecycle status. |
| `threadId` | `string` | Yes | Unique thread identifier. |

---
<!-- GENERATED_END -->