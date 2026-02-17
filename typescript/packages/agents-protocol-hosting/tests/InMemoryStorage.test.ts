import { InMemoryStorage } from '../src/storage/InMemoryStorage.js';

describe('InMemoryStorage', () => {
  let storage: InMemoryStorage;

  beforeEach(() => {
    storage = new InMemoryStorage();
  });

  describe('setAsync', () => {
    it('should store a value', async () => {
      await storage.setAsync('thread-1', 'key1', 'value1');
      const result = await storage.getAsync('thread-1', 'key1');
      expect(result).toBe('value1');
    });

    it('should store different types', async () => {
      await storage.setAsync('thread-1', 'string', 'hello');
      await storage.setAsync('thread-1', 'number', 42);
      await storage.setAsync('thread-1', 'boolean', true);
      await storage.setAsync('thread-1', 'object', { a: 1 });
      await storage.setAsync('thread-1', 'array', [1, 2, 3]);

      expect(await storage.getAsync('thread-1', 'string')).toBe('hello');
      expect(await storage.getAsync('thread-1', 'number')).toBe(42);
      expect(await storage.getAsync('thread-1', 'boolean')).toBe(true);
      expect(await storage.getAsync('thread-1', 'object')).toEqual({ a: 1 });
      expect(await storage.getAsync('thread-1', 'array')).toEqual([1, 2, 3]);
    });

    it('should isolate values by threadId', async () => {
      await storage.setAsync('thread-1', 'key', 'value1');
      await storage.setAsync('thread-2', 'key', 'value2');

      expect(await storage.getAsync('thread-1', 'key')).toBe('value1');
      expect(await storage.getAsync('thread-2', 'key')).toBe('value2');
    });

    it('should overwrite existing values', async () => {
      await storage.setAsync('thread-1', 'key', 'value1');
      await storage.setAsync('thread-1', 'key', 'value2');

      expect(await storage.getAsync('thread-1', 'key')).toBe('value2');
    });
  });

  describe('getAsync', () => {
    it('should return null for non-existent key', async () => {
      const result = await storage.getAsync('thread-1', 'nonexistent');
      expect(result).toBeNull();
    });

    it('should return null for non-existent thread', async () => {
      const result = await storage.getAsync('nonexistent-thread', 'key');
      expect(result).toBeNull();
    });

    it('should retrieve stored values', async () => {
      await storage.setAsync('thread-1', 'key', 'value');
      const result = await storage.getAsync('thread-1', 'key');
      expect(result).toBe('value');
    });
  });

  describe('deleteAsync', () => {
    it('should delete existing key', async () => {
      await storage.setAsync('thread-1', 'key', 'value');
      await storage.deleteAsync('thread-1', 'key');
      const result = await storage.getAsync('thread-1', 'key');
      expect(result).toBeNull();
    });

    it('should not throw for non-existent key', async () => {
      await expect(
        storage.deleteAsync('thread-1', 'nonexistent')
      ).resolves.not.toThrow();
    });

    it('should not affect other threads', async () => {
      await storage.setAsync('thread-1', 'key', 'value1');
      await storage.setAsync('thread-2', 'key', 'value2');

      await storage.deleteAsync('thread-1', 'key');

      expect(await storage.getAsync('thread-1', 'key')).toBeNull();
      expect(await storage.getAsync('thread-2', 'key')).toBe('value2');
    });
  });

  describe('getKeysAsync', () => {
    it('should return empty array for new thread', async () => {
      const keys = await storage.getKeysAsync('thread-1');
      expect(keys).toEqual([]);
    });

    it('should return all keys for a thread', async () => {
      await storage.setAsync('thread-1', 'key1', 'value1');
      await storage.setAsync('thread-1', 'key2', 'value2');
      await storage.setAsync('thread-1', 'key3', 'value3');

      const keys = await storage.getKeysAsync('thread-1');
      expect(keys).toHaveLength(3);
      expect(keys).toContain('key1');
      expect(keys).toContain('key2');
      expect(keys).toContain('key3');
    });

    it('should not include deleted keys', async () => {
      await storage.setAsync('thread-1', 'key1', 'value1');
      await storage.setAsync('thread-1', 'key2', 'value2');
      await storage.deleteAsync('thread-1', 'key1');

      const keys = await storage.getKeysAsync('thread-1');
      expect(keys).toHaveLength(1);
      expect(keys).toContain('key2');
    });

    it('should isolate keys by thread', async () => {
      await storage.setAsync('thread-1', 'key1', 'value1');
      await storage.setAsync('thread-2', 'key2', 'value2');

      const keys1 = await storage.getKeysAsync('thread-1');
      const keys2 = await storage.getKeysAsync('thread-2');

      expect(keys1).toEqual(['key1']);
      expect(keys2).toEqual(['key2']);
    });
  });

  describe('concurrent operations', () => {
    it('should handle concurrent writes', async () => {
      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(storage.setAsync('thread-1', `key${i}`, `value${i}`));
      }

      await Promise.all(promises);

      const keys = await storage.getKeysAsync('thread-1');
      expect(keys).toHaveLength(100);
    });

    it('should handle concurrent reads', async () => {
      await storage.setAsync('thread-1', 'key', 'value');

      const promises = [];
      for (let i = 0; i < 100; i++) {
        promises.push(storage.getAsync('thread-1', 'key'));
      }

      const results = await Promise.all(promises);
      results.forEach(result => {
        expect(result).toBe('value');
      });
    });
  });
});
