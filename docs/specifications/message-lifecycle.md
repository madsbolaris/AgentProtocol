# Message Lifecycle Specification

**Version**: 1.0

## Overview

This specification defines message creation, ID assignment, storage, retrieval, and branching behavior for the Agent Runtime API.

**Key Concepts:**
- **Message**: Single message in a conversation (user input, agent response, tool call/result)
- **Thread**: Conversation containing ordered sequence of messages
- **Message ID**: Unique identifier (client-provided or server-generated)
- **Branching**: Git-like conversation trees via `parentMessageId`

## Message Model

### TypeSpec Definition

**Source**: See `ChatMessage` model in `typespec/messages.tsp`

```typescript
model ChatMessage {
  messageId?: string;              // Unique ID (client/server)
  parentMessageId?: string;        // For conversation branching
  threadId?: string;               // Conversation ID
  role: ChatRole;                  // Message role
  contents: AIContent[];           // Message content
  text?: string;                   // Concatenated text (computed)
  authorName?: string;             // Display name
  userId?: string;                 // End user ID
  agentId?: string;                // Agent/bot ID
  completionId?: string;           // Run that generated message
  createdAt?: utcDateTime;         // Creation timestamp
  completedAt?: utcDateTime;       // Completion timestamp
  metadata?: Record<unknown>;      // Custom metadata
  rawRepresentation?: unknown;     // Provider response
}
```

### Message Roles

**TypeSpec**: See `ChatRole` enum in `typespec/messages.tsp`

```typescript
enum ChatRole {
  system,      // System instructions
  developer,   // Developer-provided context
  assistant,   // Agent responses
  user,        // User messages
  tool,        // Tool execution results
  channel,     // Platform/infrastructure events
}
```

**Role Filtering:**
- **Sent to LLM**: `system`, `developer`, `user`, `assistant`, `tool`
- **Filtered from LLM**: `channel` (orchestrator-only)

## Content Types

**TypeSpec**: See `AIContent` union in `typespec/messages.tsp` (lines 370-409)

Messages contain one or more content items, each with a specific `kind` discriminator. The Agent Runtime API supports 29 content types organized into categories.

### Text & Basic Content

Core text-based content types for standard message exchange:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **TextContent** | `text` | Plain text messages | `user`, `assistant`, `system` | ✓ Yes |
| **TextReasoningContent** | `reasoning` | Chain-of-thought reasoning (extended thinking) | `assistant` | ✓ Yes |
| **DataContent** | `data` | Arbitrary structured data | `assistant`, `tool` | ✓ Yes |
| **UriContent** | `uri` | Reference to external content | Any | ✓ Yes |

### Media Content

Rich media content for multimodal scenarios:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **ImageContent** | `image` | Images (vision input/output) | `user`, `assistant` | ✓ Yes |
| **AudioContent** | `audio` | Audio files, voice messages | `user`, `assistant` | ✓ Yes |
| **VideoContent** | `video` | Video content, screen recordings | `user`, `assistant` | ✓ Yes |
| **TranscriptContent** | `transcript` | Real-time transcription for human accessibility | Any | ✗ No* |

*TranscriptContent is **excluded from LLM context** but stored in history. LLMs process audio/video directly; transcripts are for human accessibility (screen readers, closed captions).

### File Content

File attachments and hosted resources:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **FileContent** | `file` | Generic file attachments | `user`, `assistant` | ✓ Yes |
| **HostedFileContent** | `hostedFile` | Server-hosted files (OpenAI, Azure) | `user`, `assistant` | ✓ Yes |
| **HostedVectorStoreContent** | `hostedVectorStore` | Vector embeddings for RAG | `system`, `assistant` | ✓ Yes |

### Function & Tool Content

Tool calling and execution results:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **FunctionCallContent** | `functionCall` | Agent requests tool execution | `assistant` | ✓ Yes |
| **FunctionResultContent** | `functionResult` | Tool execution results | `tool` | ✓ Yes |
| **ErrorContent** | `error` | Error reporting | `tool`, `assistant` | ✓ Yes |

### Document Content

Document search and citation support:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **DocumentContent** | `document` | Document references for RAG | `system`, `assistant` | ✓ Yes |
| **SearchResultContent** | `searchResult` | Search results with citations | `tool`, `assistant` | ✓ Yes |
| **AdaptiveCardContent** | `adaptiveCard` | Rich UI cards (Teams integration) | `assistant` | ✓ Yes |

### Structured Content

System events and special content:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **EventContent** | `event` | External triggers, scheduled events | `channel` | ✓ Yes |
| **TraceContent** | `trace` | Runtime traces, debugging | `system` | ✗ No* |
| **RefusalContent** | `refusal` | Policy violation refusals | `assistant` | ✓ Yes |
| **ContentFilterResultContent** | `contentFilterResult` | Azure content moderation results | `system` | ✓ Yes |

*TraceContent is **excluded from LLM context** (debugging/telemetry only) but stored in history.

### Interactive Content

User interaction and human-in-the-loop prompts:

| Type | Kind | Use Case | Typical Roles | In History |
|------|------|----------|---------------|------------|
| **UserInputRequestContent** | `userInputRequest` | HITL prompts requesting user input | `assistant` | ✓ Yes |
| **SuggestedActionsContent** | `suggestedActions` | Quick reply buttons | `assistant` | ✓ Yes |
| **ActionContent** | `action` | Interactive action responses | `user` | ✓ Yes |
| **TypingIndicatorContent** | `typingIndicator` | Typing/thinking presence | Any | ✗ Ephemeral* |
| **MessageReactionContent** | `messageReaction` | Emoji reactions to messages | `user` | ✓ Yes |
| **MessageDeleteContent** | `messageDelete` | Message deletion requests | Any | ✓ Yes |
| **MessageUpdateContent** | `messageUpdate` | Message edit operations | Any | ✓ Yes |

*TypingIndicatorContent is ephemeral (not persisted in message history).

### Content Type Filtering

When building LLM request context, filter by content type:

- **Include**: All content types except those explicitly excluded below
- **Exclude** (never send to LLM):
  - **TranscriptContent**: Human accessibility only - LLM processes audio/video directly, not transcripts
  - **TraceContent**: Debugging/telemetry only, not for LLM consumption

**Rationale**: Transcripts are for human users (screen readers, closed captions), not for LLMs which can process the original audio/video content. Sending both would be redundant and waste tokens. Traces are for observability and debugging, not conversational context.

### Terminology Note: "Channel"

**⚠️ Important**: The term "channel" has two distinct meanings in this API:

1. **Message Role** (`ChatRole.channel`): System/infrastructure events that are filtered from LLM context
   - Examples: Scheduled triggers, webhook events, system notifications
   - Usage: `{ role: "channel", contents: [{ type: "event", ... }] }`
   - Purpose: Orchestrator-only events not sent to the LLM

2. **Platform Routing** (`ChannelInfo`): Identifies which messaging platform the conversation is from
   - Examples: Teams, Slack, Discord, WhatsApp
   - Usage: `{ channelId: "msteams", externalConversationId: "19:meeting@thread.v2" }`
   - Purpose: Route responses to correct messaging platform

These are separate concepts despite using the same term. Think of `ChatRole.channel` as "system channel" (like stderr vs stdout) and `ChannelInfo` as "messaging channel" (like Teams vs Slack).

## Message Creation

### Create Message

**API:**
```http
POST /threads/{threadId}/messages
```

**Request:**
```json
{
  "role": "user",
  "contents": [
    { "kind": "text", "text": "Hello, how are you?" }
  ],
  "messageId": "msg_custom_123",  // Optional
  "metadata": { "source": "web" }
}
```

**Response:**
```json
{
  "messageId": "msg_custom_123",  // Client-provided or server-generated
  "threadId": "thread_456",
  "role": "user",
  "contents": [...],
  "createdAt": "2026-02-05T10:30:00Z"
}
```

### Message ID Assignment

**Requirements:**

Servers MUST:

1. **Accept Client IDs**: Allow clients to provide custom `messageId`
2. **Generate IDs**: Generate GUID if `messageId` omitted
3. **Uniqueness**: Ensure `messageId` is unique within conversation store
4. **Idempotency**: Treat duplicate `messageId` as idempotent (return existing message)

**Client ID Format:**

Clients SHOULD use format: `{channelId}:{originalId}`

**Examples:**
- Teams: `teams:1234567890123.456`
- Slack: `slack:1234567890.123456`
- Custom: `web:uuid-1234-5678`

**Rationale:**
- Preserves original message IDs from external systems
- Enables idempotent message creation (retry with same ID)
- Supports message deduplication
- Facilitates correlation across systems

### Idempotency

**Behavior:**

If client sends duplicate `messageId`:
1. Server checks if message exists
2. If exists: Return 200 OK with existing message
3. If not exists: Create new message

**Example:**
```http
POST /threads/thread_1/messages
{ "messageId": "msg_123", "role": "user", ... }

Response 1: 201 Created (message created)

POST /threads/thread_1/messages (retry)
{ "messageId": "msg_123", "role": "user", ... }

Response 2: 200 OK (existing message returned)
```

### Streaming Message Creation

Messages can be created incrementally during streaming runs:

**Flow:**
```
1. Run starts: LLM begins generating response
2. First chunk: message.created event → Message stored with partial content
3. Streaming chunks: message.updated events → Message content updated incrementally
4. Final chunk: message.completed event → completedAt timestamp set
```

**Storage Behavior:**
- Messages stored **during streaming**, not just at end
- Each `message.updated` event updates stored message content
- Clients can retrieve partial messages before completion
- `createdAt` set on first chunk, `completedAt` set on final chunk

**Example:**
```typescript
// Timeline of streaming message creation
t=0ms:   POST /runs (agent starts generating)
t=50ms:  message.created event → Message stored: "Hello"
t=100ms: message.updated event → Message updated: "Hello world"
t=150ms: message.updated event → Message updated: "Hello world, how"
t=200ms: message.completed event → completedAt set, final: "Hello world, how are you?"

// At t=125ms, GET /messages/{messageId} returns:
{
  "messageId": "msg_abc",
  "contents": [{"kind": "text", "text": "Hello world"}],
  "createdAt": "2026-02-06T10:00:00.050Z",
  "completedAt": null  // Not yet completed
}
```

**Source**: [Streaming Specification](./streaming.md) - Message events

## Hook Integration with Message Lifecycle

### Overview

Hooks integrate with message lifecycle to enable event-driven interception during message operations. Hooks evaluate **synchronously** before storage and can modify, block, or observe message creation.

**Key Concepts:**
- **Hook Evaluation Points**: message.created, message.updated, message.completed events
- **Blocking Behavior**: Hooks block storage until evaluation completes
- **Content Modification**: Hooks can modify message content before storage
- **Blocked Messages**: Not stored, not retrievable (silently dropped)
- **Modified Messages**: Stored with modifications, `hookModified` metadata preserved

**Related Specifications:**
- [Hooks Specification](./hooks.md) - Hook types, conditions, responses
- [Streaming Specification](./streaming.md) - Hook integration with streaming
- [Run Lifecycle](./run-lifecycle.md) - Hook evaluation during runs

### Hook Evaluation During Message Creation

**Flow:**
```
1. Client: POST /threads/{id}/messages {role: "user", contents: [...]}
2. Server: Evaluate hooks on message.created event
3. Hook evaluation:
   - If hook blocks: Return 403 Forbidden, DO NOT store message
   - If hook modifies: Store modified content, set hookModified: true
   - If hook allows: Store original content
4. Server: Store message (if not blocked)
5. Return: Stored message to client
```

#### Message Creation Sequence with Hook Evaluation

```
Message Creation Flow - Hook Integration
═══════════════════════════════════════════════════════════════════════════════

    Client          Server        Hook System       Database
      │               │                │                │
      │ POST /threads/{id}/messages    │                │
      │ { role: "user",                │                │
      │   contents: [                  │                │
      │     { text: "My SSN is         │                │
      │       123-45-6789" }           │                │
      │   ]                            │                │
      │ }                              │                │
      ├──────────────>│                │                │
      │               │                │                │
      │               │ Evaluate message.created        │
      │               ├───────────────>│                │
      │               │                │                │
      │               │           Check Conditions      │
      │               │           (PII patterns:        │
      │               │            SSN, email, etc)     │
      │               │                │                │
      │               │           ┌────┴─────┐          │
      │               │           │ Match?   │          │
      │               │           └────┬─────┘          │
      │               │                │                │
      │               │           ┌────┴────────────┐   │
      │               │           │ Pattern Found!  │   │
      │               │           │ (SSN detected)  │   │
      │               │           └─────────────────┘   │
      │               │                │                │
      │               │                │                │
      │               │      ┌─────────┴──────────┐    │
      │               │      │ Hook Action?       │    │
      │               │      └──┬──────────────┬──┘    │
      │               │         │ (block)      │ (modify)
      │               │         │              │        │
      │      ┌────────┴─────────┤              │        │
      │      │ Scenario A:      │              │        │
      │      │ BLOCK            │              │        │
      │      └──────────────────┘              │        │
      │               │                        │        │
      │               │ BlockResponse          │        │
      │               │<───────────────────────┘        │
      │               │                │                │
      │               │ ┌───────────────────────┐       │
      │               │ │ Do NOT store message  │       │
      │               │ │ (blocked by policy)   │       │
      │               │ └───────────────────────┘       │
      │               │                │                │
      │ 403 Forbidden │                │                │
      │ { error:      │                │                │
      │   "hook_      │                │                │
      │   blocked" }  │                │                │
      │<──────────────┤                │                │
      │               │                │                │
      │               │                │                │
      │      ┌────────┴─────────────────────────┐       │
      │      │ Scenario B: MODIFY                │       │
      │      └───────────────────────────────────┘       │
      │               │                │                │
      │               │ ModifyResponse │                │
      │               │ (redact SSN)   │                │
      │               │<───────────────┘                │
      │               │                │                │
      │               │ ┌─────────────────────────┐    │
      │               │ │ Apply Modification:     │    │
      │               │ │ "My SSN is 123-45-6789" │    │
      │               │ │         ↓               │    │
      │               │ │ "My SSN is [REDACTED]"  │    │
      │               │ └─────────────────────────┘    │
      │               │                │                │
      │               │ Store Modified Message          │
      │               │ (hookModified: true)            │
      │               ├────────────────────────────────>│
      │               │                │                │
      │               │                │     ✓ Stored   │
      │               │<────────────────────────────────┤
      │               │                │                │
      │ 201 Created   │                │                │
      │ { messageId:  │                │                │
      │   "msg_abc",  │                │                │
      │   contents: [ │                │                │
      │     { text:   │                │                │
      │       "[REDACTED]"}],          │                │
      │   hookModified: true           │                │
      │ }             │                │                │
      │<──────────────┤                │                │
      │               │                │                │
      │ ┌────────────────────────────┐ │                │
      │ │ Client never sees original │ │                │
      │ │ SSN (by design for security)│                │
      │ └────────────────────────────┘ │                │
      │               │                │                │

═══════════════════════════════════════════════════════════════════════════════

Legend:
  ──────>  = Synchronous request/response
  ┌─ ─┐    = Decision point
  ✓        = Success

Key Observations:
  1. Hook evaluation is synchronous (blocks storage)
  2. Blocked messages are NEVER stored (403 returned immediately)
  3. Modified messages store ONLY modified version (original never persisted)
  4. hookModified flag indicates content filtering occurred
  5. Client cannot retrieve blocked messages (silently dropped)
```

**Example - Blocked Message:**
```typescript
// Hook configuration
{
  "kind": "block",
  "condition": {
    "kind": "content",
    "patterns": ["offensive_term"]
  },
  "eventTypes": ["message.created"]
}

// Client request
POST /threads/thread_1/messages
{
  "role": "user",
  "contents": [{"kind": "text", "text": "Message with offensive_term"}]
}

// Hook blocks: Message NOT stored
Response: 403 Forbidden
{
  "error": {
    "code": "hook_blocked",
    "message": "Message blocked by content policy"
  }
}

// GET /messages returns empty - message was never stored
```

**Example - Modified Message:**
```typescript
// Hook configuration (PII redaction)
{
  "kind": "modify",
  "condition": {
    "kind": "content",
    "patterns": ["\\d{3}-\\d{2}-\\d{4}"]  // SSN pattern
  },
  "eventTypes": ["message.created"]
}

// Client request
POST /threads/thread_1/messages
{
  "role": "user",
  "contents": [{"kind": "text", "text": "My SSN is 123-45-6789"}]
}

// Hook modifies: Content redacted, message stored with modification
Response: 201 Created
{
  "messageId": "msg_abc",
  "role": "user",
  "contents": [{"kind": "text", "text": "My SSN is [REDACTED]"}],
  "hookModified": true,  // Indicates hook modification
  "createdAt": "2026-02-06T10:00:00Z"
}

// Original content never stored, only redacted version retrievable
```

### Blocked vs Modified Messages

| Scenario | Hook Action | Storage Behavior | Retrievable |
|----------|-------------|------------------|-------------|
| Hook blocks | `BlockResponse` | Message NOT stored | No |
| Hook modifies | `ModifyResponse` | Modified message stored | Yes (modified version) |
| Hook allows | `AllowResponse` | Original message stored | Yes (original version) |
| Hook fails (early event) | Timeout/error | Message NOT stored (fail-closed) | No |

**Source**: [Hooks Specification](./hooks.md) - Event-Type-Based Fallback

### Message Retrieval with Hooks

When retrieving messages that were hook-processed:

**Fields:**
- `hookModified: true` - Indicates message was modified by hook before storage
- Original content NOT available (by design for security/compliance)
- No indication if message was allowed without modification (`hookModified` absent or `false`)

**Example:**
```typescript
// Retrieve message that was hook-modified during creation
GET /threads/thread-1/messages/msg-abc

Response:
{
  "messageId": "msg_abc",
  "role": "user",
  "contents": [{"kind": "text", "text": "My SSN is [REDACTED]"}],
  "hookModified": true,  // Client knows content was filtered
  "createdAt": "2026-02-06T10:00:00Z"
}

// Client handling
if (message.hookModified) {
  console.log("This message was filtered or modified by content policy");
}
```

**Gap Detection:**

Blocked messages are silently dropped. Clients can detect gaps but cannot determine cause:

```typescript
// Sequence of message IDs: msg_1, msg_2, msg_5 (gap: msg_3, msg_4 blocked)
// No API to retrieve blocked messages or reasons
```

**Source**: [Streaming Specification](./streaming.md) - Hook-Modified Events

## Encrypted Content in Message Lifecycle

### Overview

Encrypted content flows through message lifecycle with client-side encryption/decryption. The server stores encrypted content as **opaque** and never decrypts.

**Key Principles:**
- **Client-Side Encryption**: Content encrypted before sending to server
- **Server Opacity**: Server stores encrypted content without decryption
- **Client-Side Decryption**: Content decrypted after retrieval from server
- **Immutability**: Encrypted messages cannot be edited (ciphertext is immutable)
- **Metadata Preservation**: Encryption metadata preserved during storage

**Related Specifications:**
- [Content Encryption Specification](./content-encryption.md) - Encryption algorithms, key management
- [Streaming Specification](./streaming.md) - Streaming encrypted content

### Encryption Timing

**Creation Flow:**
```
1. Client encrypts content:
   - Plaintext → AES-256-GCM or ChaCha20-Poly1305
   - Generate IV, compute authTag
   - Base64-encode ciphertext, IV, authTag

2. Client creates message:
   POST /messages
   {
     "role": "user",
     "contents": [{
       "kind": "text",
       "text": "encrypted_base64_ciphertext...",
       "annotations": {
         "encryption": {
           "algorithm": "AES-256-GCM",
           "keyId": "key-healthcare-001",
           "iv": "base64_iv...",
           "authTag": "base64_tag..."
         }
       }
     }]
   }

3. Server stores message:
   - Stores ciphertext as opaque string
   - Stores encryption metadata unchanged
   - No decryption attempted

4. Client retrieves message:
   GET /messages/{messageId}

5. Client decrypts content:
   - Fetch key from KMS using keyId
   - Decrypt ciphertext using key, IV, authTag
   - Verify authTag (integrity check)
   - Display plaintext
```

### Server Opacity

**Requirements:**

Servers MUST:
1. **Store Encrypted Content**: Store ciphertext without modification
2. **Preserve Metadata**: Store encryption metadata (`keyId`, `iv`, `authTag`) unchanged
3. **No Decryption**: Never attempt to decrypt encrypted content
4. **No Key Access**: Server does NOT have access to encryption keys

**Validation:**

Servers MUST validate encryption metadata structure:
- `algorithm`: Must be "AES-256-GCM" or "ChaCha20-Poly1305"
- `keyId`: Must be non-empty string (opaque to server)
- `iv`: Must be valid base64 string
- `authTag`: Must be valid base64 string (if present)

Servers MUST NOT:
- Validate key existence (keyId is opaque)
- Validate IV length (client responsibility)
- Validate ciphertext (opaque bytes/string)

### Immutability of Encrypted Messages

**Restriction:** Encrypted messages CANNOT be edited after creation

**Rationale:**
- Ciphertext is immutable (changing ciphertext breaks authentication tag)
- Editing would require decryption, modification, re-encryption
- Server cannot decrypt (no key access)

**Enforcement:**

```http
PATCH /threads/{threadId}/messages/{messageId}
{
  "contents": [{"kind": "text", "text": "new_encrypted_content..."}]
}

Response: 400 Bad Request
{
  "error": {
    "code": "encrypted_content_immutable",
    "message": "Cannot modify encrypted message content. Create a new message instead."
  }
}
```

**Allowed Operations:**
- Update `metadata` field (non-encryption metadata)
- Delete message (entire message removed)
- Create new message (with new encryption)

**Branching Alternative:**

To "edit" encrypted content:
1. Create branch from parent message
2. Create new message with new encrypted content
3. Original encrypted message preserved

**Source**: [Content Encryption Specification](./content-encryption.md) - Validation Rules

### Encryption Metadata Preservation

**Stored Fields:**

| Field | Stored | Retrieved |
|-------|--------|-----------|
| `contents[].kind` | Yes | Yes |
| `contents[].text` (ciphertext) | Yes (opaque) | Yes (opaque) |
| `annotations.encryption.algorithm` | Yes | Yes |
| `annotations.encryption.keyId` | Yes | Yes |
| `annotations.encryption.iv` | Yes | Yes |
| `annotations.encryption.authTag` | Yes | Yes |

**Example - Round-Trip:**
```typescript
// Create encrypted message
POST /messages
{
  "contents": [{
    "kind": "text",
    "text": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=",
    "annotations": {
      "encryption": {
        "algorithm": "AES-256-GCM",
        "keyId": "key-healthcare-001",
        "iv": "8Kk3Kgz5XjRlipRkwB==",
        "authTag": "GxcTlipRkwB0K1Y8Kk3K=="
      }
    }
  }]
}

// Retrieve encrypted message (exact metadata preserved)
GET /messages/{messageId}
{
  "messageId": "msg_abc",
  "contents": [{
    "kind": "text",
    "text": "U2FsdGVkX1+vupppZksvRf5pq5g5XjFRlipRkwB0K1Y=",  // Exact ciphertext
    "annotations": {
      "encryption": {
        "algorithm": "AES-256-GCM",
        "keyId": "key-healthcare-001",
        "iv": "8Kk3Kgz5XjRlipRkwB==",
        "authTag": "GxcTlipRkwB0K1Y8Kk3K=="
      }
    }
  }]
}

// Client decrypts locally (server never saw plaintext)
```

## Messages and Run Lifecycle

### Overview

Messages are created during run execution and linked via `completionId`. This section explains how messages relate to runs, incremental storage, and run failure behavior.

**Key Concepts:**
- **completionId**: Links agent-generated messages to runs
- **Incremental Storage**: Messages stored during run execution
- **Run Failure**: Messages preserved even if run fails
- **Querying by Run**: Retrieve all messages from specific run

**Related Specifications:**
- [Run Lifecycle Specification](./run-lifecycle.md) - Run states and execution
- [Tool Execution Specification](./tool-execution.md) - Tool call messages

### Run-Generated Messages

**completionId Linkage:**

| Message Source | completionId | Description |
|----------------|--------------|-------------|
| User-created | `null` or absent | Messages created by client |
| Agent-generated | `run_123` | Messages created during run execution |
| Tool results | `run_123` | Tool results from specific run |

**Example:**
```typescript
// User creates message (no completionId)
POST /threads/thread_1/messages
{
  "role": "user",
  "contents": [{"kind": "text", "text": "Hello"}]
}

Response:
{
  "messageId": "msg_1",
  "role": "user",
  "completionId": null  // User message, not from run
}

// Run generates response message (has completionId)
POST /runs
{
  "threadId": "thread_1",
  "agentId": "agent_gpt4"
}

// During run: message.created event
{
  "messageId": "msg_2",
  "role": "assistant",
  "completionId": "run_456",  // Links to run
  "agentId": "agent_gpt4"
}
```

### Incremental Storage During Runs

Messages are stored **incrementally** as run executes:

**Flow:**
```
1. Run starts: status = in_progress
2. Agent begins generating: First chunk
3. Message created: message.created event → Message stored
4. Agent continues: Subsequent chunks
5. Message updated: message.updated events → Message content updated
6. Agent completes: Final content
7. Message completed: message.completed event → completedAt set
8. Run completes: status = completed
```

**Timeline Example:**
```typescript
t=0ms:    POST /runs (status: queued)
t=10ms:   Run status: in_progress
t=50ms:   Message created (partial): "Hello"
t=100ms:  Message updated: "Hello world"
t=150ms:  Message updated: "Hello world, how are you?"
t=200ms:  Message completed: completedAt set
t=210ms:  Run status: completed

// At t=125ms, GET /messages returns partial message:
{
  "messageId": "msg_2",
  "completionId": "run_456",
  "contents": [{"kind": "text", "text": "Hello world"}],
  "completedAt": null  // Not yet completed
}
```

**Source**: [Run Lifecycle Specification](./run-lifecycle.md) - Hook Evaluation Points

### Run Failure and Message Preservation

**Behavior:** Messages preserved even if run fails

**Rationale:**
- Partial output may be valuable for debugging
- Tool results provide context for failure
- Preserves conversation history

**Example:**
```typescript
// Run starts and generates partial message
t=0ms:    POST /runs
t=50ms:   Message created: "Let me help you with..."
t=100ms:  Message updated: "Let me help you with that. First, I'll..."
t=150ms:  Run fails: Agent error

// Message preserved despite run failure
GET /threads/thread_1/messages
{
  "data": [
    {
      "messageId": "msg_2",
      "role": "assistant",
      "completionId": "run_456",
      "contents": [{"kind": "text", "text": "Let me help you with that. First, I'll..."}],
      "completedAt": null  // Never completed (run failed)
    }
  ]
}

// Run status
GET /runs/run_456
{
  "runId": "run_456",
  "status": "failed",
  "error": {
    "code": "agent_error",
    "message": "LLM request failed"
  }
}
```

**Use Cases:**
- **Debugging**: Partial output shows where run failed
- **User Experience**: Show partial response with error message
- **Context Preservation**: Thread history includes failed attempts

### Querying Messages by Run

**API:**
```http
GET /threads/{threadId}/messages?completionId={runId}
```

**Example:**
```typescript
// Get all messages from specific run
GET /threads/thread_1/messages?completionId=run_456

Response:
{
  "data": [
    {
      "messageId": "msg_2",
      "role": "assistant",
      "completionId": "run_456",
      "contents": [{"kind": "text", "text": "Hello, how can I help?"}]
    },
    {
      "messageId": "msg_3",
      "role": "tool",
      "completionId": "run_456",
      "contents": [{"kind": "functionResult", "callId": "call_1", ...}]
    }
  ]
}

// Use case: Show all messages/tool calls from failed run
```

**Filtering:**
- By `completionId`: All messages from specific run
- By `completionId` + `role`: Only assistant or tool messages from run
- By `completionId` + `agentId`: Messages from specific agent's run

### Agent vs User Messages

**Distinction:**

| Property | User Messages | Agent Messages |
|----------|---------------|----------------|
| `completionId` | `null` or absent | `run_123` |
| `agentId` | `null` or absent | `agent_gpt4` |
| `role` | `user`, `developer`, `system` | `assistant`, `tool` |
| Created by | Client API call | Run execution |

**Query Examples:**
```typescript
// Get all user messages (no completionId)
GET /messages?role=user

// Get all agent-generated messages (has completionId)
GET /messages?role=assistant

// Get messages NOT from runs (user-created only)
// Note: Requires filtering completionId=null (implementation-specific)
```

## Message Storage

### Storage Requirements

Servers MUST:

1. **Persist Messages**: Store all messages in conversation store
2. **Preserve Order**: Maintain creation order via `createdAt`
3. **Link to Thread**: Associate message with thread via `threadId`
4. **Link to Run**: Associate agent messages with run via `completionId`

### Message Metadata

**Stored Fields:**

| Field | Source | Description |
|-------|--------|-------------|
| `messageId` | Client/Server | Unique identifier |
| `threadId` | Server | Thread association |
| `role` | Client | Message role |
| `contents` | Client | Message content |
| `createdAt` | Server | Creation timestamp |
| `completedAt` | Server | Completion timestamp (streaming) |
| `userId` | Client | User who created message |
| `agentId` | Server | Agent that generated message |
| `completionId` | Server | Run that generated message |
| `metadata` | Client | Custom metadata |

### Computed Fields

**`text` field** (computed, NOT stored):
- Concatenation of all `TextContent` items
- Generated on read, not persisted
- Convenience for text-only messages

## Message Retrieval

### List Messages

**API:**
```http
GET /threads/{threadId}/messages?limit=50&order=asc
```

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int32 | 50 | Max messages to return |
| `order` | string | `asc` | Sort order (`asc`, `desc`) |
| `after` | string | - | Cursor for pagination |
| `before` | string | - | Cursor for pagination |
| `role` | string | - | Filter by role |

**Response:**
```json
{
  "data": [
    { "messageId": "msg_1", "role": "user", ... },
    { "messageId": "msg_2", "role": "assistant", ... }
  ],
  "hasMore": false,
  "nextCursor": null
}
```

### Get Single Message

**API:**
```http
GET /threads/{threadId}/messages/{messageId}
```

**Response:**
```json
{
  "messageId": "msg_123",
  "threadId": "thread_456",
  "role": "user",
  "contents": [...]
}
```

### Filtering

Servers SHOULD support filtering by:
- **Role**: `GET /messages?role=user`
- **Date Range**: `GET /messages?after=2026-01-01&before=2026-02-01`
- **Author**: `GET /messages?userId=user_123`

## Conversation Branching

### Branch Model

**TypeSpec**: See `ChatMessage.parentMessageId` field in `typespec/messages.tsp`

```typescript
parentMessageId?: string;  // Parent message for branching
```

**Concept:** Git-like conversation trees

**Structure:**
```
msg-1 (user: "Tell me about Paris")
  ├─ msg-2 (assistant: "Paris is...")
  │   └─ msg-3 (user: "Thanks!")
  │
  └─ msg-2b (user: "Actually, London")  // Branch from msg-1
      └─ msg-3b (assistant: "London is...")
```

### Creating Branches

**API:**
```http
POST /threads/{threadId}/messages
{
  "messageId": "msg-2b",
  "parentMessageId": "msg-1",  // Branch point
  "role": "user",
  "contents": [{ "kind": "text", "text": "Actually, tell me about London" }]
}
```

**Requirements:**

Servers MUST:

1. **Validate Parent**: Ensure `parentMessageId` exists in thread
2. **Allow Multiple Children**: One parent can have multiple child messages
3. **Preserve DAG**: Prevent cycles (A → B → C → A)

### Retrieving Branches

**API:**
```http
GET /threads/{threadId}/messages?branch=msg-2b
```

**Behavior:**
- Returns: All ancestors + specified branch descendents
- Example: `[msg-1, msg-2b, msg-3b]` (NOT msg-2, msg-3)

### Use Cases

1. **Edit and Rerun**: User edits message-5, system creates branch from message-4
2. **A/B Testing**: Test different conversation paths
3. **Undo/Redo**: Branch to previous state
4. **Time Travel Debugging**: Explore alternate conversation paths

## Message Updates

### Update Message

**API:**
```http
PATCH /threads/{threadId}/messages/{messageId}
{
  "metadata": { "edited": true, "editedAt": "2026-02-05T10:35:00Z" }
}
```

**Allowed Updates:**
- `metadata` - Custom metadata only
- `contents` - NOT allowed (use branching instead)

**Requirements:**

Servers MUST:

1. **Reject Content Edits**: Do NOT allow editing `contents` directly
2. **Use Branching**: Direct clients to create branch for edits
3. **Update Metadata Only**: Allow metadata updates for tagging, flagging, etc.

**Rationale:**
- Preserve conversation integrity
- Maintain audit trail
- Support branching for edits

### Delete Message

**API:**
```http
DELETE /threads/{threadId}/messages/{messageId}
```

**Behavior:**

Servers MAY:
- Soft delete (mark deleted, keep data)
- Hard delete (remove from storage)

Servers SHOULD:
- Return 204 No Content on success
- Return 404 if message not found

## Message Annotations

### Content-Level Metadata (AIContentBase)

**TypeSpec**: See `AIContentBase` model in `typespec/messages.tsp` (lines 410-448)

All content types inherit from **AIContentBase**, which provides common properties:

```typescript
model AIContentBase {
  audience?: string;              // Target audience filter (comma-separated roles)
  encryption?: string;            // Encryption metadata (key reference)
  additionalProperties?: Record<unknown>;  // Client-side extensibility (not serialized)
}
```

**Use Cases:**

1. **Audience Filtering**:
   ```json
   {
     "kind": "text",
     "text": "Internal reasoning...",
     "audience": "assistant"
   }
   ```
   - Content visible only to assistant (LLM), hidden from user UI

2. **Content Encryption**:
   ```json
   {
     "kind": "text",
     "text": "Encrypted sensitive data...",
     "encryption": "aes-256-gcm:key-id-123"
   }
   ```
   - End-to-end encryption for sensitive content

3. **Combined Audience + Encryption**:
   ```json
   {
     "kind": "functionResult",
     "callId": "call_123",
     "name": "get_patient_record",
     "result": "encrypted-phi-data...",
     "audience": "assistant",
     "encryption": "hipaa-compliant-v1"
   }
   ```
   - Encrypted content visible only to LLM

## Validation Rules

### Message Creation Validation

Servers MUST reject message creation if:

1. **Missing Required Fields**:
   - `role` is missing
   - `contents` is empty array
   - `threadId` is invalid/non-existent

2. **Invalid Role**:
   - Role is not valid ChatRole enum value
   - Role is `channel` from client (reserved for system)

3. **Invalid Contents**:
   - Content items missing required fields
   - Content type discriminator invalid
   - Binary content exceeds size limits

4. **Invalid Branching**:
   - `parentMessageId` references non-existent message
   - `parentMessageId` creates cycle in DAG

### Message Retrieval Validation

Servers MUST reject retrieval if:

1. **Invalid Pagination**:
   - `limit` > 100
   - `limit` < 1
   - Invalid cursor format

2. **Invalid Filters**:
   - `role` not valid enum value
   - Invalid date format

## Performance Requirements

### Latency Targets

| Operation | Target | Maximum |
|-----------|--------|---------|
| Create message | < 50ms | 200ms |
| Get message | < 20ms | 100ms |
| List messages (50) | < 100ms | 500ms |

### Pagination

**Requirements:**

Servers MUST:

1. **Cursor-Based Pagination**: Use opaque cursors (not offset-based)
2. **Consistent Results**: Same cursor always returns same page
3. **Limit Enforcement**: Cap `limit` at 100 messages

**Cursor Format** (implementation-specific):
- Opaque string (e.g., base64-encoded)
- Contains: last message ID, timestamp, direction
- Example: `eyJpZCI6Im1zZ18xMjMiLCJ0cyI6MTcwOTcwNjAwMH0=`

## Message Ordering

### Ordering Guarantees

Servers MUST:

1. **Creation Order**: Messages ordered by `createdAt` timestamp
2. **Monotonic Timestamps**: Timestamps strictly increasing within thread
3. **Consistent Sort**: Same query parameters always return same order

### Concurrent Creation

If multiple messages created simultaneously:
- Use sub-millisecond timestamps (e.g., microseconds)
- Or use sequence numbers as tiebreaker
- Guarantee: No two messages have identical `createdAt`

## Proactive Messaging

### Event Messages

**TypeSpec**: See `EventContent` model in `typespec/messages.tsp`

External events create messages with `role: "channel"`:

```json
POST /threads/{threadId}/messages
{
  "role": "channel",
  "contents": [{
    "kind": "event",
    "name": "scheduled_trigger",
    "value": { "triggerName": "daily_report", "time": "09:00" },
    "text": "Daily report trigger fired",
    "timestamp": "2026-02-05T09:00:00Z"
  }]
}
```

**Requirements:**

Servers MUST:

1. **Accept Channel Messages**: Allow `role: "channel"` from system/scheduler
2. **Reject from Clients**: Block clients from creating `role: "channel"` messages
3. **Filter for LLM**: Exclude `role: "channel"` when building LLM context
4. **Include for Orchestrator**: Include in thread history for orchestrator logic

## Compliance

This specification aligns with:
- **TypeSpec**: `typespec/messages.tsp` (ChatMessage, ChatRole, AIContentBase)
- **API Reference**: `Docs/api-reference/models.md` (message models)
- **MAF Pattern**: ChatMessage model (message structure)
- **Activity Protocol**: EventContent for proactive messaging

## See Also

- [Run Lifecycle](./run-lifecycle.md) - Run creation and execution
- [Content Types](../api-reference/content-types.md) - Message content types
- [Streaming](./streaming.md) - Streaming message updates
- [Tool Execution](./tool-execution.md) - Tool call messages
