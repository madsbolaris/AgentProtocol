import { InMemoryStorage } from '../src/storage/InMemoryStorage.js';
import { AgentContext } from '../src/core/AgentContext.js';
import { TurnResult } from '../src/core/TurnResult.js';
import { IAgentContext } from '../src/core/IAgentContext.js';
import { AIContent } from '../src/core/types.js';

describe('Async Patterns', () => {
  describe('async state operations', () => {
    it('should handle async state operations', async () => {
      const storage = new InMemoryStorage();

      await storage.setAsync('thread1', 'key1', 'value1');
      const result = await storage.getAsync('thread1', 'key1');

      expect(result).toBe('value1');
    });

    it('should handle concurrent state operations', async () => {
      const storage = new InMemoryStorage();

      const setMultipleKeys = async (threadId: string, count: number) => {
        for (let i = 0; i < count; i++) {
          await storage.setAsync(threadId, `key${i}`, `value${i}`);
        }
      };

      // Run concurrent operations
      await Promise.all([
        setMultipleKeys('thread1', 10),
        setMultipleKeys('thread2', 10),
        setMultipleKeys('thread3', 10)
      ]);

      // Verify results
      for (let i = 0; i < 10; i++) {
        expect(await storage.getAsync('thread1', `key${i}`)).toBe(`value${i}`);
        expect(await storage.getAsync('thread2', `key${i}`)).toBe(`value${i}`);
        expect(await storage.getAsync('thread3', `key${i}`)).toBe(`value${i}`);
      }
    });
  });

  describe('async context operations', () => {
    it('should handle async respond operations', async () => {
      const storage = new InMemoryStorage();
      const responses: string[] = [];

      const callback = async (content: string | AIContent) => {
        await new Promise(resolve => setTimeout(resolve, 10)); // Simulate async work
        responses.push(typeof content === 'string' ? content : JSON.stringify(content));
      };

      const context = new AgentContext('run1', 'thread1', storage, callback);

      await context.respondAsync('Message 1');
      await context.respondAsync('Message 2');
      await context.respondAsync('Message 3');

      expect(responses).toHaveLength(3);
      expect(responses).toEqual(['Message 1', 'Message 2', 'Message 3']);
    });

    it('should handle concurrent context operations', async () => {
      const storage = new InMemoryStorage();

      const workInContext = async (context: IAgentContext, count: number) => {
        for (let i = 0; i < count; i++) {
          await context.setStateAsync(`key${i}`, `value${i}`);
          await context.logAsync(`Processed item ${i}`);
        }
      };

      const contexts = [
        new AgentContext('run0', 'thread0', storage),
        new AgentContext('run1', 'thread1', storage),
        new AgentContext('run2', 'thread2', storage),
        new AgentContext('run3', 'thread3', storage),
        new AgentContext('run4', 'thread4', storage)
      ];

      await Promise.all(contexts.map(ctx => workInContext(ctx, 10)));

      // Verify each thread has its own state
      for (let i = 0; i < 5; i++) {
        const keys = await storage.getKeysAsync(`thread${i}`);
        expect(keys).toHaveLength(10);
      }
    });
  });

  describe('async function execution', () => {
    it('should execute async functions', async () => {
      const asyncFunc = async (x: number): Promise<string> => {
        await new Promise(resolve => setTimeout(resolve, 10));
        return (x * 2).toString();
      };

      const result = await asyncFunc(5);
      expect(result).toBe('10');
    });
  });

  describe('cancellation token async', () => {
    it('should handle cancellation in async operations', async () => {
      const storage = new InMemoryStorage();
      const responses: string[] = [];

      const callback = async (content: string | AIContent) => {
        responses.push(typeof content === 'string' ? content : JSON.stringify(content));
      };

      const context = new AgentContext('run1', 'thread1', storage, callback);

      const controller = new AbortController();

      // Operations should work before cancellation
      await context.respondAsync('Message 1', controller.signal);
      expect(responses).toHaveLength(1);

      // Cancel the signal
      controller.abort();

      // Operations should be skipped after cancellation
      await expect(
        context.respondAsync('Message 2', controller.signal)
      ).rejects.toThrow('Operation was cancelled');

      expect(responses).toHaveLength(1); // Still 1, not 2
    });
  });

  describe('async handler execution', () => {
    it('should execute async handlers', async () => {
      const called: string[] = [];

      const asyncHandler = async (msg: any, ctx: IAgentContext): Promise<TurnResult> => {
        await new Promise(resolve => setTimeout(resolve, 10));
        called.push(msg);
        return TurnResult.Continue;
      };

      const storage = new InMemoryStorage();
      const context = new AgentContext('run1', 'thread1', storage);

      const result = await asyncHandler('test message', context);

      expect(result).toBe(TurnResult.Continue);
      expect(called).toHaveLength(1);
      expect(called[0]).toBe('test message');
    });

    it('should execute multiple async handlers in sequence', async () => {
      const executionOrder: number[] = [];

      const handler1 = async (msg: any, ctx: IAgentContext): Promise<TurnResult> => {
        await new Promise(resolve => setTimeout(resolve, 10));
        executionOrder.push(1);
        return TurnResult.Continue;
      };

      const handler2 = async (msg: any, ctx: IAgentContext): Promise<TurnResult> => {
        await new Promise(resolve => setTimeout(resolve, 10));
        executionOrder.push(2);
        return TurnResult.Continue;
      };

      const handler3 = async (msg: any, ctx: IAgentContext): Promise<TurnResult> => {
        await new Promise(resolve => setTimeout(resolve, 10));
        executionOrder.push(3);
        return TurnResult.Continue;
      };

      const storage = new InMemoryStorage();
      const context = new AgentContext('run1', 'thread1', storage);

      await handler1('msg', context);
      await handler2('msg', context);
      await handler3('msg', context);

      expect(executionOrder).toEqual([1, 2, 3]);
    });
  });

  describe('async error handling', () => {
    it('should handle errors in async operations', async () => {
      const failingOperation = async (): Promise<string> => {
        await new Promise(resolve => setTimeout(resolve, 10));
        throw new Error('Something went wrong');
      };

      await expect(failingOperation()).rejects.toThrow('Something went wrong');
    });
  });

  describe('async with timeout', () => {
    it('should timeout async operations', async () => {
      const slowOperation = async (): Promise<string> => {
        await new Promise(resolve => setTimeout(resolve, 10000));
        return 'done';
      };

      const timeout = (ms: number): Promise<never> => {
        return new Promise((_, reject) =>
          setTimeout(() => reject(new Error('Timeout')), ms)
        );
      };

      await expect(
        Promise.race([slowOperation(), timeout(100)])
      ).rejects.toThrow('Timeout');
    });
  });

  describe('async gather operations', () => {
    it('should gather multiple async operations', async () => {
      const storage = new InMemoryStorage();

      const setKey = async (thread: string, key: string, value: string): Promise<string> => {
        await storage.setAsync(thread, key, value);
        return `${key}:${value}`;
      };

      const results = await Promise.all([
        setKey('thread1', 'key1', 'value1'),
        setKey('thread1', 'key2', 'value2'),
        setKey('thread1', 'key3', 'value3')
      ]);

      expect(results).toEqual(['key1:value1', 'key2:value2', 'key3:value3']);
    });
  });

  describe('async state race conditions', () => {
    it('should handle concurrent state updates correctly', async () => {
      const storage = new InMemoryStorage();

      // Set initial value
      await storage.setAsync('thread1', 'counter', 0);

      const increment = async () => {
        for (let i = 0; i < 10; i++) {
          const current = await storage.getAsync<number>('thread1', 'counter');
          await new Promise(resolve => setTimeout(resolve, 1)); // Small delay
          await storage.setAsync('thread1', 'counter', (current || 0) + 1);
        }
      };

      // Run multiple concurrent increments
      await Promise.all([increment(), increment(), increment()]);

      // Final value should be greater than 0 (exact value depends on race conditions)
      const final = await storage.getAsync<number>('thread1', 'counter');
      expect(final).toBeGreaterThan(0);
    });
  });

  describe('concurrent thread state access', () => {
    it('should handle concurrent access to thread state', async () => {
      const storage = new InMemoryStorage();

      const worker = async (workerId: number) => {
        const context = new AgentContext(`run${workerId}`, 'shared_thread', storage);

        for (let i = 0; i < 5; i++) {
          await context.setStateAsync(`worker${workerId}_key${i}`, `value${i}`);
          await new Promise(resolve => setTimeout(resolve, 1));
        }
      };

      // Run multiple workers concurrently on the same thread
      await Promise.all([worker(0), worker(1), worker(2), worker(3), worker(4)]);

      // Verify all keys exist
      const keys = await storage.getKeysAsync('shared_thread');
      expect(keys).toHaveLength(25); // 5 workers * 5 keys each
    });
  });

  describe('async cleanup', () => {
    it('should handle async cleanup operations', async () => {
      const storage = new InMemoryStorage();

      // Set some data
      await storage.setAsync('thread1', 'key1', 'value1');
      await storage.setAsync('thread2', 'key2', 'value2');

      // Delete
      await storage.deleteAsync('thread1', 'key1');
      await storage.deleteAsync('thread2', 'key2');

      // Verify cleanup
      expect(await storage.getAsync('thread1', 'key1')).toBeNull();
      expect(await storage.getAsync('thread2', 'key2')).toBeNull();
    });
  });
});
