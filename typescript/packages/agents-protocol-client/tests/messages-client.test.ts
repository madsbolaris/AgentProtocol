/**
 * Tests for MessagesClient API
 */

import { MessagesClient } from '../src/client/messages-client';
import type { ChatMessage, ChatRole, TextContent } from '@microsoft/agents-protocol-abstractions';
import {
  NotFoundError,
  ValidationError,
  AuthenticationError,
} from '../src/errors';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('MessagesClient', () => {
  let client: MessagesClient;
  const baseUrl = 'http://localhost:5000';
  const threadId = 'thread-123';
  const messageId = 'msg-456';

  beforeEach(() => {
    client = new MessagesClient({
      baseUrl,
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('create', () => {
    it('should create a text message in a thread', async () => {
      const request = {
        role: 'user' as const,
        content: 'Hello, world!',
        metadata: { userId: 'user-123' },
      };

      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [
          {
            kind: 'text',
            text: 'Hello, world!',
          } as TextContent,
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const result = await client.create(threadId, request);

      expect(result).toEqual(mockMessage);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages`,
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(request),
        })
      );
    });

    it('should create a system message', async () => {
      const request = {
        role: 'system' as const,
        content: 'You are a helpful assistant.',
      };

      const mockMessage: ChatMessage = {
        role: 'system' as ChatRole,
        messageId: messageId,
        contents: [
          {
            kind: 'text',
            text: 'You are a helpful assistant.',
          } as TextContent,
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const result = await client.create(threadId, request);

      expect(result).toEqual(mockMessage);
      expect(result.role).toBe('system');
    });

    it('should create a message with structured content', async () => {
      const request = {
        role: 'user' as const,
        content: [
          { type: 'text', text: 'What is in this image?' },
          { type: 'image_url', image_url: { url: 'https://example.com/image.jpg' } },
        ],
      };

      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [
          {
            kind: 'text',
            text: 'What is in this image?',
          } as TextContent,
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const result = await client.create(threadId, request);

      expect(result).toEqual(mockMessage);
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.content).toEqual(request.content);
    });

    it('should include metadata in create request', async () => {
      const metadata = { userId: 'user-123', sessionId: 'session-456' };
      const request = {
        role: 'user' as const,
        content: 'Hello',
        metadata,
      };

      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [{ kind: 'text', text: 'Hello' } as TextContent],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      await client.create(threadId, request);

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.metadata).toEqual(metadata);
    });

    it('should support custom request options', async () => {
      const request = {
        role: 'user' as const,
        content: 'Hello',
      };

      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [{ kind: 'text', text: 'Hello' } as TextContent],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const customHeaders = { 'X-Custom-Header': 'test-value' };
      await client.create(threadId, request, {
        headers: customHeaders,
        timeout: 5000,
      });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages`,
        expect.objectContaining({
          headers: expect.objectContaining(customHeaders),
        })
      );
    });

    it('should throw ValidationError for invalid request', async () => {
      const request = {
        role: 'user' as const,
        content: '',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Content cannot be empty',
          errors: { content: ['Content is required'] },
        }),
      });

      await expect(client.create(threadId, request)).rejects.toThrow(ValidationError);
    });

    it('should throw NotFoundError when thread does not exist', async () => {
      const request = {
        role: 'user' as const,
        content: 'Hello',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: threadId,
        }),
      });

      await expect(client.create(threadId, request)).rejects.toThrow(NotFoundError);
    });
  });

  describe('retrieve', () => {
    it('should retrieve a message by ID', async () => {
      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [
          {
            kind: 'text',
            text: 'Hello, world!',
          } as TextContent,
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const result = await client.retrieve(threadId, messageId);

      expect(result).toEqual(mockMessage);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages/${messageId}`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should retrieve message with multiple content blocks', async () => {
      const mockMessage: ChatMessage = {
        role: 'agent' as ChatRole,
        messageId: messageId,
        contents: [
          { kind: 'text', text: 'Here is the result:' } as TextContent,
          { kind: 'text', text: 'Additional information.' } as TextContent,
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const result = await client.retrieve(threadId, messageId);

      expect(result).toEqual(mockMessage);
      expect(result.contents).toHaveLength(2);
    });

    it('should throw NotFoundError when message does not exist', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Message not found',
          resource: messageId,
        }),
      });

      await expect(client.retrieve(threadId, messageId)).rejects.toThrow(NotFoundError);
    });

    it('should throw NotFoundError when thread does not exist', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: threadId,
        }),
      });

      await expect(client.retrieve(threadId, messageId)).rejects.toThrow(NotFoundError);
    });

    it('should support custom request options', async () => {
      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      const customHeaders = { 'X-Request-Id': 'req-123' };
      await client.retrieve(threadId, messageId, { headers: customHeaders });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages/${messageId}`,
        expect.objectContaining({
          headers: expect.objectContaining(customHeaders),
        })
      );
    });
  });

  describe('list', () => {
    it('should list messages without pagination params', async () => {
      const mockMessages: ChatMessage[] = [
        {
          role: 'user' as ChatRole,
          messageId: 'msg-1',
          contents: [{ kind: 'text', text: 'First message' } as TextContent],
        },
        {
          role: 'agent' as ChatRole,
          messageId: 'msg-2',
          contents: [{ kind: 'text', text: 'Second message' } as TextContent],
        },
      ];

      const mockResponse = {
        data: mockMessages,
        hasMore: false,
        firstId: 'msg-1',
        lastId: 'msg-2',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.list(threadId);

      expect(result).toEqual(mockResponse);
      expect(result.data).toHaveLength(2);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list messages with limit parameter', async () => {
      const mockResponse = {
        data: [],
        hasMore: true,
        firstId: 'msg-1',
        lastId: 'msg-10',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.list(threadId, { limit: 10 });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages?limit=10`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list messages with after cursor', async () => {
      const mockResponse = {
        data: [],
        hasMore: true,
        firstId: 'msg-11',
        lastId: 'msg-20',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.list(threadId, { after: 'msg-10' });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages?after=msg-10`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list messages with before cursor', async () => {
      const mockResponse = {
        data: [],
        hasMore: false,
        firstId: 'msg-1',
        lastId: 'msg-10',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.list(threadId, { before: 'msg-11' });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages?before=msg-11`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list messages with multiple pagination params', async () => {
      const mockResponse = {
        data: [],
        hasMore: true,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.list(threadId, {
        limit: 20,
        after: 'msg-100',
      });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages?limit=20&after=msg-100`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should return empty list when thread has no messages', async () => {
      const mockResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.list(threadId);

      expect(result.data).toHaveLength(0);
      expect(result.hasMore).toBe(false);
    });

    it('should indicate more messages are available', async () => {
      const mockResponse = {
        data: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-1',
            contents: [],
          },
        ],
        hasMore: true,
        firstId: 'msg-1',
        lastId: 'msg-1',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.list(threadId, { limit: 1 });

      expect(result.hasMore).toBe(true);
    });

    it('should throw NotFoundError when thread does not exist', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: threadId,
        }),
      });

      await expect(client.list(threadId)).rejects.toThrow(NotFoundError);
    });

    it('should support custom request options', async () => {
      const mockResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const customHeaders = { 'X-Trace-Id': 'trace-123' };
      await client.list(threadId, undefined, { headers: customHeaders });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages`,
        expect.objectContaining({
          headers: expect.objectContaining(customHeaders),
        })
      );
    });
  });

  describe('update', () => {
    it('should update message metadata', async () => {
      const metadata = {
        edited: true,
        editedAt: '2024-01-15T12:00:00Z',
        reason: 'typo correction',
      };

      const mockUpdatedMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [{ kind: 'text', text: 'Updated content' } as TextContent],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockUpdatedMessage,
      });

      const result = await client.update(threadId, messageId, metadata);

      expect(result).toEqual(mockUpdatedMessage);
      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages/${messageId}`,
        expect.objectContaining({
          method: 'PATCH',
          body: JSON.stringify({ metadata }),
        })
      );
    });

    it('should update with empty metadata', async () => {
      const metadata = {};

      const mockUpdatedMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockUpdatedMessage,
      });

      await client.update(threadId, messageId, metadata);

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.metadata).toEqual({});
    });

    it('should update with complex metadata', async () => {
      const metadata = {
        tags: ['important', 'follow-up'],
        priority: 1,
        context: {
          department: 'engineering',
          project: 'agent-protocol',
        },
      };

      const mockUpdatedMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockUpdatedMessage,
      });

      await client.update(threadId, messageId, metadata);

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.metadata).toEqual(metadata);
    });

    it('should throw NotFoundError when message does not exist', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Message not found',
          resource: messageId,
        }),
      });

      await expect(
        client.update(threadId, messageId, { updated: true })
      ).rejects.toThrow(NotFoundError);
    });

    it('should throw ValidationError for invalid metadata', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid metadata format',
          errors: { metadata: ['Metadata must be an object'] },
        }),
      });

      await expect(
        client.update(threadId, messageId, { invalid: undefined })
      ).rejects.toThrow(ValidationError);
    });

    it('should support custom request options', async () => {
      const metadata = { key: 'value' };
      const mockUpdatedMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockUpdatedMessage,
      });

      const customHeaders = { 'X-Update-Source': 'automated' };
      await client.update(threadId, messageId, metadata, { headers: customHeaders });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages/${messageId}`,
        expect.objectContaining({
          headers: expect.objectContaining(customHeaders),
        })
      );
    });
  });

  describe('remove', () => {
    it('should delete a message', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => ({}),
      });

      await client.remove(threadId, messageId);

      expect(global.fetch).toHaveBeenCalledTimes(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages/${messageId}`,
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should return void on successful deletion', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => ({}),
      });

      const result = await client.remove(threadId, messageId);

      expect(result).toBeUndefined();
    });

    it('should throw NotFoundError when message does not exist', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Message not found',
          resource: messageId,
        }),
      });

      await expect(client.remove(threadId, messageId)).rejects.toThrow(NotFoundError);
    });

    it('should throw NotFoundError when thread does not exist', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: threadId,
        }),
      });

      await expect(client.remove(threadId, messageId)).rejects.toThrow(NotFoundError);
    });

    it('should support custom request options', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
        json: async () => ({}),
      });

      const customHeaders = { 'X-Delete-Reason': 'spam' };
      await client.remove(threadId, messageId, { headers: customHeaders });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages/${messageId}`,
        expect.objectContaining({
          headers: expect.objectContaining(customHeaders),
        })
      );
    });
  });

  describe('error handling', () => {
    it('should handle authentication errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Invalid or expired authentication token',
        }),
      });

      await expect(
        client.retrieve(threadId, messageId)
      ).rejects.toThrow(AuthenticationError);
    });

    it('should handle not found errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Resource not found',
          resource: messageId,
        }),
      });

      await expect(
        client.retrieve(threadId, messageId)
      ).rejects.toThrow(NotFoundError);
    });

    it('should handle validation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Validation failed',
          errors: { content: ['Content is required'] },
        }),
      });

      await expect(
        client.create(threadId, { role: 'user', content: '' })
      ).rejects.toThrow(ValidationError);
    });
  });

  describe('request validation', () => {
    it('should send correct Content-Type header', async () => {
      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      await client.create(threadId, { role: 'user', content: 'test' });

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
          }),
        })
      );
    });

    it('should handle AbortSignal for request cancellation', async () => {
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('Request aborted'));
      });

      await expect(
        client.retrieve(threadId, messageId, { signal: abortController.signal })
      ).rejects.toThrow();
    });

    it('should properly encode URL parameters', async () => {
      const specialThreadId = 'thread/with/slashes';
      const specialMessageId = 'msg-with-special-chars!@#';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await client.remove(specialThreadId, specialMessageId);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(encodeURIComponent('slashes')),
        expect.any(Object)
      );
    });

    it('should strip trailing slash from base URL', async () => {
      const clientWithTrailingSlash = new MessagesClient({
        baseUrl: 'http://localhost:5000/',
      });

      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      await clientWithTrailingSlash.retrieve(threadId, messageId);

      expect(global.fetch).toHaveBeenCalledWith(
        `http://localhost:5000/threads/${threadId}/messages/${messageId}`,
        expect.any(Object)
      );
    });

    it('should include authorization header when authToken is provided', async () => {
      const clientWithAuth = new MessagesClient({
        baseUrl,
        authToken: 'test-token-123',
      });

      const mockMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: messageId,
        contents: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockMessage,
      });

      await clientWithAuth.retrieve(threadId, messageId);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: 'Bearer test-token-123',
          }),
        })
      );
    });
  });

  describe('pagination edge cases', () => {
    it('should handle pagination with limit of 1', async () => {
      const mockResponse = {
        data: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-1',
            contents: [],
          },
        ],
        hasMore: true,
        firstId: 'msg-1',
        lastId: 'msg-1',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.list(threadId, { limit: 1 });

      expect(result.data).toHaveLength(1);
      expect(result.hasMore).toBe(true);
    });

    it('should handle pagination with large limit', async () => {
      const mockResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.list(threadId, { limit: 1000 });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages?limit=1000`,
        expect.any(Object)
      );
    });

    it('should handle both before and after cursors', async () => {
      const mockResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.list(threadId, {
        before: 'msg-100',
        after: 'msg-50',
        limit: 25,
      });

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/${threadId}/messages?limit=25&after=msg-50&before=msg-100`,
        expect.any(Object)
      );
    });
  });
});
