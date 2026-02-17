import { AIContent } from './types.js';

/**
 * Context for agent turn processing with state management and streaming.
 */
export interface IAgentContext {
  /**
   * Gets the current run ID.
   */
  readonly runId: string;

  /**
   * Gets the current thread ID.
   */
  readonly threadId: string;

  /**
   * Sends a response message to the user.
   *
   * @param content - The content to send (string or AIContent)
   * @param cancellationToken - Optional abort signal
   *
   * @example
   * ```typescript
   * await ctx.respondAsync('Hello, user!');
   * ```
   */
  respondAsync(content: string | AIContent, cancellationToken?: AbortSignal): Promise<void>;

  /**
   * Streams a token to the user (only in streaming mode).
   *
   * @param token - The token text to stream
   * @param cancellationToken - Optional abort signal
   *
   * @example
   * ```typescript
   * for (const token of tokens) {
   *   await ctx.streamAsync(token);
   * }
   * ```
   */
  streamAsync(token: string, cancellationToken?: AbortSignal): Promise<void>;

  /**
   * Logs a message (visible to debugging/observability, not sent to user).
   *
   * @param message - The message to log
   * @param level - Log level (debug, info, warn, error)
   * @param cancellationToken - Optional abort signal
   *
   * @example
   * ```typescript
   * await ctx.logAsync(`Processing request for user ${userId}`, 'info');
   * await ctx.logAsync(`Unexpected value: ${value}`, 'warn');
   * ```
   */
  logAsync(
    message: string,
    level?: 'debug' | 'info' | 'warn' | 'error',
    cancellationToken?: AbortSignal
  ): Promise<void>;

  /**
   * Gets state value for the current thread.
   *
   * @param key - State key
   * @param cancellationToken - Optional abort signal
   * @returns The state value or null if not found
   *
   * @example
   * ```typescript
   * const userPrefs = await ctx.getStateAsync<UserPreferences>('preferences');
   * if (userPrefs) {
   *   console.log(`User language: ${userPrefs.language}`);
   * }
   * ```
   */
  getStateAsync<T>(key: string, cancellationToken?: AbortSignal): Promise<T | null>;

  /**
   * Sets state value for the current thread.
   *
   * State is persisted according to the configured storage backend.
   * In distributed systems, uses the configured consistency model.
   *
   * @param key - State key
   * @param value - State value (must be JSON serializable)
   * @param cancellationToken - Optional abort signal
   *
   * @example
   * ```typescript
   * await ctx.setStateAsync('preferences', {
   *   language: 'en',
   *   theme: 'dark'
   * });
   * ```
   */
  setStateAsync<T>(key: string, value: T, cancellationToken?: AbortSignal): Promise<void>;

  /**
   * Deletes state value for the current thread.
   *
   * @param key - State key
   * @param cancellationToken - Optional abort signal
   *
   * @example
   * ```typescript
   * await ctx.deleteStateAsync('temporary_data');
   * ```
   */
  deleteStateAsync(key: string, cancellationToken?: AbortSignal): Promise<void>;

  /**
   * Gets all state keys for the current thread.
   *
   * @param cancellationToken - Optional abort signal
   * @returns Array of state keys
   *
   * @example
   * ```typescript
   * const keys = await ctx.getStateKeysAsync();
   * console.log(`Stored keys: ${keys.join(', ')}`);
   * ```
   */
  getStateKeysAsync(cancellationToken?: AbortSignal): Promise<string[]>;

  /**
   * Pauses the run and waits for approval before continuing.
   *
   * This is useful for actions that require human approval (e.g., financial transactions,
   * data deletion, external API calls).
   *
   * @param summary - Summary of what needs approval
   * @param metadata - Optional metadata about the approval request
   * @param cancellationToken - Optional abort signal
   *
   * @example
   * ```typescript
   * await ctx.pauseForApprovalAsync(
   *   'Delete 100 files from storage',
   *   { count: 100, location: 's3://bucket/path' }
   * );
   * ```
   */
  pauseForApprovalAsync(
    summary: string,
    metadata?: Record<string, unknown>,
    cancellationToken?: AbortSignal
  ): Promise<void>;

  /**
   * Records a custom metric for observability.
   *
   * @param name - Metric name
   * @param value - Metric value
   * @param tags - Optional tags for filtering/grouping
   *
   * @example
   * ```typescript
   * ctx.recordMetric('function_calls', 1, { function: 'get_weather' });
   * ctx.recordMetric('response_time_ms', 150);
   * ```
   */
  recordMetric(name: string, value: number, tags?: Record<string, string>): void;

  /**
   * Adds an attribute to the current trace span.
   *
   * @param key - Attribute key
   * @param value - Attribute value
   *
   * @example
   * ```typescript
   * ctx.addTraceAttribute('user_id', userId);
   * ctx.addTraceAttribute('intent', 'weather_query');
   * ```
   */
  addTraceAttribute(key: string, value: string | number | boolean): void;

  /**
   * Gets the trace ID for correlation across services.
   *
   * @returns The trace ID
   *
   * @example
   * ```typescript
   * const traceId = ctx.getTraceId();
   * console.log(`Processing message: ${traceId}`);
   * ```
   */
  getTraceId(): string;
}
