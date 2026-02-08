# Thread Operations

Thread operations for managing conversations, messages, and thread-scoped resources.

## Overview

Threads represent conversations that maintain message history and context. They serve as the container for multi-turn interactions with agents.

The Thread API provides operations for:

- **Thread Management**: Create, update, delete threads
- **Message Operations**: Add and retrieve messages
- **Run Management**: Create and list thread-scoped runs
- **Thread Watching**: Agent participation via ThreadWatch
- **Thread Subscriptions**: Subscribe to thread events via webhooks

**TypeSpec Source**: [execution.tsp](../../typespec/execution.tsp), [routes.tsp](../../typespec/routes.tsp)

---

## Thread Management

### POST /threads

Create a new thread.

**Request Body** (optional):
```json
{
  "metadata": {
    "userId": "user-123",
    "channelId": "teams-channel-456"
  }
}
```

**Response**: [Thread](../models/Thread.md) with server-generated `threadId`

**See**: [post-threads.md](./post-threads.md)

---

### GET /threads/{threadId}

Get thread details.

**Response**: [Thread](../models/Thread.md)

**See**: [get-threads-threadid.md](./get-threads-threadid.md)

---

### PATCH /threads/{threadId}

Update thread metadata.

**Request Body**: Partial [Thread](../models/Thread.md)

**See**: [patch-threads-threadid.md](./patch-threads-threadid.md)

---

### DELETE /threads/{threadId}

Delete thread and all associated data.

**Response**: 204 No Content

**See**: [delete-threads-threadid.md](./delete-threads-threadid.md)

---

### POST /threads/{threadId}/read

Mark thread as read (updates unreadCount).

**Response**: Updated [Thread](../models/Thread.md)

**See**: [post-threads-threadid-read.md](./post-threads-threadid-read.md)

---

### POST /threads/{threadId}/copy

Copy thread to create independent copy.

**Request Body**:
```json
{
  "includeMessages": true,
  "messageCount": 10
}
```

**Response**: New [Thread](../models/Thread.md)

**See**: [post-threads-threadid-copy.md](./post-threads-threadid-copy.md)

---

## Message Operations

### POST /threads/{threadId}/messages

Add message to thread.

**Request Body**: [ChatMessage](../models/ChatMessage.md)

**Response**: Created message with server-generated `messageId`

**Example**:
```http
POST /threads/thread-123/messages
Content-Type: application/json

{
  "role": "user",
  "contents": [{"kind": "text", "text": "Hello!"}]
}
```

**See**: [post-threads-threadid-messages.md](./post-threads-threadid-messages.md)

---

### GET /threads/{threadId}/messages

Get messages from thread.

**Query Parameters**:
- `branch?: string` - Get messages in specific branch
- `after?: string` - Pagination cursor
- `limit?: int32` - Max messages (default: 100)

**Response**: Array of [ChatMessage](../models/ChatMessage.md)

**See**: [get-threads-threadid-messages.md](./get-threads-threadid-messages.md)

---

### GET /threads/{threadId}/messages/{messageId}

Get specific message by ID.

**Response**: [ChatMessage](../models/ChatMessage.md)

**See**: [get-threads-threadid-messages-messageid.md](./get-threads-threadid-messages-messageid.md)

---

## Run Operations

### POST /threads/{threadId}/runs

Create run within thread context.

**Request Body**: [Run](../models/Run.md) (threadId inferred from URL)

**Response**: Created [Run](../models/Run.md)

**See**: [post-threads-threadid-runs.md](./post-threads-threadid-runs.md)

---

### GET /threads/{threadId}/runs

List runs within thread.

**Query Parameters**:
- `status?: RunStatus` - Filter by status
- `after?: string` - Pagination cursor
- `limit?: int32` - Max runs (default: 100)

**Response**: Array of [Run](../models/Run.md)

**See**: [get-threads-threadid-runs.md](./get-threads-threadid-runs.md)

---

## Thread Watching (Multi-Agent)

### POST /threads/{threadId}/watch

Subscribe agent to watch thread (enables auto-response).

**Request Body**:
```json
{
  "agentId": "agent-123"
}
```

**Response**: [ThreadWatch](../models/ThreadWatch.md)

**See**: [post-threads-threadid-watch.md](./post-threads-threadid-watch.md)

---

### GET /threads/{threadId}/watch

List agents watching thread.

**Response**: Array of [ThreadWatch](../models/ThreadWatch.md)

**See**: [get-threads-threadid-watch.md](./get-threads-threadid-watch.md)

---

### DELETE /threads/{threadId}/watch/{agentId}

Unsubscribe agent from watching thread.

**Response**: 204 No Content

**See**: [delete-threads-threadid-watch-agentid.md](./delete-threads-threadid-watch-agentid.md)

---

## Streaming

### GET /threads/{threadId}/stream

Stream thread events (real-time updates).

**Query Parameters**:
- `events?: string` - Event types to include
- `since?: utcDateTime` - Only events after timestamp
- `roles?: string` - Filter by message roles
- `userIds?: string` - Filter by user IDs
- `agentIds?: string` - Filter by agent IDs
- `contentTypes?: string` - Filter by content types

**Response**: Server-Sent Events (SSE) stream

**See**: [get-threads-threadid-stream.md](./get-threads-threadid-stream.md)

---

## Subscription Operations

### GET /threads/{threadId}/subscriptions

List webhook subscriptions for thread events.

**See**: [get-threads-threadid-subscriptions.md](./get-threads-threadid-subscriptions.md)

---

### POST /threads/{threadId}/subscriptions

Create webhook subscription for thread events.

**Request Body**: [ThreadSubscription](../models/ThreadSubscription.md)

**See**: [post-threads-threadid-subscriptions.md](./post-threads-threadid-subscriptions.md)

---

### GET /threads/{threadId}/subscriptions/{subscriptionId}

Get specific thread subscription.

**See**: [get-threads-threadid-subscriptions-subscriptionid.md](./get-threads-threadid-subscriptions-subscriptionid.md)

---

### DELETE /threads/{threadId}/subscriptions/{subscriptionId}

Delete thread subscription.

**See**: [delete-threads-threadid-subscriptions-subscriptionid.md](./delete-threads-threadid-subscriptions-subscriptionid.md)

---

## Related Resources

- [Thread Model](../models/Thread.md)
- [ThreadWatch Model](../models/ThreadWatch.md)
- [ChatMessage Model](../models/ChatMessage.md)
- [Run Operations](./runs.md)
- [Agent Operations](./agents.md)

## Related Specifications

- [Message Lifecycle Specification](../../specifications/message-lifecycle.md)
- [Streaming Specification](../../specifications/streaming.md)
- [Multi-Agent Guide](../../guides/multi-agent.md)
