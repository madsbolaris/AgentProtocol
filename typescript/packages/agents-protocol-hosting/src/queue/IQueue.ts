/**
 * Message for queue processing.
 */
export interface QueueMessage {
  /** Unique message ID */
  id: string;
  /** Thread ID for this message */
  threadId: string;
  /** Run ID for this message */
  runId?: string;
  /** Message content */
  content: unknown;
  /** When the message was enqueued */
  timestamp: Date;
}

/**
 * Interface for message queue.
 *
 * Implementations must support at-least-once delivery and
 * horizontal scaling.
 */
export interface IQueue {
  /**
   * Enqueues a message for processing.
   *
   * @param message - The message to enqueue
   * @param idempotencyKey - Optional key to prevent duplicates
   */
  enqueueAsync(message: QueueMessage, idempotencyKey?: string): Promise<void>;

  /**
   * Dequeues a message for processing.
   *
   * @returns The message or null if queue is empty
   */
  dequeueAsync(): Promise<QueueMessage | null>;

  /**
   * Acknowledges message processing completed successfully.
   *
   * @param messageId - The message ID
   */
  acknowledgeAsync(messageId: string): Promise<void>;

  /**
   * Rejects a message and moves it to dead letter queue.
   *
   * @param messageId - The message ID
   * @param reason - Reason for rejection
   */
  rejectAsync(messageId: string, reason: string): Promise<void>;

  /**
   * Checks if the queue is healthy.
   *
   * @returns true if healthy, false otherwise
   */
  checkHealth(): Promise<boolean>;
}

/**
 * Configuration for concurrency control.
 */
export interface ConcurrencyConfig {
  /**
   * Maximum concurrent runs per thread.
   *
   * @default 1
   */
  maxConcurrentRunsPerThread: number;

  /**
   * Maximum queued messages per thread.
   *
   * @default 100
   */
  queueDepthLimit: number;

  /**
   * What to do when queue is full.
   *
   * - 'drop': Drop oldest message
   * - 'reject': Reject new message with HTTP 429
   * - 'block': Block until space available (not recommended)
   *
   * @default 'reject'
   */
  onQueueFull: 'drop' | 'reject' | 'block';

  /**
   * Global concurrency limit across all threads.
   * Useful for rate limiting total LLM API calls.
   *
   * @default undefined (no global limit)
   */
  globalConcurrencyLimit?: number;
}
