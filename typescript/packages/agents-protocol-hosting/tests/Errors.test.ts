import {
  AgentHostingError,
  ValidationError,
  TimeoutError,
  RateLimitError,
  LLMError
} from '../src/middleware/errors.js';

describe('Error Classes', () => {
  describe('AgentHostingError', () => {
    it('should create an AgentHostingError', () => {
      const error = new AgentHostingError('Test error');

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AgentHostingError);
      expect(error.message).toBe('Test error');
      expect(error.name).toBe('AgentHostingError');
    });

    it('should have correct prototype chain', () => {
      const error = new AgentHostingError('Test error');

      expect(error instanceof Error).toBe(true);
      expect(error instanceof AgentHostingError).toBe(true);
    });

    it('should support different messages', () => {
      const error1 = new AgentHostingError('Error 1');
      const error2 = new AgentHostingError('Error 2');

      expect(error1.message).toBe('Error 1');
      expect(error2.message).toBe('Error 2');
    });
  });

  describe('ValidationError', () => {
    it('should create a ValidationError with message only', () => {
      const error = new ValidationError('Validation failed');

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AgentHostingError);
      expect(error).toBeInstanceOf(ValidationError);
      expect(error.message).toBe('Validation failed');
      expect(error.name).toBe('ValidationError');
      expect(error.field).toBeUndefined();
      expect(error.value).toBeUndefined();
    });

    it('should create a ValidationError with field', () => {
      const error = new ValidationError('Invalid value', 'username');

      expect(error.message).toBe('Invalid value');
      expect(error.field).toBe('username');
      expect(error.value).toBeUndefined();
    });

    it('should create a ValidationError with field and value', () => {
      const error = new ValidationError('Invalid email', 'email', 'not-an-email');

      expect(error.message).toBe('Invalid email');
      expect(error.field).toBe('email');
      expect(error.value).toBe('not-an-email');
    });

    it('should support various value types', () => {
      const error1 = new ValidationError('Invalid number', 'age', 150);
      const error2 = new ValidationError('Invalid boolean', 'active', false);
      const error3 = new ValidationError('Invalid object', 'data', { key: 'value' });
      const error4 = new ValidationError('Invalid null', 'field', null);

      expect(error1.value).toBe(150);
      expect(error2.value).toBe(false);
      expect(error3.value).toEqual({ key: 'value' });
      expect(error4.value).toBeNull();
    });

    it('should be throwable and catchable', () => {
      expect(() => {
        throw new ValidationError('Test error', 'field', 'value');
      }).toThrow(ValidationError);

      try {
        throw new ValidationError('Test error', 'field', 'value');
      } catch (e) {
        expect(e).toBeInstanceOf(ValidationError);
        if (e instanceof ValidationError) {
          expect(e.field).toBe('field');
          expect(e.value).toBe('value');
        }
      }
    });
  });

  describe('TimeoutError', () => {
    it('should create a TimeoutError', () => {
      const error = new TimeoutError('Operation timed out');

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AgentHostingError);
      expect(error).toBeInstanceOf(TimeoutError);
      expect(error.message).toBe('Operation timed out');
      expect(error.name).toBe('TimeoutError');
    });

    it('should support different timeout messages', () => {
      const error1 = new TimeoutError('Function execution timed out after 5s');
      const error2 = new TimeoutError('LLM request timed out');

      expect(error1.message).toBe('Function execution timed out after 5s');
      expect(error2.message).toBe('LLM request timed out');
    });

    it('should be throwable and catchable', () => {
      expect(() => {
        throw new TimeoutError('Timeout');
      }).toThrow(TimeoutError);

      try {
        throw new TimeoutError('Timeout');
      } catch (e) {
        expect(e).toBeInstanceOf(TimeoutError);
      }
    });
  });

  describe('RateLimitError', () => {
    it('should create a RateLimitError', () => {
      const error = new RateLimitError('Rate limit exceeded');

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AgentHostingError);
      expect(error).toBeInstanceOf(RateLimitError);
      expect(error.message).toBe('Rate limit exceeded');
      expect(error.name).toBe('RateLimitError');
    });

    it('should support different rate limit messages', () => {
      const error1 = new RateLimitError('Too many requests per minute');
      const error2 = new RateLimitError('Global rate limit exceeded');
      const error3 = new RateLimitError('Per-thread rate limit exceeded');

      expect(error1.message).toBe('Too many requests per minute');
      expect(error2.message).toBe('Global rate limit exceeded');
      expect(error3.message).toBe('Per-thread rate limit exceeded');
    });

    it('should be throwable and catchable', () => {
      expect(() => {
        throw new RateLimitError('Rate limit');
      }).toThrow(RateLimitError);

      try {
        throw new RateLimitError('Rate limit');
      } catch (e) {
        expect(e).toBeInstanceOf(RateLimitError);
      }
    });
  });

  describe('LLMError', () => {
    it('should create an LLMError with message only', () => {
      const error = new LLMError('LLM API failed');

      expect(error).toBeInstanceOf(Error);
      expect(error).toBeInstanceOf(AgentHostingError);
      expect(error).toBeInstanceOf(LLMError);
      expect(error.message).toBe('LLM API failed');
      expect(error.name).toBe('LLMError');
      expect(error.statusCode).toBeUndefined();
      expect(error.retryable).toBeUndefined();
    });

    it('should create an LLMError with status code', () => {
      const error = new LLMError('Request failed', 500);

      expect(error.message).toBe('Request failed');
      expect(error.statusCode).toBe(500);
      expect(error.retryable).toBeUndefined();
    });

    it('should create an LLMError with retryable flag', () => {
      const error = new LLMError('Temporary failure', undefined, true);

      expect(error.message).toBe('Temporary failure');
      expect(error.statusCode).toBeUndefined();
      expect(error.retryable).toBe(true);
    });

    it('should create an LLMError with all parameters', () => {
      const error = new LLMError('Service unavailable', 503, true);

      expect(error.message).toBe('Service unavailable');
      expect(error.statusCode).toBe(503);
      expect(error.retryable).toBe(true);
    });

    it('should support non-retryable errors', () => {
      const error = new LLMError('Invalid API key', 401, false);

      expect(error.message).toBe('Invalid API key');
      expect(error.statusCode).toBe(401);
      expect(error.retryable).toBe(false);
    });

    it('should support different HTTP status codes', () => {
      const error400 = new LLMError('Bad request', 400);
      const error401 = new LLMError('Unauthorized', 401);
      const error429 = new LLMError('Too many requests', 429);
      const error500 = new LLMError('Internal server error', 500);
      const error503 = new LLMError('Service unavailable', 503);

      expect(error400.statusCode).toBe(400);
      expect(error401.statusCode).toBe(401);
      expect(error429.statusCode).toBe(429);
      expect(error500.statusCode).toBe(500);
      expect(error503.statusCode).toBe(503);
    });

    it('should be throwable and catchable', () => {
      expect(() => {
        throw new LLMError('Error', 500, true);
      }).toThrow(LLMError);

      try {
        throw new LLMError('Error', 500, true);
      } catch (e) {
        expect(e).toBeInstanceOf(LLMError);
        if (e instanceof LLMError) {
          expect(e.statusCode).toBe(500);
          expect(e.retryable).toBe(true);
        }
      }
    });
  });

  describe('Error Inheritance', () => {
    it('should maintain proper inheritance chain', () => {
      const agentError = new AgentHostingError('Base error');
      const validationError = new ValidationError('Validation error');
      const timeoutError = new TimeoutError('Timeout error');
      const rateLimitError = new RateLimitError('Rate limit error');
      const llmError = new LLMError('LLM error');

      // All errors should be instances of Error
      expect(agentError instanceof Error).toBe(true);
      expect(validationError instanceof Error).toBe(true);
      expect(timeoutError instanceof Error).toBe(true);
      expect(rateLimitError instanceof Error).toBe(true);
      expect(llmError instanceof Error).toBe(true);

      // All errors should be instances of AgentHostingError
      expect(agentError instanceof AgentHostingError).toBe(true);
      expect(validationError instanceof AgentHostingError).toBe(true);
      expect(timeoutError instanceof AgentHostingError).toBe(true);
      expect(rateLimitError instanceof AgentHostingError).toBe(true);
      expect(llmError instanceof AgentHostingError).toBe(true);

      // Each error should be instance of its own type
      expect(validationError instanceof ValidationError).toBe(true);
      expect(timeoutError instanceof TimeoutError).toBe(true);
      expect(rateLimitError instanceof RateLimitError).toBe(true);
      expect(llmError instanceof LLMError).toBe(true);

      // Cross-type checks should fail
      expect(validationError instanceof TimeoutError).toBe(false);
      expect(timeoutError instanceof RateLimitError).toBe(false);
      expect(rateLimitError instanceof LLMError).toBe(false);
      expect(llmError instanceof ValidationError).toBe(false);
    });

    it('should allow catching by base type', () => {
      const errors = [
        new ValidationError('Error 1'),
        new TimeoutError('Error 2'),
        new RateLimitError('Error 3'),
        new LLMError('Error 4')
      ];

      errors.forEach(error => {
        try {
          throw error;
        } catch (e) {
          expect(e instanceof AgentHostingError).toBe(true);
        }
      });
    });

    it('should allow catching by specific type', () => {
      try {
        throw new ValidationError('Invalid input', 'field', 'value');
      } catch (e) {
        if (e instanceof ValidationError) {
          expect(e.field).toBe('field');
          expect(e.value).toBe('value');
        } else {
          fail('Should have caught ValidationError');
        }
      }

      try {
        throw new LLMError('API error', 500, true);
      } catch (e) {
        if (e instanceof LLMError) {
          expect(e.statusCode).toBe(500);
          expect(e.retryable).toBe(true);
        } else {
          fail('Should have caught LLMError');
        }
      }
    });
  });

  describe('Error Usage Scenarios', () => {
    it('should support error with stack trace', () => {
      const error = new ValidationError('Test error');
      expect(error.stack).toBeDefined();
      expect(error.stack).toContain('ValidationError');
    });

    it('should support error serialization', () => {
      const error = new ValidationError('Invalid email', 'email', 'not-valid');

      const serialized = {
        name: error.name,
        message: error.message,
        field: error.field,
        value: error.value
      };

      expect(serialized).toEqual({
        name: 'ValidationError',
        message: 'Invalid email',
        field: 'email',
        value: 'not-valid'
      });
    });

    it('should support error in promise rejection', async () => {
      const promise = Promise.reject(new TimeoutError('Timeout'));

      await expect(promise).rejects.toThrow(TimeoutError);
      await expect(promise).rejects.toThrow('Timeout');
    });

    it('should support error chaining', () => {
      const originalError = new Error('Original error');
      const wrappedError = new LLMError(`LLM failed: ${originalError.message}`, 500, true);

      expect(wrappedError.message).toContain('Original error');
    });
  });
});
