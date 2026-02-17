/**
 * Error classes for the Agent Protocol client
 */

export class AgentProtocolError extends Error {
  constructor(
    message: string,
    public readonly statusCode?: number,
    public readonly response?: unknown
  ) {
    super(message);
    this.name = 'AgentProtocolError';
  }
}

export class AuthenticationError extends AgentProtocolError {
  constructor(message: string = 'Authentication failed') {
    super(message, 401);
    this.name = 'AuthenticationError';
  }
}

export class NotFoundError extends AgentProtocolError {
  constructor(resource: string) {
    super(`Resource not found: ${resource}`, 404);
    this.name = 'NotFoundError';
  }
}

export class ValidationError extends AgentProtocolError {
  constructor(
    message: string,
    public readonly errors?: Record<string, string[]>
  ) {
    super(message, 400);
    this.name = 'ValidationError';
  }
}

export class RateLimitError extends AgentProtocolError {
  constructor(
    message: string = 'Rate limit exceeded',
    public readonly retryAfter?: number
  ) {
    super(message, 429);
    this.name = 'RateLimitError';
  }
}

export class TimeoutError extends AgentProtocolError {
  constructor(message: string = 'Request timeout') {
    super(message);
    this.name = 'TimeoutError';
  }
}

export class NetworkError extends AgentProtocolError {
  constructor(message: string, public readonly cause?: Error) {
    super(message);
    this.name = 'NetworkError';
  }
}
