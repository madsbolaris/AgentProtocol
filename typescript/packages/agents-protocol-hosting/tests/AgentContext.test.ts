import { AgentContext } from '../src/core/AgentContext.js';
import { InMemoryStorage } from '../src/storage/InMemoryStorage.js';
import { IStorage } from '../src/storage/IStorage.js';

describe('AgentContext', () => {
  let storage: IStorage;
  let context: AgentContext;

  beforeEach(() => {
    storage = new InMemoryStorage();
    context = new AgentContext('run-123', 'thread-456', storage);
  });

  describe('constructor', () => {
    it('should create context with runId and threadId', () => {
      expect(context.runId).toBe('run-123');
      expect(context.threadId).toBe('thread-456');
    });
  });

  describe('state management', () => {
    describe('setStateAsync', () => {
      it('should store state value', async () => {
        await context.setStateAsync('key1', { value: 'test' });
        const result = await context.getStateAsync('key1');
        expect(result).toEqual({ value: 'test' });
      });

      it('should store different types of values', async () => {
        await context.setStateAsync('string', 'hello');
        await context.setStateAsync('number', 42);
        await context.setStateAsync('boolean', true);
        await context.setStateAsync('object', { a: 1, b: 2 });
        await context.setStateAsync('array', [1, 2, 3]);

        expect(await context.getStateAsync('string')).toBe('hello');
        expect(await context.getStateAsync('number')).toBe(42);
        expect(await context.getStateAsync('boolean')).toBe(true);
        expect(await context.getStateAsync('object')).toEqual({ a: 1, b: 2 });
        expect(await context.getStateAsync('array')).toEqual([1, 2, 3]);
      });

      it('should overwrite existing state', async () => {
        await context.setStateAsync('key1', 'value1');
        await context.setStateAsync('key1', 'value2');
        const result = await context.getStateAsync('key1');
        expect(result).toBe('value2');
      });

      it('should handle cancellation', async () => {
        const controller = new AbortController();
        controller.abort();

        await expect(
          context.setStateAsync('key', 'value', controller.signal)
        ).rejects.toThrow('Operation was cancelled');
      });
    });

    describe('getStateAsync', () => {
      it('should return null for non-existent key', async () => {
        const result = await context.getStateAsync('nonexistent');
        expect(result).toBeNull();
      });

      it('should retrieve stored state', async () => {
        await context.setStateAsync('key1', 'value1');
        const result = await context.getStateAsync('key1');
        expect(result).toBe('value1');
      });

      it('should support generic type parameter', async () => {
        interface UserPrefs {
          theme: string;
          language: string;
        }

        await context.setStateAsync<UserPrefs>('prefs', {
          theme: 'dark',
          language: 'en'
        });

        const result = await context.getStateAsync<UserPrefs>('prefs');
        expect(result).toEqual({ theme: 'dark', language: 'en' });
      });

      it('should handle cancellation', async () => {
        const controller = new AbortController();
        controller.abort();

        await expect(
          context.getStateAsync('key', controller.signal)
        ).rejects.toThrow('Operation was cancelled');
      });
    });

    describe('deleteStateAsync', () => {
      it('should delete existing state', async () => {
        await context.setStateAsync('key1', 'value1');
        await context.deleteStateAsync('key1');
        const result = await context.getStateAsync('key1');
        expect(result).toBeNull();
      });

      it('should not throw when deleting non-existent key', async () => {
        await expect(
          context.deleteStateAsync('nonexistent')
        ).resolves.not.toThrow();
      });

      it('should handle cancellation', async () => {
        const controller = new AbortController();
        controller.abort();

        await expect(
          context.deleteStateAsync('key', controller.signal)
        ).rejects.toThrow('Operation was cancelled');
      });
    });

    describe('getStateKeysAsync', () => {
      it('should return empty array when no state exists', async () => {
        const keys = await context.getStateKeysAsync();
        expect(keys).toEqual([]);
      });

      it('should return all state keys', async () => {
        await context.setStateAsync('key1', 'value1');
        await context.setStateAsync('key2', 'value2');
        await context.setStateAsync('key3', 'value3');

        const keys = await context.getStateKeysAsync();
        expect(keys).toHaveLength(3);
        expect(keys).toContain('key1');
        expect(keys).toContain('key2');
        expect(keys).toContain('key3');
      });

      it('should not include deleted keys', async () => {
        await context.setStateAsync('key1', 'value1');
        await context.setStateAsync('key2', 'value2');
        await context.deleteStateAsync('key1');

        const keys = await context.getStateKeysAsync();
        expect(keys).toHaveLength(1);
        expect(keys).toContain('key2');
        expect(keys).not.toContain('key1');
      });

      it('should handle cancellation', async () => {
        const controller = new AbortController();
        controller.abort();

        await expect(
          context.getStateKeysAsync(controller.signal)
        ).rejects.toThrow('Operation was cancelled');
      });
    });
  });

  describe('respondAsync', () => {
    it('should accept string content', async () => {
      await expect(
        context.respondAsync('Hello, world!')
      ).resolves.not.toThrow();
    });

    it('should accept AIContent object', async () => {
      await expect(
        context.respondAsync({ kind: 'text', text: 'Hello!' })
      ).resolves.not.toThrow();
    });

    it('should call response callback with string content', async () => {
      const responseCallback = jest.fn().mockResolvedValue(undefined);
      const contextWithCallback = new AgentContext(
        'run-123',
        'thread-456',
        storage,
        responseCallback
      );

      await contextWithCallback.respondAsync('Hello, world!');

      expect(responseCallback).toHaveBeenCalledWith('Hello, world!');
      expect(responseCallback).toHaveBeenCalledTimes(1);
    });

    it('should call response callback with AIContent', async () => {
      const responseCallback = jest.fn().mockResolvedValue(undefined);
      const contextWithCallback = new AgentContext(
        'run-123',
        'thread-456',
        storage,
        responseCallback
      );

      const content = { kind: 'text' as const, text: 'Hello!' };
      await contextWithCallback.respondAsync(content);

      expect(responseCallback).toHaveBeenCalledWith(content);
      expect(responseCallback).toHaveBeenCalledTimes(1);
    });

    it('should handle cancellation', async () => {
      const controller = new AbortController();
      controller.abort();

      await expect(
        context.respondAsync('Hello', controller.signal)
      ).rejects.toThrow('Operation was cancelled');
    });
  });

  describe('streamAsync', () => {
    it('should stream tokens', async () => {
      await expect(
        context.streamAsync('token')
      ).resolves.not.toThrow();
    });

    it('should call stream callback', async () => {
      const streamCallback = jest.fn().mockResolvedValue(undefined);
      const contextWithCallback = new AgentContext(
        'run-123',
        'thread-456',
        storage,
        undefined,
        streamCallback
      );

      await contextWithCallback.streamAsync('token');

      expect(streamCallback).toHaveBeenCalledWith('token');
      expect(streamCallback).toHaveBeenCalledTimes(1);
    });

    it('should call stream callback multiple times', async () => {
      const streamCallback = jest.fn().mockResolvedValue(undefined);
      const contextWithCallback = new AgentContext(
        'run-123',
        'thread-456',
        storage,
        undefined,
        streamCallback
      );

      await contextWithCallback.streamAsync('token1');
      await contextWithCallback.streamAsync('token2');
      await contextWithCallback.streamAsync('token3');

      expect(streamCallback).toHaveBeenCalledTimes(3);
      expect(streamCallback).toHaveBeenNthCalledWith(1, 'token1');
      expect(streamCallback).toHaveBeenNthCalledWith(2, 'token2');
      expect(streamCallback).toHaveBeenNthCalledWith(3, 'token3');
    });

    it('should handle cancellation', async () => {
      const controller = new AbortController();
      controller.abort();

      await expect(
        context.streamAsync('token', controller.signal)
      ).rejects.toThrow('Operation was cancelled');
    });
  });

  describe('logAsync', () => {
    it('should log messages at different levels', async () => {
      await expect(context.logAsync('Debug message', 'debug')).resolves.not.toThrow();
      await expect(context.logAsync('Info message', 'info')).resolves.not.toThrow();
      await expect(context.logAsync('Warning message', 'warn')).resolves.not.toThrow();
      await expect(context.logAsync('Error message', 'error')).resolves.not.toThrow();
    });

    it('should use default log level', async () => {
      await expect(context.logAsync('Default level message')).resolves.not.toThrow();
    });

    it('should call log callback', async () => {
      const logCallback = jest.fn().mockResolvedValue(undefined);
      const contextWithCallback = new AgentContext(
        'run-123',
        'thread-456',
        storage,
        undefined,
        undefined,
        logCallback
      );

      await contextWithCallback.logAsync('Test message', 'info');

      expect(logCallback).toHaveBeenCalledWith('Test message', 'info');
      expect(logCallback).toHaveBeenCalledTimes(1);
    });

    it('should call log callback with different levels', async () => {
      const logCallback = jest.fn().mockResolvedValue(undefined);
      const contextWithCallback = new AgentContext(
        'run-123',
        'thread-456',
        storage,
        undefined,
        undefined,
        logCallback
      );

      await contextWithCallback.logAsync('Debug', 'debug');
      await contextWithCallback.logAsync('Info', 'info');
      await contextWithCallback.logAsync('Warn', 'warn');
      await contextWithCallback.logAsync('Error', 'error');

      expect(logCallback).toHaveBeenCalledTimes(4);
      expect(logCallback).toHaveBeenNthCalledWith(1, 'Debug', 'debug');
      expect(logCallback).toHaveBeenNthCalledWith(2, 'Info', 'info');
      expect(logCallback).toHaveBeenNthCalledWith(3, 'Warn', 'warn');
      expect(logCallback).toHaveBeenNthCalledWith(4, 'Error', 'error');
    });

    it('should handle cancellation', async () => {
      const controller = new AbortController();
      controller.abort();

      await expect(
        context.logAsync('Message', 'info', controller.signal)
      ).rejects.toThrow('Operation was cancelled');
    });
  });

  describe('pauseForApprovalAsync', () => {
    it('should pause for approval', async () => {
      await expect(
        context.pauseForApprovalAsync('Approve action')
      ).resolves.not.toThrow();
    });

    it('should accept metadata', async () => {
      await expect(
        context.pauseForApprovalAsync('Approve action', { count: 100 })
      ).resolves.not.toThrow();
    });

    it('should handle cancellation', async () => {
      const controller = new AbortController();
      controller.abort();

      await expect(
        context.pauseForApprovalAsync('Approve', undefined, controller.signal)
      ).rejects.toThrow('Operation was cancelled');
    });
  });

  describe('recordMetric', () => {
    it('should record metric without tags', () => {
      expect(() => {
        context.recordMetric('metric_name', 42);
      }).not.toThrow();
    });

    it('should record metric with tags', () => {
      expect(() => {
        context.recordMetric('metric_name', 42, { tag1: 'value1', tag2: 'value2' });
      }).not.toThrow();
    });
  });

  describe('addTraceAttribute', () => {
    it('should add trace attributes of different types', () => {
      expect(() => {
        context.addTraceAttribute('string_attr', 'value');
        context.addTraceAttribute('number_attr', 42);
        context.addTraceAttribute('boolean_attr', true);
      }).not.toThrow();
    });
  });

  describe('getTraceId', () => {
    it('should return a trace ID', () => {
      const traceId = context.getTraceId();
      expect(typeof traceId).toBe('string');
      expect(traceId.length).toBeGreaterThan(0);
    });

    it('should return consistent trace ID', () => {
      const traceId1 = context.getTraceId();
      const traceId2 = context.getTraceId();
      expect(traceId1).toBe(traceId2);
    });
  });
});
