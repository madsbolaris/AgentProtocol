/**
 * Tests for error classes
 */

import {
  AgentProtocolError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
  TimeoutError,
  NetworkError,
} from '../src/errors';

describe('Error classes', () => {
  describe('AgentProtocolError', () => {
    it('should create error with message', () => {
      const error = new AgentProtocolError('Test error');
      expect(error.message).toBe('Test error');
      expect(error.name).toBe('AgentProtocolError');
      expect(error.statusCode).toBeUndefined();
      expect(error.response).toBeUndefined();
    });

    it('should create error with status code', () => {
      const error = new AgentProtocolError('Test error', 500);
      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(500);
    });

    it('should create error with response data', () => {
      const response = { error: 'details' };
      const error = new AgentProtocolError('Test error', 500, response);
      expect(error.message).toBe('Test error');
      expect(error.statusCode).toBe(500);
      expect(error.response).toEqual(response);
    });

    it('should be instance of Error', () => {
      const error = new AgentProtocolError('Test');
      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AgentProtocolError);
    });
  });

  describe('AuthenticationError', () => {
    it('should create with default message', () => {
      const error = new AuthenticationError();
      expect(error.message).toBe('Authentication failed');
      expect(error.name).toBe('AuthenticationError');
      expect(error.statusCode).toBe(401);
    });

    it('should create with custom message', () => {
      const error = new AuthenticationError('Invalid API key');
      expect(error.message).toBe('Invalid API key');
      expect(error.statusCode).toBe(401);
    });

    it('should be instance of AgentProtocolError', () => {
      const error = new AuthenticationError();
      expect(error).toBeInstanceOf(AgentProtocolError);
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('NotFoundError', () => {
    it('should create with resource name', () => {
      const error = new NotFoundError('agent-123');
      expect(error.message).toBe('Resource not found: agent-123');
      expect(error.name).toBe('NotFoundError');
      expect(error.statusCode).toBe(404);
    });

    it('should be instance of AgentProtocolError', () => {
      const error = new NotFoundError('thread-456');
      expect(error).toBeInstanceOf(AgentProtocolError);
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('ValidationError', () => {
    it('should create with message only', () => {
      const error = new ValidationError('Invalid input');
      expect(error.message).toBe('Invalid input');
      expect(error.name).toBe('ValidationError');
      expect(error.statusCode).toBe(400);
      expect(error.errors).toBeUndefined();
    });

    it('should create with validation errors', () => {
      const errors = {
        name: ['Name is required'],
        email: ['Email is invalid', 'Email is required'],
      };
      const error = new ValidationError('Validation failed', errors);
      expect(error.message).toBe('Validation failed');
      expect(error.errors).toEqual(errors);
      expect(error.statusCode).toBe(400);
    });

    it('should be instance of AgentProtocolError', () => {
      const error = new ValidationError('Invalid');
      expect(error).toBeInstanceOf(AgentProtocolError);
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('RateLimitError', () => {
    it('should create with default message', () => {
      const error = new RateLimitError();
      expect(error.message).toBe('Rate limit exceeded');
      expect(error.name).toBe('RateLimitError');
      expect(error.statusCode).toBe(429);
      expect(error.retryAfter).toBeUndefined();
    });

    it('should create with custom message', () => {
      const error = new RateLimitError('Too many requests');
      expect(error.message).toBe('Too many requests');
      expect(error.statusCode).toBe(429);
    });

    it('should create with retry after time', () => {
      const error = new RateLimitError('Rate limit exceeded', 60);
      expect(error.message).toBe('Rate limit exceeded');
      expect(error.retryAfter).toBe(60);
    });

    it('should be instance of AgentProtocolError', () => {
      const error = new RateLimitError();
      expect(error).toBeInstanceOf(AgentProtocolError);
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('TimeoutError', () => {
    it('should create with default message', () => {
      const error = new TimeoutError();
      expect(error.message).toBe('Request timeout');
      expect(error.name).toBe('TimeoutError');
    });

    it('should create with custom message', () => {
      const error = new TimeoutError('Connection timed out');
      expect(error.message).toBe('Connection timed out');
    });

    it('should be instance of AgentProtocolError', () => {
      const error = new TimeoutError();
      expect(error).toBeInstanceOf(AgentProtocolError);
      expect(error).toBeInstanceOf(Error);
    });
  });

  describe('NetworkError', () => {
    it('should create with message only', () => {
      const error = new NetworkError('Network failure');
      expect(error.message).toBe('Network failure');
      expect(error.name).toBe('NetworkError');
      expect(error.cause).toBeUndefined();
    });

    it('should create with cause error', () => {
      const cause = new Error('Connection refused');
      const error = new NetworkError('Network failure', cause);
      expect(error.message).toBe('Network failure');
      expect(error.cause).toBe(cause);
    });

    it('should be instance of AgentProtocolError', () => {
      const error = new NetworkError('Network error');
      expect(error).toBeInstanceOf(AgentProtocolError);
      expect(error).toBeInstanceOf(Error);
    });
  });
});
