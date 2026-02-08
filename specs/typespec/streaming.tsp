/**
 * Streaming & Events Models
 *
 * This file defines all streaming event types, webhook subscriptions, and
 * Server-Sent Events (SSE) payloads for real-time updates.
 *
 * KEY CONCEPTS:
 * - Unified message events (message.created, message.updated, message.completed)
 * - Run lifecycle events (run.created, run.started, run.completed, run.failed, etc.)
 * - Thread lifecycle events (thread.created, thread.archived, thread.closed, etc.)
 * - Agent configuration events (agent.created, agent.updated, agent.deleted, etc.)
 * - Participant events (participant.added, participant.removed)
 * - Event sequencing (eventSeq for ordering within resources)
 * - Webhook subscriptions with message filtering
 *
 * STREAMING ENDPOINTS:
 * - GET /runs/{runId}/stream - Stream run events
 * - GET /threads/{threadId}/stream - Stream thread events
 * - GET /agents/{agentId}/stream - Stream agent events
 */

import "@typespec/http";
import "@typespec/rest";
import "./common.tsp";
import "./messages.tsp";
import "./tools.tsp";
import "./usage.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace Microsoft.Agents.AI;

// ========================================
// Unified Message Events
// ========================================

@doc("Emitted when a new message or message chunk is created")
model MessageCreatedEvent {
  @doc("Run identifier (for run streams)")
  runId?: string;

  @doc("Thread identifier (for thread streams)")
  threadId?: string;

  @doc("Agent identifier (for agent streams)")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("The message that was created")
  message: ChatMessage;

  @doc("Message creation timestamp")
  createdAt: utcDateTime;
}

@doc("Emitted when a message is updated (streaming chunk or edit)")
model MessageUpdatedEvent {
  @doc("Run identifier (for run streams)")
  runId?: string;

  @doc("Thread identifier (for thread streams)")
  threadId?: string;

  @doc("Agent identifier (for agent streams)")
  agentId?: string;

  @doc("The message being updated")
  messageId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Incremental message update")
  message: {
    @doc("Updated contents (append for streaming, replace for edits)")
    contents: AIContent[];

    @doc("Message version (increments with each update, for edit ordering)")
    version?: int32;

    @doc("Token usage (included in final chunk)")
    usage?: CompletionUsage;

    @doc("Update timestamp (for edits; omit for streaming chunks)")
    updatedAt?: utcDateTime;
  };
}

@doc("Emitted when message streaming is completed (notification only, no message content)")
model MessageCompletedEvent {
  @doc("Run identifier (for run streams)")
  runId?: string;

  @doc("Thread identifier (for thread streams)")
  threadId?: string;

  @doc("Agent identifier (for agent streams)")
  agentId?: string;

  @doc("The completed message identifier")
  messageId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Token usage statistics")
  usage?: CompletionUsage;

  @doc("Completion timestamp")
  completedAt: utcDateTime;
}

// ========================================
// Participant Events
// ========================================

@doc("Emitted when a participant joins a thread")
model ParticipantAddedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("The participant who was added")
  participant: Participant;

  @doc("When the participant was added")
  addedAt: utcDateTime;
}

@doc("Emitted when a participant leaves a thread")
model ParticipantRemovedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Participant identifier")
  participantId: string;

  @doc("Reason for removal (left, removed, banned)")
  reason?: "left" | "removed" | "banned";

  @doc("When the participant was removed")
  removedAt: utcDateTime;
}

// ========================================
// Run Lifecycle Events
// ========================================

@doc("Emitted when a run is created")
model RunCreatedEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier (required at creation; optional in subsequent events when context is known)")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "queued";

  @doc("Creation timestamp")
  createdAt: utcDateTime;
}

@doc("Emitted when a run starts executing")
model RunStartedEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "in_progress";

  @doc("Start timestamp")
  startedAt: utcDateTime;
}

@doc("Emitted when a run completes successfully")
model RunCompletedEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "completed";

  @doc("Final output messages")
  output: ChatMessage[];

  @doc("Token usage statistics")
  usage?: CompletionUsage;

  @doc("Completion timestamp")
  completedAt: utcDateTime;
}

@doc("Emitted when a run fails")
model RunFailedEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "failed";

  @doc("Error details")
  error: {
    @doc("Error code")
    code: string;

    @doc("Error message")
    message: string;

    @doc("Additional error details")
    details?: unknown;
  };

  @doc("Failure timestamp")
  failedAt: utcDateTime;
}

@doc("Emitted when a run is cancelled")
model RunCancelledEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "cancelled";

  @doc("Cancellation reason")
  reason?: string;

  @doc("Cancellation timestamp")
  cancelledAt: utcDateTime;
}

@doc("Emitted when a run times out")
model RunTimeoutEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "timeout";

  @doc("Partial output (if any)")
  output?: ChatMessage[];

  @doc("Partial usage (if any)")
  usage?: CompletionUsage;

  @doc("Timeout timestamp")
  timedOutAt: utcDateTime;
}

@doc("Emitted when a run requires tool execution approval")
model RunRequiresActionEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "requires_action";

  @doc("Required action details")
  required_action: {
    @doc("Action type")
    kind: "submit_tool_outputs";

    @doc("Tool calls requiring approval")
    tool_calls: FunctionCallContent[];
  };

  @doc("Event timestamp")
  timestamp: utcDateTime;
}

@doc("Emitted when a run requires user input")
model RunInputRequiredEvent {
  @doc("Run identifier")
  runId: string;

  @doc("Thread identifier")
  threadId?: string;

  @doc("Agent identifier")
  agentId?: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Run status")
  status: "input_required";

  @doc("Required input details")
  required_input: {
    @doc("Input prompt/question")
    prompt: string;

    @doc("Input type expected")
    type?: "text" | "choice" | "auth";

    @doc("Choices (for choice type)")
    choices?: string[];
  };

  @doc("Event timestamp")
  timestamp: utcDateTime;
}

// ========================================
// Thread Lifecycle Events
// ========================================

@doc("Emitted when a thread is created")
model ThreadCreatedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Thread status")
  status: "active";

  @doc("Creation timestamp")
  createdAt: utcDateTime;
}

@doc("Emitted when a thread is archived")
model ThreadArchivedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Archived by user/agent")
  archivedBy?: string;

  @doc("Archive timestamp")
  archivedAt: utcDateTime;
}

@doc("Emitted when a thread is closed")
model ThreadClosedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Closed by user/agent")
  closedBy?: string;

  @doc("Close reason")
  reason?: string;

  @doc("Close timestamp")
  closedAt: utcDateTime;
}

@doc("Emitted when a thread is reopened")
model ThreadReopenedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Reopened by user/agent")
  reopenedBy?: string;

  @doc("Reopen timestamp")
  reopenedAt: utcDateTime;
}

@doc("Emitted when a thread is deleted")
model ThreadDeletedEvent {
  @doc("Thread identifier")
  threadId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Deleted by user/agent")
  deletedBy?: string;

  @doc("Deletion timestamp")
  deletedAt: utcDateTime;
}

// ========================================
// Agent Configuration Events
// ========================================

@doc("Emitted when an agent is created")
model AgentCreatedEvent {
  @doc("Agent identifier")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Agent name")
  name: string;

  @doc("Model identifier")
  `model`?: string;

  @doc("Creation timestamp")
  createdAt: utcDateTime;
}

@doc("Emitted when an agent's configuration is updated")
model AgentUpdatedEvent {
  @doc("Agent identifier")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Configuration changes")
  changes: {
    @doc("Updated instructions")
    instructions?: string;

    @doc("Updated tools")
    tools?: AITool[];

    @doc("Updated model")
    `model`?: string;

    @doc("Updated metadata")
    metadata?: Record<unknown>;
  };

  @doc("Update timestamp")
  updatedAt: utcDateTime;
}

@doc("Emitted when an agent is deleted")
model AgentDeletedEvent {
  @doc("Agent identifier")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Deletion timestamp")
  deletedAt: utcDateTime;
}

@doc("Emitted when an agent is enabled")
model AgentEnabledEvent {
  @doc("Agent identifier")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Enable timestamp")
  enabledAt: utcDateTime;
}

@doc("Emitted when an agent is disabled")
model AgentDisabledEvent {
  @doc("Agent identifier")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Disable reason")
  reason?: string;

  @doc("Disable timestamp")
  disabledAt: utcDateTime;
}

@doc("Emitted when an agent encounters a configuration or deployment error")
model AgentErrorEvent {
  @doc("Agent identifier")
  agentId: string;

  @doc("Event sequence number (per resource, for ordering)")
  eventSeq: int64;

  @doc("Error details")
  error: {
    @doc("Error code")
    code: string;

    @doc("Error message")
    message: string;

    @doc("Error context (e.g., config validation failure, deployment issue)")
    context?: unknown;
  };

  @doc("Error timestamp")
  timestamp: utcDateTime;
}

// ========================================
// Webhook Subscriptions
// ========================================

/**
 * Subscription Models
 *
 * NOTE: MessageFilters, WebhookNotification, and subscription models
 * (ThreadSubscription, RunSubscription, AgentSubscription) have been moved to subscriptions.tsp.
 * Import subscriptions.tsp to use these types.
 */

// ========================================
// Event Category Unions
// ========================================

/**
 * All message-related streaming events.
 *
 * @usage
 * Use to filter or handle all message events in a unified way.
 * Useful for webhook subscriptions and event processing.
 *
 * @example Filter message events
 * ```typescript
 * if (event is MessageEvent) {
 *   // Handle message-related events
 * }
 * ```
 */
union MessageEvent {
  MessageCreatedEvent,
  MessageUpdatedEvent,
  MessageCompletedEvent,
}

/**
 * All participant-related streaming events.
 *
 * @usage
 * Use to track participant changes in threads.
 */
union ParticipantEvent {
  ParticipantAddedEvent,
  ParticipantRemovedEvent,
}

/**
 * All run lifecycle streaming events.
 *
 * @usage
 * Use to monitor run state transitions and completion status.
 * Covers the full run lifecycle from creation to completion/failure.
 *
 * @example Subscribe to run completion
 * ```typescript
 * if (event is RunEvent) {
 *   if (event.kind === "run.completed" || event.kind === "run.failed") {
 *     // Handle run completion
 *   }
 * }
 * ```
 */
union RunEvent {
  RunCreatedEvent,
  RunStartedEvent,
  RunCompletedEvent,
  RunFailedEvent,
  RunCancelledEvent,
  RunTimeoutEvent,
  RunRequiresActionEvent,
  RunInputRequiredEvent,
}

/**
 * All thread lifecycle streaming events.
 *
 * @usage
 * Use to track thread state changes.
 */
union ThreadEvent {
  ThreadCreatedEvent,
  ThreadArchivedEvent,
  ThreadClosedEvent,
  ThreadReopenedEvent,
  ThreadDeletedEvent,
}

/**
 * All agent lifecycle streaming events.
 *
 * @usage
 * Use to monitor agent configuration and state changes.
 */
union AgentEvent {
  AgentCreatedEvent,
  AgentUpdatedEvent,
  AgentDeletedEvent,
  AgentEnabledEvent,
  AgentDisabledEvent,
  AgentErrorEvent,
}

/**
 * Union of all streaming events.
 *
 * @usage
 * Use to handle any streaming event in a type-safe way.
 * Webhook handlers can pattern-match on event categories.
 *
 * @example Handle all events
 * ```typescript
 * function handleEvent(event: StreamingEvent) {
 *   if (event is MessageEvent) {
 *     // Handle message events
 *   } else if (event is RunEvent) {
 *     // Handle run events
 *   } else if (event is ThreadEvent) {
 *     // Handle thread events
 *   }
 * }
 * ```
 */
union StreamingEvent {
  MessageEvent,
  ParticipantEvent,
  RunEvent,
  ThreadEvent,
  AgentEvent,
}
