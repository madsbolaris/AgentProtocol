# Agent Auto-Response Specification

**Version**: 1.0

## Overview

This specification defines the agent auto-response system, which enables agents to automatically respond to thread activity based on configurable conditions.

**Key Concepts:**
- **Thread Watch**: Mechanism for agents to monitor and respond to thread activity
- **AutoResponseConfig**: Configuration on agents defining participation behavior
- **RunCondition**: Condition system determining when agents should respond
- **Thread Cleanup**: Automatic thread lifecycle management after run completion

**TypeSpec**: See `AutoResponseConfig` model in `typespec/agents.tsp`, `ThreadWatch` model in `typespec/execution.tsp`

## Agent Auto-Response Model

### AutoResponseConfig

**Purpose**: Configures agent's automatic response behavior

**TypeSpec**: See `AutoResponseConfig` model in `typespec/agents.tsp`

```typescript
model AutoResponseConfig {
  runCondition?: RunCondition;           // When to respond (default: always)
  maxConsecutiveRuns?: int32 = 1;        // Max consecutive runs
  threadCleanup?: ThreadCleanup;         // Thread cleanup after run
}
```

**Fields:**

- **runCondition**: Condition determining when agent should create a run
  - Default: `null` (equivalent to `AlwaysCondition` - respond to all thread activity)
  - Types: Always, Roles, Content, Mention, Expression, Remote

- **maxConsecutiveRuns**: Maximum consecutive runs agent can create
  - Default: `1` (one response per activation)
  - Purpose: Prevents infinite loops in multi-turn scenarios
  - Behavior: Counter resets when another participant (user or different agent) creates a message

- **threadCleanup**: Thread lifecycle management after run completes
  - Default: `ThreadCleanup.keep` (preserve thread)
  - Values: `keep` (preserve), `delete` (auto-delete)
  - Timing: Applied immediately when run reaches terminal status

**Example:**
```json
{
  "name": "Support Agent",
  "autoResponse": {
    "runCondition": {
      "kind": "roles",
      "roles": ["user"]
    },
    "maxConsecutiveRuns": 3,
    "threadCleanup": "delete"
  }
}
```

## Thread Watch Lifecycle

### Registration

**Endpoint**: `POST /threads/{threadId}/watch`

**Purpose**: Register agent to watch and respond to thread activity

**Request Body:**
```json
{
  "agentId": "agent_123"
}
```

**Response**:
```json
{
  "watchId": "watch_abc",
  "agentId": "agent_123",
  "threadId": "thread_456",
  "status": "active",
  "createdAt": "2026-02-06T10:00:00Z"
}
```

**Requirements:**
- Agent MUST have `autoResponse` configured
- Thread MUST exist and be active
- Agent can only watch each thread once (idempotent)

### Evaluation

**Trigger**: When new message added to watched thread

**Flow:**
1. New message added to thread
2. Server identifies all agents watching the thread
3. For each watching agent:
   - Evaluate `runCondition`
   - If condition met AND maxConsecutiveRuns not exceeded:
     - Create run with agent and thread
     - Increment consecutive run counter
   - If condition not met: Skip agent

4. Run executes normally
5. On run completion:
   - Apply `threadCleanup` if configured
   - Reset consecutive run counter if run was from different agent

**Condition Evaluation:**
- **Timing**: Synchronous before run creation
- **Timeout**: 5s (default), 30s max (WebSocket), 2s (default), 10s max (HTTP)
- **Failure Behavior**: Fail-closed - condition evaluates to `false`, agent does not participate

### Conflict Resolution

**Scenario**: Multiple agents' conditions evaluate to `true` simultaneously

**Resolution**: FIFO queueing
- Runs created in order agents were registered to watch thread
- Each run executes sequentially
- No parallel execution of multiple agents

**Example:**
```
Thread has 3 watchers: Agent A, Agent B, Agent C
New user message arrives → all 3 conditions evaluate to true

Execution order:
1. Agent A run executes
2. Agent A run completes
3. Agent B run starts
4. Agent B run completes
5. Agent C run starts
6. Agent C run completes
```

### Cleanup

**Endpoint**: `DELETE /threads/{threadId}/watch/{agentId}`

**Purpose**: Unregister agent from watching thread

**Behavior:**
- Removes watch registration
- Agent will not respond to future thread activity
- Does not affect active runs

**Automatic Cleanup:**
- Thread deletion: All watches automatically removed
- Agent deletion: All watches for that agent removed
- Connection failure (WebSocket): Watch idle timeout (24h recommended)

## RunCondition System

### Condition Types

**TypeSpec**: See `RunCondition` union in `typespec/agents.tsp`

All conditions use `@discriminator("kind")` pattern.

#### 1. AlwaysCondition

**Purpose**: Agent responds to all thread activity

```typescript
model AlwaysCondition {
  kind: "always";
}
```

**Evaluation**: Always returns `true`

**Use Case**: Agents that should respond to every message

**Example:**
```json
{
  "runCondition": {
    "kind": "always"
  }
}
```

#### 2. RolesCondition

**Purpose**: Agent responds to messages from specific roles

```typescript
model RolesCondition {
  kind: "roles";
  roles: ChatRole[];  // "user", "assistant", "system", "tool"
}
```

**Evaluation**: Returns `true` if last message role matches any role in list

**Use Case**: Respond only to user messages, ignore assistant messages

**Example:**
```json
{
  "runCondition": {
    "kind": "roles",
    "roles": ["user"]
  }
}
```

#### 3. ContentCondition

**Purpose**: Agent responds based on content types in message

**TypeSpec**: See `ContentCondition` model in `typespec/conditions.tsp`

```typescript
model ContentCondition {
  kind: "content";
  contentTypes: string[];  // ["video", "image", "file"]
}
```

**Evaluation**:

- Returns `true` if last message contains any of the specified content types
- Content types are matched against message content part kinds
- Example types: "video", "image", "file", "text", "audio"

**Use Case**: Video analyzer responds to video content, image processor responds to image uploads

**Example:**
```json
{
  "runCondition": {
    "kind": "content",
    "contentTypes": ["video", "image"]
  }
}
```

#### 4. MentionCondition

**Purpose**: Agent responds when explicitly mentioned in message

**TypeSpec**: See `MentionCondition` model in `typespec/conditions.tsp`

```typescript
model MentionCondition {
  kind: "mention";
  requireExplicitMention?: boolean = true;
}
```

**Evaluation**: Returns `true` if message contains reference to agent

**Behavior**:

- `requireExplicitMention: true` (default): Requires "@AgentName" pattern in message text
- `requireExplicitMention: false`: Any reference to agent name triggers participation
- Case-insensitive matching
- Exact word match (no partial matches)

**Use Case**: Agent responds only when directly addressed

**Example:**
```json
{
  "runCondition": {
    "kind": "mention",
    "requireExplicitMention": true
  }
}
```

#### 5. ExpressionCondition

**Purpose**: Agent responds based on custom expression logic

**TypeSpec**: See `ExpressionCondition` model in `typespec/conditions.tsp`

```typescript
model ExpressionCondition {
  kind: "expression";
  expression: string;  // Expression code
}
```

**Evaluation**:

- Expression evaluated in-process by server
- Returns `true` if expression evaluates to `true`
- Timeout: 2s (default)
- Failure: Returns `false` (fail-closed)

**Expression Language**:

- Language is inferred from expression syntax (Power Fx or CEL)
- Server determines language based on expression format
- No explicit language field required

**Expression Context**:

- `thread`: Thread object
- `lastMessage`: Last message object
- `agent`: Agent object

**Use Case**: Complex logic that doesn't fit built-in conditions

**Example (CEL syntax):**

```json
{
  "runCondition": {
    "kind": "expression",
    "expression": "lastMessage.role == 'user' && size(thread.messages) > 10"
  }
}
```

#### 6. RemoteCondition

**Purpose**: Agent responds based on remote endpoint evaluation

**TypeSpec**: See `RemoteCondition` model in `typespec/conditions.tsp`

```typescript
model RemoteCondition {
  kind: "remote";
  endpoint: string;         // Remote evaluator URL
  connection?: Connection;  // Authentication
}
```

**Protocol**: See [Remote Endpoints Specification](./remote-endpoints.md)

**Evaluation**:

- HTTP POST to remote endpoint with evaluation context
- Returns `true` if endpoint returns `{"shouldRun": true}`
- Timeout: WebSocket 5s (default), 30s max; HTTP 2s (default), 10s max
- Failure: Returns `false` (fail-closed)
- Retry: Up to 3 times with exponential backoff (100ms, 200ms, 400ms)

**Authentication**:

- Use `connection` field for authentication (Connection types: key, oauth, custom)
- Authentication headers managed via Connection configuration
- No separate headers field

**Use Case**: Complex authorization, external system integration, custom business logic

**Example:**
```json
{
  "runCondition": {
    "kind": "remote",
    "endpoint": "https://conditions.example.com/check-authorization",
    "connection": {
      "kind": "key",
      "key": "condition_api_key_123",
      "headerName": "X-API-Key"
    }
  }
}
```

**Request Format:**
```json
POST /check-authorization
X-API-Key: condition_api_key_123

{
  "threadId": "thread_456",
  "agentId": "agent_123",
  "lastMessage": {
    "role": "user",
    "contents": [{"kind": "text", "text": "Hello"}]
  },
  "context": {
    "messageCount": 5,
    "participants": ["user_1", "agent_123"]
  }
}
```

**Response Format:**
```json
{
  "shouldRun": true,
  "reason": "User is authorized for agent access"
}
```

### Condition Composition

**Note**: Current version supports single condition per agent. Future versions may support boolean composition (AND, OR, NOT).

**Workaround for complex logic**:
- Use `ExpressionCondition` for in-process composition
- Use `RemoteCondition` for remote composition

## Thread Cleanup

### ThreadCleanup Enum

**TypeSpec**: See `ThreadCleanup` enum in `typespec/execution.tsp`

```typescript
enum ThreadCleanup {
  keep,    // Preserve thread after run completes (default)
  delete,  // Auto-delete thread after run completes
}
```

### Cleanup Behavior

**Timing**: Immediately when run reaches terminal status (completed, failed, cancelled, expired)

**Actions**:

**`ThreadCleanup.keep` (default)**:
- Thread remains active
- Thread accessible for future operations
- Suitable for stateful conversations, multi-turn interactions

**`ThreadCleanup.delete`**:
- Thread deleted immediately
- All thread data removed (messages, runs, watches)
- Cannot be recovered
- Suitable for ephemeral queries, one-shot tasks

### Multi-Agent Scenarios

**Scenario**: Multiple agents watching same thread, each with different cleanup config

**Behavior**:
- First agent to complete run with `delete` triggers cleanup
- Cleanup affects all watchers
- Subsequent agent runs cancelled

**Recommendation**: Avoid mixing cleanup configs on same thread

**Example:**
```
Thread watched by:
- Agent A (cleanup: keep)
- Agent B (cleanup: delete)
- Agent C (cleanup: keep)

Flow:
1. User message arrives
2. Agent A run completes (cleanup: keep) → thread preserved
3. Agent B run starts
4. Agent B run completes (cleanup: delete) → thread deleted
5. Agent C run cancelled (thread no longer exists)
```

### Use Cases

**Keep Thread (Stateful)**:
- Customer support conversations
- Multi-turn problem solving
- Long-running projects
- Collaborative sessions

**Delete Thread (Ephemeral)**:
- One-time queries
- Anonymous feedback
- Temporary tasks
- Resource cleanup

## Consecutive Run Limiting

### Purpose

Prevents infinite loops and excessive resource usage in multi-agent or recursive scenarios.

### Configuration

**Field**: `maxConsecutiveRuns` in `AutoResponseConfig`

**Default**: `1`

**Range**: `1-100` (recommended max: `10`)

### Behavior

**Counter Tracking**:
- Server maintains consecutive run counter per agent per thread
- Counter increments when agent creates run
- Counter resets when different participant (user or other agent) creates message

**Enforcement**:
- If counter >= `maxConsecutiveRuns`, agent skipped even if condition met
- Error logged, user NOT notified
- Counter persists until reset condition

**Reset Conditions**:
1. Different agent creates run and adds message
2. User adds message
3. Thread deleted
4. Watch removed

### Examples

**Example 1: Single Response**
```json
{
  "maxConsecutiveRuns": 1
}
```

Flow:
1. User message → Agent responds (counter: 1)
2. Agent message → Condition met but counter >= 1 → Skip
3. User message → Counter reset → Agent responds (counter: 1)

**Example 2: Multi-Turn Conversation**
```json
{
  "maxConsecutiveRuns": 3
}
```

Flow:
1. User message → Agent responds (counter: 1)
2. Agent message → Agent responds again (counter: 2)
3. Agent message → Agent responds third time (counter: 3)
4. Agent message → Condition met but counter >= 3 → Skip
5. User message → Counter reset → Agent responds (counter: 1)

**Example 3: Multi-Agent Meeting**
```json
// Agent A
{"maxConsecutiveRuns": 2}

// Agent B
{"maxConsecutiveRuns": 1}
```

Flow:
1. User message → Agent A responds (A counter: 1)
2. Agent A message → Agent B responds (B counter: 1, A counter reset)
3. Agent B message → Agent A responds (A counter: 1, B counter reset)
4. Agent A message → Agent B skipped (B counter: 1), Agent A responds (A counter: 2)
5. Agent A message → Both skipped (A counter: 2, B counter: 1)
6. User message → Counters reset

## State Machine

### Watch States

```
┌─────────┐
│ initial │
└────┬────┘
     │ POST /watch
     ▼
┌─────────┐
│ active  │ ←──┐
└────┬────┘    │
     │         │ (condition not met)
     │         │
     ├─────────┘
     │ (condition met)
     ▼
┌──────────┐
│ creating │  (creating run)
└────┬─────┘
     │
     ▼
┌─────────┐
│ active  │
└────┬────┘
     │ DELETE /watch
     ▼
┌──────────┐
│ inactive │
└──────────┘
```

### Run Creation States

```
Condition Evaluation → Run Creation → Run Execution → Cleanup

┌─────────────────┐
│ Evaluate        │
│ Condition       │
└────┬─────┬──────┘
     │     │
     │     └─(false)─→ Skip
     │
     └─(true)─┐
              ▼
         ┌─────────────┐
         │ Check       │
         │ Consecutive │
         │ Counter     │
         └──┬─────┬────┘
            │     │
            │     └─(exceeded)─→ Skip
            │
            └─(ok)─┐
                   ▼
              ┌──────────┐
              │ Create   │
              │ Run      │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │ Execute  │
              │ Run      │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │ Apply    │
              │ Cleanup  │
              └──────────┘
```

## Error Handling

### Condition Evaluation Errors

**Behavior**: Fail-closed - condition evaluates to `false`

**Error Types:**
- Timeout (WebSocket: 5s default, HTTP: 2s default)
- Network error (connection refused, DNS failure)
- Server error (5xx responses)
- Invalid response format

**Retry Strategy**:
- Retry up to 3 times with exponential backoff (100ms, 200ms, 400ms)
- After max retries: Treat as `false` (fail-closed)

**Source**: [Error Handling Specification](./error-handling.md)

### Watch Registration Errors

| Error | HTTP Status | Reason | Recovery |
|-------|-------------|--------|----------|
| `AGENT_NOT_FOUND` | 404 | Agent doesn't exist | Check agent ID |
| `THREAD_NOT_FOUND` | 404 | Thread doesn't exist | Check thread ID |
| `AGENT_NOT_CONFIGURED` | 400 | Agent missing `autoResponse` | Configure agent |
| `ALREADY_WATCHING` | 409 | Agent already watching thread | Idempotent - no action needed |
| `THREAD_ARCHIVED` | 409 | Thread is archived | Reactivate thread |

### Run Creation Errors

**Errors during run creation**:
- Agent disabled: Skip agent, continue with others
- Thread deleted: Skip agent, continue with others
- Rate limit exceeded: Skip agent, log error

**No automatic retry**: Run creation is one-time evaluation per message

## Requirements

### Server Requirements

Servers MUST:

1. **Watch Management**: Track which agents are watching which threads
2. **Condition Evaluation**: Evaluate run conditions before creating runs
3. **Fail-Closed Behavior**: Treat condition errors as `false`
4. **Consecutive Run Limiting**: Enforce `maxConsecutiveRuns`
5. **Thread Cleanup**: Apply cleanup immediately on run completion
6. **FIFO Queueing**: Create runs in order of watch registration

Servers SHOULD:

1. **Timeout Configuration**: Allow configurable timeouts for remote conditions
2. **Error Logging**: Log condition evaluation failures
3. **Metrics**: Track condition evaluation success/failure rates
4. **Idle Watch Cleanup**: Remove watches after prolonged inactivity (24h recommended)

### Client Requirements

Clients MUST:

1. **Configure AutoResponse**: Provide valid `autoResponse` config on agents
2. **Handle Watch Errors**: Handle watch registration/removal errors
3. **Cleanup Awareness**: Understand thread may be deleted by any watching agent

Clients SHOULD:

1. **Condition Testing**: Test conditions before deployment
2. **Monitor Consecutive Runs**: Alert on excessive consecutive runs
3. **Cleanup Coordination**: Avoid mixing cleanup configs on same thread

## Security Considerations

### Condition Authorization

**Remote Conditions**:
- Validate endpoint URLs (no internal/localhost)
- Require authentication (Connection types)
- Rate limit condition evaluations
- Audit condition evaluation requests

**Expression Conditions**:
- Sandbox expression evaluation (no file I/O, network access)
- Timeout expression evaluation (2s default)
- Limit expression complexity (AST depth, operation count)

### Watch Authorization

**Permissions Required**:
- `threads:read` - Read thread data
- `threads:write` - Create runs in thread
- `agents:read` - Access agent configuration

**Multi-Tenant Isolation**:
- Agents can only watch threads in same tenant
- Cross-tenant watches rejected with 403 Forbidden

## Compliance

This specification aligns with:
- **TypeSpec**: `typespec/agents.tsp` (AutoResponseConfig, RunCondition)
- **TypeSpec**: `typespec/execution.tsp` (ThreadWatch, ThreadCleanup)
- **TypeSpec**: `typespec/common.tsp` (Base condition types)
- **Error Handling**: [Error Handling Specification](./error-handling.md)
- **Authentication**: [Authentication Specification](./authentication.md)

## See Also

- [Hooks Specification](./hooks.md) - Hook system for content filtering
- [Remote Endpoints Specification](./remote-endpoints.md) - WebSocket/HTTP protocol
- [Run Lifecycle](./run-lifecycle.md) - Run execution states
- [Error Handling](./error-handling.md) - Error codes and retry strategies
- [Authentication](./authentication.md) - Connection types and authorization
