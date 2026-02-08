# Webhook Subscriptions Guide

## Overview

Webhook subscriptions enable real-time notifications when activity occurs in runs, threads, or across all agent activity. Instead of polling for updates, clients register HTTPS endpoints to receive instant notifications when messages are created, runs complete, or configuration changes occur.

**Key Benefits:**
- **Real-time Updates**: Immediate notification when events occur (no polling delay)
- **Reduced Load**: Eliminate constant polling requests to check for updates
- **Event Filtering**: Subscribe only to relevant event types
- **Scalability**: Fan-out notifications to multiple subscribers
- **Reliability**: Built-in retry logic and failure tracking

Webhook subscriptions are a core component of **proactive messaging** (Phase 1), enabling agents to notify clients when agent-initiated runs complete.

## Webhooks vs Hooks System

**Important**: Webhook subscriptions and the hooks system are distinct features that serve different purposes. Understanding the difference is critical:

| Feature | Webhook Subscriptions | Hooks System |
|---------|---------------------|--------------|
| **Purpose** | Notification delivery | Event interception and policy enforcement |
| **Timing** | After events occur | Before/during event processing |
| **Direction** | Server → Client | Server evaluates conditions/executes hooks |
| **Behavior** | Passive observation | Active modification/blocking |
| **Use Case** | Real-time updates, monitoring | Content moderation, PII redaction, approvals |
| **Configuration** | `POST /threads/{threadId}/subscriptions` | Agent `hooks` array in configuration |
| **Delivery** | HTTP POST to your endpoint | Server-side evaluation |
| **Impact** | Cannot affect execution | Can block, modify, or allow execution |

### Webhook Subscriptions (This Guide)

**What**: Lightweight notifications sent AFTER events occur (run completed, message created, etc.)

**How**: Register HTTPS endpoint to receive JSON payloads when events happen

**Example**:

```json
// Create subscription
POST /threads/thread-123/subscriptions
{
  "webhookUrl": "https://myapp.com/notifications",
  "events": ["run.completed", "message.created"]
}

// Receive notification (AFTER run completes)
POST https://myapp.com/notifications
{
  "type": "thread.activity",
  "eventType": "run.completed",
  "threadId": "thread-123",
  "runId": "run-456"
}
```

**Key Characteristics**:

- Delivered after execution completes
- Cannot modify or block execution
- Used for monitoring, UI updates, workflow triggers
- Client fetches full data via GET endpoints

### Hooks System (See [Hooks Specification](../specifications/hooks.md))

**What**: Execution interception points that evaluate BEFORE/DURING event processing

**How**: Configure hooks in agent definition to intercept, modify, or block execution

**Example**:

```json
// Configure agent with hooks
POST /agents
{
  "name": "Moderated Agent",
  "model": "gpt-4o",
  "hooks": [
    {
      "kind": "block",
      "condition": {
        "kind": "content",
        "keywords": ["prohibited"]
      },
      "reason": "Content policy violation",
      "eventTypes": ["content.created"]
    }
  ]
}

// Run is BLOCKED before content is delivered to client
// No webhook notification sent because execution was blocked
```

**Key Characteristics**:

- Evaluated during execution (synchronous)
- Can block, modify, or allow execution
- Used for policy enforcement, content moderation, approvals
- Affects what client receives in streaming/final response

### When to Use Each

**Use Webhook Subscriptions When You Need:**

- Real-time notifications about completed events
- Multi-client synchronization (dashboard updates)
- Workflow orchestration (trigger next step after completion)
- Audit logging and compliance tracking
- Integration with external services (Slack, Teams, PagerDuty)

**Use Hooks System When You Need:**

- Content moderation before delivery (PII redaction, toxicity filtering)
- Policy enforcement (block prohibited content, compliance checks)
- Human-in-the-loop approvals (block execution pending approval)
- Content transformation (modify output before client receives it)
- Security controls (prevent unauthorized operations)

**Use Both Together:**

Common pattern: Hooks enforce policies during execution, webhooks notify about results

```json
// Agent with both hooks and webhook subscription

// 1. Configure agent with hooks (policy enforcement)
POST /agents
{
  "name": "Compliant Agent",
  "model": "gpt-4o",
  "hooks": [
    {
      "kind": "modify",
      "condition": { "kind": "always" },
      "modifications": [
        {
          "type": "redact",
          "pattern": "\\b\\d{3}-\\d{2}-\\d{4}\\b",
          "replacement": "[SSN REDACTED]"
        }
      ],
      "eventTypes": ["content.created"]
    }
  ]
}

// 2. Subscribe to notifications (monitoring)
POST /threads/thread-123/subscriptions
{
  "webhookUrl": "https://compliance.example.com/audit",
  "events": ["run.completed", "run.failed"]
}

// Flow:
// - Hook redacts SSN from content (BEFORE delivery)
// - Run completes with redacted content
// - Webhook notification sent (AFTER completion)
// - Compliance system logs the event
```

### Key Distinction Summary

#### Webhooks = "Tell me when something happened"

- Fire-and-forget notifications
- No impact on execution
- Delivered after facts

#### Hooks = "Control what happens"

- Policy enforcement
- Can prevent/modify execution
- Evaluated before/during execution

For complete hooks documentation, see:

- [Hooks Specification](../specifications/hooks.md) - Hook types, conditions, responses
- [Human-in-the-Loop Guide](./human-in-loop.md) - Blocking hooks for approvals
- [Remote Endpoints Specification](../specifications/remote-endpoints.md) - WebSocket/HTTP protocol for remote hooks

---

### Key Concepts

**Subscription Types**: Three types of webhook subscriptions are available:
- **RunSubscription**: Monitor specific run execution (messages, completion, failures)
- **ThreadSubscription**: Monitor conversation thread activity (messages, runs, participant changes)
- **AgentSubscription**: Monitor agent activity across all threads (runs, messages, config changes)

**Webhook Verification**: Optional HMAC-SHA256 signature validation using a shared secret ensures webhook authenticity and prevents spoofing.

**Event Types**: Fine-grained filtering allows subscribing to specific events (e.g., only run completions, not all messages).

**Delivery Tracking**: Built-in metrics track last successful delivery time and consecutive failure counts for monitoring and auto-disable.

---

## Use Cases

### 1. Real-Time Event Notifications

**Scenario**: Dashboard or monitoring UI needs instant updates when agent activity occurs.

**Implementation**:
- Subscribe to `message.created` and `run.completed` events
- Update UI in real-time when notifications arrive
- Display live agent responses as they stream

**Example**: Customer support dashboard showing live agent conversations across multiple threads.

### 2. Status Updates & Progress Tracking

**Scenario**: Long-running agent tasks need progress notifications.

**Implementation**:
- Subscribe to `run.requires_action`, `run.completed`, `run.failed` events
- Update progress indicators based on run status
- Handle tool execution requests and input prompts

**Example**: Data pipeline orchestration where agents process multi-step workflows and notify on completion.

### 3. Real-Time Synchronization

**Scenario**: Multi-client applications (web, mobile, desktop) need synchronized views of conversations.

**Implementation**:
- All clients subscribe to the same thread
- When one client sends a message, others receive webhook notifications
- Clients fetch latest thread state via GET /threads/{threadId}

**Example**: Teams-style collaboration where multiple users view and interact with the same agent conversation.

### 4. Integration with External Systems

**Scenario**: Third-party services need notifications when agent actions occur.

**Implementation**:
- Subscribe external service endpoints (Slack, Teams, PagerDuty)
- Transform webhook payloads to platform-specific formats
- Route notifications to appropriate channels/users

**Example**: Slack bot that forwards agent completion notifications to #notifications channel.

### 5. Audit & Compliance Logging

**Scenario**: Regulatory requirements mandate real-time logging of all agent interactions.

**Implementation**:
- Subscribe to all event types (`events: []` or omit to receive all)
- Forward webhook notifications to compliance logging system
- Archive for audit trails and forensic analysis

**Example**: Healthcare application logging all patient-agent interactions for HIPAA compliance.

### 6. Workflow Orchestration

**Scenario**: Multi-stage workflows where agent completion triggers downstream processes.

**Implementation**:
- Subscribe to `run.completed` events
- Trigger next workflow stage based on run output
- Chain multiple agent runs across different threads

**Example**: Customer onboarding flow where completing account setup triggers welcome email agent.

---

## Architecture

### Subscription Models

All three subscription types share a common structure with specific scoping:

#### ThreadSubscription

**TypeSpec Definition** (See `ThreadSubscription` model in `typespec/subscriptions.tsp`, lines 171-301):

```typescript
model ThreadSubscription {
  subscriptionId: string;        // Unique identifier (server-generated)
  threadId: string;              // Parent thread (read-only)
  webhookUrl: url;               // HTTPS endpoint for notifications (required)
  webhookSecret?: string;        // HMAC-SHA256 secret for verification
  events?: string[];             // Event type filter (default: all events)
  messageFilters?: MessageFilters; // Filter messages by role, content type, etc.
  expiresAt?: utcDateTime;       // Auto-delete after expiration
  active?: boolean = true;       // Enable/disable without deletion (default: true)
  createdAt: utcDateTime;        // Subscription creation time
  lastDeliveredAt?: utcDateTime; // Last successful delivery
  failureCount?: int32 = 0;      // Consecutive delivery failures (default: 0)
  metadata?: Record<unknown>;    // Custom correlation data
}
```

**Endpoint**: `POST /threads/{threadId}/subscriptions`

**Scope**: Single conversation thread

#### RunSubscription

**TypeSpec Definition** (See `RunSubscription` model in `typespec/subscriptions.tsp`, lines 323-439):

```typescript
model RunSubscription {
  subscriptionId: string;        // Unique identifier (server-generated)
  runId: string;                 // Parent run (read-only)
  webhookUrl: url;               // HTTPS endpoint for notifications (required)
  webhookSecret?: string;        // HMAC-SHA256 secret for verification
  events?: string[];             // Event type filter (default: all events)
  messageFilters?: MessageFilters; // Filter messages by role, content type, etc.
  expiresAt?: utcDateTime;       // Auto-delete after expiration
  active?: boolean = true;       // Enable/disable without deletion (default: true)
  createdAt: utcDateTime;        // Subscription creation time
  lastDeliveredAt?: utcDateTime; // Last successful delivery
  failureCount?: int32 = 0;      // Consecutive delivery failures (default: 0)
  metadata?: Record<unknown>;    // Custom correlation data
}
```

**Endpoint**: `POST /runs/{runId}/subscriptions`

**Scope**: Single run execution

#### AgentSubscription

**TypeSpec Definition** (See `AgentSubscription` model in `typespec/subscriptions.tsp`, lines 462-592):

```typescript
model AgentSubscription {
  subscriptionId: string;        // Unique identifier (server-generated)
  agentId: string;               // Agent being monitored (read-only)
  webhookUrl: url;               // HTTPS endpoint for notifications (required)
  webhookSecret?: string;        // HMAC-SHA256 secret for verification
  events?: string[];             // Event type filter (default: all events)
  threadId?: string;             // Optional: filter to specific thread
  messageFilters?: MessageFilters; // Filter messages by role, content type, etc.
  expiresAt?: utcDateTime;       // Auto-delete after expiration
  active?: boolean = true;       // Enable/disable without deletion (default: true)
  createdAt: utcDateTime;        // Subscription creation time
  lastDeliveredAt?: utcDateTime; // Last successful delivery
  failureCount?: int32 = 0;      // Consecutive delivery failures (default: 0)
  metadata?: Record<unknown>;    // Custom correlation data
}
```

**Endpoint**: `POST /agents/{agentId}/subscriptions`

**Scope**: All activity for specific agent (across all threads and runs)

### MessageFilters

**TypeSpec Definition** (See `MessageFilters` model in `typespec/subscriptions.tsp`, lines 59-75):

```typescript
model MessageFilters {
  roles?: string[];         // Only messages from specific roles (user, assistant, tool, channel)
  userIds?: string[];       // Only messages from specific users
  agentIds?: string[];      // Only messages from specific agents
  contentTypes?: string[];  // Only messages with specific content types
                            // Common: 'text', 'image', 'audio', 'video', 'file',
                            // 'functionCall', 'functionResult', 'typingIndicator',
                            // 'messageReaction', 'messageDelete', 'reasoning'
  audience?: string[];      // Only content with specific audience values
                            // Values: 'user', 'assistant'
}
```

**Examples**:

```json
// Filter user messages only
{
  "roles": ["user"]
}

// Filter messages with images or videos
{
  "contentTypes": ["image", "video"]
}

// Filter messages from specific agent
{
  "agentIds": ["agent-123"]
}

// Filter content visible to users only
{
  "audience": ["user"]
}
```

### Common Features

1. **HTTPS Requirement**: `webhookUrl` must use HTTPS for security
2. **Event Filtering**: `events` array controls which notifications are sent
3. **Message Filtering**: `messageFilters` further narrows notifications by role, content type, audience, etc.
4. **Expiration**: `expiresAt` enables time-limited subscriptions (like OAuth tokens)
5. **Active Flag**: Temporarily disable without deletion (default: true)
6. **Delivery Metrics**: Track success/failure for monitoring

### Webhook Notification Payload

**TypeSpec Definition** (See `WebhookNotification` model in `typespec/subscriptions.tsp`, lines 101-135):

```typescript
model WebhookNotification {
  kind: "thread.activity" | "run.activity" | "agent.activity";
  resourceId: string;           // Resource identifier (threadId, runId, or agentId)
  subscriptionId: string;       // Subscription identifier
  eventType: string;            // Event type that triggered notification
  sequenceNumber: int64;        // Subscription sequence number (for gap detection)
  eventSeq: int64;              // Event sequence number (for event ordering)
  timestamp: utcDateTime;       // Event timestamp
  data?: {                      // Optional event-specific data (minimal)
    messageId?: string;         // Message ID (for message events)
    runId?: string;             // Run ID (for run events within thread)
    status?: string;            // Status (for lifecycle events)
  };
}
```

When an event occurs, the server POSTs a JSON payload to `webhookUrl`. The payload structure depends on the subscription type:

#### Thread Activity Notifications

```json
{
  "kind": "thread.activity",
  "resourceId": "thread-123",
  "subscriptionId": "sub-456",
  "eventType": "message.created",
  "sequenceNumber": 42,
  "eventSeq": 1587,
  "timestamp": "2026-02-05T10:00:00Z",
  "data": {
    "messageId": "msg-999"
  }
}
```

**Client Action**: Call `GET /threads/{resourceId}` to fetch latest state.

#### Run Activity Notifications

```json
{
  "kind": "run.activity",
  "resourceId": "run-456",
  "subscriptionId": "sub-789",
  "eventType": "run.completed",
  "sequenceNumber": 15,
  "eventSeq": 42,
  "timestamp": "2026-02-05T10:01:00Z",
  "data": {
    "status": "completed"
  }
}
```

**Client Action**: Call `GET /runs/{resourceId}` to fetch run details.

#### Agent Activity Notifications

```json
{
  "kind": "agent.activity",
  "resourceId": "agent-789",
  "subscriptionId": "sub-012",
  "eventType": "agent.updated",
  "sequenceNumber": 8,
  "eventSeq": 2341,
  "timestamp": "2026-02-05T10:02:00Z",
  "data": {
    "runId": "run-456",
    "threadId": "thread-123"
  }
}
```

**Client Action**: Call `GET /agents/{resourceId}` or `GET /runs/{runId}` depending on event type.

**Notification Contract:**
- **Lightweight**: Contains identifiers, not full data (client fetches via GET)
- **Idempotent**: Same event may be delivered multiple times (use sequenceNumber for deduplication)
- **Fire-and-Forget**: Server does not wait for client processing; expects 2xx response for success
- **Ordered**: `sequenceNumber` increases per subscription for gap detection; `eventSeq` provides per-resource ordering

### Event Types

All event types are defined in `typespec/streaming.tsp` with corresponding TypeScript models. Event names use dot notation (e.g., `message.created`), while TypeScript models use PascalCase (e.g., `MessageCreatedEvent`).

#### Message Events (See `streaming.tsp`, lines 38-114)

| Event Type | TypeScript Model | Description | Triggering Condition |
|------------|------------------|-------------|----------------------|
| `message.created` | `MessageCreatedEvent` | New message or message chunk created | POST /threads/{threadId}/messages |
| `message.updated` | `MessageUpdatedEvent` | Message streaming chunk or edit | Streaming in progress or message edited |
| `message.completed` | `MessageCompletedEvent` | Message streaming finished | Streaming completed |

#### Run Lifecycle Events (See `streaming.tsp`, lines 157-371)

| Event Type | TypeScript Model | Description | Triggering Condition |
|------------|------------------|-------------|----------------------|
| `run.created` | `RunCreatedEvent` | Run was created | POST /runs |
| `run.started` | `RunStartedEvent` | Run started executing | Run.status = "in_progress" |
| `run.completed` | `RunCompletedEvent` | Run finished successfully | Run.status = "completed" |
| `run.failed` | `RunFailedEvent` | Run encountered error | Run.status = "failed" |
| `run.cancelled` | `RunCancelledEvent` | Run was cancelled | Run.status = "cancelled" |
| `run.timeout` | `RunTimeoutEvent` | Run exceeded time limit | Run.status = "timeout" |
| `run.requires_action` | `RunRequiresActionEvent` | Run needs tool execution | Run.status = "requires_action" |
| `run.input_required` | `RunInputRequiredEvent` | Run needs user input | Run.status = "input_required" |

#### Thread Lifecycle Events (See `streaming.tsp`, lines 377-453)

| Event Type | TypeScript Model | Description | Triggering Condition |
|------------|------------------|-------------|----------------------|
| `thread.created` | `ThreadCreatedEvent` | Thread was created | POST /threads |
| `thread.archived` | `ThreadArchivedEvent` | Thread was archived | Thread archived |
| `thread.closed` | `ThreadClosedEvent` | Thread was closed | Thread closed |
| `thread.reopened` | `ThreadReopenedEvent` | Thread was reopened | Thread reopened |
| `thread.deleted` | `ThreadDeletedEvent` | Thread was deleted | DELETE /threads/{threadId} |

#### Participant Events (See `streaming.tsp`, lines 120-151)

| Event Type | TypeScript Model | Description | Triggering Condition |
|------------|------------------|-------------|----------------------|
| `participant.added` | `ParticipantAddedEvent` | New participant joined | Participant added to Thread.participants |
| `participant.removed` | `ParticipantRemovedEvent` | Participant left | Participant removed from Thread.participants |

#### Agent Configuration Events (See `streaming.tsp`, lines 459-565)

| Event Type | TypeScript Model | Description | Triggering Condition |
|------------|------------------|-------------|----------------------|
| `agent.created` | `AgentCreatedEvent` | Agent registered | POST /agents |
| `agent.updated` | `AgentUpdatedEvent` | Agent config changed | PATCH /agents/{agentId} |
| `agent.deleted` | `AgentDeletedEvent` | Agent removed | DELETE /agents/{agentId} |
| `agent.enabled` | `AgentEnabledEvent` | Agent enabled | Agent enabled |
| `agent.disabled` | `AgentDisabledEvent` | Agent disabled | Agent disabled |
| `agent.error` | `AgentErrorEvent` | Agent error occurred | Configuration or deployment error |

**Filtering Examples:**

```json
// Subscribe only to run completions and failures
{
  "webhookUrl": "https://example.com/webhook",
  "events": ["run.completed", "run.failed"]
}

// Subscribe to all message events
{
  "webhookUrl": "https://example.com/webhook",
  "events": ["message.created", "message.updated", "message.completed"]
}

// Subscribe to all events (default)
{
  "webhookUrl": "https://example.com/webhook",
  "events": []  // or omit field entirely
}
```

### Webhook Signature Verification

**HMAC-SHA256 Pattern** (like GitHub, Stripe, Twilio):

1. **Registration**: Client provides `webhookSecret` when creating subscription
2. **Signing**: Server computes `HMAC-SHA256(secret, payload)` and includes in `X-Signature` header
3. **Verification**: Client recomputes signature and compares to prevent spoofing

**Header Format**:
```
X-Signature: sha256=<hex_encoded_signature>
X-Timestamp: 2026-02-05T10:00:00Z
```

**Security Benefits:**
- Prevents webhook spoofing (unauthorized POSTs)
- Validates payload integrity (detects tampering)
- Timestamp prevents replay attacks

---

## Implementation

### 1. Creating a Subscription

**REST API** (`POST /threads/{threadId}/subscriptions`):

```bash
curl -X POST https://api.example.com/threads/thread-123/subscriptions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "webhookUrl": "https://myapp.com/webhooks/agent-notifications",
    "webhookSecret": "whsec_a1b2c3d4e5f6",
    "events": ["message.created", "run.completed"],
    "expiresAt": "2026-12-31T23:59:59Z",
    "metadata": {
      "clientId": "mobile-app-v1.2",
      "userId": "user-789"
    }
  }'
```

**Response** (201 Created):

```json
{
  "subscriptionId": "sub-456",
  "threadId": "thread-123",
  "webhookUrl": "https://myapp.com/webhooks/agent-notifications",
  "events": ["message.created", "run.completed"],
  "expiresAt": "2026-12-31T23:59:59Z",
  "active": true,
  "createdAt": "2026-02-05T10:00:00Z",
  "failureCount": 0,
  "metadata": {
    "clientId": "mobile-app-v1.2",
    "userId": "user-789"
  }
}
```

### 2. Webhook Server Setup

#### Python (FastAPI) - Async Handler

```python
from fastapi import FastAPI, Header, HTTPException, Request
import hmac
import hashlib
import json
from datetime import datetime

app = FastAPI()

WEBHOOK_SECRET = "whsec_a1b2c3d4e5f6"

def verify_signature(payload: bytes, signature: str, timestamp: str) -> bool:
    """Verify HMAC-SHA256 signature."""
    # Prevent replay attacks (reject if timestamp > 5 minutes old)
    try:
        webhook_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        age_seconds = (datetime.now(webhook_time.tzinfo) - webhook_time).total_seconds()
        if age_seconds > 300:  # 5 minutes
            return False
    except ValueError:
        return False

    # Compute expected signature
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Extract signature from header (format: "sha256=<hex>")
    if not signature.startswith("sha256="):
        return False
    provided = signature.split("=", 1)[1]

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(expected, provided)

@app.post("/webhooks/agent-notifications")
async def handle_webhook(
    request: Request,
    x_signature: str = Header(None),
    x_timestamp: str = Header(None)
):
    """Handle webhook notification with signature verification."""

    # Read raw body for signature verification
    body = await request.body()

    # Verify signature if secret was provided
    if x_signature and x_timestamp:
        if not verify_signature(body, x_signature, x_timestamp):
            raise HTTPException(status_code=401, detail="Invalid signature")

    # Parse notification payload
    notification = json.loads(body)

    # Route based on event type
    if notification["eventType"] == "run.completed":
        await handle_run_completed(notification)
    elif notification["eventType"] == "message.created":
        await handle_message_created(notification)
    elif notification["eventType"] == "run.failed":
        await handle_run_failed(notification)

    # Return 200 OK to acknowledge receipt
    return {"status": "processed"}

async def handle_run_completed(notification: dict):
    """Process run completion notification."""
    # Get resource ID from notification (could be threadId, runId, or agentId)
    resource_id = notification["resourceId"]

    # For thread subscriptions, resourceId is threadId
    if notification["kind"] == "thread.activity":
        thread_id = resource_id
        thread = await fetch_thread(thread_id)

        # Get runId from notification data if available
        run_id = notification.get("data", {}).get("runId")
        if run_id:
            run = await fetch_run(run_id)
            print(f"Run {run_id} completed in thread {thread_id}")

    # For run subscriptions, resourceId is runId
    elif notification["kind"] == "run.activity":
        run_id = resource_id
        run = await fetch_run(run_id)
        print(f"Run {run_id} completed")
        # Trigger downstream workflow, send notification, update UI, etc.

async def handle_message_created(notification: dict):
    """Process new message notification."""
    resource_id = notification["resourceId"]
    message_id = notification.get("data", {}).get("messageId")

    # For thread subscriptions, resourceId is threadId
    if notification["kind"] == "thread.activity":
        thread_id = resource_id
        messages = await fetch_messages(thread_id, limit=10)
        latest_message = messages[0] if messages else None

        if latest_message and latest_message.get("role") == "assistant":
            print(f"Agent response: {latest_message.get('text')}")
            # Update UI, send push notification, etc.

async def handle_run_failed(notification: dict):
    """Process run failure notification."""
    resource_id = notification["resourceId"]

    # For thread subscriptions, get runId from data
    if notification["kind"] == "thread.activity":
        run_id = notification.get("data", {}).get("runId")
        if run_id:
            run = await fetch_run(run_id)
    # For run subscriptions, resourceId is runId
    elif notification["kind"] == "run.activity":
        run_id = resource_id
        run = await fetch_run(run_id)

    if run and run.get("error"):
        error = run["error"]
        print(f"Run {run_id} failed: {error['code']} - {error['message']}")
        # Alert on-call engineer, log to monitoring, retry with backoff, etc.
```

#### Node.js (Express) - Queue Integration

```javascript
const express = require('express');
const crypto = require('crypto');
const { Queue } = require('bullmq');

const app = express();
const webhookQueue = new Queue('webhook-processing', {
  connection: { host: 'localhost', port: 6379 }
});

const WEBHOOK_SECRET = 'whsec_a1b2c3d4e5f6';

function verifySignature(payload, signature, timestamp) {
  // Check timestamp freshness (5 minute window)
  const webhookTime = new Date(timestamp);
  const ageSeconds = (Date.now() - webhookTime.getTime()) / 1000;
  if (ageSeconds > 300) return false;

  // Compute expected signature
  const expected = crypto
    .createHmac('sha256', WEBHOOK_SECRET)
    .update(payload)
    .digest('hex');

  // Extract provided signature
  const provided = signature.split('=')[1];

  // Constant-time comparison
  return crypto.timingSafeEqual(
    Buffer.from(expected),
    Buffer.from(provided)
  );
}

app.post('/webhooks/agent-notifications', express.raw({ type: 'application/json' }), async (req, res) => {
  const signature = req.headers['x-signature'];
  const timestamp = req.headers['x-timestamp'];

  // Verify signature
  if (signature && timestamp) {
    if (!verifySignature(req.body, signature, timestamp)) {
      return res.status(401).json({ error: 'Invalid signature' });
    }
  }

  // Parse notification
  const notification = JSON.parse(req.body);

  // Queue for async processing (don't block webhook response)
  await webhookQueue.add('process-notification', notification, {
    attempts: 3,
    backoff: { type: 'exponential', delay: 2000 }
  });

  // Immediate 200 OK response (don't make server wait)
  res.status(200).json({ status: 'queued' });
});

// Worker process (separate from webhook handler)
const { Worker } = require('bullmq');

const worker = new Worker('webhook-processing', async job => {
  const notification = job.data;

  // Process based on event type
  switch (notification.eventType) {
    case 'run.completed':
      await handleRunCompleted(notification);
      break;
    case 'message.created':
      await handleMessageCreated(notification);
      break;
    case 'run.failed':
      await handleRunFailed(notification);
      break;
  }
}, { connection: { host: 'localhost', port: 6379 } });

async function handleRunCompleted(notification) {
  const resourceId = notification.resourceId;

  // For thread subscriptions, resourceId is threadId
  if (notification.kind === 'thread.activity') {
    const threadId = resourceId;
    const response = await fetch(`https://api.example.com/threads/${threadId}`, {
      headers: { 'Authorization': `Bearer ${process.env.API_TOKEN}` }
    });
    const thread = await response.json();
    console.log(`Run completed in thread ${threadId}`);
  }
  // For run subscriptions, resourceId is runId
  else if (notification.kind === 'run.activity') {
    const runId = resourceId;
    const response = await fetch(`https://api.example.com/runs/${runId}`, {
      headers: { 'Authorization': `Bearer ${process.env.API_TOKEN}` }
    });
    const run = await response.json();
    console.log(`Run ${runId} completed`);
  }
  // Trigger next workflow step, send email, update database, etc.
}
```

### 3. Signature Verification Middleware

**Reusable FastAPI Dependency**:

```python
from fastapi import Header, HTTPException, Request
from typing import Optional
import hmac
import hashlib

async def verify_webhook_signature(
    request: Request,
    x_signature: Optional[str] = Header(None),
    x_timestamp: Optional[str] = Header(None)
):
    """Dependency for webhook signature verification."""

    # Skip if no signature provided (for testing/non-production)
    if not x_signature or not x_timestamp:
        return

    body = await request.body()
    secret = get_webhook_secret()  # From config/env

    # Verify timestamp freshness
    from datetime import datetime
    webhook_time = datetime.fromisoformat(x_timestamp.replace('Z', '+00:00'))
    age = (datetime.now(webhook_time.tzinfo) - webhook_time).total_seconds()
    if age > 300:
        raise HTTPException(status_code=401, detail="Webhook timestamp too old")

    # Verify signature
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    provided = x_signature.split("=", 1)[1]

    if not hmac.compare_digest(expected, provided):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

# Usage
@app.post("/webhooks/agent", dependencies=[Depends(verify_webhook_signature)])
async def handle_webhook(notification: dict):
    # Signature already verified by dependency
    return {"status": "ok"}
```

### 4. Retry Logic & Idempotency

**Server-Side Retry Strategy** (implemented by Agent Runtime API):

```python
import asyncio
from datetime import datetime, timedelta

async def deliver_webhook(subscription: ThreadSubscription, notification: dict):
    """Deliver webhook with exponential backoff retry."""

    max_attempts = 5
    base_delay = 1  # seconds

    for attempt in range(max_attempts):
        try:
            # Compute signature
            payload = json.dumps(notification).encode()
            signature = hmac.new(
                subscription.webhookSecret.encode(),
                payload,
                hashlib.sha256
            ).hexdigest()

            # POST to webhook URL
            response = await http_client.post(
                subscription.webhookUrl,
                json=notification,
                headers={
                    "Content-Type": "application/json",
                    "X-Signature": f"sha256={signature}",
                    "X-Timestamp": datetime.utcnow().isoformat() + "Z"
                },
                timeout=10  # 10 second timeout
            )

            # Success: 2xx response
            if 200 <= response.status_code < 300:
                subscription.lastDeliveredAt = datetime.utcnow()
                subscription.failureCount = 0
                await save_subscription(subscription)
                return True

            # Client error (4xx): Don't retry
            if 400 <= response.status_code < 500:
                print(f"Client error {response.status_code}, not retrying")
                break

        except (asyncio.TimeoutError, ConnectionError) as e:
            print(f"Webhook delivery failed (attempt {attempt + 1}): {e}")

        # Exponential backoff: 1s, 2s, 4s, 8s, 16s
        if attempt < max_attempts - 1:
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)

    # All attempts failed
    subscription.failureCount += 1

    # Auto-disable after 10 consecutive failures
    if subscription.failureCount >= 10:
        subscription.active = False
        print(f"Subscription {subscription.subscriptionId} disabled after 10 failures")

    await save_subscription(subscription)
    return False
```

**Client-Side Idempotency**:

```python
# Track processed notifications to prevent duplicate processing
processed_notifications = set()

@app.post("/webhooks/agent-notifications")
async def handle_webhook(notification: dict):
    # Create unique key from notification
    notification_key = f"{notification['subscriptionId']}:{notification['timestamp']}"

    # Check if already processed
    if notification_key in processed_notifications:
        print(f"Duplicate notification ignored: {notification_key}")
        return {"status": "duplicate"}

    # Process notification
    await process_notification(notification)

    # Mark as processed (use Redis/database for distributed systems)
    processed_notifications.add(notification_key)

    # Cleanup old entries (keep last 1 hour)
    # ... implement TTL-based cleanup ...

    return {"status": "processed"}
```

---

## Examples - Stress Test Scenarios

### 1. High-Volume Webhook Handling

**Scenario**: Handling 1000+ webhook notifications per second.

**Challenge**: Avoid blocking webhook responses; process asynchronously.

**Solution**: Queue-based processing with rate limiting.

```python
from fastapi import FastAPI, BackgroundTasks
from redis import Redis
from rq import Queue
import time

app = FastAPI()
redis_conn = Redis(host='localhost', port=6379)
webhook_queue = Queue('webhooks', connection=redis_conn)

# Rate limiter (using Redis)
def check_rate_limit(subscription_id: str) -> bool:
    """Rate limit: max 100 webhooks per minute per subscription."""
    key = f"rate_limit:{subscription_id}"
    count = redis_conn.incr(key)

    if count == 1:
        redis_conn.expire(key, 60)  # 60 second window

    return count <= 100

@app.post("/webhooks/high-volume")
async def handle_high_volume_webhook(notification: dict):
    """Handle webhook with rate limiting and queueing."""

    subscription_id = notification["subscriptionId"]

    # Rate limit check
    if not check_rate_limit(subscription_id):
        return {"status": "rate_limited"}, 429

    # Queue for async processing (non-blocking)
    job = webhook_queue.enqueue(
        'tasks.process_webhook',
        notification,
        job_timeout='5m'
    )

    # Immediate response
    return {"status": "queued", "job_id": job.id}

# Worker process (tasks.py)
def process_webhook(notification: dict):
    """Background worker processes webhook."""
    event_type = notification["eventType"]
    resource_id = notification["resourceId"]
    kind = notification["kind"]

    # Handle based on subscription type
    if kind == "thread.activity":
        thread_id = resource_id
        thread = fetch_thread(thread_id)

        # Process based on event type
        if event_type == "run.completed":
            # Heavy processing: update dashboards, send emails, etc.
            update_dashboard(thread)
            send_completion_email(thread)

        print(f"Processed webhook for thread {thread_id}")
    elif kind == "run.activity":
        run_id = resource_id
        run = fetch_run(run_id)
        print(f"Processed webhook for run {run_id}")
```

### 2. Multiple Webhook Endpoints (Fan-Out Pattern)

**Scenario**: Route notifications to multiple services (Slack, Teams, PagerDuty).

**Implementation**: One subscription per service with custom metadata.

```python
# Register multiple subscriptions for same thread
subscriptions = [
    {
        "webhookUrl": "https://hooks.slack.com/services/T00/B00/XXX",
        "events": ["run.completed", "run.failed"],
        "metadata": {"service": "slack", "channel": "#agent-notifications"}
    },
    {
        "webhookUrl": "https://outlook.office.com/webhook/XXX",
        "events": ["run.completed"],
        "metadata": {"service": "teams", "channel": "Agent Updates"}
    },
    {
        "webhookUrl": "https://events.pagerduty.com/v2/enqueue",
        "events": ["run.failed"],
        "metadata": {"service": "pagerduty", "severity": "high"}
    }
]

for sub in subscriptions:
    response = requests.post(
        f"https://api.example.com/threads/{thread_id}/subscriptions",
        json=sub,
        headers={"Authorization": f"Bearer {token}"}
    )
```

**Webhook Handler with Platform Transformation**:

```python
@app.post("/webhooks/fanout/{service}")
async def handle_fanout_webhook(service: str, notification: dict):
    """Transform webhook payload for specific platform."""

    if service == "slack":
        await send_slack_notification(notification)
    elif service == "teams":
        await send_teams_notification(notification)
    elif service == "pagerduty":
        await send_pagerduty_alert(notification)

    return {"status": "forwarded"}

async def send_slack_notification(notification: dict):
    """Transform to Slack message format."""
    resource_id = notification["resourceId"]
    event_type = notification["eventType"]
    kind = notification["kind"]

    # Determine resource type and build appropriate URL
    if kind == "thread.activity":
        resource_type = "Thread"
        view_url = f"https://app.example.com/threads/{resource_id}"
    elif kind == "run.activity":
        resource_type = "Run"
        view_url = f"https://app.example.com/runs/{resource_id}"
    elif kind == "agent.activity":
        resource_type = "Agent"
        view_url = f"https://app.example.com/agents/{resource_id}"

    # Build Slack message
    slack_message = {
        "text": f"Agent Event: {event_type}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{resource_type}*: {resource_id}\n*Event*: {event_type}\n*Time*: {notification['timestamp']}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": f"View {resource_type}"},
                        "url": view_url
                    }
                ]
            }
        ]
    }

    # POST to Slack webhook
    await http_client.post(
        "https://hooks.slack.com/services/T00/B00/XXX",
        json=slack_message
    )
```

### 3. Webhook Failure Recovery

**Scenario**: Handle temporary endpoint failures gracefully.

**Implementation**: Exponential backoff with circuit breaker pattern.

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failures detected, stop sending
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout  # seconds before retry
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""

        if self.state == CircuitState.OPEN:
            # Check if timeout elapsed
            if datetime.now() - self.last_failure_time > timedelta(seconds=self.timeout):
                self.state = CircuitState.HALF_OPEN
                print("Circuit breaker: HALF_OPEN (testing recovery)")
            else:
                raise Exception("Circuit breaker OPEN - not sending webhook")

        try:
            result = func(*args, **kwargs)

            # Success: reset circuit
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                print("Circuit breaker: CLOSED (recovered)")

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            # Open circuit if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"Circuit breaker: OPEN (failed {self.failure_count} times)")

            raise

# Per-subscription circuit breakers
circuit_breakers = {}

async def deliver_webhook_with_circuit_breaker(subscription: ThreadSubscription, notification: dict):
    """Deliver webhook with circuit breaker protection."""

    # Get or create circuit breaker for this subscription
    if subscription.subscriptionId not in circuit_breakers:
        circuit_breakers[subscription.subscriptionId] = CircuitBreaker(
            failure_threshold=5,
            timeout=60  # 1 minute cooldown
        )

    breaker = circuit_breakers[subscription.subscriptionId]

    try:
        # Attempt delivery through circuit breaker
        breaker.call(send_webhook, subscription, notification)
        print(f"Webhook delivered to {subscription.webhookUrl}")

    except Exception as e:
        print(f"Webhook delivery failed: {e}")

        # If circuit is open, disable subscription temporarily
        if breaker.state == CircuitState.OPEN:
            subscription.active = False
            await save_subscription(subscription)

            # Schedule re-enable after timeout
            await schedule_reactivation(subscription, breaker.timeout)

def send_webhook(subscription: ThreadSubscription, notification: dict):
    """Actual webhook delivery (raises on failure)."""
    response = requests.post(
        subscription.webhookUrl,
        json=notification,
        timeout=10
    )
    response.raise_for_status()  # Raises for 4xx/5xx
```

### 4. Event Replay & Audit Log

**Scenario**: Replay missed webhook notifications after downtime.

**Implementation**: Persistent event log with replay API.

```python
from sqlalchemy import create_engine, Column, String, DateTime, JSON, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class WebhookEvent(Base):
    __tablename__ = 'webhook_events'

    id = Column(Integer, primary_key=True)
    subscription_id = Column(String, index=True)
    thread_id = Column(String, index=True)
    event_type = Column(String, index=True)
    payload = Column(JSON)
    timestamp = Column(DateTime, index=True, default=datetime.utcnow)
    delivered = Column(Boolean, default=False)
    delivery_attempts = Column(Integer, default=0)
    last_attempt_at = Column(DateTime, nullable=True)

# Log all webhook events
async def log_webhook_event(subscription: ThreadSubscription, notification: dict):
    """Persist webhook event for audit trail and replay."""
    event = WebhookEvent(
        subscription_id=subscription.subscriptionId,
        thread_id=notification["threadId"],
        event_type=notification["eventType"],
        payload=notification,
        timestamp=datetime.fromisoformat(notification["timestamp"].replace('Z', '+00:00'))
    )
    session.add(event)
    session.commit()

# Replay API endpoint
@app.post("/admin/webhooks/replay")
async def replay_webhooks(
    subscription_id: str,
    since: datetime,
    until: datetime
):
    """Replay webhook events for a subscription in a time range."""

    # Fetch events from audit log
    events = session.query(WebhookEvent).filter(
        WebhookEvent.subscription_id == subscription_id,
        WebhookEvent.timestamp >= since,
        WebhookEvent.timestamp <= until,
        WebhookEvent.delivered == False  # Only undelivered
    ).all()

    # Fetch subscription
    subscription = await get_subscription(subscription_id)

    replayed_count = 0
    for event in events:
        try:
            # Attempt delivery
            await deliver_webhook(subscription, event.payload)

            # Mark as delivered
            event.delivered = True
            event.delivery_attempts += 1
            event.last_attempt_at = datetime.utcnow()
            replayed_count += 1

        except Exception as e:
            print(f"Replay failed for event {event.id}: {e}")
            event.delivery_attempts += 1
            event.last_attempt_at = datetime.utcnow()

    session.commit()

    return {
        "replayed": replayed_count,
        "total": len(events)
    }
```

### 5. Multi-Tenant Webhook Isolation

**Scenario**: SaaS platform with per-tenant webhook subscriptions.

**Implementation**: Tenant-scoped subscriptions with isolation.

```python
from fastapi import Depends, HTTPException

# Tenant context middleware
async def get_tenant_id(authorization: str = Header(None)) -> str:
    """Extract tenant ID from JWT token."""
    token = authorization.replace("Bearer ", "")
    decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return decoded["tenant_id"]

# Tenant-scoped subscription creation
@app.post("/threads/{thread_id}/subscriptions")
async def create_subscription(
    thread_id: str,
    subscription: ThreadSubscription,
    tenant_id: str = Depends(get_tenant_id)
):
    """Create subscription with tenant isolation."""

    # Verify thread belongs to tenant
    thread = await get_thread(thread_id)
    if thread.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Thread not found")

    # Add tenant_id to subscription metadata
    subscription.metadata = subscription.metadata or {}
    subscription.metadata["tenant_id"] = tenant_id

    # Create subscription
    created = await create_subscription_record(subscription)
    return created

# Webhook delivery with tenant isolation
async def deliver_webhook(subscription: ThreadSubscription, notification: dict):
    """Deliver webhook with tenant context."""

    tenant_id = subscription.metadata.get("tenant_id")

    # Generate tenant-scoped JWT for webhook
    tenant_token = jwt.encode(
        {"tenant_id": tenant_id, "exp": datetime.utcnow() + timedelta(minutes=5)},
        SECRET_KEY,
        algorithm="HS256"
    )

    # Include tenant context in webhook headers
    response = await http_client.post(
        subscription.webhookUrl,
        json=notification,
        headers={
            "Content-Type": "application/json",
            "X-Tenant-ID": tenant_id,
            "X-Tenant-Token": tenant_token  # For webhook authentication
        }
    )
```

### 6. Webhook Monitoring & Alerting

**Scenario**: Monitor webhook health and alert on failures.

**Implementation**: Metrics collection with alerting thresholds.

```python
from prometheus_client import Counter, Histogram, Gauge
import asyncio

# Prometheus metrics
webhook_deliveries_total = Counter(
    'webhook_deliveries_total',
    'Total webhook delivery attempts',
    ['subscription_id', 'event_type', 'status']
)

webhook_delivery_duration = Histogram(
    'webhook_delivery_duration_seconds',
    'Webhook delivery latency',
    ['subscription_id']
)

webhook_failure_count = Gauge(
    'webhook_consecutive_failures',
    'Consecutive delivery failures per subscription',
    ['subscription_id']
)

async def deliver_webhook_with_metrics(subscription: ThreadSubscription, notification: dict):
    """Deliver webhook with metrics tracking."""

    start_time = asyncio.get_event_loop().time()

    try:
        # Attempt delivery
        await deliver_webhook(subscription, notification)

        # Record success
        webhook_deliveries_total.labels(
            subscription_id=subscription.subscriptionId,
            event_type=notification["eventType"],
            status="success"
        ).inc()

        # Reset failure gauge
        webhook_failure_count.labels(
            subscription_id=subscription.subscriptionId
        ).set(0)

    except Exception as e:
        # Record failure
        webhook_deliveries_total.labels(
            subscription_id=subscription.subscriptionId,
            event_type=notification["eventType"],
            status="failed"
        ).inc()

        # Increment failure gauge
        current_failures = subscription.failureCount
        webhook_failure_count.labels(
            subscription_id=subscription.subscriptionId
        ).set(current_failures)

        # Alert if threshold exceeded
        if current_failures >= 5:
            await send_alert(
                f"Webhook {subscription.subscriptionId} has {current_failures} consecutive failures"
            )

    finally:
        # Record latency
        duration = asyncio.get_event_loop().time() - start_time
        webhook_delivery_duration.labels(
            subscription_id=subscription.subscriptionId
        ).observe(duration)

async def send_alert(message: str):
    """Send alert to monitoring system (PagerDuty, Slack, etc.)."""
    await http_client.post(
        "https://events.pagerduty.com/v2/enqueue",
        json={
            "event_action": "trigger",
            "payload": {
                "summary": message,
                "severity": "error",
                "source": "webhook-delivery-system"
            }
        }
    )
```

---

## Integration Examples

### Slack Integration

```python
import json
import requests

async def send_slack_notification(notification: dict):
    """Send formatted notification to Slack channel."""

    resource_id = notification["resourceId"]
    event_type = notification["eventType"]
    kind = notification["kind"]

    # Fetch resource details based on subscription type
    if kind == "thread.activity":
        thread_id = resource_id
        response = requests.get(
            f"https://api.example.com/threads/{thread_id}",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        resource = response.json()
        resource_type = "Thread"
        view_url = f"https://app.example.com/threads/{thread_id}"

        # Get latest message
        latest_message = resource.get("messages", [])[-1] if resource.get("messages") else None
    elif kind == "run.activity":
        run_id = resource_id
        response = requests.get(
            f"https://api.example.com/runs/{run_id}",
            headers={"Authorization": f"Bearer {API_TOKEN}"}
        )
        resource = response.json()
        resource_type = "Run"
        view_url = f"https://app.example.com/runs/{run_id}"
        latest_message = None

    # Build Slack message
    slack_payload = {
        "channel": "#agent-notifications",
        "username": "Agent Runtime",
        "icon_emoji": ":robot_face:",
        "attachments": [{
            "color": "#36a64f" if event_type == "run.completed" else "#ff0000",
            "title": f"Agent Event: {event_type}",
            "fields": [
                {"title": resource_type, "value": resource_id, "short": True},
                {"title": "Event Type", "value": event_type, "short": True},
                {"title": "Timestamp", "value": notification["timestamp"], "short": True}
            ],
            "actions": [{
                "type": "button",
                "text": f"View {resource_type}",
                "url": view_url
            }]
        }]
    }

    # Add message preview if available (thread subscriptions only)
    if latest_message and latest_message.get("role") == "assistant":
        slack_payload["attachments"][0]["fields"].append({
            "title": "Latest Response",
            "value": latest_message.get("text", "")[:200],  # Truncate
            "short": False
        })

    # POST to Slack webhook
    requests.post(
        "https://hooks.slack.com/services/T00/B00/XXX",
        json=slack_payload
    )
```

### Teams Integration

```python
async def send_teams_notification(notification: dict):
    """Send adaptive card to Microsoft Teams channel."""

    resource_id = notification["resourceId"]
    event_type = notification["eventType"]
    kind = notification["kind"]

    # Determine resource type and URL
    if kind == "thread.activity":
        resource_type = "Thread"
        resource_label = "Thread ID"
        view_url = f"https://app.example.com/threads/{resource_id}"
    elif kind == "run.activity":
        resource_type = "Run"
        resource_label = "Run ID"
        view_url = f"https://app.example.com/runs/{resource_id}"
    elif kind == "agent.activity":
        resource_type = "Agent"
        resource_label = "Agent ID"
        view_url = f"https://app.example.com/agents/{resource_id}"

    # Build Teams Adaptive Card
    card = {
        "type": "message",
        "attachments": [{
            "contentType": "application/vnd.microsoft.card.adaptive",
            "content": {
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": f"Agent Event: {event_type}",
                        "weight": "Bolder",
                        "size": "Medium"
                    },
                    {
                        "type": "FactSet",
                        "facts": [
                            {"title": resource_label, "value": resource_id},
                            {"title": "Event Type", "value": event_type},
                            {"title": "Timestamp", "value": notification["timestamp"]}
                        ]
                    }
                ],
                "actions": [{
                    "type": "Action.OpenUrl",
                    "title": f"View {resource_type}",
                    "url": view_url
                }]
            }
        }]
    }

    # POST to Teams webhook
    await http_client.post(
        "https://outlook.office.com/webhook/XXX",
        json=card
    )
```

### CI/CD Pipeline Trigger

```python
async def trigger_cicd_pipeline(notification: dict):
    """Trigger GitHub Actions workflow based on agent completion."""

    if notification["eventType"] != "run.completed":
        return

    thread_id = notification["threadId"]

    # Fetch completed run
    runs = await fetch_runs(thread_id, status="completed", limit=1)
    run = runs[0] if runs else None

    if not run:
        return

    # Check if run indicates deployment approval
    approval_message = next(
        (msg for msg in run["output"] if "approved" in msg.get("text", "").lower()),
        None
    )

    if approval_message:
        # Trigger GitHub Actions workflow
        await http_client.post(
            "https://api.github.com/repos/owner/repo/actions/workflows/deploy.yml/dispatches",
            headers={
                "Authorization": f"token {GITHUB_TOKEN}",
                "Accept": "application/vnd.github.v3+json"
            },
            json={
                "ref": "main",
                "inputs": {
                    "environment": "production",
                    "approved_by": thread_id
                }
            }
        )
        print(f"Triggered deployment for thread {thread_id}")
```

### Real-Time Dashboard Updates

```python
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        if thread_id not in self.active_connections:
            self.active_connections[thread_id] = set()
        self.active_connections[thread_id].add(websocket)

    def disconnect(self, websocket: WebSocket, thread_id: str):
        self.active_connections[thread_id].discard(websocket)

    async def broadcast(self, thread_id: str, message: dict):
        """Broadcast message to all WebSocket clients for a thread."""
        if thread_id in self.active_connections:
            for connection in self.active_connections[thread_id]:
                await connection.send_json(message)

manager = ConnectionManager()

# WebSocket endpoint for dashboard
@app.websocket("/ws/threads/{thread_id}")
async def websocket_endpoint(websocket: WebSocket, thread_id: str):
    await manager.connect(websocket, thread_id)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, thread_id)

# Webhook handler broadcasts to WebSocket clients
@app.post("/webhooks/dashboard")
async def handle_dashboard_webhook(notification: dict):
    """Receive webhook and broadcast to WebSocket clients."""

    resource_id = notification["resourceId"]
    kind = notification["kind"]

    # For thread subscriptions, broadcast to clients watching that thread
    if kind == "thread.activity":
        thread_id = resource_id
        # Fetch latest thread state
        thread = await fetch_thread(thread_id)

        # Broadcast to all WebSocket clients watching this thread
        await manager.broadcast(thread_id, {
            "type": "thread_update",
            "eventType": notification["eventType"],
            "thread": thread
        })

    return {"status": "broadcasted"}
```

---

## Troubleshooting

### Webhook Not Receiving Notifications

**Symptoms**: Subscription created successfully but no webhooks arriving.

**Debugging Steps**:

1. **Check Subscription Status**:
   ```bash
   GET /threads/{threadId}/subscriptions/{subscriptionId}
   ```
   - Verify `active: true`
   - Check `failureCount` (high count indicates delivery failures)
   - Review `lastDeliveredAt` (should update on successful delivery)

2. **Verify HTTPS Endpoint**:
   - Webhook URL must use HTTPS (not HTTP)
   - Certificate must be valid (not self-signed)
   - Test endpoint manually:
     ```bash
     curl -X POST https://your-webhook-url.com/path \
       -H "Content-Type: application/json" \
       -d '{"test": "payload"}'
     ```

3. **Check Firewall Rules**:
   - Ensure webhook endpoint is publicly accessible
   - Whitelist Agent Runtime server IPs if using firewall restrictions
   - Verify no reverse proxy blocking POST requests

4. **Review Event Filters**:
   - Check `events` array in subscription
   - Ensure expected event types are included
   - Try removing filter (empty array = all events)

### Webhook Signature Verification Failing

**Symptoms**: Receiving webhooks but signature validation returns 401.

**Debugging Steps**:

1. **Check Secret Matches**:
   - Verify `webhookSecret` used in subscription creation matches verification code
   - Secrets are case-sensitive

2. **Inspect Signature Header**:
   ```python
   print(f"Received signature: {x_signature}")
   print(f"Expected format: sha256=<hex>")
   ```

3. **Verify Timestamp Freshness**:
   - Signature includes timestamp in computation
   - Reject webhooks older than 5 minutes (replay attack prevention)
   - Ensure server clocks are synchronized (use NTP)

4. **Use Raw Body for Verification**:
   ```python
   # CORRECT: Verify against raw body bytes
   body = await request.body()
   expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()

   # INCORRECT: Verify against parsed JSON (signatures won't match)
   # payload = await request.json()
   # body = json.dumps(payload).encode()  # Different byte order!
   ```

### High Failure Count

**Symptoms**: `subscription.failureCount` increasing, notifications not delivered.

**Debugging Steps**:

1. **Check Endpoint Availability**:
   - Test webhook URL manually
   - Verify endpoint returns 2xx status code
   - Ensure response time < 10 seconds (server timeout)

2. **Review Server Logs**:
   - Check webhook endpoint logs for errors
   - Look for timeout exceptions, 500 errors, crashes

3. **Reduce Processing Time**:
   - Don't perform heavy work in webhook handler
   - Return 200 OK immediately, then process asynchronously:
     ```python
     @app.post("/webhook")
     async def handle_webhook(notification: dict, background_tasks: BackgroundTasks):
         # Queue for background processing
         background_tasks.add_task(process_notification, notification)
         # Immediate response
         return {"status": "queued"}
     ```

4. **Implement Circuit Breaker**:
   - Temporarily disable failing subscriptions
   - Implement exponential backoff on client-side retries
   - Use circuit breaker pattern (see examples above)

### Duplicate Notifications

**Symptoms**: Receiving the same webhook notification multiple times.

**Explanation**: Webhook delivery uses **at-least-once delivery** semantics. Duplicates can occur during:
- Network retries after timeout
- Server restarts mid-delivery
- Client returned 500 error, server retried

**Solution**: Implement idempotency checks on client-side:

```python
# Use Redis for distributed deduplication
redis_client = Redis(host='localhost', port=6379)

@app.post("/webhook")
async def handle_webhook(notification: dict):
    # Create unique key from notification
    notification_key = f"{notification['subscriptionId']}:{notification['timestamp']}"

    # Check if already processed (Redis SETNX is atomic)
    if not redis_client.set(notification_key, "1", nx=True, ex=3600):
        return {"status": "duplicate", "message": "Already processed"}

    # Process notification
    await process_notification(notification)

    return {"status": "processed"}
```

### Subscription Auto-Disabled

**Symptoms**: Subscription `active` field changed to `false` unexpectedly.

**Cause**: Server auto-disables subscriptions after 10 consecutive delivery failures.

**Resolution**:

1. **Fix Endpoint Issues**:
   - Resolve webhook endpoint errors
   - Ensure endpoint returns 2xx status codes
   - Reduce response time to < 10 seconds

2. **Re-enable Subscription**:
   ```bash
   PATCH /threads/{threadId}/subscriptions/{subscriptionId}
   {"active": true}
   ```

3. **Monitor Failure Count**:
   - Set up alerts when `failureCount > 3`
   - Investigate before reaching auto-disable threshold

### Webhook Latency Too High

**Symptoms**: Notifications arrive several seconds after events occur.

**Debugging Steps**:

1. **Check Network Latency**:
   - Measure round-trip time to webhook endpoint
   - Use CDN or edge deployment if client is geographically distant

2. **Reduce Webhook Processing Time**:
   - Return 200 OK immediately (don't wait for processing)
   - Use background queues for heavy work:
     ```python
     @app.post("/webhook")
     async def handle_webhook(notification: dict):
         webhook_queue.enqueue('tasks.process_webhook', notification)
         return {"status": "queued"}  # Instant response
     ```

3. **Review Server-Side Queue**:
   - Check if webhook delivery queue is backed up
   - Ensure sufficient worker threads/processes

### Missing Events

**Symptoms**: Some events not triggering webhook notifications.

**Debugging Steps**:

1. **Verify Event Subscription**:
   ```bash
   GET /threads/{threadId}/subscriptions/{subscriptionId}
   ```
   - Check `events` array includes expected event types
   - Use empty array (`[]`) to receive all events

2. **Check Event Type Spelling**:
   - Event types are case-sensitive
   - Correct: `"run.completed"`
   - Incorrect: `"run.complete"`, `"Run.Completed"`

3. **Review Server Logs**:
   - Check if events are being generated but not delivered
   - Look for errors in webhook delivery pipeline

---

## Best Practices

### 1. Security

**Use HTTPS Only**: Never accept webhooks over HTTP (credentials/data exposed).

**Verify Signatures**: Always validate `X-Signature` header to prevent spoofing:
```python
if not verify_signature(body, x_signature, x_timestamp):
    raise HTTPException(status_code=401)
```

**Validate Timestamps**: Reject webhooks older than 5 minutes to prevent replay attacks.

**Rotate Secrets**: Periodically update `webhookSecret` and update subscription:
```bash
PATCH /threads/{threadId}/subscriptions/{subscriptionId}
{"webhookSecret": "new_secret_value"}
```

### 2. Reliability

**Return 200 OK Quickly**: Don't block webhook response waiting for processing:
```python
# Good: Immediate response
@app.post("/webhook")
async def handle_webhook(notification: dict):
    await queue.enqueue(notification)
    return {"status": "queued"}

# Bad: Slow response (may timeout)
@app.post("/webhook")
async def handle_webhook(notification: dict):
    await heavy_processing(notification)  # 30 seconds
    return {"status": "done"}  # Server already timed out!
```

**Implement Idempotency**: Handle duplicate deliveries gracefully:
```python
if notification_key in processed_set:
    return {"status": "duplicate"}
```

**Use Retries with Backoff**: Client-side retry logic for transient failures:
```python
for attempt in range(3):
    try:
        process_notification(notification)
        break
    except TransientError:
        await asyncio.sleep(2 ** attempt)  # 1s, 2s, 4s
```

### 3. Performance

**Queue Background Work**: Don't perform heavy work in webhook handler:
```python
# Use background queue (Redis, RabbitMQ, Celery, etc.)
webhook_queue.enqueue('tasks.process_notification', notification)
```

**Batch Fetch Operations**: When processing multiple notifications, batch API calls:
```python
# Bad: N API calls
for notification in notifications:
    thread = await fetch_thread(notification["threadId"])

# Good: 1 API call
thread_ids = [n["threadId"] for n in notifications]
threads = await fetch_threads_batch(thread_ids)
```

**Rate Limit Webhook Handlers**: Prevent overload from notification bursts:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/webhook")
@limiter.limit("100/minute")
async def handle_webhook(notification: dict):
    ...
```

### 4. Monitoring

**Track Delivery Metrics**: Monitor success rate, latency, failure count:
```python
# Prometheus metrics
webhook_deliveries_total.labels(status="success").inc()
webhook_delivery_duration.observe(latency_seconds)
```

**Alert on Failures**: Set up alerts when `failureCount > threshold`:
```python
if subscription.failureCount >= 5:
    await send_alert(f"Webhook {subscription.subscriptionId} failing")
```

**Log Webhook Events**: Persist audit trail for compliance and debugging:
```python
await log_webhook_event(subscription, notification, status="delivered")
```

### 5. Debugging

**Expose Webhook Logs**: Provide UI or API to view webhook delivery history:
```bash
GET /threads/{threadId}/subscriptions/{subscriptionId}/deliveries
```

**Test Webhooks Manually**: Provide endpoint to trigger test notifications:
```bash
POST /threads/{threadId}/subscriptions/{subscriptionId}/test
```

**Use Webhook Development Tools**: Services like `ngrok`, `webhook.site`, `requestbin.com` for local testing:
```bash
ngrok http 8000
# Use https://<random>.ngrok.io as webhookUrl for testing
```

---

## Summary

Webhook subscriptions provide real-time, scalable event notifications for conversation threads. Key takeaways:

- **Register webhooks** via `POST /threads/{threadId}/subscriptions` with HTTPS endpoints
- **Verify signatures** using HMAC-SHA256 to prevent spoofing
- **Filter events** to receive only relevant notifications
- **Return 200 OK quickly** from webhook handlers (queue heavy work)
- **Handle duplicates** with idempotency checks
- **Monitor failures** with delivery metrics and alerts
- **Use fan-out** for multiple services (Slack, Teams, PagerDuty)

For more details, see:
- **Proactive Messaging Guide**: Agent-initiated conversations using EventContent + webhooks
- **Getting Started Guide**: Basic API usage and authentication
- **Run Lifecycle Specification**: Event types and run state transitions
