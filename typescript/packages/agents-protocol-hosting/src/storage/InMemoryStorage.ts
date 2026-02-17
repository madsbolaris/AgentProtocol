import { IStorage } from './IStorage.js';

/**
 * In-memory storage implementation.
 * Data is lost when the process restarts.
 * Use only for development or testing.
 */
export class InMemoryStorage implements IStorage {
  private storage: Map<string, Map<string, unknown>> = new Map();

  /**
   * Creates a new in-memory storage instance.
   */
  constructor() {}

  async getAsync<T>(threadId: string, key: string): Promise<T | null> {
    const threadStorage = this.storage.get(threadId);
    if (!threadStorage) {
      return null;
    }

    const value = threadStorage.get(key);
    return value !== undefined ? (value as T) : null;
  }

  async setAsync<T>(threadId: string, key: string, value: T): Promise<void> {
    let threadStorage = this.storage.get(threadId);
    if (!threadStorage) {
      threadStorage = new Map<string, unknown>();
      this.storage.set(threadId, threadStorage);
    }

    threadStorage.set(key, value);
  }

  async deleteAsync(threadId: string, key: string): Promise<void> {
    const threadStorage = this.storage.get(threadId);
    if (threadStorage) {
      threadStorage.delete(key);
    }
  }

  async getKeysAsync(threadId: string): Promise<string[]> {
    const threadStorage = this.storage.get(threadId);
    if (!threadStorage) {
      return [];
    }

    return Array.from(threadStorage.keys());
  }

  async checkHealth(): Promise<boolean> {
    return true;
  }
}
