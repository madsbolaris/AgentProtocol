/**
 * Subscription & Webhook Models
 *
 * This file defines subscription models for webhook notifications across different resources.
 *
 * CONTENTS:
 * - ThreadSubscription: Subscribe to thread activity (messages, runs, status changes)
 * - RunSubscription: Subscribe to run lifecycle events
 * - AgentSubscription: Subscribe to agent activity across all threads
 * - MessageFilters: Filter webhook notifications by message characteristics
 * - WebhookNotification: Webhook payload format
 *
 * @usage
 * Subscriptions enable real-time notifications via webhooks for resource activity.
 * Clients receive lightweight notifications and fetch full details via REST APIs.
 *
 * Subscription Pattern:
 * 1. Create subscription with webhookUrl and optional filters
 * 2. Receive webhook POST with notification payload
 * 3. Fetch latest state via GET /resources/{id}
 * 4. Verify webhook signature using webhookSecret (optional)
 *
 * Subscription Types:
 * - Thread: Monitor conversation activity (messages, participants, status)
 * - Run: Monitor execution lifecycle (started, completed, failed, cancelled)
 * - Agent: Monitor agent behavior across all runs (activity, errors, configuration)
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Microsoft.Agents.AI;

/**
 * Message Filters
 *
 * @usage
 * Filter webhook notifications by message characteristics.
 * Reduces notification volume by subscribing only to relevant messages.
 *
 * @example Filter user messages only
 * ```json
 * {
 *   "roles": ["user"]
 * }
 * ```
 *
 * @example Filter messages with images or videos
 * ```json
 * {
 *   "contentTypes": ["image", "video"]
 * }
 * ```
 */
@doc("Message filters for webhook subscriptions")
model MessageFilters {
  @doc("Only messages from specific roles (user, assistant, tool, channel). Values: 'user', 'assistant', 'tool', 'channel'")
  roles?: string[];

  @doc("Only messages from specific users")
  userIds?: string[];

  @doc("Only messages from specific agents")
  agentIds?: string[];

  @doc("Only messages with specific content types. Common types: 'text', 'image', 'audio', 'video', 'file', 'functionCall', 'functionResult', 'typingIndicator', 'messageReaction', 'messageDelete', 'reasoning'")
  contentTypes?: string[];

  @doc("Only content with specific audience annotations. Values: 'user', 'assistant'")
  audience?: string[];
}

/**
 * Webhook Notification
 *
 * @usage
 * Webhook payload sent to subscription webhookUrl when subscribed events occur.
 * Contains minimal event data - clients should fetch full details via REST API.
 *
 * @example Thread activity notification
 * ```json
 * {
 *   "kind": "thread.activity",
 *   "resourceId": "thread_123",
 *   "subscriptionId": "sub_456",
 *   "eventType": "message.created",
 *   "sequenceNumber": 42,
 *   "eventSeq": 10,
 *   "timestamp": "2026-02-07T10:00:00Z",
 *   "data": {
 *     "messageId": "msg_789",
 *     "runId": "run_001"
 *   }
 * }
 * ```
 */
@doc("Webhook notification payload")
model WebhookNotification {
  @doc("Notification type")
  kind: "thread.activity" | "run.activity" | "agent.activity";

  @doc("Resource identifier (threadId, runId, or agentId)")
  resourceId: string;

  @doc("Subscription identifier")
  subscriptionId: string;

  @doc("Event type that triggered notification")
  eventType: string;

  @doc("Subscription sequence number (monotonically increasing per subscription, for gap detection)")
  sequenceNumber: int64;

  @doc("Event sequence number (monotonically increasing per resource, for event ordering)")
  eventSeq: int64;

  @doc("Event timestamp")
  timestamp: utcDateTime;

  @doc("Optional event-specific data (minimal)")
  data?: {
    @doc("Message ID (for message events)")
    messageId?: string;

    @doc("Run ID (for run events within thread)")
    runId?: string;

    @doc("Status (for lifecycle events)")
    status?: string;
  };
}

/**
 * Thread Subscription - Webhook Notification Registration
 *
 * @usage
 *
 * Use Cases:
 * - Real-time conversation monitoring
 * - Message notification delivery
 * - Thread status tracking (archived, closed)
 * - Participant changes (joined, left)
 * - Build messaging app UIs
 *
 * @example Subscribe to all thread activity
 * ```http
 * POST /threads/{threadId}/subscriptions
 * {
 *   "webhookUrl": "https://example.com/webhook",
 *   "webhookSecret": "secret_xyz"
 * }
 * ```
 *
 * @example Subscribe to user messages only
 * ```http
 * POST /threads/{threadId}/subscriptions
 * {
 *   "webhookUrl": "https://example.com/webhook",
 *   "events": ["message.created", "message.completed"],
 *   "messageFilters": {
 *     "roles": ["user"]
 *   }
 * }
 * ```
 */
model ThreadSubscription {
  /**
   * Unique subscription identifier.
   * GENERATED: Server-generated GUID
   */
  @key
  @visibility("read")
  subscriptionId: string;

  /**
   * Thread being subscribed to.
   * FROM: Parent resource relationship
   */
  @visibility("read")
  threadId: string;

  /**
   * Webhook URL to POST notifications to.
   * REQUIRED: Must be HTTPS endpoint
   *
   * WEBHOOK PAYLOAD EXAMPLE:
   * {
   *   "type": "thread.activity",
   *   "threadId": "thread-123",
   *   "subscriptionId": "sub-456",
   *   "eventType": "message.created" | "run.completed" | "status.changed",
   *   "timestamp": "2026-01-29T10:00:00Z"
   * }
   *
   * CLIENT ACTION: GET /threads/{threadId} to fetch latest state
   */
  webhookUrl: string;

  /**
   * Secret for webhook signature validation.
   * OPTIONAL: For webhook authenticity verification
   *
   * PATTERN: Like GitHub webhook secrets (HMAC-SHA256 signature)
   */
  @secret
  webhookSecret?: string;

  /**
   * Event types to subscribe to.
   * DEFAULT: All events if omitted
   *
   * EVENT TYPES:
   * - "message.created": New message in thread
   * - "message.updated": Message streaming chunk or edit
   * - "message.completed": Message streaming finished
   * - "run.created": Run was created
   * - "run.started": Run started executing
   * - "run.completed": Run finished (completed)
   * - "run.failed": Run encountered error
   * - "run.cancelled": Run was cancelled
   * - "run.timeout": Run exceeded time limit
   * - "run.requires_action": Run needs tool execution or human input
   * - "run.input_required": Run needs user input
   * - "thread.created": Thread was created
   * - "thread.archived": Thread was archived
   * - "thread.closed": Thread was closed
   * - "thread.reopened": Thread was reopened
   * - "thread.deleted": Thread was deleted
   * - "participant.added": New participant joined
   * - "participant.removed": Participant left
   *
   * RATIONALE: Allow filtering to reduce notification volume
   */
  events?: string[];

  /**
   * Message filters for webhook subscriptions.
   * OPTIONAL: Filter which messages trigger notifications
   *
   * FILTERS:
   * - roles: Only messages from specific roles (user, assistant, tool, channel)
   * - userIds: Only messages from specific users
   * - agentIds: Only messages from specific agents
   * - contentTypes: Only messages with specific content types
   * - audience: Only content with specific audience annotations
   *
   * RATIONALE: Reduce noise by filtering out irrelevant messages
   */
  messageFilters?: MessageFilters;

  /**
   * Subscription expiration time.
   * OPTIONAL: Subscription automatically deleted after this time
   *
   * DEFAULT: No expiration (permanent until explicitly deleted)
   *
   * RATIONALE: Like OAuth tokens - can have TTL for security
   */
  expiresAt?: utcDateTime;

  /**
   * Whether subscription is currently active.
   * DEFAULT: true
   *
   * RATIONALE: Allows temporary disable without deletion
   */
  active?: boolean = true;

  /**
   * Timestamp when subscription was created.
   */
  @visibility("read")
  createdAt: utcDateTime;

  /**
   * Timestamp of last successful webhook delivery.
   * UPDATED: By server after successful POST (HTTP 200-299)
   */
  @visibility("read")
  lastDeliveredAt?: utcDateTime;

  /**
   * Number of consecutive failed delivery attempts.
   * INCREMENTED: On failed webhook POST (timeout, 4xx, 5xx)
   * RESET: On successful delivery
   *
   * RATIONALE: Automatic subscription disable after max failures
   */
  @visibility("read")
  failureCount?: int32 = 0;

  /**
   * Custom metadata for subscription.
   * FLEXIBLE: Client can store correlation IDs, user info, etc.
   */
  metadata?: Record<unknown>;
}

/**
 * Run Subscription - Webhook Notification Registration
 *
 * @usage
 *
 * Use Cases:
 * - Monitor long-running executions
 * - Track run lifecycle for orchestration
 * - Get notified when specific runs complete
 * - Build run activity dashboards
 *
 * @example Subscribe to run completion
 * ```http
 * POST /runs/{runId}/subscriptions
 * {
 *   "webhookUrl": "https://example.com/webhook",
 *   "events": ["run.completed", "run.failed"]
 * }
 * ```
 */
model RunSubscription {
  /**
   * Unique subscription identifier.
   * GENERATED: Server-generated GUID
   */
  @key
  @visibility("read")
  subscriptionId: string;

  /**
   * Run being subscribed to.
   * FROM: Parent resource relationship
   */
  @visibility("read")
  runId: string;

  /**
   * Webhook URL to POST notifications to.
   * REQUIRED: Must be HTTPS endpoint
   *
   * WEBHOOK PAYLOAD EXAMPLE:
   * {
   *   "type": "run.activity",
   *   "resourceId": "run-123",
   *   "subscriptionId": "sub-456",
   *   "eventType": "run.started" | "message.created" | "run.completed",
   *   "sequenceNumber": 42,
   *   "eventSeq": 10,
   *   "timestamp": "2026-02-06T10:00:00Z"
   * }
   *
   * CLIENT ACTION: GET /runs/{runId} to fetch latest state
   */
  webhookUrl: string;

  /**
   * Secret for webhook signature validation.
   * OPTIONAL: For webhook authenticity verification
   *
   * PATTERN: Like GitHub webhook secrets (HMAC-SHA256 signature)
   */
  @secret
  webhookSecret?: string;

  /**
   * Event types to subscribe to.
   * DEFAULT: All run events if omitted
   *
   * EVENT TYPES:
   * - "run.started": Run started executing
   * - "message.created": New message in run
   * - "message.updated": Message streaming chunk
   * - "message.completed": Message streaming finished
   * - "run.completed": Run finished successfully
   * - "run.failed": Run encountered error
   * - "run.cancelled": Run was cancelled
   * - "run.timeout": Run exceeded time limit
   * - "run.requires_action": Run needs tool execution
   * - "run.input_required": Run needs user input
   *
   * RATIONALE: Allow filtering to reduce notification volume
   */
  events?: string[];

  /**
   * Message filters for webhook subscriptions.
   * OPTIONAL: Filter which messages trigger notifications
   *
   * RATIONALE: Reduce noise by filtering out irrelevant messages
   */
  messageFilters?: MessageFilters;

  /**
   * Subscription expiration time.
   * OPTIONAL: Subscription automatically deleted after this time
   *
   * DEFAULT: No expiration (permanent until explicitly deleted)
   */
  expiresAt?: utcDateTime;

  /**
   * Whether subscription is currently active.
   * DEFAULT: true
   *
   * RATIONALE: Allows temporary disable without deletion
   */
  active?: boolean = true;

  /**
   * Timestamp when subscription was created.
   */
  @visibility("read")
  createdAt: utcDateTime;

  /**
   * Timestamp of last successful webhook delivery.
   * UPDATED: By server after successful POST (HTTP 200-299)
   */
  @visibility("read")
  lastDeliveredAt?: utcDateTime;

  /**
   * Number of consecutive failed delivery attempts.
   * INCREMENTED: On failed webhook POST (timeout, 4xx, 5xx)
   * RESET: On successful delivery
   *
   * RATIONALE: Automatic subscription disable after max failures
   */
  @visibility("read")
  failureCount?: int32 = 0;

  /**
   * Custom metadata for subscription.
   * FLEXIBLE: Client can store correlation IDs, user info, etc.
   */
  metadata?: Record<unknown>;
}

/**
 * Agent Subscription - Webhook Notification Registration
 *
 * @usage
 *
 * Use Cases:
 * - Monitor agent activity across all threads
 * - Track agent configuration changes
 * - Build agent analytics dashboards
 * - Debug agent behavior in production
 * - Track agent errors and failures
 *
 * @example Subscribe to agent errors
 * ```http
 * POST /agents/{agentId}/subscriptions
 * {
 *   "webhookUrl": "https://example.com/webhook",
 *   "events": ["run.failed", "agent.error"]
 * }
 * ```
 */
model AgentSubscription {
  /**
   * Unique subscription identifier.
   * GENERATED: Server-generated GUID
   */
  @key
  @visibility("read")
  subscriptionId: string;

  /**
   * Agent being subscribed to.
   */
  @visibility("read")
  agentId: string;

  /**
   * Webhook URL to POST notifications to.
   * REQUIRED: Must be HTTPS endpoint
   *
   * WEBHOOK PAYLOAD EXAMPLE:
   * {
   *   "type": "agent.activity",
   *   "resourceId": "agent-123",
   *   "subscriptionId": "sub-456",
   *   "eventType": "run.started" | "message.created" | "agent.updated",
   *   "sequenceNumber": 42,
   *   "eventSeq": 1587,
   *   "timestamp": "2026-02-06T10:00:00Z"
   * }
   *
   * CLIENT ACTION: GET /agents/{agentId} or GET /runs/{runId} to fetch latest state
   */
  webhookUrl: string;

  /**
   * Secret for webhook signature validation.
   * OPTIONAL: For webhook authenticity verification
   *
   * PATTERN: Like GitHub webhook secrets (HMAC-SHA256 signature)
   */
  @secret
  webhookSecret?: string;

  /**
   * Event types to subscribe to.
   * DEFAULT: All agent events if omitted
   *
   * EVENT TYPES:
   * - "message.created": New message from agent
   * - "message.updated": Message streaming chunk
   * - "message.completed": Message streaming finished
   * - "run.created": Run created for this agent
   * - "run.started": Run started
   * - "run.completed": Run completed
   * - "run.failed": Run failed
   * - "run.cancelled": Run cancelled
   * - "run.timeout": Run timed out
   * - "run.requires_action": Run needs action
   * - "run.input_required": Run needs input
   * - "agent.created": Agent registered
   * - "agent.updated": Agent config changed
   * - "agent.deleted": Agent removed
   * - "agent.enabled": Agent enabled
   * - "agent.disabled": Agent disabled
   * - "agent.error": Agent error occurred
   *
   * RATIONALE: Allow filtering to reduce notification volume
   */
  events?: string[];

  /**
   * Filter by specific thread.
   * OPTIONAL: Only notify for activity in this thread
   *
   * RATIONALE: Narrow agent monitoring to specific conversation
   */
  threadId?: string;

  /**
   * Message filters for webhook subscriptions.
   * OPTIONAL: Filter which messages trigger notifications
   *
   * RATIONALE: Reduce noise by filtering out irrelevant messages
   */
  messageFilters?: MessageFilters;

  /**
   * Subscription expiration time.
   * OPTIONAL: Subscription automatically deleted after this time
   *
   * DEFAULT: No expiration (permanent until explicitly deleted)
   */
  expiresAt?: utcDateTime;

  /**
   * Whether subscription is currently active.
   * DEFAULT: true
   *
   * RATIONALE: Allows temporary disable without deletion
   */
  active?: boolean = true;

  /**
   * Timestamp when subscription was created.
   */
  @visibility("read")
  createdAt: utcDateTime;

  /**
   * Timestamp of last successful webhook delivery.
   * UPDATED: By server after successful POST (HTTP 200-299)
   */
  @visibility("read")
  lastDeliveredAt?: utcDateTime;

  /**
   * Number of consecutive failed delivery attempts.
   * INCREMENTED: On failed webhook POST (timeout, 4xx, 5xx)
   * RESET: On successful delivery
   *
   * RATIONALE: Automatic subscription disable after max failures
   */
  @visibility("read")
  failureCount?: int32 = 0;

  /**
   * Custom metadata for subscription.
   * FLEXIBLE: Client can store correlation IDs, user info, etc.
   */
  metadata?: Record<unknown>;
}
