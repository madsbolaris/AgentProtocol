/**
 * Tests for BaseClient
 */

import { BaseClient } from '../src/client/base-client';
import {
  AgentProtocolError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
} from '../src/errors';

// Mock fetch globally for testing
global.fetch = jest.fn();

// Create a test class that extends BaseClient to test protected methods
class TestClient extends BaseClient {
  public testGet<T>(path: string, options?: any): Promise<T> {
    return this.get(path, options);
  }

  public testPost<T>(path: string, body?: unknown, options?: any): Promise<T> {
    return this.post(path, body, options);
  }

  public testPut<T>(path: string, body?: unknown, options?: any): Promise<T> {
    return this.put(path, body, options);
  }

  public testPatch<T>(path: string, body?: unknown, options?: any): Promise<T> {
    return this.patch(path, body, options);
  }

  public testDelete<T>(path: string, options?: any): Promise<T> {
    return this.delete(path, options);
  }
}

describe('BaseClient', () => {
  let client: TestClient;

  beforeEach(() => {
    client = new TestClient({
      baseUrl: 'http://localhost:5000',
      authToken: 'test-token',
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with config', () => {
      const client = new TestClient({
        baseUrl: 'http://localhost:5000/',
        authToken: 'test-token',
        timeout: 60000,
        maxRetries: 5,
        debug: true,
        headers: { 'X-Custom': 'value' },
      });

      expect(client).toBeDefined();
    });

    it('should remove trailing slash from baseUrl', () => {
      const client = new TestClient({
        baseUrl: 'http://localhost:5000/',
      });

      expect((client as any).baseUrl).toBe('http://localhost:5000');
    });

    it('should set default timeout', () => {
      const client = new TestClient({
        baseUrl: 'http://localhost:5000',
      });

      expect((client as any).defaultTimeout).toBe(30000);
    });

    it('should set default maxRetries', () => {
      const client = new TestClient({
        baseUrl: 'http://localhost:5000',
      });

      expect((client as any).maxRetries).toBe(3);
    });

    it('should add authorization header when authToken provided', () => {
      const client = new TestClient({
        baseUrl: 'http://localhost:5000',
        authToken: 'my-token',
      });

      expect((client as any).headers['Authorization']).toBe('Bearer my-token');
    });

    it('should merge custom headers', () => {
      const client = new TestClient({
        baseUrl: 'http://localhost:5000',
        headers: { 'X-Custom': 'value' },
      });

      expect((client as any).headers['X-Custom']).toBe('value');
      expect((client as any).headers['Content-Type']).toBe('application/json');
    });
  });

  describe('request method', () => {
    it('should make successful GET request', async () => {
      const mockData = { id: '123', name: 'Test' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockData,
      });

      const result = await client.testGet('/test');

      expect(result).toEqual(mockData);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            Authorization: 'Bearer test-token',
          }),
        })
      );
    });

    it('should handle 204 No Content response', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      const result = await client.testDelete('/test');

      expect(result).toBeUndefined();
    });

    it('should retry on failure', async () => {
      (global.fetch as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({ success: true }),
        });

      const result = await client.testGet('/test');

      expect(result).toEqual({ success: true });
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('should not retry on AuthenticationError', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: 'Unauthorized' }),
      });

      await expect(client.testGet('/test')).rejects.toThrow(AuthenticationError);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry on NotFoundError', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ message: 'Not found' }),
      });

      await expect(client.testGet('/test')).rejects.toThrow(NotFoundError);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry on ValidationError', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ message: 'Validation failed' }),
      });

      await expect(client.testGet('/test')).rejects.toThrow(ValidationError);
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry when signal is aborted', async () => {
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('Aborted'));
      });

      await expect(
        client.testGet('/test', { signal: abortController.signal })
      ).rejects.toThrow();

      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should exhaust all retries and throw last error', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));

      await expect(client.testGet('/test', { maxRetries: 2 })).rejects.toThrow(
        'Network error'
      );

      expect(global.fetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    });

    it('should handle timeout', async () => {
      (global.fetch as jest.Mock).mockImplementationOnce(
        () =>
          new Promise((_resolve, reject) => {
            setTimeout(() => reject(new Error('Timeout')), 200);
          })
      );

      await expect(
        client.testGet('/test', { timeout: 100, maxRetries: 0 })
      ).rejects.toThrow();
    }, 10000);

    it('should combine abort signals', async () => {
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      });

      await client.testGet('/test', { signal: abortController.signal });

      expect(global.fetch).toHaveBeenCalled();
    });

    it('should use custom timeout from options', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      });

      await client.testGet('/test', { timeout: 5000 });

      expect(global.fetch).toHaveBeenCalled();
    });

    it('should merge custom headers from options', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      });

      await client.testGet('/test', {
        headers: { 'X-Custom-Header': 'custom-value' },
      });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Custom-Header': 'custom-value',
          }),
        })
      );
    });

    it('should log debug messages when debug enabled', async () => {
      const debugClient = new TestClient({
        baseUrl: 'http://localhost:5000',
        debug: true,
      });

      const consoleSpy = jest.spyOn(console, 'log').mockImplementation();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ success: true }),
      });

      await debugClient.testGet('/test');

      expect(consoleSpy).toHaveBeenCalled();
      consoleSpy.mockRestore();
    });

    it('should throw AgentProtocolError when all retries exhausted without error', async () => {
      // This is a rare edge case, but we should test it
      const testClient = new TestClient({
        baseUrl: 'http://localhost:5000',
      });

      (global.fetch as jest.Mock).mockImplementation(() => {
        throw null; // Throw non-Error object
      });

      await expect(testClient.testGet('/test', { maxRetries: 0 })).rejects.toThrow(
        AgentProtocolError
      );
    });
  });

  describe('error handling', () => {
    it('should handle 401 Unauthorized', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ message: 'Invalid token' }),
      });

      await expect(client.testGet('/test')).rejects.toThrow(AuthenticationError);
    });

    it('should handle 404 Not Found', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ resource: 'agent-123' }),
      });

      await expect(client.testGet('/test')).rejects.toThrow(NotFoundError);
    });

    it('should handle 400 Validation Error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Validation failed',
          errors: { name: ['Required'] },
        }),
      });

      await expect(client.testGet('/test')).rejects.toThrow(ValidationError);
    });

    it('should handle 429 Rate Limit', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 429,
        headers: {
          get: (name: string) => (name === 'Retry-After' ? '60' : null),
        },
        json: async () => ({ message: 'Rate limit exceeded' }),
      });

      try {
        await client.testGet('/test', { maxRetries: 0 });
      } catch (error) {
        expect(error).toBeInstanceOf(RateLimitError);
        expect((error as RateLimitError).retryAfter).toBe(60);
      }
    });

    it('should handle 429 without Retry-After header', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 429,
        headers: {
          get: () => null,
        },
        json: async () => ({ message: 'Rate limit exceeded' }),
      });

      await expect(client.testGet('/test', { maxRetries: 0 })).rejects.toThrow(
        RateLimitError
      );
    });

    it('should handle 500 Server Error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ message: 'Internal server error' }),
      });

      await expect(client.testGet('/test', { maxRetries: 0 })).rejects.toThrow(
        AgentProtocolError
      );
    });

    it('should handle error response without JSON body', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => {
          throw new Error('Not JSON');
        },
      });

      await expect(client.testGet('/test', { maxRetries: 0 })).rejects.toThrow(
        AgentProtocolError
      );
    });

    it('should use error field from response if message not present', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ error: 'Something went wrong' }),
      });

      await expect(client.testGet('/test', { maxRetries: 0 })).rejects.toThrow(
        'Something went wrong'
      );
    });

    it('should use default message if neither message nor error present', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({}),
      });

      await expect(client.testGet('/test', { maxRetries: 0 })).rejects.toThrow(
        'Unknown error'
      );
    });
  });

  describe('HTTP methods', () => {
    it('should make POST request with body', async () => {
      const body = { name: 'Test' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: '123' }),
      });

      await client.testPost('/test', body);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(body),
        })
      );
    });

    it('should make PUT request with body', async () => {
      const body = { name: 'Updated' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: '123' }),
      });

      await client.testPut('/test', body);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify(body),
        })
      );
    });

    it('should make PATCH request with body', async () => {
      const body = { name: 'Patched' };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({ id: '123' }),
      });

      await client.testPatch('/test', body);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify(body),
        })
      );
    });

    it('should make DELETE request', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await client.testDelete('/test');

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });
  });
});
