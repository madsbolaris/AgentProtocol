# Validation Specification

**Version**: 1.0

## Overview

This specification defines input validation rules, business constraints, and validation patterns for the Agent Runtime API.

**Validation Principles:**
- **Fail Fast**: Reject invalid requests immediately
- **Clear Errors**: Provide actionable error messages
- **Schema-First**: Use JSON Schema for parameter validation
- **Business Rules**: Enforce domain constraints beyond schema

## Validation Layers

### Layer 1: Schema Validation

**TypeSpec Contracts**: Auto-generated JSON Schema from TypeSpec

**Validates:**
- Required fields present
- Field types correct
- Enum values valid
- Format constraints (URIs, dates, etc.)

### Layer 2: Business Logic Validation

**Custom Validation Rules**: Domain-specific constraints

**Validates:**
- Resource relationships (e.g., thread exists)
- State transitions (e.g., run status changes)
- Permissions (e.g., user can access thread)
- Resource limits (e.g., max message size)

### Layer 3: External Validation

**Provider/Service Validation**: Downstream validation

**Validates:**
- LLM provider API constraints
- Tool execution requirements
- OAuth2 scope availability

## Run Validation

### Create Run Validation

**Required Fields:**
```typescript
{
  agentId: string,      // Must reference existing agent OR
  agent: AgentDefinition, // Provide inline agent definition
  input: ChatMessage[]   // Must be non-empty array
}
```

**Validation Rules:**

1. **Agent Validation**:
   ```
   IF agentId provided:
     - MUST reference existing agent
     - MUST be accessible by user
   ELSE IF agent provided:
     - MUST be valid AgentDefinition
     - MUST pass agent schema validation
   ELSE:
     - REJECT: "Either agentId or agent required"
   ```

2. **Thread Validation**:
   ```
   IF threadId provided:
     - MUST reference existing thread
     - MUST NOT be archived
     - MUST be accessible by user
   ELSE:
     - Optional: stateless execution allowed
   ```

3. **Input Validation**:
   ```
   - MUST be array with length > 0
   - MUST reject empty array (input: []) with 400 Bad Request
   - Each message MUST have valid role
   - Each message MUST have non-empty contents
   - Tool results MUST reference pending tool calls
   ```

   **Empty Input Error Response**:
   ```json
   {
     "error": {
       "code": "invalid_request",
       "message": "input array cannot be empty. Provide at least one message."
     }
   }
   ```

   **Rationale**: Runs require actual input messages to process. With ThreadAutoResponder pattern, the server automatically provides input when creating auto-runs - clients never submit empty input directly.

4. **Options Validation**:
   ```
   IF options.maxTurns provided:
     - MUST be >= 1
     - MUST be <= 100 (server limit)
   ```

**Examples:**

**Valid:**
```json
{
  "agentId": "agent_123",
  "threadId": "thread_456",
  "input": [{
    "role": "user",
    "contents": [{ "kind": "text", "text": "Hello" }]
  }]
}
```

**Invalid - Empty Input:**
```json
{
  "agentId": "agent_123",
  "input": []
}
// Error: "input must be non-empty array"
```

**Invalid - Missing Agent:**
```json
{
  "threadId": "thread_456",
  "input": [...]
}
// Error: "Either agentId or agent required"
```

### Submit Tool Outputs Validation

**Required:**
```typescript
{
  tool_outputs: [{
    callId: string,   // Must match pending tool call
    result: string | AIContent[]
  }]
}
```

**Validation Rules:**

1. **Run Status**:
   ```
   - MUST be in "requires_action" status
   - REJECT if status is "completed", "failed", "cancelled"
   ```

2. **Call ID Matching**:
   ```
   - Each callId MUST match pending tool call
   - REJECT if callId not found
   - REJECT if callId already submitted
   ```

3. **Complete Results**:
   ```
   - MUST provide results for ALL pending tool calls
   - REJECT if missing results for some calls
   ```

**Examples:**

**Valid:**
```json
{
  "tool_outputs": [
    { "callId": "call_1", "result": "Weather: 18°C" },
    { "callId": "call_2", "result": "Time: 10:30 AM" }
  ]
}
```

**Invalid - Missing Results:**
```json
{
  "tool_outputs": [
    { "callId": "call_1", "result": "..." }
    // Missing call_2!
  ]
}
// Error: "Missing tool outputs for: call_2"
```

**Invalid - Wrong Status:**
```json
POST /runs/{runId}/submit_tool_outputs
// Run status: "completed"
// Error: "Run not in requires_action status"
```

## Message Validation

### Create Message Validation

**Required Fields:**
```typescript
{
  role: ChatRole,        // Must be valid enum value
  contents: AIContent[]  // Must be non-empty array
}
```

**Validation Rules:**

1. **Role Validation**:
   ```
   - MUST be valid ChatRole enum
   - MUST NOT be "channel" (reserved for system)
   - Valid client roles: "user", "system", "developer", "assistant", "tool"
   ```

2. **Contents Validation**:
   ```
   - MUST be non-empty array
   - Each content MUST have valid type discriminator
   - Each content MUST pass type-specific validation
   ```

3. **Thread Validation**:
   ```
   - threadId MUST reference existing thread
   - Thread MUST NOT be archived
   ```

4. **Branching Validation**:
   ```
   IF parentMessageId provided:
     - MUST reference existing message in thread
     - MUST NOT create cycle in DAG
   ```

**Examples:**

**Valid:**
```json
{
  "role": "user",
  "contents": [
    { "kind": "text", "text": "Hello!" }
  ]
}
```

**Invalid - Channel Role:**
```json
{
  "role": "channel",
  "contents": [...]
}
// Error: "role 'channel' reserved for system"
```

**Invalid - Empty Contents:**
```json
{
  "role": "user",
  "contents": []
}
// Error: "contents must be non-empty array"
```

**Invalid - Cycle:**
```json
{
  "messageId": "msg_1",
  "parentMessageId": "msg_1"
}
// Error: "parentMessageId creates cycle"
```

## Content Validation

### TextContent

**Required**: `text` field

**Validation:**
```
- text MUST be non-empty string
- text length MUST be <= 100,000 characters (server limit)
```

### FunctionCallContent

**Required**: `callId`, `name`

**Validation:**
```
- callId MUST be unique within message
- name MUST match tool in agent's tool list
- IF arguments provided:
  - MUST be valid JSON string OR object
  - MUST match tool's parameter schema
```

**Example - Invalid Arguments:**
```json
{
  "kind": "functionCall",
  "callId": "call_1",
  "name": "search",
  "arguments": { "query": 123 }  // Should be string
}
// Error: "arguments.query: expected string, got number"
```

### FunctionResultContent

**Required**: `callId`, `name`

**Validation:**
```
- callId MUST match pending tool call
- name MUST match tool call name
- IF exception provided:
  - MUST be valid ErrorContent
```

### ImageContent

**Required**: At least one of `uri`, `dataUri`, or `data`

**Validation:**
```
- IF uri: MUST be valid URL
- IF dataUri: MUST be valid data URI (data:image/png;base64,...)
- IF data: MUST be valid base64-encoded bytes
- IF mimeType: MUST match actual content type
- IF width/height: MUST be > 0
```

**Size Limits:**
```
- data field: Max 10MB
- URI: Max 2048 characters
```

### AudioContent / VideoContent

**Required**: At least one of `uri`, `dataUri`, or `data`

**Validation:**
```
- Same as ImageContent
- duration: MUST be > 0 if provided
```

## Agent Validation

### AgentCard Validation

**Required**: `id`, `name`

**Validation:**
```
- id: MUST be unique
- name: MUST be non-empty, max 100 characters
- description: Max 1000 characters
- instructions: Max 50,000 characters
- IF scopes provided:
  - Each scope MUST be valid URI
  - Descriptions MUST be non-empty
- IF connections provided:
  - Each connection MUST be valid Connection type
```

### PromptAgent Validation

**Required**: Inherits from AgentCard

**Additional Validation:**
```
- model: MUST be supported model ID
- IF maxTokens provided:
  - MUST be >= 1
  - MUST be <= model's max context length
- IF temperature provided:
  - MUST be >= 0.0
  - MUST be <= 2.0
- IF topP provided:
  - MUST be >= 0.0
  - MUST be <= 1.0
```

## Tool Validation

### AITool Validation

**Required**: `name`, `description`

**Validation:**
```
- name: MUST be valid identifier ([a-zA-Z0-9_-]+)
- name: MUST be unique within agent's tool list
- description: MUST be non-empty, max 1000 characters
- IF parameters provided:
  - MUST be valid JSON Schema Draft 7
  - MUST have "type": "object" at root
- IF returnType provided:
  - MUST be valid JSON Schema Draft 7
- IF scopes provided:
  - Each scope MUST be valid URI
```

**Example - Invalid Name:**
```json
{
  "name": "search web",  // Contains space
  "description": "..."
}
// Error: "name must be valid identifier (no spaces)"
```

**Example - Invalid Schema:**
```json
{
  "name": "search",
  "parameters": {
    "type": "string"  // Should be "object"
  }
}
// Error: "parameters.type must be 'object'"
```

## Connection Validation

### ReferenceConnection

**Required**: `kind`, `name`

**Validation:**
```
- kind: MUST be "reference"
- name: MUST reference existing connection
- authority: MUST be "user" or "system" if provided
```

### ApiKeyConnection

**Required**: `kind`, `key`

**Validation:**
```
- kind: MUST be "key"
- key: MUST be non-empty string
- headerName: Default "Authorization"
```

### RemoteConnection

**Required**: `kind`, `endpoint`

**Validation:**
```
- kind: MUST be "remote"
- endpoint: MUST be valid URL
- credentials: Can be any object structure
```

### AnonymousConnection

**Required**: `kind`

**Validation:**
```
- kind: MUST be "anonymous"
```

## Scope Validation

### Scope Format

**OpenAPI 3.0 Format**: `Record<string>` (scope name → description)

**Validation:**
```
- Keys: MUST be valid URIs (https://domain/scope)
- Values: MUST be non-empty strings (descriptions)
- NO duplicate keys
```

**Examples:**

**Valid:**
```json
{
  "https://graph.microsoft.com/Calendars.Read": "Read calendar events",
  "https://graph.microsoft.com/Mail.Send": "Send mail"
}
```

**Invalid - Not URI:**
```json
{
  "calendars": "Read calendar"  // Not fully-qualified URI
}
// Error: "scope key must be URI"
```

**Invalid - Empty Description:**
```json
{
  "https://graph.microsoft.com/Mail.Send": ""
}
// Error: "scope description must be non-empty"
```

## Hook Validation

### Overview

Hooks enable event-driven interception and modification of run execution. This section defines validation rules for all hook types.

**Related Specifications:**
- [Hooks Specification](./hooks.md) - Complete hook documentation
- [Remote Endpoints](./remote-endpoints.md) - WebSocket/HTTP protocol
- [Error Handling](./error-handling.md) - Hook error codes

### HookConfiguration Validation

**Common Fields** (all hook types):

```typescript
{
  hookId?: string,        // Optional, server-generated if omitted
  kind: HookKind,         // Required discriminator
  eventTypes: EventType[], // Required, non-empty
  priority?: number        // Optional, 0-100
}
```

**Validation Rules:**

1. **hookId** (optional):
   ```
   - IF provided: MUST be unique
   - IF omitted: Server generates unique ID
   ```

2. **kind** (required):
   ```
   - MUST be valid HookKind enum value
   - Valid values: "block", "modify", "remote", "telemetry", "sendMessage"
   ```

3. **eventTypes** (required):
   ```
   - MUST be non-empty array
   - Each value MUST be valid EventType enum
   - Valid EventType values:
     - "run.started", "run.completed", "run.failed", "run.cancelled"
     - "content.created", "content.updated"
     - "message.created", "message.updated", "message.completed"
     - "tool.called", "tool.result"
   ```

4. **priority** (optional):
   ```
   - MUST be >= 0
   - MUST be <= 100
   - Default: 50 (if omitted)
   ```

**Example - Invalid:**
```json
{
  "kind": "block",
  "eventTypes": []
}
// Error: "eventTypes must be non-empty array"
```

### BlockHook Validation

**Required**: `kind`, `condition`, `eventTypes`

```typescript
{
  kind: "block",
  condition: HookCondition,
  eventTypes: EventType[]
}
```

**Validation Rules:**

1. **kind**: MUST be "block"

2. **condition**: MUST be valid HookCondition
   - See "Hook Condition Validation" below

**Examples:**

**Valid:**
```json
{
  "kind": "block",
  "condition": {
    "kind": "content",
    "patterns": ["offensive_term"]
  },
  "eventTypes": ["message.created"]
}
```

**Invalid - Missing Condition:**
```json
{
  "kind": "block",
  "eventTypes": ["run.started"]
}
// Error: "condition is required for BlockHook"
```

### ModifyHook Validation

**Required**: `kind`, `condition`, `eventTypes`, `action`

```typescript
{
  kind: "modify",
  condition: HookCondition,
  eventTypes: EventType[],
  action: ModifyAction
}
```

**Validation Rules:**

1. **kind**: MUST be "modify"

2. **condition**: MUST be valid HookCondition

3. **action**: MUST be valid ModifyAction
   ```typescript
   {
     kind: "modify",
     content: unknown  // Content transformation
   }
   ```

   **Action Validation:**
   ```
   - action.kind MUST be "modify"
   - action.content MUST be provided
   - action.content type depends on event:
     - message.created: Partial<ChatMessage>
     - content.created: Partial<AIContent>
     - tool.result: Partial<FunctionResultContent>
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "modify",
  "condition": {
    "kind": "content",
    "patterns": ["\\d{3}-\\d{2}-\\d{4}"]
  },
  "eventTypes": ["message.created"],
  "action": {
    "kind": "modify",
    "content": {
      "contents": [{"kind": "text", "text": "[REDACTED]"}]
    }
  }
}
```

**Invalid - Missing Action:**
```json
{
  "kind": "modify",
  "condition": {"kind": "always"},
  "eventTypes": ["content.created"]
}
// Error: "action is required for ModifyHook"
```

### RemoteHook Validation

**Required**: `kind`, `endpoint`, `eventTypes`

```typescript
{
  kind: "remote",
  endpoint: RemoteEndpoint,
  eventTypes: EventType[],
  timeout?: number
}
```

**Validation Rules:**

1. **kind**: MUST be "remote"

2. **endpoint**: MUST be valid RemoteEndpoint
   - See "Remote Endpoint Validation" section below

3. **timeout** (optional):
   ```
   - MUST be >= 1000 (1 second)
   - MUST be <= 30000 (30 seconds)
   - Default: 5000 (5 seconds)
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "remote",
  "endpoint": {
    "protocol": "websocket",
    "url": "wss://hooks.example.com/evaluate"
  },
  "eventTypes": ["tool.called"],
  "timeout": 10000
}
```

**Invalid - Timeout Out of Range:**
```json
{
  "kind": "remote",
  "endpoint": {
    "protocol": "websocket",
    "url": "wss://hooks.example.com"
  },
  "eventTypes": ["run.started"],
  "timeout": 50000
}
// Error: "timeout must be between 1000 and 30000 milliseconds"
```

**Invalid - Missing Endpoint:**
```json
{
  "kind": "remote",
  "eventTypes": ["content.created"]
}
// Error: "endpoint is required for RemoteHook"
```

### TelemetryHook Validation

**Required**: `kind`, `condition`, `eventTypes`, `destination`

```typescript
{
  kind: "telemetry",
  condition: HookCondition,
  eventTypes: EventType[],
  destination: string
}
```

**Validation Rules:**

1. **kind**: MUST be "telemetry"

2. **condition**: MUST be valid HookCondition

3. **destination**: MUST be non-empty string
   ```
   - Identifies telemetry destination system
   - Examples: "datadog", "splunk", "cloudwatch", "custom_log"
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "telemetry",
  "condition": {"kind": "always"},
  "eventTypes": ["run.completed", "run.failed"],
  "destination": "datadog"
}
```

**Invalid - Empty Destination:**
```json
{
  "kind": "telemetry",
  "condition": {"kind": "always"},
  "eventTypes": ["tool.called"],
  "destination": ""
}
// Error: "destination must be non-empty string"
```

### SendMessageHook Validation

**Required**: `kind`, `condition`, `eventTypes`, `threadId`, `message`

```typescript
{
  kind: "sendMessage",
  condition: HookCondition,
  eventTypes: EventType[],
  threadId: string,
  message: ChatMessage
}
```

**Validation Rules:**

1. **kind**: MUST be "sendMessage"

2. **condition**: MUST be valid HookCondition

3. **threadId**: MUST reference existing thread
   ```
   - MUST be valid thread ID
   - Thread MUST NOT be archived
   - User MUST have access to thread
   ```

4. **message**: MUST be valid ChatMessage
   ```
   - Apply same validation as "Create Message Validation" section
   - message.role MUST be valid
   - message.contents MUST be non-empty
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "sendMessage",
  "condition": {
    "kind": "expression",
    "expression": "event.runStatus == 'failed'"
  },
  "eventTypes": ["run.failed"],
  "threadId": "thread_123",
  "message": {
    "role": "system",
    "contents": [{"kind": "text", "text": "Run failed. Please review."}]
  }
}
```

**Invalid - Thread Not Found:**
```json
{
  "kind": "sendMessage",
  "condition": {"kind": "always"},
  "eventTypes": ["run.completed"],
  "threadId": "thread_nonexistent",
  "message": {...}
}
// Error: "threadId does not reference existing thread"
```

**Invalid - Invalid Message:**
```json
{
  "kind": "sendMessage",
  "condition": {"kind": "always"},
  "eventTypes": ["run.completed"],
  "threadId": "thread_123",
  "message": {
    "role": "user",
    "contents": []
  }
}
// Error: "message.contents must be non-empty array"
```

### Hook Condition Validation

**HookCondition Union:**
```typescript
type HookCondition = ContentCondition | AlwaysCondition | ExpressionCondition
```

#### ContentCondition

**Required**: `kind`, `patterns`

```typescript
{
  kind: "content",
  patterns: string[]  // Regex patterns
}
```

**Validation Rules:**

1. **kind**: MUST be "content"

2. **patterns**: MUST be non-empty array
   ```
   - Each pattern MUST be valid regex
   - Validate by attempting compilation (new RegExp(pattern))
   - Common errors: unclosed groups, invalid escapes
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "content",
  "patterns": ["\\d{3}-\\d{2}-\\d{4}", "\\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\\.[A-Z]{2,}\\b"]
}
```

**Invalid - Invalid Regex:**
```json
{
  "kind": "content",
  "patterns": ["[unclosed"]
}
// Error: "patterns[0]: invalid regex syntax - unterminated character class"
```

**Invalid - Empty Patterns:**
```json
{
  "kind": "content",
  "patterns": []
}
// Error: "patterns must be non-empty array"
```

#### ExpressionCondition

**Required**: `kind`, `expression`

```typescript
{
  kind: "expression",
  expression: string  // CEL expression
}
```

**Validation Rules:**

1. **kind**: MUST be "expression"

2. **expression**: MUST be valid CEL syntax
   ```
   - Validate CEL syntax before execution
   - Expression MUST return boolean type
   - Common errors:
     - Undefined variables
     - Type mismatches (e.g., "string" == 123)
     - Syntax errors (e.g., unclosed parentheses)
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "expression",
  "expression": "event.toolName == 'execute_command' && event.arguments.command.contains('rm')"
}
```

**Invalid - Syntax Error:**
```json
{
  "kind": "expression",
  "expression": "event.toolName == 'execute_command' &&"
}
// Error: "expression: syntax error - incomplete expression"
```

**Invalid - Undefined Variable:**
```json
{
  "kind": "expression",
  "expression": "event.undefinedField == 'value'"
}
// Error: "expression: undefined variable 'undefinedField'"
```

**Invalid - Type Mismatch:**
```json
{
  "kind": "expression",
  "expression": "event.toolName + 123"
}
// Error: "expression: type mismatch - cannot add string and number"
```

#### AlwaysCondition

**Required**: `kind`

```typescript
{
  kind: "always"
}
```

**Validation Rules:**

1. **kind**: MUST be "always"
2. No additional fields allowed

**Example:**
```json
{
  "kind": "always"
}
```

## Condition Validation

### Overview

Conditions determine when auto-runs trigger in the agent auto-response system. This section defines validation rules for all condition types.

**Related Specifications:**
- [Agent Auto-Response Specification](./agent-auto-response.md) - Complete auto-response documentation
- [Remote Endpoints](./remote-endpoints.md) - RemoteCondition protocol

### RunCondition Union

```typescript
type RunCondition =
  | TimeCondition
  | EventCondition
  | ExpressionCondition
  | ContentCondition
  | RemoteCondition
  | AlwaysCondition
  | NeverCondition
```

**Validation**: MUST be one of the 7 condition types (discriminated by `kind` field)

### TimeCondition Validation

**Required**: `kind`, `schedule`

```typescript
{
  kind: "time",
  schedule: string,    // Cron expression
  timezone?: string    // IANA timezone
}
```

**Validation Rules:**

1. **kind**: MUST be "time"

2. **schedule**: MUST be valid cron expression
   ```
   - Format: "minute hour day month weekday" (5 fields)
   - Alternative: "second minute hour day month weekday" (6 fields)
   - Each field: * or specific value or range
   - Examples: "0 9 * * *" (9am daily), "*/15 * * * *" (every 15 minutes)
   - Validate syntax: parse and verify field count
   ```

   **Cron Field Ranges:**
   | Field | Range | Special Values |
   |-------|-------|----------------|
   | Minute | 0-59 | * / , - |
   | Hour | 0-23 | * / , - |
   | Day | 1-31 | * / , - L W |
   | Month | 1-12 | * / , - JAN-DEC |
   | Weekday | 0-6 | * / , - SUN-SAT |

3. **timezone** (optional):
   ```
   - MUST be valid IANA timezone
   - Examples: "America/New_York", "Europe/London", "UTC"
   - Default: "UTC" if omitted
   - Validate by checking against IANA timezone database
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "time",
  "schedule": "0 9 * * 1-5",
  "timezone": "America/New_York"
}
```

**Invalid - Invalid Cron:**
```json
{
  "kind": "time",
  "schedule": "0 0 0 0 0 0 0"
}
// Error: "schedule: invalid cron expression (expected 5 or 6 fields, got 7)"
```

**Invalid - Field Out of Range:**
```json
{
  "kind": "time",
  "schedule": "60 9 * * *"
}
// Error: "schedule: minute field out of range (expected 0-59, got 60)"
```

**Invalid - Timezone:**
```json
{
  "kind": "time",
  "schedule": "0 9 * * *",
  "timezone": "Invalid/Timezone"
}
// Error: "timezone: not a valid IANA timezone"
```

### EventCondition Validation

**Required**: `kind`, `eventTypes`

```typescript
{
  kind: "event",
  eventTypes: EventType[]
}
```

**Validation Rules:**

1. **kind**: MUST be "event"

2. **eventTypes**: MUST be non-empty array
   ```
   - Each value MUST be valid EventType enum
   - Valid values: "run.started", "run.completed", "run.failed", "message.created", "tool.called", etc.
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "event",
  "eventTypes": ["message.created", "message.updated"]
}
```

**Invalid - Empty Array:**
```json
{
  "kind": "event",
  "eventTypes": []
}
// Error: "eventTypes must be non-empty array"
```

**Invalid - Invalid EventType:**
```json
{
  "kind": "event",
  "eventTypes": ["invalid_event"]
}
// Error: "eventTypes[0]: invalid EventType value"
```

### ExpressionCondition Validation

**Required**: `kind`, `expression`

```typescript
{
  kind: "expression",
  expression: string  // CEL expression
}
```

**Validation Rules:**

1. **kind**: MUST be "expression"

2. **expression**: MUST be valid CEL syntax
   ```
   - Same validation as HookCondition ExpressionCondition
   - Validate CEL syntax before execution
   - Expression MUST return boolean type
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "expression",
  "expression": "event.threadId == 'thread_123' && event.role == 'user'"
}
```

**Invalid - Syntax Error:**
```json
{
  "kind": "expression",
  "expression": "event.threadId =="
}
// Error: "expression: syntax error - incomplete expression"
```

### ContentCondition Validation

**Required**: `kind`, `patterns`

```typescript
{
  kind: "content",
  patterns: string[]  // Regex patterns
}
```

**Validation Rules:**

1. **kind**: MUST be "content"

2. **patterns**: MUST be non-empty array
   ```
   - Each pattern MUST be valid regex
   - Same validation as HookCondition ContentCondition
   ```

**Examples:**

**Valid:**
```json
{
  "kind": "content",
  "patterns": ["@agent", "help"]
}
```

**Invalid - Invalid Regex:**
```json
{
  "kind": "content",
  "patterns": ["(unclosed"]
}
// Error: "patterns[0]: invalid regex syntax - unterminated group"
```

### RemoteCondition Validation

**Required**: `kind`, `endpoint`

```typescript
{
  kind: "remote",
  endpoint: RemoteEndpoint
}
```

**Validation Rules:**

1. **kind**: MUST be "remote"

2. **endpoint**: MUST be valid RemoteEndpoint
   - See "Remote Endpoint Validation" section below

**Examples:**

**Valid:**
```json
{
  "kind": "remote",
  "endpoint": {
    "protocol": "http",
    "url": "https://conditions.example.com/evaluate",
    "httpMethod": "POST"
  }
}
```

**Invalid - Missing Endpoint:**
```json
{
  "kind": "remote"
}
// Error: "endpoint is required for RemoteCondition"
```

### AlwaysCondition / NeverCondition Validation

**Required**: `kind`

```typescript
{ kind: "always" }
{ kind: "never" }
```

**Validation Rules:**

1. **kind**: MUST be "always" or "never"
2. No additional fields allowed

**Examples:**
```json
{"kind": "always"}
{"kind": "never"}
```

## Auto-Response Validation

### Overview

Auto-response configurations enable agents to automatically respond to thread events. This section defines validation rules for ThreadWatch and AutoResponseConfig.

**Related Specifications:**
- [Agent Auto-Response Specification](./agent-auto-response.md) - Complete auto-response documentation

### ThreadWatch Validation

**Required**: `threadId`, `agentId`, `enabled`, `condition`

```typescript
{
  threadId: string,
  agentId: string,
  enabled: boolean,
  condition: RunCondition,
  maxConsecutiveRuns?: number
}
```

**Validation Rules:**

1. **threadId**: MUST reference existing thread
   ```
   - MUST be valid thread ID
   - Thread MUST NOT be archived
   - User MUST have access to thread
   ```

2. **agentId**: MUST reference existing agent
   ```
   - MUST be valid agent ID
   - Agent MUST be accessible by user
   ```

3. **enabled**: MUST be boolean

4. **condition**: MUST be valid RunCondition
   - See "Condition Validation" section above

5. **maxConsecutiveRuns** (optional):
   ```
   - MUST be >= 1
   - MUST be <= 100
   - Default: 10 (if omitted)
   ```

**Examples:**

**Valid:**
```json
{
  "threadId": "thread_123",
  "agentId": "agent_456",
  "enabled": true,
  "condition": {
    "kind": "event",
    "eventTypes": ["message.created"]
  },
  "maxConsecutiveRuns": 5
}
```

**Invalid - Thread Not Found:**
```json
{
  "threadId": "thread_nonexistent",
  "agentId": "agent_456",
  "enabled": true,
  "condition": {"kind": "always"}
}
// Error: "threadId does not reference existing thread"
```

**Invalid - Excessive Consecutive Runs:**
```json
{
  "threadId": "thread_123",
  "agentId": "agent_456",
  "enabled": true,
  "condition": {"kind": "always"},
  "maxConsecutiveRuns": 500
}
// Error: "maxConsecutiveRuns must be between 1 and 100"
```

### AutoResponseConfig Validation

**Required**: `enabled`, `conditions` (if enabled is true)

```typescript
{
  enabled: boolean,
  conditions?: RunCondition[],
  maxConsecutiveRuns?: number
}
```

**Validation Rules:**

1. **enabled**: MUST be boolean

2. **conditions** (conditionally required):
   ```
   IF enabled is true:
     - MUST be non-empty array
     - Each condition MUST be valid RunCondition
   IF enabled is false:
     - Optional (ignored if provided)
   ```

3. **maxConsecutiveRuns** (optional):
   ```
   - MUST be >= 1
   - MUST be <= 100
   - Default: 10 (if omitted)
   ```

**Examples:**

**Valid:**
```json
{
  "enabled": true,
  "conditions": [
    {"kind": "event", "eventTypes": ["message.created"]},
    {"kind": "content", "patterns": ["@agent"]}
  ],
  "maxConsecutiveRuns": 5
}
```

**Valid - Disabled:**
```json
{
  "enabled": false
}
```

**Invalid - Missing Conditions:**
```json
{
  "enabled": true
}
// Error: "conditions is required when enabled is true"
```

**Invalid - Empty Conditions:**
```json
{
  "enabled": true,
  "conditions": []
}
// Error: "conditions must be non-empty array when enabled is true"
```

**Invalid - Excessive Consecutive Runs:**
```json
{
  "enabled": true,
  "conditions": [{"kind": "always"}],
  "maxConsecutiveRuns": 200
}
// Error: "maxConsecutiveRuns must be between 1 and 100"
```

## Remote Endpoint Validation

### Overview

Remote endpoints enable integration with external services for remote hooks and conditions. This section defines validation rules for WebSocket and HTTP endpoints.

**Related Specifications:**
- [Remote Endpoints Specification](./remote-endpoints.md) - Complete protocol documentation

### RemoteEndpoint Union

```typescript
type RemoteEndpoint = WebSocketEndpoint | HttpEndpoint
```

**Validation**: MUST be one of the 2 endpoint types (discriminated by `protocol` field)

### WebSocketEndpoint Validation

**Required**: `protocol`, `url`

```typescript
{
  protocol: "websocket",
  url: string  // ws:// or wss://
}
```

**Validation Rules:**

1. **protocol**: MUST be "websocket"

2. **url**: MUST be valid WebSocket URL
   ```
   - MUST start with "wss://" (secure)
   - MAY start with "ws://" (non-secure, development only)
   - Recommendation: REJECT "ws://" in production for security
   - MUST be valid URL format (parse without error)
   - Max length: 2048 characters
   ```

**Examples:**

**Valid:**
```json
{
  "protocol": "websocket",
  "url": "wss://hooks.example.com/evaluate"
}
```

**Invalid - Non-Secure URL (Production):**
```json
{
  "protocol": "websocket",
  "url": "ws://hooks.example.com"
}
// Warning (or Error in production): "WebSocket URL should use wss:// for security"
```

**Invalid - Invalid URL:**
```json
{
  "protocol": "websocket",
  "url": "https://hooks.example.com"
}
// Error: "url must start with ws:// or wss:// for WebSocket protocol"
```

**Invalid - Malformed URL:**
```json
{
  "protocol": "websocket",
  "url": "wss://invalid url with spaces"
}
// Error: "url: invalid URL format"
```

### HttpEndpoint Validation

**Required**: `protocol`, `url`, `httpMethod`

```typescript
{
  protocol: "http",
  url: string,
  httpMethod: "POST" | "GET",
  headers?: Record<string, string>
}
```

**Validation Rules:**

1. **protocol**: MUST be "http"

2. **url**: MUST be valid HTTPS URL
   ```
   - MUST start with "https://" (secure)
   - MUST NOT use "http://" (reject for security)
   - MUST be valid URL format
   - Max length: 2048 characters
   ```

3. **httpMethod**: MUST be "POST" or "GET"

4. **headers** (optional):
   ```
   - Keys MUST be valid HTTP header names
   - Header names MUST be lowercase
   - Header names MUST match: ^[a-z0-9-]+$
   - Values MUST be non-empty strings
   ```

**Examples:**

**Valid:**
```json
{
  "protocol": "http",
  "url": "https://hooks.example.com/evaluate",
  "httpMethod": "POST",
  "headers": {
    "authorization": "Bearer token123",
    "x-custom-header": "value"
  }
}
```

**Invalid - Non-Secure URL:**
```json
{
  "protocol": "http",
  "url": "http://hooks.example.com",
  "httpMethod": "POST"
}
// Error: "url must use https:// for security"
```

**Invalid - Invalid HTTP Method:**
```json
{
  "protocol": "http",
  "url": "https://hooks.example.com",
  "httpMethod": "PUT"
}
// Error: "httpMethod must be 'POST' or 'GET'"
```

**Invalid - Invalid Header Name:**
```json
{
  "protocol": "http",
  "url": "https://hooks.example.com",
  "httpMethod": "POST",
  "headers": {
    "Invalid Header": "value"
  }
}
// Error: "headers: invalid header name 'Invalid Header' (must be lowercase alphanumeric + hyphen)"
```

**Invalid - Empty Header Value:**
```json
{
  "protocol": "http",
  "url": "https://hooks.example.com",
  "httpMethod": "POST",
  "headers": {
    "authorization": ""
  }
}
// Error: "headers.authorization: value must be non-empty string"
```

### WebSocket Message Validation

**Request Message:**
```typescript
{
  requestId: string,
  event: EventType,
  data: unknown
}
```

**Validation Rules:**

1. **requestId**: MUST be non-empty string
   ```
   - Used to correlate request/response
   - Client-generated (UUID recommended)
   ```

2. **event**: MUST be valid EventType enum

3. **data**: MUST be valid event data
   ```
   - Structure depends on event type
   - Validate against event-specific schema
   ```

**Response Message:**
```typescript
{
  requestId: string,
  response: HookActionResponse
}
```

**Validation Rules:**

1. **requestId**: MUST match request requestId

2. **response**: MUST be valid HookActionResponse
   - See "HookActionResponse Validation" below

### HTTP Request/Response Validation

**Request Body:**
```json
{
  "event": "tool.called",
  "data": { ... }
}
```

**Validation Rules:**

1. **event**: MUST be valid EventType enum

2. **data**: MUST be valid event data

**Response Body:**
```json
{
  "kind": "block",
  "reason": "Policy violation"
}
```

**Validation Rules:**

1. MUST be valid HookActionResponse

### HookActionResponse Validation

**Response Union:**
```typescript
type HookActionResponse = AllowResponse | BlockResponse | ModifyResponse
```

**AllowResponse:**
```typescript
{
  kind: "allow"
}
```

**Validation**: kind MUST be "allow", no additional fields

**BlockResponse:**
```typescript
{
  kind: "block",
  reason?: string
}
```

**Validation:**
- kind MUST be "block"
- reason is optional string (human-readable explanation)

**ModifyResponse:**
```typescript
{
  kind: "modify",
  content: unknown
}
```

**Validation:**
- kind MUST be "modify"
- content MUST be provided (event-specific modification)

**Examples:**

**Valid:**
```json
{"kind": "allow"}
{"kind": "block", "reason": "Content policy violation"}
{"kind": "modify", "content": {"text": "[REDACTED]"}}
```

**Invalid - Missing Content:**
```json
{
  "kind": "modify"
}
// Error: "content is required for ModifyResponse"
```

**Invalid - Unknown Kind:**
```json
{
  "kind": "unknown"
}
// Error: "kind must be 'allow', 'block', or 'modify'"
```

## Resource Limits

### Message Limits

| Resource | Limit | Error Code |
|----------|-------|------------|
| Text content length | 100,000 chars | `TEXT_TOO_LONG` |
| Image data size | 10 MB | `IMAGE_TOO_LARGE` |
| Audio data size | 50 MB | `AUDIO_TOO_LARGE` |
| Video data size | 100 MB | `VIDEO_TOO_LARGE` |
| Contents per message | 100 items | `TOO_MANY_CONTENTS` |
| Messages per request | 1,000 messages | `TOO_MANY_MESSAGES` |

### Run Limits

| Resource | Limit | Error Code |
|----------|-------|------------|
| Max turns per run | 100 turns | `MAX_TURNS_EXCEEDED` |
| Max tokens per run | 1,000,000 tokens | `CONTEXT_LENGTH_EXCEEDED` |
| Max parallel tool calls | 10 calls | `TOO_MANY_TOOL_CALLS` |
| Max tool argument size | 100 KB | `TOOL_ARGUMENT_TOO_LARGE` |
| Max tool result size | 1 MB | `TOOL_RESULT_TOO_LARGE` |

### Agent Limits

| Resource | Limit | Error Code |
|----------|-------|------------|
| Agent instructions length | 50,000 chars | `INSTRUCTIONS_TOO_LONG` |
| Tools per agent | 100 tools | `TOO_MANY_TOOLS` |
| Scopes per agent | 50 scopes | `TOO_MANY_SCOPES` |

## Validation Error Format

### Error Response

**Structure:**
```typescript
{
  error: {
    code: string;               // Machine-readable code
    message: string;            // Human-readable message
    field?: string;             // Field that failed validation
    details?: Record<unknown>;  // Additional context
  }
}
```

**Example:**
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Validation failed for field 'input'",
    "field": "input[0].contents",
    "details": {
      "reason": "contents must be non-empty array",
      "provided": []
    }
  }
}
```

### Validation Error Codes

#### Generic Validation Codes

| Code | Description |
|------|-------------|
| `INVALID_INPUT` | Generic input validation failure |
| `REQUIRED_FIELD_MISSING` | Required field not provided |
| `INVALID_FIELD_TYPE` | Field type doesn't match schema |
| `INVALID_ENUM_VALUE` | Enum value not recognized |
| `INVALID_FORMAT` | Format validation failed (URI, date, etc.) |
| `RESOURCE_NOT_FOUND` | Referenced resource doesn't exist |
| `INVALID_STATE` | Operation not valid in current state |
| `LIMIT_EXCEEDED` | Resource limit exceeded |
| `SCHEMA_VALIDATION_FAILED` | JSON Schema validation failed |
| `VALIDATION_FAILED` | Generic validation failure |

#### Hook Validation Codes

| Code | Description |
|------|-------------|
| `HOOK_VALIDATION_FAILED` | Generic hook validation failure |
| `INVALID_HOOK_KIND` | Hook kind not recognized |
| `INVALID_EVENT_TYPE` | EventType not recognized |
| `INVALID_HOOK_CONDITION` | HookCondition validation failed |
| `INVALID_REGEX_PATTERN` | Regex pattern syntax error |
| `INVALID_CEL_EXPRESSION` | CEL expression syntax error |
| `HOOK_TIMEOUT_INVALID` | Timeout out of range (1-30 seconds) |

#### Condition Validation Codes

| Code | Description |
|------|-------------|
| `CONDITION_VALIDATION_FAILED` | Generic condition validation failure |
| `INVALID_CONDITION_KIND` | Condition kind not recognized |
| `INVALID_CRON_EXPRESSION` | Cron expression syntax error |
| `INVALID_TIMEZONE` | IANA timezone not recognized |

#### Auto-Response Validation Codes

| Code | Description |
|------|-------------|
| `AUTO_RESPONSE_VALIDATION_FAILED` | Generic auto-response validation failure |
| `MAX_CONSECUTIVE_RUNS_EXCEEDED` | Consecutive run limit exceeded (1-100) |

#### Endpoint Validation Codes

| Code | Description |
|------|-------------|
| `ENDPOINT_VALIDATION_FAILED` | Generic endpoint validation failure |
| `INVALID_ENDPOINT_PROTOCOL` | Protocol not recognized |
| `INVALID_WEBSOCKET_URL` | WebSocket URL format invalid |
| `INVALID_HTTP_URL` | HTTP URL format invalid |
| `INSECURE_ENDPOINT_URL` | URL does not use secure protocol |
| `INVALID_ENDPOINT_URL` | Endpoint URL validation failed |

## Requirements

### Server Requirements

Servers MUST:

1. **Validate All Inputs**: Check all API inputs before processing
2. **Fail Fast**: Reject invalid requests immediately (don't process)
3. **Clear Errors**: Return actionable error messages with field names
4. **Enforce Limits**: Enforce all resource limits
5. **Schema Validation**: Validate against JSON Schema

Servers SHOULD:

1. **Cache Validation**: Cache validation results for performance
2. **Partial Validation**: Validate fields incrementally (streaming)
3. **Sanitize Inputs**: Sanitize user inputs to prevent injection

### Client Requirements

Clients SHOULD:

1. **Pre-Validate**: Validate inputs before sending to server
2. **Handle Errors**: Display validation errors to users
3. **Retry Logic**: Don't retry validation errors (fix input first)

## JSON Schema Validation

### Tool Parameters

**Example Schema:**
```json
{
  "type": "object",
  "properties": {
    "query": {
      "type": "string",
      "description": "Search query",
      "minLength": 1,
      "maxLength": 500
    },
    "limit": {
      "type": "integer",
      "description": "Max results",
      "minimum": 1,
      "maximum": 100,
      "default": 10
    }
  },
  "required": ["query"],
  "additionalProperties": false
}
```

**Validation:**
```
- "type" MUST be present
- "properties" MUST be object
- "required" MUST be array of strings
- Each property MUST have valid JSON Schema
```

### PropertySchema (Agent Input/Output)

**Alias to JSONSchema**: `alias PropertySchema = JSONSchema;`

**Validation**: Same as tool parameters (JSON Schema Draft 7)

## Best Practices

### Fail Fast

**Good:**
```python
def create_run(request):
    validate_agent_id(request.agent_id)  # Fail immediately
    validate_input_messages(request.input)
    validate_thread_id(request.thread_id)

    # Only proceed if all validation passes
    return execute_run(request)
```

**Bad:**
```python
def create_run(request):
    # Process first, validate later
    result = execute_run(request)
    validate_agent_id(request.agent_id)  # Too late!
    return result
```

### Clear Error Messages

**Good:**
```json
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Field 'input[0].role' must be one of: user, system, developer, assistant, tool",
    "field": "input[0].role",
    "details": { "provided": "invalid_role", "allowed": ["user", "system", ...] }
  }
}
```

**Bad:**
```json
{
  "error": {
    "code": "ERROR",
    "message": "Invalid request"
  }
}
```

### Schema-Driven Validation

**Use JSON Schema**: Define validation rules in schema
```json
{
  "type": "string",
  "minLength": 1,
  "maxLength": 1000,
  "pattern": "^[a-zA-Z0-9_-]+$"
}
```

**Not in Code**: Don't hardcode validation logic
```python
# Bad
if len(name) < 1 or len(name) > 1000:
    raise ValidationError("Name too long/short")
```

## Compliance

This specification aligns with:
- **TypeSpec**: All models in `typespec/` directory
- **JSON Schema**: Draft 7 for parameter validation
- **OpenAPI 3.0**: Scope format, validation patterns
- **RFC 7807**: Problem Details for HTTP APIs (error format)

## See Also

- [Run Lifecycle](./run-lifecycle.md) - Run validation rules
- [Message Lifecycle](./message-lifecycle.md) - Message validation rules
- [Tool Execution](./tool-execution.md) - Tool validation rules
- [Authentication](./authentication.md) - Connection validation rules
- [Error Handling](./error-handling.md) - Validation error codes
