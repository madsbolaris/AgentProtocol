import { AIContent } from '../core/types.js';

/**
 * Publishes out-of-band messages to threads from background services, webhooks, or scheduled tasks.
 * Messages are enqueued for processing, ensuring horizontal scalability.
 */
export interface IOutOfBandPublisher {
  /**
   * Sends a message to a thread from outside the normal request/response flow.
   *
   * @param threadId - The thread ID to send to
   * @param content - The content to send
   * @param runId - Optional run ID if associated with a specific run
   * @param idempotencyKey - Idempotency key to prevent duplicate sends
   * @param cancellationToken - Optional abort signal
   * @returns A promise representing the async operation
   *
   * @example
   * ```typescript
   * await publisher.sendToThreadAsync(
   *   'thread-123',
   *   { kind: 'text', text: 'Reminder: Your appointment is tomorrow' },
   *   undefined,
   *   'reminder-2024-01-01'
   * );
   * ```
   */
  sendToThreadAsync(
    threadId: string,
    content: AIContent,
    runId?: string,
    idempotencyKey?: string,
    cancellationToken?: AbortSignal
  ): Promise<void>;

  /**
   * Sends a text message to a thread from outside the normal request/response flow.
   *
   * @param threadId - The thread ID to send to
   * @param text - The text to send
   * @param runId - Optional run ID if associated with a specific run
   * @param idempotencyKey - Idempotency key to prevent duplicate sends
   * @param cancellationToken - Optional abort signal
   * @returns A promise representing the async operation
   *
   * @example
   * ```typescript
   * await publisher.sendToThreadAsync(
   *   'thread-123',
   *   'Reminder: Your appointment is tomorrow',
   *   undefined,
   *   'reminder-2024-01-01'
   * );
   * ```
   */
  sendToThreadAsync(
    threadId: string,
    text: string,
    runId?: string,
    idempotencyKey?: string,
    cancellationToken?: AbortSignal
  ): Promise<void>;
}
