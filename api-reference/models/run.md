# Run

Run - Execution Instance

<!-- GENERATED_START -->

## Run

Run - Execution Instance
MAF MAPPING:
- Run.input → ExecuteAsync prompt parameter (ChatMessage[])
- Run.agent → ExecuteAsync with inline agent configuration
- Run.options → ExecuteAsync ChatOptions parameter
- Run.output → ExecuteAsync returns ChatCompletion with Messages
- Run.usage → ChatCompletion.Usage (token counts)
KEY DESIGN DECISIONS:
1. Adopted 11-state lifecycle (expanded from OpenAI's 8 states and Azure's 5 states)
- Added: queued, requires_action, input_required, auth_required, cancelling, timeout
2. Added threadCleanup from LangChain Agent Protocol (ephemeral vs stateful runs)
3. Made threadId optional (supports stateless execution without thread)
M365 REQUIREMENTS:
- Supports orchestration pipeline tracking (runId, status, timestamps)
- Enables conversation-scoped execution (threadId)
- Tracks token usage for cost management (usage)
- Stores guardrail results for compliance (input/output/tool guardrails)
PROACTIVE MESSAGING SUPPORT:
Runs can be triggered by user messages OR external events:
1. User-Initiated Run (Traditional):
POST /runs
{ threadId: "...", input: [{ role: "user", contents: [{ kind: "text", text: "Hello" }] }] }
2. Agent-Initiated Run (Proactive):
External event (timer, webhook, system alert) →
POST /threads/{threadId}/messages (creates EventContent message with role="channel") →
POST /runs { threadId: "...", input: [] } (agent processes trigger event from thread) →
POST to ThreadSubscription.webhookUrl (notify client of completion)
SEE ALSO:
- ThreadSubscription: Webhook registration for proactive notifications
- EventContent (messages.tsp): External trigger events with role="channel"
- Thread.lastActivityAt: Polling support for clients without webhooks
Key Capabilities:
- 11-state lifecycle (queued → in_progress → completed/failed/cancelled)
- Stateful execution with thread persistence (threadId)
- Stateless/ephemeral execution (threadId optional, threadCleanup=delete)
- Token usage tracking for cost management
- Webhook notifications for async completion
- Proactive messaging support (user-initiated or event-triggered)
Execution Modes:
- Synchronous: POST /runs/wait (blocks until complete)
- Asynchronous: POST /runs (returns immediately, poll or webhook)
- Ephemeral: POST /runs/wait with threadCleanup=delete (no persistence)
M365 Integration:
- Links to Thread for conversation tracking
- Links to Agent Journal for cross-conversation memory
- Stores guardrail results for compliance

### Usage

Core execution model representing a single agent invocation within a conversation.
Tracks lifecycle, input/output messages, token usage, and execution results.
Supports both stateful (with thread) and stateless (without thread) execution.

Key Capabilities:
- 11-state lifecycle (queued → in_progress → completed/failed/cancelled)
- Stateful execution with thread persistence (threadId)
- Stateless/ephemeral execution (threadId optional, threadCleanup=delete)
- Token usage tracking for cost management
- Webhook notifications for async completion
- Proactive messaging support (user-initiated or event-triggered)

Execution Modes:
- Synchronous: POST /runs/wait (blocks until complete)
- Asynchronous: POST /runs (returns immediately, poll or webhook)
- Ephemeral: POST /runs/wait with threadCleanup=delete (no persistence)

M365 Integration:
- Links to Thread for conversation tracking
- Links to Agent Journal for cross-conversation memory
- Stores guardrail results for compliance

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

### Examples

#### Stateful run with thread

```json
{
"agentId": "agent_001",
"threadId": "thread_123",
"input": [
{
"role": "user",
"contents": [{ "kind": "text", "text": "What's 2+2?" }]
}
]
}
```

#### Stateless run without thread

```json
{
"agentId": "agent_001",
"input": [
{
"role": "user",
"contents": [{ "kind": "text", "text": "Translate 'hello' to Spanish" }]
}
],
"threadCleanup": "delete"
}
```

#### Run with inline agent definition

```json
{
"agent": {
"type": "prompt",
"model": "gpt-4o",
"instructions": "You are a math tutor"
},
"input": [
{
"role": "user",
"contents": [{ "kind": "text", "text": "Explain calculus" }]
}
]
}
```

#### Run with webhook notification

```json
{
"agentId": "agent_001",
"threadId": "thread_123",
"input": [
{
"role": "user",
"contents": [{ "kind": "text", "text": "Generate report" }]
}
],
"webhook": "https://example.com/webhook"
}
```

---
<!-- GENERATED_END -->