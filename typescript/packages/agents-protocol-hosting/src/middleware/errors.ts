/**
 * Custom error types for the Agents Hosting SDK.
 */

/**
 * Base error for all SDK errors.
 */
export class AgentHostingError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AgentHostingError';
  }
}

/**
 * Error thrown when validation fails.
 */
export class ValidationError extends AgentHostingError {
  constructor(
    message: string,
    public readonly field?: string,
    public readonly value?: unknown
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

/**
 * Error thrown when a function execution times out.
 */
export class TimeoutError extends AgentHostingError {
  constructor(message: string) {
    super(message);
    this.name = 'TimeoutError';
  }
}

/**
 * Error thrown when rate limit is exceeded.
 */
export class RateLimitError extends AgentHostingError {
  constructor(message: string) {
    super(message);
    this.name = 'RateLimitError';
  }
}

/**
 * Error thrown when LLM API call fails.
 */
export class LLMError extends AgentHostingError {
  constructor(
    message: string,
    public readonly statusCode?: number,
    public readonly retryable?: boolean
  ) {
    super(message);
    this.name = 'LLMError';
  }
}
