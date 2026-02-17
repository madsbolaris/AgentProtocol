import { InMemoryQueue } from '../src/queue/InMemoryQueue.js';
import { QueueMessage } from '../src/queue/IQueue.js';

describe('InMemoryQueue', () => {
  let queue: InMemoryQueue;

  beforeEach(() => {
    queue = new InMemoryQueue();
  });

  describe('constructor', () => {
    it('should create a new InMemoryQueue instance', () => {
      expect(queue).toBeInstanceOf(InMemoryQueue);
    });
  });

  describe('enqueueAsync', () => {
    it('should enqueue a message', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message);

      const dequeued = await queue.dequeueAsync();
      expect(dequeued).toEqual(message);
    });

    it('should enqueue multiple messages', async () => {
      const message1: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Message 1',
        timestamp: new Date()
      };

      const message2: QueueMessage = {
        id: 'msg-2',
        threadId: 'thread-2',
        content: 'Message 2',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message1);
      await queue.enqueueAsync(message2);

      const dequeued1 = await queue.dequeueAsync();
      const dequeued2 = await queue.dequeueAsync();

      expect(dequeued1).toEqual(message1);
      expect(dequeued2).toEqual(message2);
    });

    it('should handle idempotency key', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message, 'idempotency-key-1');
      await queue.enqueueAsync(message, 'idempotency-key-1'); // Should be ignored

      const dequeued1 = await queue.dequeueAsync();
      const dequeued2 = await queue.dequeueAsync();

      expect(dequeued1).toEqual(message);
      expect(dequeued2).toBeNull(); // Second enqueue was ignored
    });

    it('should allow same message with different idempotency keys', async () => {
      const message1: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      const message2: QueueMessage = {
        id: 'msg-2',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message1, 'key-1');
      await queue.enqueueAsync(message2, 'key-2');

      const dequeued1 = await queue.dequeueAsync();
      const dequeued2 = await queue.dequeueAsync();

      expect(dequeued1).toEqual(message1);
      expect(dequeued2).toEqual(message2);
    });

    it('should enqueue without idempotency key', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message);

      const dequeued = await queue.dequeueAsync();
      expect(dequeued).toEqual(message);
    });
  });

  describe('dequeueAsync', () => {
    it('should return null for empty queue', async () => {
      const message = await queue.dequeueAsync();
      expect(message).toBeNull();
    });

    it('should dequeue in FIFO order', async () => {
      const message1: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'First',
        timestamp: new Date()
      };

      const message2: QueueMessage = {
        id: 'msg-2',
        threadId: 'thread-2',
        content: 'Second',
        timestamp: new Date()
      };

      const message3: QueueMessage = {
        id: 'msg-3',
        threadId: 'thread-3',
        content: 'Third',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message1);
      await queue.enqueueAsync(message2);
      await queue.enqueueAsync(message3);

      expect(await queue.dequeueAsync()).toEqual(message1);
      expect(await queue.dequeueAsync()).toEqual(message2);
      expect(await queue.dequeueAsync()).toEqual(message3);
      expect(await queue.dequeueAsync()).toBeNull();
    });

    it('should track processing IDs', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message);
      const dequeued = await queue.dequeueAsync();

      expect(dequeued).toEqual(message);
      // Processing ID should be tracked internally
    });
  });

  describe('acknowledgeAsync', () => {
    it('should acknowledge a message', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message);
      const dequeued = await queue.dequeueAsync();

      expect(dequeued).not.toBeNull();
      await queue.acknowledgeAsync('msg-1');
    });

    it('should handle acknowledging non-existent message', async () => {
      await queue.acknowledgeAsync('non-existent-id');
      // Should not throw
    });

    it('should complete the message lifecycle', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      // Enqueue
      await queue.enqueueAsync(message);

      // Dequeue
      const dequeued = await queue.dequeueAsync();
      expect(dequeued).toEqual(message);

      // Acknowledge
      await queue.acknowledgeAsync('msg-1');

      // Queue should be empty
      const next = await queue.dequeueAsync();
      expect(next).toBeNull();
    });
  });

  describe('rejectAsync', () => {
    it('should reject a message', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message);
      const dequeued = await queue.dequeueAsync();

      expect(dequeued).not.toBeNull();
      await queue.rejectAsync('msg-1', 'Processing failed');

      expect(consoleErrorSpy).toHaveBeenCalledWith('Message msg-1 rejected: Processing failed');
      consoleErrorSpy.mockRestore();
    });

    it('should reject with different reasons', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      await queue.rejectAsync('msg-2', 'Timeout');
      await queue.rejectAsync('msg-3', 'Invalid format');
      await queue.rejectAsync('msg-4', 'Unknown error');

      expect(consoleErrorSpy).toHaveBeenCalledWith('Message msg-2 rejected: Timeout');
      expect(consoleErrorSpy).toHaveBeenCalledWith('Message msg-3 rejected: Invalid format');
      expect(consoleErrorSpy).toHaveBeenCalledWith('Message msg-4 rejected: Unknown error');

      consoleErrorSpy.mockRestore();
    });

    it('should handle rejecting non-existent message', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      await queue.rejectAsync('non-existent-id', 'Some reason');

      expect(consoleErrorSpy).toHaveBeenCalledWith('Message non-existent-id rejected: Some reason');
      consoleErrorSpy.mockRestore();
    });
  });

  describe('checkHealth', () => {
    it('should always return true', async () => {
      const health = await queue.checkHealth();
      expect(health).toBe(true);
    });

    it('should return true even with messages', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Test message',
        timestamp: new Date()
      };

      await queue.enqueueAsync(message);

      const health = await queue.checkHealth();
      expect(health).toBe(true);
    });
  });

  describe('integration', () => {
    it('should handle complete message flow', async () => {
      const consoleErrorSpy = jest.spyOn(console, 'error').mockImplementation();

      // Enqueue several messages
      await queue.enqueueAsync({
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Message 1',
        timestamp: new Date()
      });

      await queue.enqueueAsync({
        id: 'msg-2',
        threadId: 'thread-2',
        content: 'Message 2',
        timestamp: new Date()
      });

      await queue.enqueueAsync({
        id: 'msg-3',
        threadId: 'thread-3',
        content: 'Message 3',
        timestamp: new Date()
      });

      // Process first message successfully
      const msg1 = await queue.dequeueAsync();
      expect(msg1?.id).toBe('msg-1');
      await queue.acknowledgeAsync('msg-1');

      // Process second message with failure
      const msg2 = await queue.dequeueAsync();
      expect(msg2?.id).toBe('msg-2');
      await queue.rejectAsync('msg-2', 'Processing error');

      // Process third message successfully
      const msg3 = await queue.dequeueAsync();
      expect(msg3?.id).toBe('msg-3');
      await queue.acknowledgeAsync('msg-3');

      // Queue should be empty
      expect(await queue.dequeueAsync()).toBeNull();

      // Health check should still pass
      expect(await queue.checkHealth()).toBe(true);

      consoleErrorSpy.mockRestore();
    });

    it('should handle idempotency correctly', async () => {
      const message: QueueMessage = {
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Idempotent message',
        timestamp: new Date()
      };

      // Try to enqueue same message multiple times with same key
      await queue.enqueueAsync(message, 'unique-key');
      await queue.enqueueAsync(message, 'unique-key');
      await queue.enqueueAsync(message, 'unique-key');

      // Should only get one message
      const dequeued1 = await queue.dequeueAsync();
      expect(dequeued1).toEqual(message);

      const dequeued2 = await queue.dequeueAsync();
      expect(dequeued2).toBeNull();
    });

    it('should handle mixed operations', async () => {
      // Enqueue
      await queue.enqueueAsync({
        id: 'msg-1',
        threadId: 'thread-1',
        content: 'Message 1',
        timestamp: new Date()
      });

      // Dequeue
      const msg1 = await queue.dequeueAsync();
      expect(msg1?.id).toBe('msg-1');

      // Enqueue more while processing
      await queue.enqueueAsync({
        id: 'msg-2',
        threadId: 'thread-2',
        content: 'Message 2',
        timestamp: new Date()
      });

      // Acknowledge first
      await queue.acknowledgeAsync('msg-1');

      // Enqueue with idempotency
      await queue.enqueueAsync({
        id: 'msg-3',
        threadId: 'thread-3',
        content: 'Message 3',
        timestamp: new Date()
      }, 'key-3');

      // Dequeue remaining
      const msg2 = await queue.dequeueAsync();
      const msg3 = await queue.dequeueAsync();

      expect(msg2?.id).toBe('msg-2');
      expect(msg3?.id).toBe('msg-3');

      await queue.acknowledgeAsync('msg-2');
      await queue.acknowledgeAsync('msg-3');

      expect(await queue.dequeueAsync()).toBeNull();
    });
  });
});
