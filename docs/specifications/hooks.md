# Hooks Specification

**Version**: 1.0

## Overview

This specification defines the hooks system, which enables runtime interception, modification, and auditing of agent behavior through event-based hooks.

**Key Concepts:**
- **Hook**: Event-triggered interception for agent runtime events
- **RunCondition**: Condition determining when hook should evaluate
- **HookActionResponse**: Response from hook indicating action to take
- **Blocking vs Non-Blocking**: Whether hook blocks run execution
- **Lifecycle Points**: When hooks are triggered (beforeRun, afterRun, beforeToolExecution, afterToolExecution)

**TypeSpec**: See `Hook` union in `typespec/hooks.tsp`, `RunCondition` union in `typespec/conditions.tsp`, `HookActionResponse` union in `typespec/hooks.tsp`

## Hook System Purpose

**Use Cases:**
1. **Content Moderation**: Block inappropriate content before delivery
2. **PII Redaction**: Remove sensitive information from responses
3. **Approval Workflows**: Require human approval for specific actions
4. **Compliance Auditing**: Log all agent interactions for compliance
5. **Content Enhancement**: Add context or modify responses
6. **Policy Enforcement**: Enforce organizational policies

## Hook Types

**TypeSpec**: See `Hook` union in `typespec/hooks.tsp` (lines 53-59)

All hook types use `@discriminator("kind")` pattern and include a `name` field for identification.

### 1. RemoteHook

**Purpose**: External service evaluates and responds to events

```typescript
model RemoteHook {
  kind: "remote";
  name: string;                  // Hook name (unique per run)
  endpoint: string;              // Remote hook service URL (WebSocket or HTTP)
  connection?: Connection;       // Authentication
  condition?: RunCondition;      // When to evaluate
  config?: Record<unknown>;      // Hook-specific configuration sent in handshake
}
```

**Behavior:**
- HTTP POST or WebSocket to remote endpoint with event data
- Endpoint returns action response (allow, block, modify, sendMessage, telemetry)
- Client-side filtering via optional `condition` to reduce unnecessary network calls

**Use Case**: Custom business logic, external system integration, complex workflows

**Example:**
```json
{
  "kind": "remote",
  "name": "content-filter",
  "endpoint": "https://hooks.example.com/content-filter",
  "connection": {
    "kind": "key",
    "key": "Bearer hook_secret_123",
    "headerName": "Authorization"
  },
  "condition": {
    "kind": "content",
    "contentTypes": ["text"]
  },
  "config": {
    "strictMode": true,
    "categories": ["violence", "hate-speech"]
  }
}
```

### 2. BlockHook

**Purpose**: Unconditionally block execution when condition met

```typescript
model BlockHook {
  kind: "block";
  name: string;                  // Hook name (unique per run)
  condition?: RunCondition;      // When to block
  message: string;               // Message explaining why content was blocked
}
```

**Behavior:**
- Evaluates condition
- If condition met: Blocks execution immediately
- No remote call needed
- Always blocking mode

**Use Case**: Simple policy enforcement, testing, emergency stops

**Example:**
```json
{
  "kind": "block",
  "name": "keyword-blocker",
  "condition": {
    "kind": "content",
    "contentTypes": ["text"]
  },
  "message": "Content contains prohibited keywords"
}
```

### 3. ModifyHook

**Purpose**: Automatically modify content when condition met using pattern-based redaction

```typescript
model ModifyHook {
  kind: "modify";
  name: string;                  // Hook name (unique per run)
  condition?: RunCondition;      // When to modify
  predefinedPatterns?: string[]; // Predefined redaction patterns (e.g., "email", "phone", "ssn")
  regexPatterns?: string[];      // Custom regex patterns for redaction
  replacement?: string;          // Replacement text (default: "[REDACTED]")
}
```

**Behavior:**
- Evaluates condition
- If condition met: Applies pattern-based redaction to content
- Predefined patterns provide common PII detection (email, phone, SSN)
- Custom regex patterns allow additional redaction rules
- All matches replaced with specified replacement text

**Use Case**: PII redaction, content sanitization, credential removal

**Example:**
```json
{
  "kind": "modify",
  "name": "pii-redactor",
  "condition": {
    "kind": "always"
  },
  "predefinedPatterns": ["email", "phone"],
  "regexPatterns": [
    "\\b[A-Z]{2}\\d{6}\\b"
  ],
  "replacement": "[REDACTED]"
}
```

### 4. TelemetryHook

**Purpose**: Emit telemetry events for auditing, monitoring, or analytics

```typescript
model TelemetryHook {
  kind: "telemetry";
  name: string;                  // Hook name (unique per run)
  condition?: RunCondition;      // When to emit telemetry
  event: string;                 // Telemetry event name
  properties?: Record<string>;   // Telemetry event properties
}
```

**Behavior:**
- Evaluates condition
- If condition met: Emits telemetry event with specified properties
- Non-blocking: Does not wait for response
- Does not affect run execution

**Use Case**: Compliance logging, monitoring, analytics, debugging

**Example:**
```json
{
  "kind": "telemetry",
  "name": "audit-logger",
  "condition": {
    "kind": "always"
  },
  "event": "content.created",
  "properties": {
    "source": "agent-runtime",
    "compliance": "required"
  }
}
```

### 5. SendMessageHook

**Purpose**: Inject additional messages into the run (afterRun lifecycle only)

```typescript
model SendMessageHook {
  kind: "sendMessage";
  name: string;                  // Hook name (unique per run)
  condition?: RunCondition;      // When to send message
  message: ChatMessage;          // Message to inject (for LLM regeneration)
}
```

**Behavior:**
- Evaluates condition
- If condition met: Injects message into the run
- Used to trigger LLM regeneration or provide additional context
- Only available in afterRun lifecycle hook

**Use Case**: LLM regeneration, correction, additional context, feedback loops

**Example:**
```json
{
  "kind": "sendMessage",
  "name": "regenerate-on-failure",
  "condition": {
    "kind": "expression",
    "expression": "run.status == 'failed'"
  },
  "message": {
    "role": "system",
    "content": [
      {
        "kind": "text",
        "text": "Please try again with a different approach."
      }
    ]
  }
}
```

## Hook Lifecycle Points

**TypeSpec**: See hooks.tsp lines 16-20

Hooks can be attached to four lifecycle points in the run execution:

### 1. beforeRun

**Trigger**: Before agent execution starts

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook

**Use Cases**:
- Pre-execution validation
- Input sanitization
- Content moderation
- Access control checks

**Example:**
```json
{
  "beforeRun": [
    {
      "kind": "block",
      "name": "production-guard",
      "condition": {
        "kind": "expression",
        "expression": "thread.environment != 'production'"
      },
      "message": "Run blocked: Not authorized for production environment"
    }
  ]
}
```

### 2. afterRun

**Trigger**: After agent execution completes

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook, SendMessageHook

**Use Cases**:
- Post-execution review
- Output sanitization
- Compliance logging
- LLM regeneration

**Example:**
```json
{
  "afterRun": [
    {
      "kind": "sendMessage",
      "name": "quality-checker",
      "condition": {
        "kind": "expression",
        "expression": "message.content.length < 50"
      },
      "message": {
        "role": "system",
        "content": [
          {
            "kind": "text",
            "text": "Please provide a more detailed response."
          }
        ]
      }
    }
  ]
}
```

### 3. beforeToolExecution

**Trigger**: Before each tool call

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook

**Use Cases**:
- Tool call authorization
- Parameter validation
- Sensitive operation approval
- Cost control

**Example:**
```json
{
  "beforeToolExecution": [
    {
      "kind": "block",
      "name": "expensive-tool-guard",
      "condition": {
        "kind": "expression",
        "expression": "tool.name == 'expensive_operation' && user.tier != 'premium'"
      },
      "message": "This operation requires a premium subscription"
    }
  ]
}
```

### 4. afterToolExecution

**Trigger**: After each tool call

**Available Hooks**: RemoteHook, BlockHook, ModifyHook, TelemetryHook

**Use Cases**:
- Result sanitization
- Output redaction
- Success/failure logging
- Error recovery

**Example:**
```json
{
  "afterToolExecution": [
    {
      "kind": "modify",
      "name": "sanitize-output",
      "condition": {
        "kind": "always"
      },
      "predefinedPatterns": ["email", "phone", "ssn"],
      "replacement": "[REDACTED]"
    }
  ]
}
```

## HookActionResponse Types

**TypeSpec**: See `HookActionResponse` union in `typespec/hooks.tsp` (lines 254-260)

RemoteHook endpoints return action responses to indicate what action to take on events.

All response types use `@discriminator("kind")` pattern and include `eventSeqs: int64[]` to specify which events the response applies to.

### 1. AllowResponse

**Purpose**: Allow execution to proceed

```typescript
model AllowResponse {
  kind: "allow";
  eventSeqs: int64[];            // Event sequence numbers to allow
}
```

**Behavior**: Run continues normally

**Use Case**: Explicit approval, default response

**Example:**
```json
{
  "kind": "allow",
  "eventSeqs": [100, 101, 102]
}
```

### 2. BlockResponse

**Purpose**: Block execution and return error

```typescript
model BlockResponse {
  kind: "block";
  eventSeqs: int64[];            // Event sequence numbers to block
  message?: string;              // Reason for blocking (optional)
}
```

**Behavior**:
- Run stops immediately
- Error returned to client
- Status: `failed`
- Error: `HOOK_BLOCKED`

**Use Case**: Content moderation, policy violation, approval rejection

**Example:**
```json
{
  "kind": "block",
  "eventSeqs": [100, 101, 102],
  "message": "Content violates community guidelines"
}
```

### 3. ModifyResponse

**Purpose**: Modify content and continue

```typescript
model ModifyResponse {
  kind: "modify";
  eventSeqs: int64[];            // Event sequence numbers this replaces
  contentIndex: int32;           // Content index within message
  modifiedContent: AIContent;    // Complete modified content (not deltas)
}
```

**Behavior**:
- Replace event content with modified content
- Run continues with modified content
- Original content replaced in streaming

**Content Type Changes**: Framework allows changing content types (e.g., `functionCall` → `text`). Changing types effectively replaces the content's purpose. Framework validates that `modifiedContent` is valid `AIContent` structure.

**Use Case**: PII redaction, content enhancement, translation, blocking tool calls

**Example:**
```json
{
  "kind": "modify",
  "eventSeqs": [100, 101, 102],
  "contentIndex": 0,
  "modifiedContent": {
    "kind": "text",
    "text": "User email is [REDACTED] and phone is [REDACTED]"
  }
}
```

**Blocking Tool Calls Example:**
```json
{
  "kind": "modify",
  "eventSeqs": [100],
  "contentIndex": 0,
  "modifiedContent": {
    "kind": "text",
    "text": "[Tool call blocked by security policy]"
  }
}
```

### 4. SendMessageResponse

**Purpose**: Inject additional messages (afterRun only)

```typescript
model SendMessageResponse {
  kind: "sendMessage";
  eventSeqs: int64[];            // Event sequence numbers after which to insert message
  injectedMessage: ChatMessage;  // Message to inject
}
```

**Behavior**:
- Injects message into run for LLM regeneration
- Run continues with injected message
- Only valid in afterRun lifecycle hook

**Use Case**: LLM regeneration, correction, additional context

**Example:**
```json
{
  "kind": "sendMessage",
  "eventSeqs": [100, 101, 102],
  "injectedMessage": {
    "role": "system",
    "content": [
      {
        "kind": "text",
        "text": "Please revise your response to be more concise."
      }
    ]
  }
}
```

### 5. TelemetryResponse

**Purpose**: Emit telemetry event and continue

```typescript
model TelemetryResponse {
  kind: "telemetry";
  eventSeqs: int64[];                // Event sequence numbers after which to insert telemetry
  telemetryEvent: string;            // Telemetry event name
  telemetryProperties?: Record<unknown>; // Telemetry event properties (optional)
}
```

**Behavior**:
- Log telemetry data
- Run continues normally

**Use Case**: Custom metrics, debugging, analytics

**Example:**
```json
{
  "kind": "telemetry",
  "eventSeqs": [100, 101, 102],
  "telemetryEvent": "hook.warning",
  "telemetryProperties": {
    "sentiment": "positive",
    "confidence": 0.92,
    "topics": ["support", "billing"]
  }
}
```

## RunCondition System

**TypeSpec**: See `RunCondition` union in `typespec/conditions.tsp` (lines 202-209)

All hooks support optional `condition` field to determine when the hook should evaluate.

All conditions use `@discriminator("kind")` pattern.

### Condition Types

1. **AlwaysCondition**: Always evaluates to `true`
2. **RolesCondition**: Match message roles (user, assistant, system)
3. **ContentCondition**: Match content types (text, image, video, etc.)
4. **MentionCondition**: Match explicit @mentions
5. **ExpressionCondition**: Custom expression logic (Power Fx or CEL)
6. **RemoteCondition**: Remote endpoint evaluation

### AlwaysCondition

**Purpose**: Always evaluates to `true`

```typescript
model AlwaysCondition {
  kind: "always";
}
```

**Example:**
```json
{
  "kind": "always"
}
```

### RolesCondition

**Purpose**: Match message roles

```typescript
model RolesCondition {
  kind: "roles";
  roles: ChatRole[];             // Message roles that trigger match
}
```

**Example:**
```json
{
  "kind": "roles",
  "roles": ["user"]
}
```

### ContentCondition

**Purpose**: Match content types

```typescript
model ContentCondition {
  kind: "content";
  contentTypes: string[];        // Content types that trigger match
}
```

**Example:**
```json
{
  "kind": "content",
  "contentTypes": ["video", "image"]
}
```

### MentionCondition

**Purpose**: Match explicit @mentions

```typescript
model MentionCondition {
  kind: "mention";
  requireExplicitMention?: boolean; // Requires "@AgentName" in message (default: true)
}
```

**Example:**
```json
{
  "kind": "mention",
  "requireExplicitMention": true
}
```

### ExpressionCondition

**Purpose**: In-process evaluation using Power Fx or CEL

```typescript
model ExpressionCondition {
  kind: "expression";
  expression: string;            // Expression for evaluation
}
```

**Example:**
```json
{
  "kind": "expression",
  "expression": "message.content[0].kind == 'text' && len(message.content[0].text) > 100"
}
```

### RemoteCondition

**Purpose**: Custom evaluation logic via remote endpoint

```typescript
model RemoteCondition {
  kind: "remote";
  endpoint: string;              // Remote endpoint for evaluation
  connection?: Connection;       // Authentication
}
```

**Example:**
```json
{
  "kind": "remote",
  "endpoint": "https://conditions.example.com/should-block",
  "connection": {
    "kind": "key",
    "key": "Bearer condition_key_123",
    "headerName": "Authorization"
  }
}
```

### Condition Evaluation

**Timing**: Synchronous before hook execution

**Timeout**: 2s (default) for expression/remote conditions

**Failure Behavior**: Fail-closed - condition evaluates to `false`

## Evaluation Flow

### Event Lifecycle

**Hook Evaluation Points:**

```
Run Lifecycle Events:
├─ run.started         (before run begins)
├─ content.created     (before content generated)
├─ content.updated     (during streaming)
├─ content.completed   (after content done)
├─ message.completed   (after message done)
├─ tool.calling        (before tool execution)
├─ tool.called         (after tool execution)
└─ run.completed       (after run ends)
```

### Evaluation Process

**Flow:**

```
1. Event Triggered
   │
   ▼
2. Identify Applicable Hooks
   (Hooks configured for this lifecycle point)
   │
   ▼
3. For Each Hook:
   │
   ├─ Evaluate RunCondition
   │  ├─ Condition FALSE → Skip hook
   │  └─ Condition TRUE → Continue
   │
   ├─ Execute Hook
   │  ├─ Remote: Call endpoint, await response
   │  ├─ Block: Block immediately
   │  ├─ Modify: Apply pattern-based modifications
   │  ├─ Telemetry: Emit telemetry event
   │  └─ SendMessage: Inject message
   │
   └─ Process Response
      ├─ Allow: Continue execution
      ├─ Block: Stop execution, return error
      ├─ Modify: Apply modifications, continue
      ├─ SendMessage: Inject message, continue
      └─ Telemetry: Log event, continue
   │
   ▼
4. All Hooks Complete
   │
   ▼
5. Continue Run Execution
```

## Edge Cases and Protocol Clarifications

This section documents important edge cases and protocol clarifications for hook implementations.

### Multiple Responses for Same Event

**Question**: Can a hook send multiple responses for the same event (e.g., telemetry + allow)?

**Answer**: YES - Hooks can send multiple responses, with the following rules:

1. **Side-Effect Responses** (telemetry, sendMessage): Can be sent multiple times
2. **Approval Responses** (allow, block, modify): Only ONE per event
3. **Processing Order**: Side-effects are processed immediately upon receipt
4. **Idempotency**: Multiple allow responses for same event are idempotent (no error)

**Example Flow:**

```text
Hook receives event 100 (content.updated)
→ Hook sends: {"kind": "telemetry", "eventSeqs": [100], ...}
  Framework logs telemetry
→ Hook sends: {"kind": "allow", "eventSeqs": [100]}
  Framework allows event 100
→ Hook sends: {"kind": "allow", "eventSeqs": [100]} (duplicate)
  Framework ignores (already allowed)
```

**Use Case**: A hook may want to log analytics (telemetry) while also approving content (allow).

### Modification Completion Signaling

**Question**: How does a hook signal it's done modifying content that spans multiple chunks?

**Answer**: Hooks MUST respond to the `content.completed` event with final modification decision.

**Behavior:**

1. Hook receives multiple `content.updated` events (streaming chunks)
2. Hook can buffer events and wait for more context
3. Hook can send partial `modify` responses as chunks arrive
4. Hook MUST respond to `content.completed` with final decision (allow or modify)
5. If hook doesn't respond to `content.completed`, timeout fallback applies

**Example Flow:**

```text
Events 100, 101, 102: "My", " email", " is"
Hook waits (buffering)
Event 103: " john@example.com"
→ Hook responds: {"kind": "modify", "eventSeqs": [100,101,102,103], ...}
Event 104: content.completed
→ Hook responds: {"kind": "allow", "eventSeqs": [104]}
Framework forwards modified content
```

**Important**: Modifications should cover ALL events seen by the hook, not partial modifications.

### EventSeq Contiguity Requirement

**Question**: Can hooks approve events out of order (e.g., approve event 105 without approving 100-104)?

**Answer**: NO - Hooks must approve events in order with contiguous eventSeqs.

**Rules:**

1. Hooks receive events in strict `eventSeq` order
2. Hook responses can reference multiple events (batching)
3. Referenced `eventSeqs` MUST be contiguous (no gaps)
4. Framework REJECTS responses with non-contiguous eventSeqs
5. Rejection triggers timeout fallback behavior

**Valid Examples:**

- `[100]` - Single event ✅
- `[100, 101, 102]` - Contiguous batch ✅
- `[100, 101, 102, 103]` - Contiguous batch ✅

**Invalid Examples:**

- `[100, 102]` - Gap (missing 101) ❌
- `[100, 101, 999]` - Invalid eventSeq (999 not sent) ❌
- `[105, 100]` - Out of order ❌

**Error Response**: Framework returns `400 Bad Request` (HTTP) or closes WebSocket with code `1008` (policy violation).

**Rationale**: Ensures hooks process events in order and don't skip events that may contain critical content.

### Infinite Loop Protection (Max Regenerations)

**Question**: What prevents infinite loops when hooks inject messages that trigger more hooks?

**Answer**: Servers MUST implement a max regeneration limit to prevent infinite loops.

**Requirements:**

1. **Default Limit**: 3 regenerations per run (RECOMMENDED)
2. **Configurable**: `maxRegenerations` in run configuration
3. **Trigger**: `sendMessage` hook responses that inject developer/system messages
4. **Behavior**: After limit reached, framework ignores `sendMessage` responses
5. **Warning**: Framework emits `run.warning` event when limit is hit

**Example Scenario:**

```text
1. Agent completes message → message.completed event
2. Hook A sends: {"kind": "sendMessage", "injectedMessage": {...}}
3. Framework regenerates → new message.completed event
4. Hook A sends: {"kind": "sendMessage", "injectedMessage": {...}} (again)
5. Framework regenerates → new message.completed event
6. Hook A sends: {"kind": "sendMessage", "injectedMessage": {...}} (again)
7. Framework reaches maxRegenerations (3), ignores sendMessage
8. Framework emits run.warning: "Max regenerations reached"
9. Run completes normally
```

**Recommended Configuration:**
```json
{
  "maxRegenerations": 3,
  "maxRegenerationDepth": 5
}
```

**Hook State Tracking**: Hooks SHOULD track state across events (via `contextEvents` field or external storage) to prevent unintentional loops.

### Content Type Changes in Modifications

**Question**: Can hooks change content types in modifications (e.g., functionCall → text)?

**Answer**: YES - Content type changes are ALLOWED but have significant semantic implications.

**Rules:**

1. **Type Changes Allowed**: Hooks can replace any content type with any other valid `AIContent` type
2. **Validation Required**: Framework MUST validate modified content is valid `AIContent`
3. **Semantic Impact**: Type changes may break message structure expectations
4. **Invalid Content**: Framework rejects modifications with protocol violation error

**Valid Modifications:**

- `functionCall` → `text` (effectively blocks the tool call) ✅
- `text` → `text` (PII redaction) ✅
- `image` → `text` (replace with description) ✅
- Multiple chunks → single chunk (content consolidation) ✅

**Use Cases:**

- **Block Tool Calls**: Change `functionCall` to `text` with explanation
- **Redact Media**: Replace `image` or `audio` with text placeholder
- **Content Consolidation**: Merge multiple text chunks into one

**Example:**
```json
{
  "kind": "modify",
  "eventSeqs": [100],
  "contentIndex": 0,
  "modifiedContent": {
    "kind": "text",
    "text": "[Tool call blocked by security policy]"
  }
}
```

**Warning**: Changing `functionCall` to `text` prevents tool execution. The agent will see the text instead of executing the tool. Use with caution.

**Recommendation**: Document expected content types in hook conditions to avoid unexpected type changes.

## Error Handling

### Hook Evaluation Errors

| Error Type | Behavior | Retry Strategy |
|------------|----------|----------------|
| Timeout | Retry with backoff | Up to 3 retries (100ms, 200ms, 400ms) |
| Connection Refused | Retry with backoff | Up to 3 retries |
| 5xx Server Error | Retry with backoff | Up to 3 retries |
| 4xx Client Error | Fail immediately | No retry |
| Invalid Response | Fail immediately | No retry |

### Hook Configuration Errors

| Error | HTTP Status | Reason | Recovery |
|-------|-------------|--------|----------|
| `INVALID_HOOK` | 400 | Hook config invalid | Fix hook configuration |
| `INVALID_ENDPOINT` | 400 | Endpoint URL invalid | Fix endpoint URL |
| `CONDITION_INVALID` | 400 | Condition config invalid | Fix condition |
| `DUPLICATE_HOOK` | 409 | Hook name already exists | Update existing hook or use different name |

### Run Errors

**When Hook Blocks Run:**
- Run status: `failed`
- Error code: `HOOK_BLOCKED`
- Error message: Reason from `BlockResponse`
- User-facing: Show block reason

**Example:**
```json
{
  "runId": "run_123",
  "status": "failed",
  "error": {
    "code": "HOOK_BLOCKED",
    "message": "Content violates community guidelines",
    "details": {
      "hookName": "content-filter",
      "lifecyclePoint": "afterRun"
    }
  }
}
```

## Requirements

### Server Requirements

Servers MUST:

1. **Hook Registration**: Allow hooks to be configured on agents with unique names per run
2. **Hook Evaluation**: Evaluate hooks at appropriate lifecycle points (beforeRun, afterRun, beforeToolExecution, afterToolExecution)
3. **Condition Evaluation**: Evaluate hook conditions before hook execution
4. **Retry Logic**: Retry failed hooks up to 3 times with exponential backoff
5. **Error Propagation**: Return hook block errors to clients
6. **EventSeq Validation**: Reject responses with non-contiguous eventSeqs
7. **Max Regeneration Limit**: Implement configurable max regeneration limit (default: 3)

Servers SHOULD:

1. **Timeout Configuration**: Allow configurable hook timeouts
2. **Hook Ordering**: Execute hooks in deterministic order
3. **Metrics**: Track hook evaluation success/failure rates
4. **Audit Logging**: Log all hook evaluations for compliance

### Client Requirements

Clients MUST:

1. **Handle Hook Errors**: Handle `HOOK_BLOCKED` errors gracefully
2. **Configure Hooks**: Provide valid hook configurations with unique names
3. **Understand Lifecycle**: Understand which hooks are valid at which lifecycle points

Clients SHOULD:

1. **Test Hooks**: Test hook configurations before production
2. **Monitor Hooks**: Monitor hook success/failure rates
3. **Graceful Degradation**: Handle hook failures gracefully

## Security Considerations

### Hook Authorization

**Permissions Required:**
- `runs:read` - Read run data for evaluation
- `runs:write` - Modify run behavior (block, modify)
- `hooks:configure` - Configure hooks on agents

**Endpoint Validation:**
- Validate endpoint URLs (no internal/localhost)
- Require authentication (Connection types)
- Rate limit hook requests
- Audit all hook evaluations

### Content Modification

**Risks:**
- Hooks can modify content arbitrarily
- Malicious hooks could inject harmful content

**Mitigations:**
- Require hook approval/authorization
- Audit all modifications
- Validate modified content
- Limit hook capabilities

### PII Handling

**Hooks have access to all content, including PII:**
- Encrypt hook requests (HTTPS/WSS only)
- Require explicit consent for PII access
- Audit PII access
- Limit PII retention at hook endpoints

## Compliance

This specification aligns with:
- **TypeSpec**: `typespec/hooks.tsp` (Hook, HookActionResponse)
- **TypeSpec**: `typespec/conditions.tsp` (RunCondition)
- **TypeSpec**: `typespec/common.tsp` (Connection, base types)
- **Error Handling**: [Error Handling Specification](./error-handling.md)
- **Authentication**: [Authentication Specification](./authentication.md)

## See Also

- [Run Lifecycle](./run-lifecycle.md) - Run execution states and lifecycle events
- [Error Handling](./error-handling.md) - Error codes and retry strategies
- [Streaming](./streaming.md) - Streaming with hook integration
- [Remote Endpoints Specification](./remote-endpoints.md) - WebSocket/HTTP protocol for RemoteHook
