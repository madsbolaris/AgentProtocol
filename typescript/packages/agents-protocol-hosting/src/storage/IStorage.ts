/**
 * Interface for persistent state storage.
 *
 * Implementations must be thread-safe and support the configured
 * consistency model.
 */
export interface IStorage {
  /**
   * Gets a value from storage.
   *
   * @param threadId - The thread ID
   * @param key - The state key
   * @returns The value or null if not found
   */
  getAsync<T>(threadId: string, key: string): Promise<T | null>;

  /**
   * Sets a value in storage.
   *
   * @param threadId - The thread ID
   * @param key - The state key
   * @param value - The value (must be JSON serializable)
   */
  setAsync<T>(threadId: string, key: string, value: T): Promise<void>;

  /**
   * Deletes a value from storage.
   *
   * @param threadId - The thread ID
   * @param key - The state key
   */
  deleteAsync(threadId: string, key: string): Promise<void>;

  /**
   * Gets all keys for a thread.
   *
   * @param threadId - The thread ID
   * @returns Array of keys
   */
  getKeysAsync(threadId: string): Promise<string[]>;

  /**
   * Checks if the storage is healthy.
   *
   * @returns true if healthy, false otherwise
   */
  checkHealth(): Promise<boolean>;
}

/**
 * Configuration for PostgreSQL storage.
 */
export interface PostgresStorageConfig {
  /**
   * Database connection string.
   */
  connectionString: string;

  /**
   * Connection pool configuration.
   */
  pool?: {
    min: number;
    max: number;
    idleTimeoutMillis?: number;
  };

  /**
   * Consistency model for distributed systems.
   *
   * - 'strong': Reads always return latest write
   * - 'eventual': Reads may return stale data
   * - 'causal': Reads respect causal ordering
   *
   * @default 'strong'
   */
  consistency?: 'strong' | 'eventual' | 'causal';

  /**
   * Conflict resolution strategy.
   *
   * - 'last-write-wins': Latest write wins on conflict
   * - 'first-write-wins': First write wins on conflict
   *
   * @default 'last-write-wins'
   */
  conflictResolution?: 'last-write-wins' | 'first-write-wins';
}
