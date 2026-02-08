# Streaming Specification

**Version**: 2.0
**Date**: 2026-02-06
**Status**: Specification

## Overview

This specification defines streaming behavior for the Agent Runtime API using Server-Sent Events (SSE) and webhooks for real-time updates.

**Key Principles:**

1. **Unified event types** - Same events (`message.created`, `message.updated`) across all resources
2. **Context in payload** - Resource IDs (runId, threadId, agentId) in data, not event names
3. **Event sequencing** - `eventSeq` provides deterministic ordering per resource
4. **Content type reuse** - Leverage existing AIContent types for all message payloads

---

## Event Naming Convention

This specification uses two different naming conventions for events, depending on the context:

### SSE Wire Format (Event Field)

The `event:` field in Server-Sent Events uses **dot notation** with lowercase letters:

```text
event: message.created
event: message.updated
event: message.completed
event: run.started
event: run.completed
event: thread.archived
```

**Pattern**: `<resource>.<action>` (e.g., `message.created`, `run.failed`)

### TypeSpec Model Names

The TypeSpec definitions use **PascalCase** with "Event" suffix:

```typescript
MessageCreatedEvent;
MessageUpdatedEvent;
MessageCompletedEvent;
RunStartedEvent;
RunCompletedEvent;
ThreadArchivedEvent;
```

**Pattern**: `<Resource><Action>Event` (e.g., `MessageCreatedEvent`, `RunFailedEvent`)

**Source**: See [streaming.tsp](../typespec/streaming.tsp) for all event model definitions.

### Key Distinctions

| Context         | Naming Style | Example               | Where Used                  |
| --------------- | ------------ | --------------------- | --------------------------- |
| SSE event field | dot.notation | `message.created`     | `event:` line in SSE stream |
| TypeSpec model  | PascalCase   | `MessageCreatedEvent` | TypeSpec definitions, docs  |
| Event data      | JSON         | `{...fields...}`      | `data:` line in SSE stream  |

**Both refer to the same event**, just in different contexts:

- The SSE `event:` field identifies the event type for client routing
- The `data:` field contains the TypeSpec model instance as JSON
- Documentation may reference either name depending on context

### Complete SSE Event Structure

```text
event: message.created
data: {"runId":"run-123","agentId":"agent-gpt4","eventSeq":2,"message":{...},"createdAt":"2026-02-06T10:00:01Z"}
```

**Breakdown**:

- **`event: message.created`** - SSE event type (dot notation) for client event listener
- **`data: {...}`** - JSON payload conforming to `MessageCreatedEvent` TypeSpec model

### Implementation Notes

**Client-Side Event Listeners**:

```typescript
// Use dot notation for event listeners
eventSource.addEventListener("message.created", (e) => {
  const data = JSON.parse(e.data); // Data conforms to MessageCreatedEvent
  // ...
});

eventSource.addEventListener("run.completed", (e) => {
  const data = JSON.parse(e.data); // Data conforms to RunCompletedEvent
  // ...
});
```

**TypeSpec References**:

```typescript
// TypeSpec model names are used in type definitions and documentation
model MessageCreatedEvent {
  runId?: string;
  message: ChatMessage;
  eventSeq: int64;
  createdAt: utcDateTime;
}
```

---

## Streaming Endpoints

### Run Streaming

**Endpoint**: `GET /runs/{runId}/stream`

**Purpose**: Stream events for a specific run execution

**Events Emitted**:

- `run.started`
- `message.created`, `message.updated`, `message.completed`
- `run.completed`, `run.failed`, `run.cancelled`, `run.timeout`
- `run.requires_action`, `run.input_required`

**Query Parameters**:

- `events` - Filter event types: `?events=message.created,run.completed`
- `since` - Events after timestamp: `?since=2026-02-06T10:00:00Z`

### Thread Streaming

**Endpoint**: `GET /threads/{threadId}/stream`

**Purpose**: Stream all activity in a thread (multi-participant conversations)

**Events Emitted**:

- `message.created`, `message.updated`, `message.completed`
- `run.created`, `run.started`, `run.completed`, `run.failed`, etc.
- `participant.added`, `participant.removed`
- `thread.created`, `thread.archived`, `thread.closed`, `thread.reopened`, `thread.deleted`

**Query Parameters**:

- `events` - Filter event types
- `since` - Events after timestamp
- `roles` - Filter by message role: `?roles=user,assistant`
- `userIds` - Filter by user IDs: `?userIds=user-alice,user-bob`
- `agentIds` - Filter by agent IDs: `?agentIds=agent-support`
- `contentTypes` - Filter by content types: `?contentTypes=text,image`
- `audience` - Filter by audience: `?audience=user`

### Agent Streaming

**Endpoint**: `GET /agents/{agentId}/stream`

**Purpose**: Monitor all activity for a specific agent across all threads

**Events Emitted**:

- All run and message events for this agent
- `agent.created`, `agent.updated`, `agent.deleted`
- `agent.enabled`, `agent.disabled`, `agent.error`

**Query Parameters**: Same as thread streaming, plus:

- `threadId` - Filter by thread: `?threadId=thread-123`

---

## Event Types

### Unified Message Events

These events use **identical event types** across runs, threads, and agents.

| Event Type          | Description                | Payload Fields                                                                      |
| ------------------- | -------------------------- | ----------------------------------------------------------------------------------- |
| `message.created`   | New message or first chunk | `runId?`, `threadId?`, `agentId?`, `message`, `eventSeq`, `createdAt`               |
| `message.updated`   | Streaming chunk or edit    | `runId?`, `threadId?`, `agentId?`, `messageId`, `message: { contents }`, `eventSeq` |
| `message.completed` | Streaming finished         | `runId?`, `threadId?`, `agentId?`, `messageId`, `usage`, `eventSeq`, `completedAt`  |

### Run Lifecycle Events

| Event Type            | Description         | Payload Fields                                                                                            |
| --------------------- | ------------------- | --------------------------------------------------------------------------------------------------------- |
| `run.created`         | Run created         | `runId`, `threadId?`, `agentId`, `status: "queued"`, `eventSeq`, `createdAt`                              |
| `run.started`         | Run started         | `runId`, `threadId?`, `agentId?`, `status: "in_progress"`, `eventSeq`, `startedAt`                        |
| `run.completed`       | Run succeeded       | `runId`, `threadId?`, `agentId?`, `status: "completed"`, `output`, `usage?`, `eventSeq`, `completedAt`    |
| `run.failed`          | Run failed          | `runId`, `threadId?`, `agentId?`, `status: "failed"`, `error`, `eventSeq`, `failedAt`                     |
| `run.cancelled`       | Run cancelled       | `runId`, `threadId?`, `agentId?`, `status: "cancelled"`, `reason?`, `eventSeq`, `cancelledAt`             |
| `run.timeout`         | Run timed out       | `runId`, `threadId?`, `agentId?`, `status: "timeout"`, `output?`, `usage?`, `eventSeq`, `timedOutAt`      |
| `run.requires_action` | Needs tool approval | `runId`, `threadId?`, `agentId?`, `status: "requires_action"`, `required_action`, `eventSeq`, `timestamp` |
| `run.input_required`  | Needs user input    | `runId`, `threadId?`, `agentId?`, `status: "input_required"`, `required_input`, `eventSeq`, `timestamp`   |

### Thread Lifecycle Events

| Event Type        | Description     | Payload Fields                                             |
| ----------------- | --------------- | ---------------------------------------------------------- |
| `thread.created`  | Thread created  | `threadId`, `status: "active"`, `eventSeq`, `createdAt`    |
| `thread.archived` | Thread archived | `threadId`, `archivedBy?`, `eventSeq`, `archivedAt`        |
| `thread.closed`   | Thread closed   | `threadId`, `closedBy?`, `reason?`, `eventSeq`, `closedAt` |
| `thread.reopened` | Thread reopened | `threadId`, `reopenedBy?`, `eventSeq`, `reopenedAt`        |
| `thread.deleted`  | Thread deleted  | `threadId`, `deletedBy?`, `eventSeq`, `deletedAt`          |

### Participant Events

| Event Type            | Description        | Payload Fields                                                  |
| --------------------- | ------------------ | --------------------------------------------------------------- |
| `participant.added`   | Participant joined | `threadId`, `participant`, `eventSeq`, `addedAt`                |
| `participant.removed` | Participant left   | `threadId`, `participantId`, `reason?`, `eventSeq`, `removedAt` |

### Agent Configuration Events

| Event Type       | Description      | Payload Fields                                       |
| ---------------- | ---------------- | ---------------------------------------------------- |
| `agent.created`  | Agent registered | `agentId`, `name`, `model?`, `eventSeq`, `createdAt` |
| `agent.updated`  | Config changed   | `agentId`, `changes`, `eventSeq`, `updatedAt`        |
| `agent.deleted`  | Agent removed    | `agentId`, `eventSeq`, `deletedAt`                   |
| `agent.enabled`  | Agent enabled    | `agentId`, `eventSeq`, `enabledAt`                   |
| `agent.disabled` | Agent disabled   | `agentId`, `reason?`, `eventSeq`, `disabledAt`       |
| `agent.error`    | Agent error      | `agentId`, `error`, `eventSeq`, `timestamp`          |

---

## Hook Integration with Streaming

### Overview

Hooks integrate with streaming to enable real-time content moderation, filtering, and modification. When hooks are configured, they evaluate events **before** they are emitted to SSE clients or webhooks.

**Key Concepts:**

- **Hook Evaluation Points**: Specific event types trigger hook evaluation
- **Blocking Hooks**: Synchronous evaluation that buffers the stream
- **Non-Blocking Hooks**: Asynchronous evaluation (telemetry, logging)
- **Content Modification**: Hooks can modify event data before emission
- **Event Metadata**: Events include `hookModified` flag when altered
- **Fallback Behavior**: Event-type-based fallback on hook failure

**Related Specifications:**

- [Hooks Specification](./hooks.md) - Hook types, conditions, responses
- [Hooks TypeSpec](../typespec/hooks.tsp) - Hook model definitions
- [Remote Endpoints](./remote-endpoints.md) - WebSocket/HTTP protocol

### Hook Evaluation Points

Hooks evaluate at specific points in the streaming lifecycle:

| Event Type          | Hook Evaluation | Blocking Allowed | Common Use Cases                   |
| ------------------- | --------------- | ---------------- | ---------------------------------- |
| `run.started`       | Before emission | Yes              | Authorization check, rate limiting |
| `content.created`   | Before emission | Yes              | PII redaction, content filtering   |
| `content.updated`   | Before emission | No (streaming)   | Real-time moderation, telemetry    |
| `message.created`   | Before emission | Yes              | Content approval, filtering        |
| `message.updated`   | Before emission | No (streaming)   | Chunk filtering, telemetry         |
| `message.completed` | Before emission | Yes              | Final approval, compliance check   |
| `run.completed`     | Before emission | Yes              | Output validation, audit logging   |

**Early Events** (block on failure): `run.started`, `content.created`, `message.created`
**Late Events** (allow on failure): `content.updated`, `message.updated`, `message.completed`

**Source**: [Hooks Specification](./hooks.md) - Event-Type-Based Fallback

### Hook-Modified Events

When a hook modifies event data, the event includes `hookModified` metadata:

#### Original Event (No Hooks)

**SSE Wire Format**:

```text
event: message.created
data: {"runId":"run-123","agentId":"agent-gpt4","eventSeq":2,"message":{"messageId":"msg-abc","role":"assistant","contents":[{"kind":"text","text":"Your SSN is 123-45-6789."}]},"createdAt":"2026-02-06T10:00:01Z"}
```

**Formatted (MessageCreatedEvent model)**:

```json
{
  "runId": "run-123",
  "agentId": "agent-gpt4",
  "eventSeq": 2,
  "message": {
    "messageId": "msg-abc",
    "role": "assistant",
    "contents": [
      {
        "kind": "text",
        "text": "Your SSN is 123-45-6789."
      }
    ]
  },
  "createdAt": "2026-02-06T10:00:01Z"
}
```

#### Modified Event (With PII Redaction Hook)

**SSE Wire Format**:

```text
event: message.created
data: {"runId":"run-123","agentId":"agent-gpt4","eventSeq":2,"message":{"messageId":"msg-abc","role":"assistant","contents":[{"kind":"text","text":"Your SSN is [REDACTED]."}]},"hookModified":true,"createdAt":"2026-02-06T10:00:01Z"}
```

**Formatted (MessageCreatedEvent model with hookModified)**:

```json
{
  "runId": "run-123",
  "agentId": "agent-gpt4",
  "eventSeq": 2,
  "message": {
    "messageId": "msg-abc",
    "role": "assistant",
    "contents": [
      {
        "kind": "text",
        "text": "Your SSN is [REDACTED]."
      }
    ]
  },
  "hookModified": true,
  "createdAt": "2026-02-06T10:00:01Z"
}
```

**Fields Added**:

- `hookModified: true` - Indicates content was altered by a hook
- Original `eventSeq` preserved (modification is transparent to ordering)

#### Blocked Event

When a hook blocks an event, **no event is emitted**:

```typescript
// Hook configuration
{
  "kind": "block",
  "condition": {
    "kind": "content",
    "patterns": ["offensive_term"]
  }
}

// Result: No message.created event emitted
// Stream continues with next event
```

**Behavior:**

- Blocked events are **silently dropped** from stream
- `eventSeq` increments normally (gap in sequence indicates blocked event)
- No indication to client that event was blocked (by design for security)

### Event Ordering with Hooks

Hook evaluation affects event timing but preserves `eventSeq` ordering:

#### Without Hooks (Normal Flow)

```typescript
t=0ms:   Run starts
t=10ms:  eventSeq 1: event: run.started (RunStartedEvent)
t=50ms:  eventSeq 2: event: message.created (MessageCreatedEvent) "Hello"
t=100ms: eventSeq 3: event: message.updated (MessageUpdatedEvent) " world"
t=150ms: eventSeq 4: event: message.completed (MessageCompletedEvent)
```

#### With Blocking Hooks (Delayed Flow)

```typescript
t=0ms:   Run starts
t=10ms:  Hook evaluates RunStartedEvent (blocking, 50ms latency)
t=60ms:  eventSeq 1: event: run.started (emitted after hook approval)
t=100ms: Hook evaluates MessageCreatedEvent (blocking, 30ms latency)
t=130ms: eventSeq 2: event: message.created "[REDACTED]" (modified, emitted)
t=180ms: eventSeq 3: event: message.updated " world" (non-blocking hook, no delay)
t=230ms: eventSeq 4: event: message.completed
```

**Key Observations**:

- `eventSeq` preserves logical order (1, 2, 3, 4)
- Timing delays from blocking hooks (50ms, 30ms)
- Non-blocking hooks don't delay emission
- Modified content transparent to clients (same `eventSeq`)

**Source**: [Hooks Specification](./hooks.md) - Hook Evaluation Flow

### Blocking Hooks in Streaming

Blocking hooks pause stream emission until evaluation completes:

#### Client Experience

```typescript
// Client receives events with variable timing

t=0s:    eventSource.onopen()
t=0.06s: event: run.started         // Delayed by 50ms hook
t=0.13s: event: message.created     // Delayed by 30ms hook
t=0.18s: event: message.updated     // No delay (non-blocking)
t=0.23s: event: message.completed
```

**Characteristics:**

- **Buffering**: Server buffers subsequent events during hook evaluation
- **Timeout**: Hooks timeout after configurable period (default 5s, max 30s)
- **Fallback**: On timeout, apply event-type-based fallback (block early events, allow late events)
- **Transparency**: Clients see normal SSE stream (delays are internal)

#### Server-Side Buffering

```typescript
// Pseudocode for hook evaluation with buffering
async function emitEvent(event: StreamEvent, hooks: Hook[]) {
  const applicableHooks = hooks.filter((h) =>
    h.eventTypes.includes(event.type),
  );

  if (applicableHooks.length === 0) {
    // No hooks: emit immediately
    sseStream.emit(event);
    return;
  }

  // Evaluate hooks (may block)
  const hookResults = await Promise.all(
    applicableHooks.map((hook) => evaluateHook(hook, event)),
  );

  // Apply hook results
  const blockedByHook = hookResults.some((r) => r.action.kind === "block");
  if (blockedByHook) {
    // Drop event silently
    return;
  }

  // Apply modifications
  let modifiedEvent = event;
  let wasModified = false;

  for (const result of hookResults) {
    if (result.action.kind === "modify") {
      modifiedEvent = applyModification(modifiedEvent, result.action.content);
      wasModified = true;
    }
  }

  if (wasModified) {
    modifiedEvent.hookModified = true;
  }

  // Emit modified or original event
  sseStream.emit(modifiedEvent);
}
```

**Buffer Limits:**

- Max buffered events: 1000 (per stream)
- Max buffer time: 10s (per event)
- Exceeded limits: Close stream with error

**Source**: [Remote Endpoints](./remote-endpoints.md) - WebSocket Buffering

### Client Handling of Hook-Modified Events

Clients should handle `hookModified` metadata gracefully:

#### Basic Handling

```typescript
const eventSource = new EventSource("/runs/run-123/stream");

eventSource.addEventListener("message.created", (e) => {
  const data = JSON.parse(e.data);

  // Check if hook modified the content
  if (data.hookModified) {
    console.log("Content was filtered or modified by hooks");
  }

  // Render content normally (modifications are already applied)
  renderMessage(data.message);
});
```

#### Sequence Gap Detection (Blocked Events)

```typescript
let lastEventSeq = 0;

eventSource.addEventListener("message", (e) => {
  const data = JSON.parse(e.data);

  // Detect gaps in eventSeq (indicates blocked events)
  if (data.eventSeq > lastEventSeq + 1) {
    const gapSize = data.eventSeq - lastEventSeq - 1;
    console.log(`${gapSize} events were blocked by hooks`);
  }

  lastEventSeq = data.eventSeq;
  processEvent(data);
});
```

#### Handling Modified Streaming Chunks

```typescript
let accumulatedText = "";
let chunkModifications = [];

eventSource.addEventListener("message.updated", (e) => {
  const data = JSON.parse(e.data);

  if (data.message?.contents) {
    data.message.contents.forEach((content) => {
      if (content.kind === "text" && content.text) {
        // Track if this chunk was modified
        if (data.hookModified) {
          chunkModifications.push({
            eventSeq: data.eventSeq,
            originalLength: accumulatedText.length,
            modifiedText: content.text,
          });
        }

        accumulatedText += content.text;
        updateUI(accumulatedText);
      }
    });
  }
});

eventSource.addEventListener("message.completed", (e) => {
  const data = JSON.parse(e.data);

  if (chunkModifications.length > 0) {
    console.log(`${chunkModifications.length} chunks were modified by hooks`);
  }

  // Final content is already hook-processed
  finalizeMessage(accumulatedText, data.usage);
});
```

### Hook Failures in Streaming

When hooks fail (timeout, network error, server error), fallback behavior applies:

#### Early Event Failure (Block on Failure)

```typescript
// Hook timeout evaluating run.started
// Fallback: Block event

// No run.started event emitted
// Stream terminates with error
event: error
data: {
  "code": "hook_evaluation_failed",
  "message": "Hook timeout during run.started evaluation",
  "details": {
    "eventType": "run.started",
    "hookId": "hook-123",
    "reason": "timeout"
  }
}

// Connection closed by server
```

#### Late Event Failure (Allow on Failure)

```typescript
// Hook timeout evaluating message.updated
// Fallback: Allow event (emit original)

event: message.updated
data: {
  "runId": "run-123",
  "messageId": "msg-abc",
  "eventSeq": 3,
  "message": {
    "contents": [{"kind": "text", "text": " world"}]
  },
  "hookModified": false  // Hook failed, original content emitted
}

// Stream continues normally
```

**Fallback Summary:**

| Event Type          | Fallback Behavior        | Stream Impact                |
| ------------------- | ------------------------ | ---------------------------- |
| `run.started`       | Block (no event emitted) | Stream terminates with error |
| `content.created`   | Block (no event emitted) | Stream terminates with error |
| `message.created`   | Block (no event emitted) | Stream terminates with error |
| `content.updated`   | Allow (emit original)    | Stream continues             |
| `message.updated`   | Allow (emit original)    | Stream continues             |
| `message.completed` | Allow (emit original)    | Stream continues             |
| `run.completed`     | Allow (emit original)    | Stream continues             |

**Source**: [Error Handling](./error-handling.md) - Fallback Strategies

### Hook Evaluation Latency

Hook evaluation adds latency to streaming:

| Hook Type              | Typical Latency     | Impact     |
| ---------------------- | ------------------- | ---------- |
| BlockHook              | <1ms                | Negligible |
| ModifyHook             | 1-5ms (local regex) | Low        |
| RemoteHook (WebSocket) | 10-100ms            | Moderate   |
| RemoteHook (HTTP)      | 50-500ms            | High       |

**Optimization Strategies:**

1. **Use WebSocket for Remote Hooks**: Lower latency than HTTP
2. **Non-Blocking When Possible**: Use TelemetryHook for logging (doesn't block)
3. **Optimize Remote Endpoints**: Keep hook evaluation fast (<50ms)
4. **Batch Non-Critical Checks**: Group telemetry hooks, evaluate asynchronously
5. **Client-Side Caching**: Cache hook results for repeated patterns

**Source**: [Remote Endpoints](./remote-endpoints.md) - Protocol Selection

### Implementation Requirements

#### Server Requirements

Servers implementing streaming with hooks MUST:

1. **Hook Evaluation Order**: Evaluate hooks before emitting events
2. **Blocking Behavior**: Buffer stream during blocking hook evaluation
3. **Timeout Enforcement**: Apply timeout limits (5s default, 30s max)
4. **Fallback Behavior**: Apply event-type-based fallback on hook failure
5. **Metadata Addition**: Add `hookModified: true` to modified events
6. **Sequence Preservation**: Maintain monotonic `eventSeq` regardless of hook results

Servers SHOULD:

1. **Hook Latency Tracking**: Monitor hook evaluation duration
2. **Circuit Breaker**: Disable failing hooks after repeated failures
3. **Hook Result Caching**: Cache hook results for identical events (short TTL)
4. **Graceful Degradation**: Continue streaming on non-critical hook failures

#### Client Requirements

Clients consuming streams with hooks SHOULD:

1. **Handle `hookModified` Flag**: Log or display indication when content is filtered
2. **Detect Sequence Gaps**: Identify blocked events via `eventSeq` gaps
3. **Graceful Handling**: Continue processing when events are blocked or modified
4. **Reconnection Logic**: Reconnect on stream termination due to hook failures
5. **User Feedback**: Inform users when content is filtered or modified (if applicable)

---

## Streaming Encrypted Content

### Overview

Encrypted content can be streamed incrementally, but encryption/decryption occurs at the message level, not per chunk. This section explains how encrypted streaming works and client handling requirements.

**Key Principles:**

- **Message-Level Encryption**: Encrypt complete message, not individual chunks
- **Client Buffering**: Client buffers encrypted chunks until completion
- **Decrypt After Completion**: Client decrypts after `message.completed` event
- **Server Opacity**: Server streams encrypted chunks as opaque data

**Related Specifications:**

- [Content Encryption Specification](./content-encryption.md) - Encryption algorithms
- [Message Lifecycle Specification](./message-lifecycle.md) - Message storage

### Encryption Pattern

**Incorrect Approach (Per-Chunk Encryption):**

```typescript
// ❌ WRONG: Don't encrypt individual chunks
t=50ms:  Chunk 1: "Hello" → Encrypt → Stream
t=100ms: Chunk 2: " world" → Encrypt → Stream
t=150ms: Chunk 3: "!" → Encrypt → Stream

// Problem: Each chunk has different IV, can't be decrypted incrementally
```

**Correct Approach (Complete Message Encryption):**

```typescript
// ✅ CORRECT: Encrypt complete message after generation

// 1. Agent generates complete message (server-side)
Agent generates: "Hello world, how can I help you today?"

// 2. Server encrypts complete message
Plaintext: "Hello world, how can I help you today?"
Encrypt with AES-256-GCM:
  - Ciphertext: "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=..."
  - IV: "8Kk3Kgz5XjRlipRkwB=="
  - AuthTag: "GxcTlipRkwB0K1Y8Kk3K=="

// 3. Server streams encrypted message in chunks
t=50ms:  message.created: {
  contents: [{
    kind: "text",
    text: "U2FsdGVkX1+vupppZksv",  // First chunk of ciphertext
    annotations: {
      encryption: {
        algorithm: "AES-256-GCM",
        keyId: "key-1",
        iv: "8Kk3Kgz5XjRlipRkwB==",
        authTag: "GxcTlipRkwB0K1Y8Kk3K=="
      }
    }
  }]
}

t=100ms: message.updated: {
  contents: [{
    kind: "text",
    text: "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=..."  // More ciphertext
  }]
}

t=150ms: message.completed: {
  contents: [{
    kind: "text",
    text: "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=..."  // Complete ciphertext
  }]
}

// 4. Client buffers encrypted chunks and decrypts after completion
Client receives all chunks → Reconstructs complete ciphertext → Decrypts → Displays plaintext
```

### Client Handling

**Streaming Encrypted Content Flow:**

```typescript
// Client implementation
const eventSource = new EventSource("/runs/run-123/stream");
let encryptedBuffer = "";
let encryptionMetadata = null;

eventSource.addEventListener("message.created", (e) => {
  const data = JSON.parse(e.data);

  if (data.message?.contents) {
    data.message.contents.forEach((content) => {
      // Check if content is encrypted
      if (content.annotations?.encryption) {
        // Store encryption metadata (IV, authTag, keyId)
        encryptionMetadata = content.annotations.encryption;

        // Buffer encrypted content (don't display yet)
        encryptedBuffer = content.text;

        // Show loading indicator
        showLoadingIndicator("Loading encrypted message...");
      } else {
        // Non-encrypted content: display immediately
        displayContent(content.text);
      }
    });
  }
});

eventSource.addEventListener("message.updated", (e) => {
  const data = JSON.parse(e.data);

  if (data.message?.contents && encryptionMetadata) {
    // Encrypted streaming: buffer chunks
    data.message.contents.forEach((content) => {
      if (content.kind === "text") {
        encryptedBuffer = content.text; // Update buffer with latest chunk
      }
    });

    // Update loading indicator (show progress)
    updateLoadingIndicator(`Received ${encryptedBuffer.length} bytes...`);
  }
});

eventSource.addEventListener("message.completed", async (e) => {
  const data = JSON.parse(e.data);

  if (encryptionMetadata) {
    // Encrypted content complete: decrypt now
    try {
      // Fetch decryption key from KMS
      const key = await fetchKeyFromKMS(encryptionMetadata.keyId);

      // Decrypt complete ciphertext
      const plaintext = await decryptAESGCM(
        encryptedBuffer,
        key,
        encryptionMetadata.iv,
        encryptionMetadata.authTag,
      );

      // Display decrypted plaintext
      displayContent(plaintext);
      hideLoadingIndicator();
    } catch (error) {
      // Decryption failed (tampered content or wrong key)
      showError("Failed to decrypt message: " + error.message);
    }

    // Clear buffer
    encryptedBuffer = "";
    encryptionMetadata = null;
  }
});
```

### Server Behavior

**Requirements:**

Servers MUST:

1. **Generate Complete Message First**: Agent generates complete plaintext message
2. **Encrypt Before Streaming**: Encrypt complete message before sending first chunk
3. **Stream Ciphertext Incrementally**: Break ciphertext into chunks for streaming
4. **Include Metadata in First Chunk**: Include `encryption` metadata in `message.created` event
5. **Preserve Metadata Consistency**: Same IV, authTag, keyId across all chunks

**Implementation Pattern:**

```typescript
// Server-side pseudocode
async function streamEncryptedMessage(run: Run, message: string) {
  // 1. Generate complete message
  const plaintext = await agent.generate(run.input);

  // 2. Check if encryption required (from agent config)
  if (run.agent.encryptionConfig) {
    // 3. Encrypt complete message
    const key = await fetchKeyFromKMS(run.agent.encryptionConfig.keyId);
    const { ciphertext, iv, authTag } = encryptAESGCM(plaintext, key);

    // 4. Stream encrypted message in chunks
    const chunkSize = 100; // Bytes per chunk
    for (let i = 0; i < ciphertext.length; i += chunkSize) {
      const chunk = ciphertext.slice(i, i + chunkSize);

      if (i === 0) {
        // First chunk: include encryption metadata
        emitEvent({
          event: "message.created",
          data: {
            message: {
              contents: [
                {
                  kind: "text",
                  text: chunk,
                  annotations: {
                    encryption: {
                      algorithm: "AES-256-GCM",
                      keyId: run.agent.encryptionConfig.keyId,
                      iv: base64Encode(iv),
                      authTag: base64Encode(authTag),
                    },
                  },
                },
              ],
            },
          },
        });
      } else {
        // Subsequent chunks: no metadata (already sent)
        emitEvent({
          event: "message.updated",
          data: {
            message: {
              contents: [
                {
                  kind: "text",
                  text: ciphertext.slice(0, i + chunkSize), // Cumulative
                },
              ],
            },
          },
        });
      }

      await sleep(10); // Simulate streaming delay
    }

    // 5. Complete message
    emitEvent({
      event: "message.completed",
      data: {
        message: {
          contents: [
            {
              kind: "text",
              text: ciphertext, // Complete ciphertext
            },
          ],
        },
      },
    });
  }
}
```

### Security Considerations

**Content Length Visibility:**

Streaming encrypted content reveals content length to server:

**Tradeoff:**

- **Pro**: Enables real-time streaming user experience
- **Con**: Server can infer message length (leaks metadata)

**Acceptable for most use cases:**

- Healthcare: Length leak is acceptable (HIPAA allows)
- Legal: Length leak is acceptable (minimal risk)
- Finance: Length leak is acceptable (content confidentiality preserved)

**Mitigation (if needed):**

- Pad plaintext to fixed size before encryption
- Use block-level padding (e.g., 1KB blocks)

**Example:**

```typescript
// Pad message to fixed size (1KB blocks)
function padMessage(plaintext: string): string {
  const blockSize = 1024;
  const paddingNeeded = blockSize - (plaintext.length % blockSize);
  return plaintext + "\x00".repeat(paddingNeeded);
}

// Encrypt padded message
const padded = padMessage("Hello world"); // Padded to 1024 bytes
const { ciphertext, iv, authTag } = encryptAESGCM(padded, key);

// Stream ciphertext (all messages same length)
```

**Authentication Tag Verification:**

Client MUST verify authentication tag after decryption:

```typescript
try {
  const plaintext = await decryptAESGCM(ciphertext, key, iv, authTag);
  // Tag verified automatically by AEAD algorithm
} catch (error) {
  if (error.code === "AUTHENTICATION_FAILED") {
    // Content was tampered or corrupted
    showError("Message integrity verification failed");
    logSecurityEvent("encrypted_content_tampered", { messageId });
  }
}
```

**Source**: [Content Encryption Specification](./content-encryption.md) - Security Considerations

### Limitations

**Encrypted streaming has these limitations:**

1. **No Incremental Display**: Client cannot display content until decryption completes
   - User sees loading indicator during streaming
   - No "typing effect" for encrypted messages

2. **Increased Latency**: Decryption adds latency after `message.completed`
   - AES-256-GCM: ~10-50ms for typical message
   - Key fetch from KMS: +50-200ms (if not cached)

3. **Memory Buffering**: Client must buffer entire ciphertext before decryption
   - Large messages (>1MB) may cause memory pressure
   - Consider chunking large documents separately

4. **No Partial Retry**: If decryption fails, entire message must be re-fetched
   - No way to retry individual chunks
   - Client must GET /messages/{messageId} to retry

### Performance Optimization

**Recommendations:**

1. **Cache Decryption Keys**: Cache keys in memory (1 hour TTL)

   ```typescript
   const keyCache = new Map<string, CryptoKey>();

   async function getCachedKey(keyId: string): Promise<CryptoKey> {
     if (keyCache.has(keyId)) {
       return keyCache.get(keyId);
     }
     const key = await fetchKeyFromKMS(keyId);
     keyCache.set(keyId, key);
     return key;
   }
   ```

2. **Pre-fetch Keys**: Fetch key during `message.created` (parallel with buffering)

   ```typescript
   eventSource.addEventListener("message.created", async (e) => {
     if (encryptionMetadata) {
       // Start key fetch immediately (don't await)
       fetchKeyFromKMS(encryptionMetadata.keyId).then((key) => {
         cachedKey = key;
       });
     }
   });
   ```

3. **Show Progress**: Update UI during buffering

   ```typescript
   eventSource.addEventListener("message.updated", (e) => {
     const progress = (encryptedBuffer.length / estimatedSize) * 100;
     updateProgressBar(progress);
   });
   ```

4. **Web Workers**: Decrypt in background thread (avoid blocking UI)

   ```typescript
   const decryptWorker = new Worker("decrypt-worker.js");

   decryptWorker.postMessage({
     ciphertext: encryptedBuffer,
     key: key,
     iv: encryptionMetadata.iv,
     authTag: encryptionMetadata.authTag,
   });

   decryptWorker.onmessage = (e) => {
     displayContent(e.data.plaintext);
   };
   ```

**Source**: [Content Encryption Specification](./content-encryption.md) - Performance Considerations

---

## Event Sequencing

### Event Sequence Numbers (`eventSeq`)

Each event includes `eventSeq` for deterministic ordering within a resource.

**Properties**:

- Monotonically increasing per resource (thread, agent, or run)
- Independent across resources (each thread has its own sequence starting from 1)
- Includes all events: messages, runs, lifecycle changes
- Used for client-side ordering when events arrive out of order

**Example**:

```typescript
// Thread A
eventSeq 1: message.created
eventSeq 2: message.updated
eventSeq 3: participant.added

// Thread B (separate sequence)
eventSeq 1: message.created
eventSeq 2: message.updated
```

### Chunk Ordering

Message streaming chunks are ordered by `eventSeq`:

```typescript
eventSeq 100: message.created msg-1, chunk: "Hello"
eventSeq 101: message.updated msg-1, chunk: " world"
eventSeq 102: message.updated msg-1, chunk: "!"
eventSeq 103: message.completed msg-1
```

Clients accumulate chunks in `eventSeq` order for correct rendering.

### Complete SSE Event Timeline

```text
Server-Sent Events Timeline - Run with Tool Call and Message Streaming
═══════════════════════════════════════════════════════════════════════════════════

Time     eventSeq  SSE Event Type     TypeSpec Model           Client Action
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=0ms   │         │ (Client connects)│                       │ GET /runs/run-123
        │         │                  │                       │ /stream
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=50ms  │    1    │ run.started      │ RunStartedEvent       │ ▶ Display:
        │         │                  │                       │   "Run started"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=100ms │    2    │ message.created  │ MessageCreatedEvent   │ ▶ Create message
        │         │                  │                       │   Display: "H"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=120ms │    3    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "He"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=140ms │    4    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Hel"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=160ms │    5    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Hell"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=180ms │    6    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Hello"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=200ms │    7    │ message.completed│ MessageCompletedEvent │ ▶ Finalize msg
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=250ms │    8    │ run.requires_    │ RunRequiresAction     │ ▶ Show: "Calling
        │         │ action           │ Event                 │   search_web..."
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=300ms │         │ (Client executes │                       │ result = await
        │         │  tool)           │                       │ search_web(...)
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=500ms │         │ (Client submits) │                       │ POST submit_tool_
        │         │                  │                       │ outputs
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=600ms │   10    │ message.created  │ MessageCreatedEvent   │ ▶ New message: "B"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=620ms │   11    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Ba"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=640ms │   12    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Bas"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=660ms │   13    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Base"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=680ms │   14    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Based"
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=700ms │   15    │ message.updated  │ MessageUpdatedEvent   │ ▶ Append: "Based
        │         │                  │                       │   on..."
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=750ms │   16    │ message.completed│ MessageCompletedEvent │ ▶ Finalize msg
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────
t=800ms │   17    │ run.completed    │ RunCompletedEvent     │ ▶ Display: "Run
        │         │                  │                       │   completed"
        │         │                  │                       │   Close SSE
────────┼─────────┼──────────────────┼───────────────────────┼───────────────────

═══════════════════════════════════════════════════════════════════════════════════

Legend:
  ▶ = Client UI Update
  eventSeq = Monotonically increasing sequence number

Key Observations:
  1. SSE uses dot notation (message.created), TypeSpec uses PascalCase (MessageCreatedEvent)
  2. Message chunks arrive incrementally (eventSeq 2-7, 10-16)
  3. Client accumulates chunks to render streaming text
  4. Tool call interrupts streaming (eventSeq 8: run.requires_action)
  5. Run pauses at requires_action, resumes after tool results submitted
  6. All events ordered by eventSeq for deterministic replay
```

---

## SSE Protocol

### Connection

```http
GET /runs/run-123/stream HTTP/1.1
Accept: text/event-stream
```

### Event Format

All SSE events follow this format: the `event:` field uses dot notation, the `data:` field contains JSON matching the corresponding TypeSpec model.

```text
event: run.started
data: {"runId":"run-123","agentId":"agent-gpt4","eventSeq":1,"status":"in_progress","startedAt":"2026-02-06T10:00:00Z"}

event: message.created
data: {"runId":"run-123","agentId":"agent-gpt4","eventSeq":2,"message":{"messageId":"msg-abc","role":"assistant","contents":[{"kind":"text","text":"Hello"}]},"createdAt":"2026-02-06T10:00:01Z"}

event: message.updated
data: {"runId":"run-123","agentId":"agent-gpt4","messageId":"msg-abc","eventSeq":3,"message":{"contents":[{"kind":"text","text":" world!"}]}}

event: message.completed
data: {"runId":"run-123","agentId":"agent-gpt4","messageId":"msg-abc","eventSeq":4,"usage":{"totalTokens":10},"completedAt":"2026-02-06T10:00:02Z"}

event: run.completed
data: {"runId":"run-123","agentId":"agent-gpt4","eventSeq":5,"status":"completed","output":[{"messageId":"msg-abc","role":"assistant","contents":[{"kind":"text","text":"Hello world!"}]}],"usage":{"totalTokens":10},"completedAt":"2026-02-06T10:00:05Z"}
```

**Event to Model Mapping**:

| SSE Event (`event:` field) | TypeSpec Model          | Description                |
| -------------------------- | ----------------------- | -------------------------- |
| `run.started`              | `RunStartedEvent`       | Run execution begins       |
| `message.created`          | `MessageCreatedEvent`   | New message or first chunk |
| `message.updated`          | `MessageUpdatedEvent`   | Streaming chunk or edit    |
| `message.completed`        | `MessageCompletedEvent` | Streaming finished         |
| `run.completed`            | `RunCompletedEvent`     | Run succeeded              |

See [streaming.tsp](../typespec/streaming.tsp) for complete event model definitions.

### Client Implementation

```typescript
const eventSource = new EventSource("/runs/run-123/stream");
let accumulatedText = "";

// Listen for SSE event: message.created
// Data conforms to MessageCreatedEvent TypeSpec model
eventSource.addEventListener("message.created", (e) => {
  const data = JSON.parse(e.data); // MessageCreatedEvent
  if (data.message?.contents) {
    data.message.contents.forEach((content) => {
      if (content.kind === "text" && content.text) {
        accumulatedText += content.text;
        updateUI(accumulatedText);
      }
    });
  }
});

// Listen for SSE event: message.updated
// Data conforms to MessageUpdatedEvent TypeSpec model
eventSource.addEventListener("message.updated", (e) => {
  const data = JSON.parse(e.data); // MessageUpdatedEvent
  if (data.message?.contents) {
    data.message.contents.forEach((content) => {
      if (content.kind === "text" && content.text) {
        accumulatedText += content.text;
        updateUI(accumulatedText);
      }
    });
  }
});

// Listen for SSE event: message.completed
// Data conforms to MessageCompletedEvent TypeSpec model
eventSource.addEventListener("message.completed", (e) => {
  const data = JSON.parse(e.data); // MessageCompletedEvent
  console.log("Streaming complete", data.usage);
});

// Listen for SSE event: run.completed
// Data conforms to RunCompletedEvent TypeSpec model
eventSource.addEventListener("run.completed", (e) => {
  const data = JSON.parse(e.data); // RunCompletedEvent
  console.log("Run finished", data.output);
  eventSource.close();
});

eventSource.onerror = (error) => {
  console.error("SSE error:", error);
  // Implement reconnection logic
};
```

---

## Webhooks

### Webhook Subscriptions

Webhook subscriptions are available for all three resource types: runs, threads, and agents.

**Related Specifications:**

- [Subscriptions TypeSpec](../typespec/subscriptions.tsp) - Subscription model definitions
- [Thread Subscriptions API](../api-reference/operations/thread-subscriptions.md) - REST API operations

#### Thread Subscriptions

**Endpoint**: `POST /threads/{threadId}/subscriptions`

**Request**:

```json
{
  "webhookUrl": "https://app.example.com/webhooks/thread-activity",
  "events": ["message.completed", "run.completed"],
  "messageFilters": {
    "roles": ["assistant"],
    "audience": ["user"],
    "contentTypes": ["text"]
  },
  "webhookSecret": "whsec_abc123xyz",
  "active": true
}
```

#### Run Subscriptions

**Endpoint**: `POST /runs/{runId}/subscriptions`

**Request**:

```json
{
  "webhookUrl": "https://app.example.com/webhooks/run-activity",
  "events": ["run.started", "message.created", "run.completed"],
  "messageFilters": {
    "roles": ["assistant"],
    "contentTypes": ["text"]
  },
  "webhookSecret": "whsec_abc123xyz",
  "active": true
}
```

**Use Cases**:

- Monitor specific long-running executions
- Track run lifecycle for orchestration pipelines
- Get notified when critical runs complete
- Build run-specific activity dashboards

#### Agent Subscriptions

**Endpoint**: `POST /agents/{agentId}/subscriptions`

**Request**:

```json
{
  "webhookUrl": "https://app.example.com/webhooks/agent-activity",
  "events": ["run.completed", "agent.updated", "agent.error"],
  "threadId": "thread-123",
  "messageFilters": {
    "roles": ["assistant"],
    "audience": ["user"]
  },
  "webhookSecret": "whsec_abc123xyz",
  "active": true
}
```

**Use Cases**:

- Monitor agent activity across all threads
- Track agent configuration changes
- Build agent analytics dashboards
- Debug agent behavior in production
- Track agent errors and failures

**Note**: Agent subscriptions can optionally filter by `threadId` to narrow monitoring to specific conversations.

### Message Filters

Filter which messages trigger webhook notifications:

| Filter         | Type       | Description            | Example                 |
| -------------- | ---------- | ---------------------- | ----------------------- |
| `roles`        | `string[]` | Filter by message role | `["user", "assistant"]` |
| `userIds`      | `string[]` | Filter by user IDs     | `["user-alice"]`        |
| `agentIds`     | `string[]` | Filter by agent IDs    | `["agent-support"]`     |
| `contentTypes` | `string[]` | Filter by content type | `["text", "image"]`     |
| `audience`     | `string[]` | Filter by audience     | `["user"]`              |

**Filter Logic**:

- Multiple filters use AND logic (all must match)
- Array values within a filter use OR logic
- Empty or omitted filters match all values

### Webhook Payload

```typescript
{
  "type": "thread.activity",
  "resourceId": "thread-123",
  "subscriptionId": "sub-456",
  "eventType": "message.completed",
  "sequenceNumber": 42,  // Per-subscription gap detection
  "eventSeq": 1587,      // Per-resource event ordering
  "timestamp": "2026-02-06T10:00:00Z",
  "data": {
    "messageId": "msg-999"
  }
}
```

### Webhook Security

Verify webhook signatures using HMAC-SHA256:

```typescript
function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string,
): boolean {
  const hmac = crypto.createHmac("sha256", secret);
  hmac.update(payload);
  const expectedSignature = "sha256=" + hmac.digest("hex");
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature),
  );
}

app.post("/webhooks/thread-activity", (req, res) => {
  const signature = req.headers["x-webhook-signature"];
  const rawBody = req.rawBody || JSON.stringify(req.body);

  if (!verifyWebhookSignature(rawBody, signature, webhookSecret)) {
    return res.status(401).send("Invalid signature");
  }

  res.status(200).send("OK");

  // Process webhook asynchronously
  processWebhook(req.body);
});
```

---

## Error Handling

### SSE Errors

```typescript
eventSource.onerror = (error) => {
  console.error("SSE connection error:", error);

  // Reconnect with exponential backoff
  setTimeout(() => {
    const newSource = new EventSource("/runs/run-123/stream");
  }, backoffMs);
};
```

### Run Failures

```
event: run.failed
data: {
  "runId": "run-123",
  "agentId": "agent-gpt4",
  "eventSeq": 7,
  "status": "failed",
  "error": {
    "code": "rate_limit_exceeded",
    "message": "Retry after 60s",
    "details": { "retryAfter": 60 }
  },
  "failedAt": "2026-02-06T10:00:10Z"
}
```

### Webhook Failures

Server retries failed webhooks with exponential backoff:

- Initial retry: 1 second
- Max retries: 5 attempts
- Subscription disabled after max failures

---

## Implementation Guidelines

### Event Ordering

1. **Server-side**: Assign `eventSeq` in strict order
2. **Client-side**: Buffer events and process by `eventSeq`
3. **Out-of-order**: Sort by `eventSeq` before processing

### Message Accumulation

```typescript
const messages = new Map();

// On message.created
messages.set(msg.messageId, msg);

// On message.updated
const existingMsg = messages.get(data.messageId);
const updatedMsg = {
  ...existingMsg,
  contents: [...existingMsg.contents, ...data.message.contents],
};
messages.set(data.messageId, updatedMsg);
```

### Reconnection

1. Track last received `eventSeq`
2. On reconnect, use `?since=<timestamp>` to resume
3. Deduplicate events using `eventSeq`

### Webhook Gap Detection

```typescript
const lastSeq = await db.getLastSequenceNumber(subscriptionId);

if (notification.sequenceNumber !== lastSeq + 1) {
  console.warn("Gap detected, recovering...");

  // Fetch missed events
  const missedData = await fetch(
    `/threads/${threadId}/messages?since=${lastTimestamp}`,
  );

  processMissedData(missedData);
}

await db.setLastSequenceNumber(subscriptionId, notification.sequenceNumber);
```

---

## See Also

- [Content Types](../api-reference/content-types.md) - All AIContent types
- [Thread Auto-Responders](../api-reference/operations/thread-autoresponders.md) - Proactive messaging
- [Thread Subscriptions](../api-reference/operations/thread-subscriptions.md) - Webhook configuration
- [Message Lifecycle](./message-lifecycle.md) - Message state transitions
- [Run Lifecycle](./run-lifecycle.md) - Run state machine
