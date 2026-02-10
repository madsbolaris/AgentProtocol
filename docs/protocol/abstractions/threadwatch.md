# ThreadWatch

Thread Watch - Agent Participation Tracking

<!-- GENERATED_START -->

## ThreadWatch

Thread Watch - Agent Participation Tracking

### Usage

Use Cases:
- Support agents: Watch support threads for user messages
- Monitoring agents: Watch threads for specific content types
- Multi-agent: Multiple agents watching same thread with different conditions

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `activationCount` | `int32 = 0` | No | Number of runs created by this watch. |
| `active` | `boolean = true` | No | Whether watch is currently active. |
| `agentId` | `string` | Yes | Agent watching the thread. |
| `createdAt` | `utcDateTime` | Yes | Timestamp when watch was created. |
| `lastActivatedAt` | `utcDateTime` | No | Timestamp of last activation (last time agent created run for this thread). |
| `metadata` | `Record<unknown>` | No | Custom metadata for watch. |
| `threadId` | `string` | Yes | Thread being watched. |
| `watchId` | `string` | Yes | Unique watch identifier. |

---
<!-- GENERATED_END -->