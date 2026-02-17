/**
 * Tests for ThreadsClient low-level API
 * Matches .NET ThreadsClientTests.cs for consistency
 */

import { ThreadsClient } from '../src/client/threads-client';
import type { Thread, ChatMessage, TextContent } from '@microsoft/agents-protocol-abstractions';
import {
  AgentProtocolError,
  NotFoundError,
  ValidationError,
  AuthenticationError,
} from '../src/errors';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('ThreadsClient', () => {
  let client: ThreadsClient;
  const baseUrl = 'https://api.example.com';

  beforeEach(() => {
    client = new ThreadsClient({
      baseUrl,
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('create', () => {
    it('should create a thread with initial messages', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_001',
        status: 'active',
        participants: [
          {
            id: 'user_001',
            role: 'user',
            name: 'John Doe',
          },
        ],
        messages: [
          {
            messageId: 'msg_001',
            role: 'user',
            contents: [
              {
                kind: 'text',
                text: 'Hello, I need help',
              } as TextContent,
            ],
            userId: 'user_001',
          } as ChatMessage,
        ],
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedThread,
      });

      const result = await client.create({
        messages: [
          {
            messageId: 'msg_001',
            role: 'user',
            contents: [
              {
                kind: 'text',
                text: 'Hello, I need help',
              } as TextContent,
            ],
            userId: 'user_001',
          } as ChatMessage,
        ],
      });

      expect(result).toEqual(expectedThread);
      expect(result.threadId).toBe('thread_001');
      expect(result.participants).toHaveLength(1);
      expect(result.messages).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads`,
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should create an empty thread without messages', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_002',
        status: 'active',
        participants: [],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedThread,
      });

      const result = await client.create();

      expect(result).toEqual(expectedThread);
      expect(result.threadId).toBe('thread_002');
      expect(result.messages).toHaveLength(0);
    });

    it('should create thread with metadata', async () => {
      const metadata = {
        userId: 'user_123',
        sessionId: 'session_456',
        source: 'web',
      };

      const expectedThread: Thread = {
        threadId: 'thread_003',
        status: 'active',
        participants: [],
        messages: [],
        metadata,
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedThread,
      });

      const result = await client.create({ metadata });

      expect(result.metadata).toEqual(metadata);
      const callBody = JSON.parse(
        (global.fetch as jest.Mock).mock.calls[0][1].body
      );
      expect(callBody.metadata).toEqual(metadata);
    });

    it('should handle validation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid request',
          errors: {
            messages: ['Messages array cannot be null'],
          },
        }),
      });

      await expect(client.create()).rejects.toThrow(ValidationError);
    });
  });

  describe('retrieve', () => {
    it('should retrieve a thread by ID', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_123',
        status: 'active',
        participants: [
          {
            id: 'user_001',
            role: 'user',
            name: 'John Doe',
          },
        ],
        messages: [
          {
            messageId: 'msg_001',
            role: 'user',
            contents: [
              {
                kind: 'text',
                text: 'Test message',
              } as TextContent,
            ],
          } as ChatMessage,
        ],
        createdAt: new Date().toISOString(),
        lastMessageAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.retrieve('thread_123');

      expect(result).toEqual(expectedThread);
      expect(result.threadId).toBe('thread_123');
      expect(result.status).toBe('active');
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/thread_123`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should handle thread not found', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: 'thread_999',
        }),
      });

      await expect(client.retrieve('thread_999')).rejects.toThrow(NotFoundError);
    });

    it('should retrieve archived thread', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_archived',
        status: 'archived',
        participants: [],
        messages: [],
        createdAt: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
        lastActivityAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.retrieve('thread_archived');

      expect(result.status).toBe('archived');
      expect(result.threadId).toBe('thread_archived');
    });
  });

  describe('list', () => {
    it('should list threads with default pagination', async () => {
      const expectedResponse = {
        data: [
          {
            threadId: 'thread_001',
            status: 'active',
            participants: [],
            messages: [],
            createdAt: new Date().toISOString(),
          } as Thread,
          {
            threadId: 'thread_002',
            status: 'active',
            participants: [],
            messages: [],
            createdAt: new Date().toISOString(),
          } as Thread,
        ],
        hasMore: false,
        firstId: 'thread_001',
        lastId: 'thread_002',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list();

      expect(result.data).toHaveLength(2);
      expect(result.hasMore).toBe(false);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list threads with pagination parameters', async () => {
      const expectedResponse = {
        data: [
          {
            threadId: 'thread_003',
            status: 'active',
            participants: [],
            messages: [],
            createdAt: new Date().toISOString(),
          } as Thread,
        ],
        hasMore: true,
        firstId: 'thread_003',
        lastId: 'thread_003',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({
        limit: 50,
        after: 'thread_002',
      });

      expect(result.data).toHaveLength(1);
      expect(result.hasMore).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads?limit=50&after=thread_002`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list threads with before cursor for backward pagination', async () => {
      const expectedResponse = {
        data: [
          {
            threadId: 'thread_001',
            status: 'active',
            participants: [],
            messages: [],
            createdAt: new Date().toISOString(),
          } as Thread,
        ],
        hasMore: false,
        firstId: 'thread_001',
        lastId: 'thread_001',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({
        before: 'thread_002',
        limit: 10,
      });

      expect(result.data).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads?limit=10&before=thread_002`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should return empty list when no threads exist', async () => {
      const expectedResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list();

      expect(result.data).toHaveLength(0);
      expect(result.hasMore).toBe(false);
    });
  });

  describe('update', () => {
    it('should update thread metadata', async () => {
      const updatedMetadata = {
        priority: 'high',
        category: 'support',
        assignee: 'agent_001',
      };

      const expectedThread: Thread = {
        threadId: 'thread_123',
        status: 'active',
        participants: [],
        messages: [],
        metadata: updatedMetadata,
        createdAt: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
        lastActivityAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.update('thread_123', {
        metadata: updatedMetadata,
      });

      expect(result.metadata).toEqual(updatedMetadata);
      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/thread_123`,
        expect.objectContaining({
          method: 'PATCH',
        })
      );

      const callBody = JSON.parse(
        (global.fetch as jest.Mock).mock.calls[0][1].body
      );
      expect(callBody.metadata).toEqual(updatedMetadata);
    });

    it('should update thread with empty metadata', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_123',
        status: 'active',
        participants: [],
        messages: [],
        metadata: {},
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.update('thread_123', {
        metadata: {},
      });

      expect(result.metadata).toEqual({});
    });

    it('should handle update validation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid metadata format',
          errors: {
            metadata: ['Metadata values must be strings or numbers'],
          },
        }),
      });

      await expect(
        client.update('thread_123', {
          metadata: { invalid: undefined },
        })
      ).rejects.toThrow(ValidationError);
    });

    it('should handle thread not found on update', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: 'thread_999',
        }),
      });

      await expect(
        client.update('thread_999', { metadata: {} })
      ).rejects.toThrow(NotFoundError);
    });
  });

  describe('remove', () => {
    it('should delete a thread successfully', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await client.remove('thread_123');

      expect(global.fetch).toHaveBeenCalledWith(
        `${baseUrl}/threads/thread_123`,
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should handle thread not found on delete', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: 'thread_999',
        }),
      });

      await expect(client.remove('thread_999')).rejects.toThrow(NotFoundError);
    });

    it('should delete archived thread', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await client.remove('thread_archived_001');

      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('error handling', () => {
    it('should handle authentication errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Authentication required',
        }),
      });

      await expect(client.retrieve('thread_123')).rejects.toThrow(
        AuthenticationError
      );
    });

    it(
      'should handle rate limit errors',
      async () => {
        // Create client with no retries to avoid timeout
        const noRetryClient = new ThreadsClient({
          baseUrl,
          maxRetries: 0,
          debug: false,
        });

        (global.fetch as jest.Mock).mockImplementation(() => {
          return Promise.resolve({
            ok: false,
            status: 429,
            headers: new Headers({
              'Retry-After': '60',
            }),
            json: () => Promise.resolve({
              message: 'Rate limit exceeded',
            }),
          });
        });

        await expect(noRetryClient.list()).rejects.toThrow(AgentProtocolError);
      },
      10000
    );

    it(
      'should handle network errors',
      async () => {
        // Create client with no retries and short timeout to avoid hanging
        const noRetryClient = new ThreadsClient({
          baseUrl,
          maxRetries: 0,
          timeout: 1000,
          debug: false,
        });

        (global.fetch as jest.Mock).mockRejectedValueOnce(
          new Error('Network error')
        );

        await expect(noRetryClient.retrieve('thread_123')).rejects.toThrow();
      },
      10000
    );

    it(
      'should handle malformed JSON responses',
      async () => {
        // Create client with no retries and short timeout to avoid hanging
        const noRetryClient = new ThreadsClient({
          baseUrl,
          maxRetries: 0,
          timeout: 1000,
          debug: false,
        });

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => {
            throw new Error('Invalid JSON');
          },
        });

        await expect(noRetryClient.retrieve('thread_123')).rejects.toThrow();
      },
      10000
    );

    it(
      'should handle server errors',
      async () => {
        // Create client with no retries to avoid timeout
        const noRetryClient = new ThreadsClient({
          baseUrl,
          maxRetries: 0,
          debug: false,
        });

        (global.fetch as jest.Mock).mockImplementation(() => {
          return Promise.resolve({
            ok: false,
            status: 500,
            json: () => Promise.resolve({
              message: 'Internal server error',
            }),
          });
        });

        await expect(noRetryClient.create()).rejects.toThrow(AgentProtocolError);
      },
      10000
    );
  });

  describe('request validation', () => {
    it('should validate thread ID format', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid thread ID format',
        }),
      });

      await expect(client.retrieve('')).rejects.toThrow(ValidationError);
    });

    it('should include custom headers in requests', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_123',
        status: 'active',
        participants: [],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      await client.retrieve('thread_123', {
        headers: {
          'X-Custom-Header': 'custom-value',
        },
      });

      const callHeaders = (global.fetch as jest.Mock).mock.calls[0][1].headers;
      expect(callHeaders['X-Custom-Header']).toBe('custom-value');
    });

    it('should respect timeout options', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_123',
        status: 'active',
        participants: [],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      await client.retrieve('thread_123', {
        timeout: 5000,
      });

      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should support abort signal for cancellation', async () => {
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('AbortError'));
      });

      await expect(
        client.retrieve('thread_123', { signal: abortController.signal })
      ).rejects.toThrow();
    });

    it('should retry failed requests with exponential backoff', async () => {
      const clientWithRetry = new ThreadsClient({
        baseUrl,
        maxRetries: 1, // Only 1 retry for faster test
        timeout: 1000,
        debug: false,
      });

      const mockThread: Thread = {
        threadId: 'thread_123',
        status: 'active',
        participants: [],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      // First attempt fails with retryable error (500), second succeeds
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: false,
          status: 503,
          json: async () => ({ message: 'Service unavailable' }),
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockThread,
        });

      const result = await clientWithRetry.retrieve('thread_123');

      expect(result.threadId).toBe('thread_123');
      expect(global.fetch).toHaveBeenCalledTimes(2);
    }, 10000);

    it('should not retry authentication errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Authentication required',
        }),
      });

      await expect(client.retrieve('thread_123')).rejects.toThrow(
        AuthenticationError
      );

      // Should only be called once (no retries)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry not found errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Thread not found',
          resource: 'thread_999',
        }),
      });

      await expect(client.retrieve('thread_999')).rejects.toThrow(NotFoundError);

      // Should only be called once (no retries)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });
  });

  describe('integration scenarios', () => {
    it('should create, retrieve, update, and delete a thread', async () => {
      // Create
      const createdThread: Thread = {
        threadId: 'thread_new',
        status: 'active',
        participants: [],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => createdThread,
      });

      const created = await client.create();
      expect(created.threadId).toBe('thread_new');

      // Retrieve
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => createdThread,
      });

      const retrieved = await client.retrieve('thread_new');
      expect(retrieved.threadId).toBe('thread_new');

      // Update
      const updatedThread: Thread = {
        ...createdThread,
        metadata: { updated: true },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updatedThread,
      });

      const updated = await client.update('thread_new', {
        metadata: { updated: true },
      });
      expect(updated.metadata).toEqual({ updated: true });

      // Delete
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await client.remove('thread_new');

      expect(global.fetch).toHaveBeenCalledTimes(4);
    });

    it('should handle thread lifecycle transitions', async () => {
      const baseThread: Thread = {
        threadId: 'thread_lifecycle',
        status: 'active',
        participants: [],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      // Start as active
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => baseThread,
      });

      let thread = await client.retrieve('thread_lifecycle');
      expect(thread.status).toBe('active');

      // Transition to closed
      const closedThread: Thread = {
        ...baseThread,
        status: 'closed',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => closedThread,
      });

      thread = await client.retrieve('thread_lifecycle');
      expect(thread.status).toBe('closed');

      // Transition to archived
      const archivedThread: Thread = {
        ...baseThread,
        status: 'archived',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => archivedThread,
      });

      thread = await client.retrieve('thread_lifecycle');
      expect(thread.status).toBe('archived');
    });

    it('should handle pagination through multiple pages', async () => {
      // First page
      const firstPage = {
        data: [
          {
            threadId: 'thread_001',
            status: 'active',
            participants: [],
            messages: [],
            createdAt: new Date().toISOString(),
          } as Thread,
        ],
        hasMore: true,
        lastId: 'thread_001',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => firstPage,
      });

      const page1 = await client.list({ limit: 1 });
      expect(page1.data).toHaveLength(1);
      expect(page1.hasMore).toBe(true);

      // Second page
      const secondPage = {
        data: [
          {
            threadId: 'thread_002',
            status: 'active',
            participants: [],
            messages: [],
            createdAt: new Date().toISOString(),
          } as Thread,
        ],
        hasMore: false,
        lastId: 'thread_002',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => secondPage,
      });

      const page2 = await client.list({ limit: 1, after: page1.lastId });
      expect(page2.data).toHaveLength(1);
      expect(page2.hasMore).toBe(false);
      expect(page2.data[0].threadId).toBe('thread_002');
    });
  });

  describe('thread with complex data', () => {
    it('should handle thread with multiple participants', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_multi',
        status: 'active',
        participants: [
          {
            id: 'user_001',
            role: 'user',
            name: 'Alice',
          },
          {
            id: 'user_002',
            role: 'user',
            name: 'Bob',
          },
          {
            id: 'agent_001',
            role: 'agent',
            name: 'Support Agent',
          },
        ],
        messages: [],
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.retrieve('thread_multi');

      expect(result.participants).toHaveLength(3);
      expect(result.participants[0].name).toBe('Alice');
      expect(result.participants[1].name).toBe('Bob');
      expect(result.participants[2].role).toBe('agent');
    });

    it('should handle thread with multiple messages', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_msgs',
        status: 'active',
        participants: [],
        messages: [
          {
            messageId: 'msg_001',
            role: 'user',
            contents: [
              {
                kind: 'text',
                text: 'First message',
              } as TextContent,
            ],
          } as ChatMessage,
          {
            messageId: 'msg_002',
            role: 'agent',
            contents: [
              {
                kind: 'text',
                text: 'Agent response',
              } as TextContent,
            ],
          } as ChatMessage,
          {
            messageId: 'msg_003',
            role: 'user',
            contents: [
              {
                kind: 'text',
                text: 'Follow-up question',
              } as TextContent,
            ],
          } as ChatMessage,
        ],
        createdAt: new Date().toISOString(),
        lastMessageAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.retrieve('thread_msgs');

      expect(result.messages).toHaveLength(3);
      expect(result.messages[0].role).toBe('user');
      expect(result.messages[1].role).toBe('agent');
      expect(result.messages[2].role).toBe('user');
    });

    it('should handle thread with unread count', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_unread',
        status: 'active',
        participants: [],
        messages: [],
        unreadCount: 5,
        createdAt: new Date().toISOString(),
        lastActivityAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.retrieve('thread_unread');

      expect(result.unreadCount).toBe(5);
      expect(result.lastActivityAt).toBeDefined();
    });

    it('should handle thread with channel info', async () => {
      const expectedThread: Thread = {
        threadId: 'thread_channel',
        status: 'active',
        participants: [],
        messages: [],
        channelInfo: {
          channelId: 'msteams',
          externalConversationId: 'conv_123',
        },
        createdAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedThread,
      });

      const result = await client.retrieve('thread_channel');

      expect(result.channelInfo).toBeDefined();
      expect(result.channelInfo?.channelId).toBe('msteams');
      expect(result.channelInfo?.externalConversationId).toBe('conv_123');
    });
  });
});
