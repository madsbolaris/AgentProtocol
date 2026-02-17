import { IQueue, QueueMessage } from './IQueue.js';

/**
 * In-memory queue implementation.
 * Not suitable for distributed systems or production use.
 * Use only for development or testing.
 */
export class InMemoryQueue implements IQueue {
  private queue: QueueMessage[] = [];
  private processingIds: Set<string> = new Set();
  private idempotencyKeys: Set<string> = new Set();

  /**
   * Creates a new in-memory queue instance.
   */
  constructor() {}

  async enqueueAsync(message: QueueMessage, idempotencyKey?: string): Promise<void> {
    // Check idempotency
    if (idempotencyKey && this.idempotencyKeys.has(idempotencyKey)) {
      return; // Already processed
    }

    this.queue.push(message);

    if (idempotencyKey) {
      this.idempotencyKeys.add(idempotencyKey);
    }
  }

  async dequeueAsync(): Promise<QueueMessage | null> {
    if (this.queue.length === 0) {
      return null;
    }

    const message = this.queue.shift();
    if (message) {
      this.processingIds.add(message.id);
    }

    return message || null;
  }

  async acknowledgeAsync(messageId: string): Promise<void> {
    this.processingIds.delete(messageId);
  }

  async rejectAsync(messageId: string, reason: string): Promise<void> {
    this.processingIds.delete(messageId);
    // In a real implementation, would move to dead letter queue
    console.error(`Message ${messageId} rejected: ${reason}`);
  }

  async checkHealth(): Promise<boolean> {
    return true;
  }
}
