# Models Reference

Complete reference of all TypeSpec models in the Agent Runtime API.

**TypeSpec Source**: All `.tsp` files in [typespec/](../typespec/)

---

## Overview

The Agent Runtime API is defined using TypeSpec, which generates OpenAPI 3.0 schemas. This document provides a quick reference to all models organized by domain.

**Total Models**: 97 schemas in OpenAPI output

---

## Core Models

### Execution & Lifecycle

| Model | File | Description |
|-------|------|-------------|
| **Run** | [execution.tsp](../typespec/execution.tsp) | Agent execution instance with lifecycle |
| **Thread** | [execution.tsp](../typespec/execution.tsp) | Conversation context and message container |
| **ThreadWatch** | [execution.tsp](../typespec/execution.tsp) | Agent subscription to thread for auto-response |
| **RunStatus** | [execution.tsp](../typespec/execution.tsp) | Enum: 11 lifecycle states |
| **ThreadStatus** | [execution.tsp](../typespec/execution.tsp) | Enum: active, archived, deleted |
| **ThreadCleanup** | [execution.tsp](../typespec/execution.tsp) | Enum: keep, delete |
| **CancelAction** | [execution.tsp](../typespec/execution.tsp) | Enum: interrupt, rollback |

**Key Fields**:
- `Run`: agentId, threadId?, input[], output[], status, usage, webhook?, journalId?
- `Thread`: threadId, metadata, createdAt, lastActivityAt
- `ThreadWatch`: watchId, threadId, agentId, active, activationCount

---

### Messages

| Model | File | Description |
|-------|------|-------------|
| **ChatMessage** | [messages.tsp](../typespec/messages.tsp) | Message with role and contents |
| **AIContent** | [messages.tsp](../typespec/messages.tsp) | Union of 29 content types |
| **AIContentBase** | [messages.tsp](../typespec/messages.tsp) | Base model for content (audience, encryption, additionalProperties) |
| **ChatRole** | [messages.tsp](../typespec/messages.tsp) | Enum: user, assistant, system, developer, tool, channel |

**Content Types** (29 total): See [content-types.md](./content-types.md)

---

### Agents

| Model | File | Description |
|-------|------|-------------|
| **Agent** | [agents.tsp](../typespec/agents.tsp) | Union: PromptAgent |
| **PromptAgent** | [agents.tsp](../typespec/agents.tsp) | Agent with model and instructions |
| **AgentCard** | [agents.tsp](../typespec/agents.tsp) | Agent metadata and capabilities |
| **AutoResponseConfig** | [agents.tsp](../typespec/agents.tsp) | Auto-response participation rules |

**Key Fields**:
- `AgentCard`: agentId, displayName, description, capabilities, model, tools[], scopes
- `AutoResponseConfig`: runCondition, maxConsecutiveRuns?, threadCleanup?

---

### Tools

| Model | File | Description |
|-------|------|-------------|
| **AITool** | [tools.tsp](../typespec/tools.tsp) | Tool definition with JSON Schema |
| **ToolLifecycleHooks** | [tools.tsp](../typespec/tools.tsp) | Before/after tool execution hooks |
| **JSONSchema** | [tools.tsp](../typespec/tools.tsp) | JSON Schema Draft 7 |

**Key Fields**:
- `AITool`: name, description, parameters, returnType?, strict?, scopes?, lifecycleHooks?

---

## Conditions & Hooks

### Conditions

| Model | File | Description |
|-------|------|-------------|
| **RunCondition** | [conditions.tsp](../typespec/conditions.tsp) | Union of 6 condition types |
| **AlwaysCondition** | [conditions.tsp](../typespec/conditions.tsp) | Always match |
| **RolesCondition** | [conditions.tsp](../typespec/conditions.tsp) | Match message roles |
| **ContentCondition** | [conditions.tsp](../typespec/conditions.tsp) | Match content types |
| **MentionCondition** | [conditions.tsp](../typespec/conditions.tsp) | Match explicit @mentions |
| **ExpressionCondition** | [conditions.tsp](../typespec/conditions.tsp) | CEL/Power Fx evaluation |
| **RemoteCondition** | [conditions.tsp](../typespec/conditions.tsp) | Remote endpoint evaluation |

---

### Hooks

| Model | File | Description |
|-------|------|-------------|
| **Hook** | [hooks.tsp](../typespec/hooks.tsp) | Union of 5 hook types |
| **RemoteHook** | [hooks.tsp](../typespec/hooks.tsp) | Delegate to external service |
| **BlockHook** | [hooks.tsp](../typespec/hooks.tsp) | Block events with predefined message |
| **ModifyHook** | [hooks.tsp](../typespec/hooks.tsp) | PII redaction via patterns |
| **TelemetryHook** | [hooks.tsp](../typespec/hooks.tsp) | Emit inline telemetry |
| **SendMessageHook** | [hooks.tsp](../typespec/hooks.tsp) | Inject messages (afterRun only) |
| **HookActionResponse** | [hooks.tsp](../typespec/hooks.tsp) | Union of 5 response types |

**Response Types**: AllowResponse, BlockResponse, ModifyResponse, SendMessageResponse, TelemetryResponse

---

## Subscriptions & Streaming

### Subscriptions

| Model | File | Description |
|-------|------|-------------|
| **ThreadSubscription** | [subscriptions.tsp](../typespec/subscriptions.tsp) | Webhook for thread events |
| **RunSubscription** | [subscriptions.tsp](../typespec/subscriptions.tsp) | Webhook for run events |
| **AgentSubscription** | [subscriptions.tsp](../typespec/subscriptions.tsp) | Webhook for agent events |
| **MessageFilters** | [subscriptions.tsp](../typespec/subscriptions.tsp) | Filter by roles, users, agents, content |

---

### Streaming Events

| Model | File | Description |
|-------|------|-------------|
| **StreamEvent** | [streaming.tsp](../typespec/streaming.tsp) | Union of all event types |
| **MessageEvent** | [streaming.tsp](../typespec/streaming.tsp) | Union: Created, Updated, Completed, Deleted |
| **RunEvent** | [streaming.tsp](../typespec/streaming.tsp) | Union: Started, Completed, Failed, etc. |
| **ThreadEvent** | [streaming.tsp](../typespec/streaming.tsp) | Union: Created, Updated, Archived, Deleted |
| **AgentEvent** | [streaming.tsp](../typespec/streaming.tsp) | Union: Activity, Error |

**SSE Event Names**: `message.created`, `run.started`, `thread.updated`, etc.

**TypeSpec Model Names**: `MessageCreatedEvent`, `RunStartedEvent`, `ThreadUpdatedEvent`, etc.

See [Streaming Specification](../specifications/streaming.md) for event naming details.

---

## Common Models

| Model | File | Description |
|-------|------|-------------|
| **Connection** | [common.tsp](../typespec/common.tsp) | Union: Reference, ApiKey, Remote, Anonymous |
| **Scopes** | [common.tsp](../typespec/common.tsp) | Record<string> (scope URI → description) |
| **Usage** | [usage.tsp](../typespec/usage.tsp) | Token and resource usage |

---

## Error Models

| Model | File | Description |
|-------|------|-------------|
| **NotFoundError** | [routes.tsp](../typespec/routes.tsp) | 404 error |
| **ConflictError** | [routes.tsp](../typespec/routes.tsp) | 409 error |
| **RunError** | [execution.tsp](../typespec/execution.tsp) | Run failure details |

---

## Navigation

### By Domain

- **Execution**: [Run Operations](./operations/runs.md), [Thread Operations](./operations/threads.md)
- **Messages**: [Content Types](./content-types.md), [Message Lifecycle Spec](../specifications/message-lifecycle.md)
- **Agents**: [Agent Operations](./operations/agents.md), [Agent Auto-Response Spec](../specifications/agent-auto-response.md)
- **Tools**: [Tool Execution Spec](../specifications/tool-execution.md)
- **Hooks**: [Hooks Spec](../specifications/hooks.md)
- **Streaming**: [Streaming Spec](../specifications/streaming.md)

### By File

- [execution.tsp](../typespec/execution.tsp) - Run, Thread, ThreadWatch, RunStatus
- [messages.tsp](../typespec/messages.tsp) - ChatMessage, AIContent, ChatRole
- [agents.tsp](../typespec/agents.tsp) - Agent, AgentCard, AutoResponseConfig
- [tools.tsp](../typespec/tools.tsp) - AITool, ToolLifecycleHooks
- [conditions.tsp](../typespec/conditions.tsp) - RunCondition types
- [hooks.tsp](../typespec/hooks.tsp) - Hook types and responses
- [subscriptions.tsp](../typespec/subscriptions.tsp) - Subscription models
- [streaming.tsp](../typespec/streaming.tsp) - StreamEvent types
- [common.tsp](../typespec/common.tsp) - Connection, Scopes
- [usage.tsp](../typespec/usage.tsp) - Usage tracking
- [routes.tsp](../typespec/routes.tsp) - API routes and operations

---

## TypeSpec Compilation

To regenerate OpenAPI schema from TypeSpec:

```bash
cd typespec
npm run compile
```

**Output**: `../.generated/openapi.json` (97 schemas)

---

## Related Resources

- [TypeSpec Documentation](https://typespec.io)
- [OpenAPI 3.0 Specification](https://spec.openapis.org/oas/v3.0.0)
- [API Operations](./operations/)
- [Specifications](../specifications/)
