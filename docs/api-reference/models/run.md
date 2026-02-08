# Run

<!-- GENERATED_START -->

## Run

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `agent` | `AgentDefinition` | No | Agent configuration for this run. |
| `agentId` | `string` | Yes | Unique identifier for the agent that processed this run. |
| `cancellationReason` | `string` | No | Reason for cancellation (if provided by user). |
| `cancelledAt` | `utcDateTime` | No | Timestamp when the run was cancelled (if status=cancelled). |
| `completedAt` | `utcDateTime` | No | Timestamp when the run finished (completed, failed, or cancelled). |
| `createdAt` | `utcDateTime` | Yes | Timestamp when the run was created. |
| `error` | `RunError` | No | Error details if run failed or completed incompletely. |
| `input` | `ChatMessage[]` | Yes | Input messages that started this run. |
| `journalId` | `string` | No | Optional identifier for the agent's journal. |
| `metadata` | `Record<unknown>` | No | Custom metadata for the run. |
| `options` | `RunOptions` | No | Configuration options for run execution. |
| `output` | `ChatMessage[]` | Yes | Messages generated during this run. |
| `overrides` | `PromptAgent` | No | Optional overrides for existing agent configuration. |
| `rawRepresentation` | `unknown` | No | Underlying provider representation. |
| `runId` | `string` | Yes | Unique identifier for this run. |
| `status` | `RunStatus` | Yes | Current lifecycle status of the run. |
| `threadCleanup` | `ThreadCleanup = ThreadCleanup.keep` | No | Thread cleanup strategy for this run. |
| `threadId` | `string` | No | Optional identifier for the conversation thread. |
| `updatedAt` | `utcDateTime` | Yes | Timestamp of last status update. |
| `usage` | `CompletionUsage` | Yes | Token usage statistics for this run. |
| `userId` | `string` | No | User who initiated this run. |
| `webhook` | `url` | No | Webhook URL for run completion notification. |

---
<!-- GENERATED_END -->