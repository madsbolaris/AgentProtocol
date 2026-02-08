# Proactive Messaging Guide

## Overview

Proactive messaging enables agents to respond automatically to external events, scheduled triggers, and system alerts without manual intervention. This guide covers three key patterns:

1. **Thread Watch Pattern**: Agents monitor threads and automatically create runs when conditions are met
2. **Webhook Completion Notifications**: Server notifies clients when runs complete
3. **External Event Triggers**: External systems inject events that trigger agent runs

### Key Concepts

**Thread Watch**: Agents subscribe to monitor threads using `POST /threads/{threadId}/watch`. When new messages arrive matching the agent's run conditions, the server automatically creates a run for that agent.

**Webhook Notifications**: When a run completes, the server POSTs a notification to the webhook URL specified in the run request.

**Event-Triggered Runs**: External events (timers, webhooks, system alerts) create messages with `role="channel"` and `EventContent`, which can trigger agent runs.

**Thread Subscriptions**: Clients subscribe to thread activity via `POST /threads/{threadId}/subscriptions` to receive real-time notifications.

---

## Architecture

### Pattern 1: Thread Watch (Auto-Response)

```
1. Agent subscribes to monitor thread
   POST /threads/{threadId}/watch
   {
     "agentId": "agent-456"
   }

2. New message arrives in thread
   POST /threads/{threadId}/messages
   {
     "role": "user",
     "contents": [{ "kind": "text", "text": "Hello" }]
   }

3. Server automatically creates run
   (Internal) POST /runs
   {
     "threadId": "{threadId}",
     "agentId": "agent-456",
     "input": [new_message]
   }

4. Agent processes and responds
   Run executes, agent adds response to thread
```

### Pattern 2: Webhook Completion Notifications

```
1. Create run with webhook URL
   POST /runs
   {
     "threadId": "thread-123",
     "agentId": "agent-456",
     "input": [{ "role": "user", "contents": [...] }],
     "webhook": "https://example.com/webhook"
   }

2. Server executes run asynchronously
   Run status: queued → in_progress → completed

3. Server POSTs to webhook on completion
   POST https://example.com/webhook
   {
     "runId": "run-789",
     "status": "completed",
     "timestamp": "2026-02-07T10:00:00Z"
   }

4. Client fetches run results
   GET /runs/run-789
```

### Pattern 3: External Event Triggers

```
1. External system posts event to thread
   POST /threads/{threadId}/messages
   {
     "role": "channel",
     "contents": [{
       "kind": "event",
       "name": "cpu_threshold_exceeded",
       "value": { "cpu": "95%", "host": "web-01" }
     }]
   }

2. Agent watching thread creates run
   (If agent is watching with runCondition matching channel role)

3. Agent processes event and responds
   Run executes, agent posts analysis to thread

4. Optional: Webhook notification sent
   (If ThreadSubscription exists with webhookUrl)
```

---

## Use Cases

### 1. Customer Support Agent

**Scenario**: Agent automatically responds to support messages

```json
// Setup: Subscribe agent to watch thread
POST /threads/thread-support-123/watch
{
  "agentId": "agent-support"
}

// Agent must have autoResponseConfig with runCondition:
// { "kind": "roles", "config": { "roles": ["user"] } }

// Usage: User sends message
POST /threads/thread-support-123/messages
{
  "role": "user",
  "contents": [{ "kind": "text", "text": "I need help with my order" }]
}

// Result: Agent automatically responds
// Server evaluates agent's runCondition, creates run, agent processes message
```

### 2. Monitoring Agent with Proactive Runs

**Scenario**: External monitoring system triggers agent via events

```json
// Setup 1: Agent configured with auto-response for channel events
// autoResponseConfig: { "runCondition": { "kind": "roles", "config": { "roles": ["channel"] } } }

// Setup 2: Subscribe agent to watch monitoring thread
POST /threads/thread-monitoring/watch
{
  "agentId": "agent-monitor"
}

// Setup 3: Client subscribes for completion notifications
POST /threads/thread-monitoring/subscriptions
{
  "webhookUrl": "https://ops.example.com/webhook",
  "events": ["run.completed", "run.failed"]
}

// Trigger: Monitoring system posts alert
POST /threads/thread-monitoring/messages
{
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "cpu_threshold_exceeded",
    "value": { "cpu": "95%", "host": "web-01" }
  }]
}

// Result 1: Agent automatically creates run and analyzes alert
// Result 2: Webhook notification sent to ops.example.com when run completes
```

### 3. Scheduled Task Agent

**Scenario**: Timer triggers daily report generation

```json
// Setup 1: Agent configured with auto-response for channel events
// autoResponseConfig: { "runCondition": { "kind": "roles", "config": { "roles": ["channel"] } } }

// Setup 2: Subscribe agent to watch thread
POST /threads/thread-tasks/watch
{
  "agentId": "agent-scheduler"
}

// Trigger: Scheduler posts daily event
POST /threads/thread-tasks/messages
{
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "daily_report_trigger",
    "value": { "time": "09:00", "date": "2026-02-07" }
  }]
}

// Result: Agent generates and posts daily report
```

### 4. Background Task with Webhook Notification

**Scenario**: Long-running task with completion notification

```json
// Create run with webhook for completion notification
POST /runs
{
  "threadId": "thread-123",
  "agentId": "agent-worker",
  "input": [{
    "role": "user",
    "contents": [{ "kind": "text", "text": "Generate quarterly report" }]
  }],
  "webhook": "https://app.example.com/webhook"
}

// Response: Run created, executes asynchronously
{
  "runId": "run-789",
  "status": "queued",
  "createdAt": "2026-02-07T10:00:00Z"
}

// Webhook notification when complete
POST https://app.example.com/webhook
{
  "runId": "run-789",
  "status": "completed",
  "timestamp": "2026-02-07T10:05:00Z"
}

// Client fetches results
GET /runs/run-789
```

---

## API Reference

### Thread Watch Operations

#### Subscribe Agent to Thread

**Endpoint**: `POST /threads/{threadId}/watch`

**Purpose**: Subscribe an agent to watch a specific thread for auto-response

**Request Body**:
```json
{
  "agentId": "agent-123"
}
```

**Response** (201 Created):
```json
{
  "watchId": "watch-789",
  "threadId": "thread-123",
  "agentId": "agent-123",
  "active": true,
  "createdAt": "2026-02-07T10:00:00Z",
  "activationCount": 0
}
```

**Requirements**:
- Agent must have `autoResponseConfig` with `runCondition` defined
- Agent's `runCondition` determines when the agent responds

#### List Thread Watchers

**Endpoint**: `GET /threads/{threadId}/watch`

**Response** (200 OK):
```json
[
  {
    "watchId": "watch-789",
    "threadId": "thread-123",
    "agentId": "agent-123",
    "active": true,
    "createdAt": "2026-02-07T10:00:00Z",
    "activationCount": 42
  }
]
```

#### Unsubscribe Agent from Thread

**Endpoint**: `DELETE /threads/{threadId}/watch/{agentId}`

**Response**: 204 No Content

---

### Thread Subscriptions (Client Notifications)

#### Create Thread Subscription

**Endpoint**: `POST /threads/{threadId}/subscriptions`

**Purpose**: Subscribe to receive webhook notifications for thread activity

**Request Body**:
```json
{
  "webhookUrl": "https://example.com/webhook",
  "webhookSecret": "secret_xyz",
  "events": ["message.created", "run.completed", "run.failed"],
  "messageFilters": {
    "roles": ["assistant"]
  }
}
```

**Response** (201 Created):
```json
{
  "subscriptionId": "sub-456",
  "threadId": "thread-123",
  "webhookUrl": "https://example.com/webhook",
  "events": ["message.created", "run.completed", "run.failed"],
  "active": true,
  "createdAt": "2026-02-07T10:00:00Z"
}
```

**Webhook Notification Format**:
```json
{
  "kind": "thread.activity",
  "resourceId": "thread-123",
  "subscriptionId": "sub-456",
  "eventType": "run.completed",
  "sequenceNumber": 42,
  "eventSeq": 10,
  "timestamp": "2026-02-07T10:00:00Z",
  "data": {
    "runId": "run-789",
    "status": "completed"
  }
}
```

#### List Thread Subscriptions

**Endpoint**: `GET /threads/{threadId}/subscriptions`

**Response** (200 OK):
```json
[
  {
    "subscriptionId": "sub-456",
    "threadId": "thread-123",
    "webhookUrl": "https://example.com/webhook",
    "events": ["message.created", "run.completed"],
    "active": true,
    "createdAt": "2026-02-07T10:00:00Z"
  }
]
```

#### Delete Thread Subscription

**Endpoint**: `DELETE /threads/{threadId}/subscriptions/{subscriptionId}`

**Response**: 204 No Content

---

### Run Webhook Notifications

#### Create Run with Webhook

**Endpoint**: `POST /runs`

**Request Body**:
```json
{
  "threadId": "thread-123",
  "agentId": "agent-456",
  "input": [{
    "role": "user",
    "contents": [{ "kind": "text", "text": "Generate report" }]
  }],
  "webhook": "https://example.com/webhook"
}
```

**Response** (202 Accepted):
```json
{
  "runId": "run-789",
  "status": "queued",
  "createdAt": "2026-02-07T10:00:00Z"
}
```

**Webhook Notification** (when run completes):
```
POST https://example.com/webhook

{
  "runId": "run-789",
  "status": "completed",
  "timestamp": "2026-02-07T10:05:00Z"
}
```

**Client Action**: Fetch run results via `GET /runs/{runId}`

---

### External Event Messages

#### Post Event to Thread

**Endpoint**: `POST /threads/{threadId}/messages`

**Purpose**: Inject external event that can trigger agent runs

**Request Body**:
```json
{
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "cpu_threshold_exceeded",
    "value": {
      "cpu": "95%",
      "host": "web-01",
      "timestamp": "2026-02-07T10:00:00Z"
    }
  }]
}
```

**Response** (201 Created):
```json
{
  "messageId": "msg-123",
  "threadId": "thread-456",
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "cpu_threshold_exceeded",
    "value": { "cpu": "95%", "host": "web-01" }
  }],
  "createdAt": "2026-02-07T10:00:00Z"
}
```

**Key Properties**:
- `role="channel"`: Marks message as external event (not sent to LLM)
- `EventContent`: Structured event data with name and value
- Stored in thread history for audit trail
- Can trigger agents watching with `runCondition` matching `channel` role

---

## Run Conditions

Configure when agents should respond using flexible condition types.

### Condition Type: Roles

Respond to messages with specific roles:

```json
{
  "kind": "roles",
  "config": { "roles": ["user"] }
}
```

| Role | Description | Typical Use |
|------|-------------|-------------|
| `user` | User messages | Chat applications, support |
| `channel` | External events/triggers | Monitoring, scheduled tasks |
| `assistant` | Other agent responses | Multi-agent workflows |
| `tool` | Tool execution results | Tool monitoring |
| `system` | System messages | Admin triggers |
| `developer` | Developer messages | Debug/control |

**Default**: When `runCondition` is omitted, responds to messages with `role="user"`

**Examples**:
- `{"kind": "roles", "config": {"roles": ["user"]}}`: Chat agent responding to users
- `{"kind": "roles", "config": {"roles": ["channel"]}}`: Monitoring agent processing events only
- `{"kind": "roles", "config": {"roles": ["user", "channel"]}}`: Hybrid agent handling both

### Condition Type: Content

Respond to specific content types:

```json
{
  "kind": "content",
  "config": { "contentTypes": ["video", "image"] }
}
```

### Condition Type: Mention

Respond when explicitly mentioned:

```json
{
  "kind": "mention",
  "config": { "requireExplicitMention": true }
}
```

### Advanced Condition Types

**Webhook**: Custom logic via HTTP endpoint
```json
{
  "kind": "webhook",
  "config": {
    "evaluatorUrl": "https://app.example.com/evaluate",
    "evaluatorSecret": "secret123"
  }
}
```

**Expression**: Custom expression evaluation
```json
{
  "kind": "expression",
  "config": {
    "expression": "message.role == 'user' && message.text.contains('help')"
  }
}
```

---

## Event Content Reference

### EventContent Model

From `typespec/messages.tsp` (lines 1205-1222):

```typescript
model EventContent {
  kind: "event";

  /** Event name */
  name: string;

  /** Event payload */
  value?: Record<unknown>;

  /** Human-readable description */
  text?: string;

  /** Event timestamp */
  timestamp?: utcDateTime;

  /** Additional properties */
  additionalProperties?: Record<unknown>;
}
```

### Event Message Pattern

Messages with `role="channel"` represent external events/triggers:
- **Stored in thread history** (for context and audit trail)
- **NOT sent to LLM** (filtered from LLM context)
- **Used as triggers** for agent auto-responders

### Creating Event Messages

```json
POST /threads/{threadId}/messages
{
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "scheduled_trigger",
    "value": {
      "triggerName": "daily_report",
      "time": "09:00"
    }
  }]
}
```

### Common Event Types

**System Alerts**:
```json
{
  "kind": "event",
  "name": "cpu_threshold_exceeded",
  "value": { "cpu": "95%", "host": "web-01" }
}
```

**Scheduled Triggers**:
```json
{
  "kind": "event",
  "name": "daily_report_trigger",
  "value": { "time": "09:00", "date": "2026-02-07" }
}
```

**Webhook Events**:
```json
{
  "kind": "event",
  "name": "payment_received",
  "value": { "amount": 99.99, "currency": "USD", "orderId": "order-123" }
}
```

**Lifecycle Events**:
```json
{
  "kind": "event",
  "name": "participant_added",
  "value": { "userId": "user-456", "role": "user" }
}
```

---

## Webhook Security

### Signature Validation

Use `webhookSecret` for HMAC-SHA256 signature validation:

```
X-Signature: sha256=<hmac_signature>
```

**Verification Example** (Python):
```python
import hmac
import hashlib

def verify_webhook(payload: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)
```

**Verification Example** (Node.js):
```javascript
const crypto = require('crypto');

function verifyWebhook(payload, signature, secret) {
  const expected = crypto
    .createHmac('sha256', secret)
    .update(payload)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(`sha256=${expected}`),
    Buffer.from(signature)
  );
}
```

---

## Best Practices

### 1. Use Specific Run Conditions

```json
// Good: Specific to user messages
{
  "runCondition": {
    "kind": "roles",
    "config": { "roles": ["user"] }
  }
}

// Avoid: Too broad, agent responds to everything
{
  "runCondition": {
    "kind": "roles",
    "config": { "roles": ["user", "assistant", "tool", "channel"] }
  }
}
```

### 2. Combine Thread Watch and Webhooks

```json
// Agent watches thread for auto-response
POST /threads/{threadId}/watch
{ "agentId": "agent-support" }

// Client subscribes for completion notifications
POST /threads/{threadId}/subscriptions
{
  "webhookUrl": "https://app.example.com/webhook",
  "events": ["run.completed", "run.failed"]
}
```

### 3. Use Webhook Notifications for Long-Running Tasks

```json
// Create run with webhook
POST /runs
{
  "threadId": "thread-123",
  "agentId": "agent-worker",
  "input": [{ "role": "user", "contents": [...] }],
  "webhook": "https://app.example.com/webhook"
}

// Get notified when run completes
// Avoid polling via GET /runs/{runId}
```

### 4. Filter Thread Subscriptions

```json
// Subscribe only to agent responses and failures
POST /threads/{threadId}/subscriptions
{
  "webhookUrl": "https://app.example.com/webhook",
  "events": ["run.completed", "run.failed"],
  "messageFilters": {
    "roles": ["assistant"]
  }
}
```

### 5. Multi-Agent Coordination

```json
// Primary agent handles user messages
POST /threads/{threadId}/watch
{
  "agentId": "agent-primary"
}
// Agent has runCondition: { "kind": "roles", "config": { "roles": ["user"] } }

// Background agent handles scheduled tasks
POST /threads/{threadId}/watch
{
  "agentId": "agent-background"
}
// Agent has runCondition: { "kind": "roles", "config": { "roles": ["channel"] } }
```

---

## Advanced Patterns

### Cascading Agents

Agent 1 completes → Agent 2 automatically triggers

```json
// Agent 1: Primary processor
POST /threads/{threadId}/watch
{
  "agentId": "agent-processor"
}
// runCondition: { "kind": "roles", "config": { "roles": ["user"] } }

// Agent 2: Monitors for agent-processor's responses
POST /threads/{threadId}/watch
{
  "agentId": "agent-reviewer"
}
// runCondition: { "kind": "roles", "config": { "roles": ["assistant"] } }
// Plus filter: metadata.monitorsFor = "agent-processor"

// Flow: User message → agent-processor responds → agent-reviewer validates
```

### Conditional Activation

Use webhook or expression conditions for complex logic:

```json
POST /threads/{threadId}/watch
{
  "agentId": "agent-conditional"
}

// Agent's runCondition:
{
  "kind": "expression",
  "config": {
    "expression": "message.role == 'channel' && message.contents[0].value.cpu > 90"
  }
}

// Agent only responds to channel messages with CPU > 90%
```

### Proactive Run Creation

Create runs without user input (triggered by external events):

```json
// Step 1: External event posts to thread
POST /threads/{threadId}/messages
{
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "threshold_exceeded",
    "value": { "metric": "cpu", "value": 95 }
  }]
}

// Step 2: Agent watching thread creates run automatically
// (Agent has runCondition: { "kind": "roles", "config": { "roles": ["channel"] } })

// Step 3: Agent processes event from thread history
// Run input includes recent messages from thread

// Step 4: Webhook notification sent (if ThreadSubscription exists)
```

---

## Troubleshooting

### Agent Not Triggering

**Check**:
1. Thread watch is `active: true` (`GET /threads/{threadId}/watch`)
2. Message matches agent's `runCondition` criteria
3. Agent exists and has `autoResponseConfig` defined
4. Thread exists
5. Check `maxConsecutiveRuns` hasn't been exceeded

```json
// Verify watch status
GET /threads/{threadId}/watch

// Check agent configuration
GET /agents/{agentId}/card

// Check if agent responded
GET /threads/{threadId}/messages
GET /threads/{threadId}/runs
```

### Webhook Not Firing

**Check**:
1. `webhookUrl` is HTTPS
2. Webhook endpoint is reachable
3. Check ThreadSubscription or Run webhook configuration
4. Verify webhook secret signature validation

```json
// Check thread subscriptions
GET /threads/{threadId}/subscriptions

// Check run webhook field
GET /runs/{runId}
```

### Too Many Triggers

**Solution**: Be more specific with run conditions

```json
// Too broad - triggers on everything
{
  "runCondition": {
    "kind": "roles",
    "config": { "roles": ["user", "assistant", "channel"] }
  }
}

// Better - specific to user messages
{
  "runCondition": {
    "kind": "roles",
    "config": { "roles": ["user"] }
  }
}
```

### Event Messages Not Triggering Agents

**Check**:
1. Message has `role="channel"`
2. Agent's `runCondition` includes `"channel"` role
3. Agent is watching the thread
4. Event content is properly formatted

```json
// Verify event message format
POST /threads/{threadId}/messages
{
  "role": "channel",  // Must be "channel"
  "contents": [{
    "kind": "event",  // Must be "event"
    "name": "event_name",
    "value": { ... }
  }]
}

// Verify agent runCondition includes channel
GET /agents/{agentId}/card
// Should have: runCondition.config.roles includes "channel"
```

---

## See Also

### TypeSpec Definitions
- **Execution & Runs**: `/Users/mabolan/AgentProtocol/typespec/execution.tsp` (Run model with webhook field, lines 378-389)
- **Thread Subscriptions**: `/Users/mabolan/AgentProtocol/typespec/subscriptions.tsp` (ThreadSubscription model, lines 138-301)
- **Event Content**: `/Users/mabolan/AgentProtocol/typespec/messages.tsp` (EventContent model, lines 1205-1222; ChatRole enum with channel, lines 316-338)

### API Reference
- **Thread Watch Operations**: `/Users/mabolan/AgentProtocol/api-reference/operations/post-threads-threadid-watch.md`
- **Thread Watch List**: `/Users/mabolan/AgentProtocol/api-reference/operations/get-threads-threadid-watch.md`
- **Thread Watch Delete**: `/Users/mabolan/AgentProtocol/api-reference/operations/delete-threads-threadid-watch-agentid.md`
- **Thread Subscriptions**: `/Users/mabolan/AgentProtocol/api-reference/operations/post-threads-threadid-subscriptions.md`
- **Run Creation**: `/Users/mabolan/AgentProtocol/api-reference/operations/post-runs.md`
- **Post Messages**: `/Users/mabolan/AgentProtocol/api-reference/operations/post-threads-threadid-messages.md`

### Related Guides
- **Agent Auto-Response**: `/Users/mabolan/AgentProtocol/specifications/agent-auto-response.md` (ThreadWatch and RunCondition details)
- **Message Lifecycle**: `/Users/mabolan/AgentProtocol/specifications/message-lifecycle.md`
- **Multi-Agent Guide**: `/Users/mabolan/AgentProtocol/guides/multi-agent.md` (Pattern 7: Auto-Response Coordination)

---
