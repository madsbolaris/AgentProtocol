/**
 * SSE Event types from the Agent Protocol
 */

import type { ChatMessage, Run, Thread } from '@microsoft/agents-protocol-abstractions';

export type StreamEventType =
  // Message events
  | 'message.created'
  | 'message.updated'
  | 'message.completed'
  | 'message.deleted'
  // Run events
  | 'run.created'
  | 'run.started'
  | 'run.completed'
  | 'run.failed'
  | 'run.cancelled'
  | 'run.timeout'
  | 'run.requires_action'
  | 'run.input_required'
  // Thread events
  | 'thread.created'
  | 'thread.updated'
  | 'thread.deleted'
  // Generic
  | 'error'
  | 'done';

export interface BaseStreamEvent {
  /** Event type */
  event: StreamEventType;

  /** Event sequence number (for ordering) */
  eventSeq?: number;

  /** Run ID (if applicable) */
  runId?: string;

  /** Thread ID (if applicable) */
  threadId?: string;

  /** Agent ID (if applicable) */
  agentId?: string;

  /** Timestamp */
  createdAt?: string;
}

export interface MessageCreatedEvent extends BaseStreamEvent {
  event: 'message.created';
  message: ChatMessage;
}

export interface MessageUpdatedEvent extends BaseStreamEvent {
  event: 'message.updated';
  message: ChatMessage;
  delta?: {
    content?: string;
  };
}

export interface MessageCompletedEvent extends BaseStreamEvent {
  event: 'message.completed';
  message: ChatMessage;
}

export interface RunCreatedEvent extends BaseStreamEvent {
  event: 'run.created';
  run: Run;
}

export interface RunStartedEvent extends BaseStreamEvent {
  event: 'run.started';
  run: Run;
}

export interface RunCompletedEvent extends BaseStreamEvent {
  event: 'run.completed';
  run: Run;
}

export interface RunFailedEvent extends BaseStreamEvent {
  event: 'run.failed';
  run: Run;
  error: {
    code: string;
    message: string;
  };
}

export interface RunRequiresActionEvent extends BaseStreamEvent {
  event: 'run.requires_action';
  run: Run;
}

export interface ErrorEvent extends BaseStreamEvent {
  event: 'error';
  error: {
    code: string;
    message: string;
  };
}

export interface DoneEvent extends BaseStreamEvent {
  event: 'done';
}

export type StreamEvent =
  | MessageCreatedEvent
  | MessageUpdatedEvent
  | MessageCompletedEvent
  | RunCreatedEvent
  | RunStartedEvent
  | RunCompletedEvent
  | RunFailedEvent
  | RunRequiresActionEvent
  | ErrorEvent
  | DoneEvent
  | BaseStreamEvent;
