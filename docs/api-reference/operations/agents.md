# Agent Operations

Agent operations for retrieving agent cards, streaming agent activity, and managing agent subscriptions.

## Overview

Agents represent AI assistants with specific capabilities, configurations, and tool access. The Agent Runtime API provides operations for:

- **Agent Discovery**: Get agent cards with capabilities and metadata
- **Agent Monitoring**: Stream agent activity across all runs
- **Agent Subscriptions**: Subscribe to agent-level events via webhooks

**TypeSpec Source**: [agents.tsp](../../typespec/agents.tsp), [routes.tsp](../../typespec/routes.tsp)

---

## Operations

### GET /agents/{agentId}/card

Get agent card with capabilities, model configuration, tools, and metadata.

**Response**: [AgentCard](../models/AgentCard.md)

**Example**:
```http
GET /agents/agent-123/card
```

**See**: [get-agents-agentid-card.md](./get-agents-agentid-card.md)

---

### GET /agents/{agentId}/stream

Stream all activity for a specific agent across all runs.

**Query Parameters**:
- `events?: string` - Comma-separated event types to include
- `since?: utcDateTime` - Only events after this timestamp

**Response**: Server-Sent Events (SSE) stream

**Example**:
```http
GET /agents/agent-123/stream?events=run.started,run.completed
```

**See**: [get-agents-agentid-stream.md](./get-agents-agentid-stream.md)

---

### GET /agents/{agentId}/subscriptions

List all webhook subscriptions for agent events.

**Query Parameters**:
- `limit?: int32` - Maximum subscriptions to return (default: 100)

**Response**: Array of [AgentSubscription](../models/AgentSubscription.md)

**See**: [get-agents-agentid-subscriptions.md](./get-agents-agentid-subscriptions.md)

---

### POST /agents/{agentId}/subscriptions

Create webhook subscription for agent events.

**Request Body**: [AgentSubscription](../models/AgentSubscription.md)

**Response**: Created subscription with server-generated ID

**Example**:
```http
POST /agents/agent-123/subscriptions
Content-Type: application/json

{
  "webhookUrl": "https://example.com/webhooks/agent-events",
  "events": ["run.failed", "agent.error"]
}
```

---

### GET /agents/{agentId}/subscriptions/{subscriptionId}

Get specific agent subscription by ID.

**Response**: [AgentSubscription](../models/AgentSubscription.md)

**See**: [get-agents-agentid-subscriptions-subscriptionid.md](./get-agents-agentid-subscriptions-subscriptionid.md)

---

### DELETE /agents/{agentId}/subscriptions/{subscriptionId}

Delete agent subscription.

**Response**: 204 No Content on success

**See**: [delete-agents-agentid-subscriptions-subscriptionid.md](./delete-agents-agentid-subscriptions-subscriptionid.md)

---

## Related Resources

- [Agent Model](../models/Agent.md)
- [AgentCard Model](../models/AgentCard.md)
- [AgentSubscription Model](../models/AgentSubscription.md)
- [Run Operations](./runs.md)
- [Thread Operations](./threads.md)

## Related Specifications

- [Agent Auto-Response Specification](../../specifications/agent-auto-response.md)
- [Streaming Specification](../../specifications/streaming.md)
- [Webhook Guide](../../guides/webhooks.md)
