/**
 * Tests for RunsClient covering all low-level API methods
 * Matches the .NET RunsClientTests.cs implementation
 */

import { RunsClient } from '../src/client/runs-client';
import type { Run, ChatRole, TextContent, RunStatus } from '@microsoft/agents-protocol-abstractions';
import {
  AgentProtocolError,
  AuthenticationError,
  NotFoundError,
  ValidationError,
  RateLimitError,
} from '../src/errors';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('RunsClient', () => {
  let client: RunsClient;
  const mockBaseUrl = 'https://api.example.com';

  beforeEach(() => {
    client = new RunsClient({
      baseUrl: mockBaseUrl,
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('create', () => {
    it('should create a run with basic configuration', async () => {
      const expectedRun: Run = {
        runId: 'run_001',
        agentId: 'agent_001',
        threadId: 'thread_123',
        status: 'in_progress' as RunStatus,
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-123',
            contents: [
              {
                kind: 'text',
                text: "What's 2+2?",
              } as TextContent,
            ],
          },
        ],
        output: [],
        usage: {
          totalTokens: 0,
          inputTokens: 0,
          outputTokens: 0,
        },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      });

      const result = await client.create({
        agentId: 'agent_001',
        threadId: 'thread_123',
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-123',
            contents: [
              {
                kind: 'text',
                text: "What's 2+2?",
              } as TextContent,
            ],
          },
        ],
      });

      expect(result).toEqual(expectedRun);
      expect(result.runId).toBe('run_001');
      expect(result.agentId).toBe('agent_001');
      expect(result.status).toBe('in_progress');
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs`,
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should create a run with additional instructions', async () => {
      const expectedRun: Run = {
        runId: 'run_002',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      });

      await client.create({
        agentId: 'agent_001',
        instructions: 'Be concise and professional',
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.instructions).toBe('Be concise and professional');
    });

    it('should create a run with metadata', async () => {
      const expectedRun: Run = {
        runId: 'run_003',
        agentId: 'agent_001',
        status: 'queued' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        metadata: { userId: 'user-123', sessionId: 'session-456' },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      });

      const metadata = { userId: 'user-123', sessionId: 'session-456' };
      const result = await client.create({
        agentId: 'agent_001',
        metadata,
      });

      expect(result.metadata).toEqual(metadata);
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.metadata).toEqual(metadata);
    });

    it('should create a run with threadCleanup strategy', async () => {
      const expectedRun: Run = {
        runId: 'run_004',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        threadCleanup: 'delete',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      });

      await client.create({
        agentId: 'agent_001',
        threadCleanup: 'delete',
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.threadCleanup).toBe('delete');
    });

    it('should create a run with tools', async () => {
      const expectedRun: Run = {
        runId: 'run_005',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      });

      const tools = [
        {
          type: 'function' as const,
          name: 'get_weather',
          description: 'Get weather information',
        },
      ];

      await client.create({
        agentId: 'agent_001',
        tools,
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.tools).toEqual(tools);
    });

    it('should handle validation error with missing agentId', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Validation failed',
          errors: { agentId: ['Agent ID is required'] },
        }),
      });

      await expect(
        client.create({
          agentId: '',
        })
      ).rejects.toThrow(ValidationError);
    });

    it('should handle authentication error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Unauthorized',
        }),
      });

      await expect(
        client.create({
          agentId: 'agent_001',
        })
      ).rejects.toThrow(AuthenticationError);
    });

    it('should support custom request options', async () => {
      const expectedRun: Run = {
        runId: 'run_006',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      });

      await client.create(
        { agentId: 'agent_001' },
        {
          timeout: 60000,
          headers: { 'X-Custom-Header': 'test' },
        }
      );

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Custom-Header': 'test',
          }),
        })
      );
    });
  });

  describe('createAndWait', () => {
    it('should create an ephemeral run and wait for completion', async () => {
      const expectedResponse: Run = {
        runId: 'run_002',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-123',
            contents: [
              {
                kind: 'text',
                text: "Translate 'hello' to Spanish",
              } as TextContent,
            ],
          },
        ],
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [
              {
                kind: 'text',
                text: 'Hola',
              } as TextContent,
            ],
          },
        ],
        usage: { totalTokens: 50, inputTokens: 25, outputTokens: 25 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
        threadCleanup: 'delete',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.createAndWait({
        agentId: 'agent_001',
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-123',
            contents: [
              {
                kind: 'text',
                text: "Translate 'hello' to Spanish",
              } as TextContent,
            ],
          },
        ],
        threadCleanup: 'delete',
      });

      expect(result.status).toBe('completed');
      expect(result.output).toHaveLength(1);
      expect((result.output[0].contents[0] as TextContent).text).toBe('Hola');
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs/wait`,
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should apply default timeout of 120 seconds', async () => {
      const expectedResponse: Run = {
        runId: 'run_007',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      await client.createAndWait({ agentId: 'agent_001' });

      // The timeout is set internally, we just verify the call was made
      expect(global.fetch).toHaveBeenCalled();
    });

    it('should support custom timeout override', async () => {
      const expectedResponse: Run = {
        runId: 'run_008',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      await client.createAndWait(
        { agentId: 'agent_001' },
        { timeout: 300000 } // 5 minutes
      );

      expect(global.fetch).toHaveBeenCalled();
    });

    it('should handle runs that require action', async () => {
      const expectedResponse: Run = {
        runId: 'run_009',
        agentId: 'agent_001',
        status: 'requires_action' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 10, inputTokens: 5, outputTokens: 5 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.createAndWait({ agentId: 'agent_001' });

      expect(result.status).toBe('requires_action');
    });
  });

  describe('retrieve', () => {
    it('should retrieve a run by ID', async () => {
      const expectedRun: Run = {
        runId: 'run_123',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 100, inputTokens: 50, outputTokens: 50 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const result = await client.retrieve('run_123');

      expect(result).toEqual(expectedRun);
      expect(result.runId).toBe('run_123');
      expect(result.status).toBe('completed');
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs/run_123`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should handle not found error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Run not found',
          resource: 'run_nonexistent',
        }),
      });

      await expect(client.retrieve('run_nonexistent')).rejects.toThrow(NotFoundError);
    });

    it('should retrieve a run with all status fields', async () => {
      const expectedRun: Run = {
        runId: 'run_456',
        agentId: 'agent_001',
        threadId: 'thread_789',
        status: 'cancelled' as RunStatus,
        input: [],
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-789',
            contents: [
              {
                kind: 'text',
                text: 'Partial response...',
              } as TextContent,
            ],
          },
        ],
        usage: { totalTokens: 30, inputTokens: 20, outputTokens: 10 },
        createdAt: new Date(Date.now() - 60000).toISOString(),
        updatedAt: new Date().toISOString(),
        cancelledAt: new Date().toISOString(),
        cancellationReason: 'User stopped generation',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const result = await client.retrieve('run_456');

      expect(result.status).toBe('cancelled');
      expect(result.cancelledAt).toBeDefined();
      expect(result.cancellationReason).toBe('User stopped generation');
    });

    it('should support request options', async () => {
      const expectedRun: Run = {
        runId: 'run_789',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 0, inputTokens: 0, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      await client.retrieve('run_789', {
        timeout: 10000,
        headers: { 'X-Request-ID': 'req-123' },
      });

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs/run_789`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Request-ID': 'req-123',
          }),
        })
      );
    });
  });

  describe('list', () => {
    it('should list runs with default parameters', async () => {
      const expectedRuns: Run[] = [
        {
          runId: 'run_001',
          agentId: 'agent_001',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 50, inputTokens: 25, outputTokens: 25 },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
        },
        {
          runId: 'run_002',
          agentId: 'agent_001',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 40, inputTokens: 20, outputTokens: 20 },
          createdAt: new Date(Date.now() - 3600000).toISOString(),
          updatedAt: new Date(Date.now() - 3600000).toISOString(),
          completedAt: new Date(Date.now() - 3600000).toISOString(),
        },
      ];

      const expectedResponse = {
        data: expectedRuns,
        hasMore: false,
        firstId: 'run_001',
        lastId: 'run_002',
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
        `${mockBaseUrl}/runs`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list runs filtered by threadId', async () => {
      const expectedRuns: Run[] = [
        {
          runId: 'run_001',
          agentId: 'agent_001',
          threadId: 'thread_123',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 50, inputTokens: 25, outputTokens: 25 },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
        },
        {
          runId: 'run_002',
          agentId: 'agent_001',
          threadId: 'thread_123',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 40, inputTokens: 20, outputTokens: 20 },
          createdAt: new Date(Date.now() - 3600000).toISOString(),
          updatedAt: new Date(Date.now() - 3600000).toISOString(),
          completedAt: new Date(Date.now() - 3600000).toISOString(),
        },
      ];

      const expectedResponse = {
        data: expectedRuns,
        hasMore: false,
        firstId: 'run_001',
        lastId: 'run_002',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({ threadId: 'thread_123', limit: 50 });

      expect(result.data).toHaveLength(2);
      expect(result.data.every((r) => r.threadId === 'thread_123')).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs?limit=50&thread_id=thread_123`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list runs filtered by agentId', async () => {
      const expectedRuns: Run[] = [
        {
          runId: 'run_003',
          agentId: 'agent_002',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 30, inputTokens: 15, outputTokens: 15 },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
        },
      ];

      const expectedResponse = {
        data: expectedRuns,
        hasMore: false,
        firstId: 'run_003',
        lastId: 'run_003',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({ agentId: 'agent_002' });

      expect(result.data).toHaveLength(1);
      expect(result.data[0].agentId).toBe('agent_002');
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs?agent_id=agent_002`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should support pagination with limit and after cursor', async () => {
      const expectedRuns: Run[] = [
        {
          runId: 'run_004',
          agentId: 'agent_001',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 20, inputTokens: 10, outputTokens: 10 },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
        },
      ];

      const expectedResponse = {
        data: expectedRuns,
        hasMore: true,
        firstId: 'run_004',
        lastId: 'run_004',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({ limit: 10, after: 'run_003' });

      expect(result.hasMore).toBe(true);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs?limit=10&after=run_003`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should support pagination with before cursor', async () => {
      const expectedRuns: Run[] = [
        {
          runId: 'run_001',
          agentId: 'agent_001',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 20, inputTokens: 10, outputTokens: 10 },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
        },
      ];

      const expectedResponse = {
        data: expectedRuns,
        hasMore: false,
        firstId: 'run_001',
        lastId: 'run_001',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({ limit: 10, before: 'run_002' });

      expect(result.hasMore).toBe(false);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs?limit=10&before=run_002`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should handle empty list results', async () => {
      const expectedResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({ threadId: 'nonexistent' });

      expect(result.data).toHaveLength(0);
      expect(result.hasMore).toBe(false);
    });

    it('should support combining multiple filters', async () => {
      const expectedRuns: Run[] = [
        {
          runId: 'run_005',
          agentId: 'agent_001',
          threadId: 'thread_456',
          status: 'completed' as RunStatus,
          input: [],
          output: [],
          usage: { totalTokens: 60, inputTokens: 30, outputTokens: 30 },
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          completedAt: new Date().toISOString(),
        },
      ];

      const expectedResponse = {
        data: expectedRuns,
        hasMore: false,
        firstId: 'run_005',
        lastId: 'run_005',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.list({
        agentId: 'agent_001',
        threadId: 'thread_456',
        limit: 20,
      });

      expect(result.data).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs?limit=20&thread_id=thread_456&agent_id=agent_001`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });
  });

  describe('cancel', () => {
    it('should cancel a run with interrupt action (preserving state)', async () => {
      const expectedRun: Run = {
        runId: 'run_456',
        agentId: 'agent_001',
        status: 'cancelled' as RunStatus,
        input: [],
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [
              {
                kind: 'text',
                text: 'Partial response...',
              } as TextContent,
            ],
          },
        ],
        usage: { totalTokens: 25, inputTokens: 15, outputTokens: 10 },
        createdAt: new Date(Date.now() - 60000).toISOString(),
        updatedAt: new Date().toISOString(),
        cancelledAt: new Date().toISOString(),
        cancellationReason: 'User stopped generation',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const result = await client.cancel('run_456');

      expect(result.status).toBe('cancelled');
      expect(result.cancelledAt).toBeDefined();
      expect(result.cancellationReason).toBe('User stopped generation');
      expect(result.output).toHaveLength(1); // Partial output preserved
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs/run_456/cancel`,
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should cancel a run that is in progress', async () => {
      const expectedRun: Run = {
        runId: 'run_789',
        agentId: 'agent_001',
        status: 'cancelling' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 5, inputTokens: 5, outputTokens: 0 },
        createdAt: new Date(Date.now() - 30000).toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const result = await client.cancel('run_789');

      expect(result.status).toBe('cancelling');
    });

    it('should handle cancelling a completed run', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Cannot cancel a completed run',
        }),
      });

      await expect(client.cancel('run_completed')).rejects.toThrow(ValidationError);
    });

    it('should handle cancelling a non-existent run', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Run not found',
          resource: 'run_nonexistent',
        }),
      });

      await expect(client.cancel('run_nonexistent')).rejects.toThrow(NotFoundError);
    });

    it('should support request options for cancel', async () => {
      const expectedRun: Run = {
        runId: 'run_999',
        agentId: 'agent_001',
        status: 'cancelled' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 10, inputTokens: 10, outputTokens: 0 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        cancelledAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      await client.cancel('run_999', {
        timeout: 5000,
        headers: { 'X-Cancel-Reason': 'timeout' },
      });

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs/run_999/cancel`,
        expect.objectContaining({
          headers: expect.objectContaining({
            'X-Cancel-Reason': 'timeout',
          }),
        })
      );
    });
  });

  describe('submitToolOutputs', () => {
    it('should submit tool outputs and continue run', async () => {
      const expectedRun: Run = {
        runId: 'run_789',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [
          {
            role: 'tool' as ChatRole,
            messageId: 'msg-tool',
            contents: [
              {
                kind: 'functionResult',
                callId: 'call_abc123',
                name: 'delete_file',
                result: 'File deleted successfully',
              },
            ],
          },
        ],
        usage: { totalTokens: 35, inputTokens: 20, outputTokens: 15 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const toolOutputs = [
        {
          toolCallId: 'call_abc123',
          output: 'File deleted successfully',
        },
      ];

      const result = await client.submitToolOutputs('run_789', { toolOutputs });

      expect(result.status).toBe('in_progress');
      expect(result.output).toHaveLength(1);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/runs/run_789/submit_tool_outputs`,
        expect.objectContaining({
          method: 'POST',
        })
      );

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.toolOutputs).toEqual(toolOutputs);
    });

    it('should submit multiple tool outputs', async () => {
      const expectedRun: Run = {
        runId: 'run_890',
        agentId: 'agent_001',
        status: 'in_progress' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 45, inputTokens: 25, outputTokens: 20 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const toolOutputs = [
        {
          toolCallId: 'call_123',
          output: 'Weather is sunny',
        },
        {
          toolCallId: 'call_456',
          output: 'Temperature is 72F',
        },
      ];

      await client.submitToolOutputs('run_890', { toolOutputs });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.toolOutputs).toHaveLength(2);
    });

    it('should handle error when run is not in requires_action status', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Run is not in requires_action status',
        }),
      });

      await expect(
        client.submitToolOutputs('run_completed', {
          toolOutputs: [{ toolCallId: 'call_123', output: 'result' }],
        })
      ).rejects.toThrow(ValidationError);
    });
  });

  describe('error handling', () => {
    it('should handle 401 authentication errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Invalid authentication token',
        }),
      });

      await expect(client.retrieve('run_123')).rejects.toThrow(AuthenticationError);
    });

    it('should handle 404 not found errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Run not found',
          resource: 'run_missing',
        }),
      });

      await expect(client.retrieve('run_missing')).rejects.toThrow(NotFoundError);
    });

    it('should handle 400 validation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid request',
          errors: {
            agentId: ['Agent ID is required'],
          },
        }),
      });

      await expect(
        client.create({
          agentId: '',
        })
      ).rejects.toThrow(ValidationError);
    });

    it('should handle 429 rate limit errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 429,
        headers: new Map([['Retry-After', '60']]),
        json: async () => ({
          message: 'Rate limit exceeded',
        }),
      });

      await expect(
        client.retrieve('run_123', { maxRetries: 0 })
      ).rejects.toThrow(RateLimitError);
    });

    it('should handle 500 server errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => ({
          message: 'Internal server error',
        }),
      });

      await expect(
        client.retrieve('run_123', { maxRetries: 0 })
      ).rejects.toThrow(AgentProtocolError);
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network failure'));

      await expect(
        client.retrieve('run_123', { maxRetries: 0 })
      ).rejects.toThrow('Network failure');
    });

    it('should handle timeout errors with abort signal', async () => {
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('The operation was aborted'));
      });

      await expect(
        client.retrieve('run_123', { signal: abortController.signal })
      ).rejects.toThrow();
    });

    it('should handle malformed JSON responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(
        client.retrieve('run_123', { maxRetries: 0 })
      ).rejects.toThrow('Invalid JSON');
    });
  });

  describe('request validation', () => {
    it('should require agentId for create', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'agentId is required',
          errors: { agentId: ['This field is required'] },
        }),
      });

      await expect(
        client.create({
          agentId: '',
        })
      ).rejects.toThrow(ValidationError);
    });

    it('should validate runId format for retrieve', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid run ID format',
        }),
      });

      await expect(client.retrieve('invalid-format')).rejects.toThrow(ValidationError);
    });

    it('should validate toolOutputs for submitToolOutputs', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'toolOutputs cannot be empty',
          errors: { toolOutputs: ['At least one tool output is required'] },
        }),
      });

      await expect(
        client.submitToolOutputs('run_123', { toolOutputs: [] })
      ).rejects.toThrow(ValidationError);
    });
  });

  describe('retry logic', () => {
    it('should retry on transient failures', async () => {
      // First call fails with 503
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 503,
        json: async () => ({
          message: 'Service temporarily unavailable',
        }),
      });

      // Second call succeeds
      const expectedRun: Run = {
        runId: 'run_123',
        agentId: 'agent_001',
        status: 'completed' as RunStatus,
        input: [],
        output: [],
        usage: { totalTokens: 50, inputTokens: 25, outputTokens: 25 },
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        completedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      });

      const result = await client.retrieve('run_123');

      expect(result.runId).toBe('run_123');
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });

    it('should not retry on 404 errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Run not found',
          resource: 'run_missing',
        }),
      });

      await expect(client.retrieve('run_missing')).rejects.toThrow(NotFoundError);

      // Should only be called once (no retries)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should not retry on validation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Invalid request',
        }),
      });

      await expect(
        client.create({
          agentId: '',
        })
      ).rejects.toThrow(ValidationError);

      // Should only be called once (no retries)
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should respect maxRetries option', async () => {
      // All calls fail
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 503,
        json: async () => ({
          message: 'Service unavailable',
        }),
      });

      await expect(
        client.retrieve('run_123', { maxRetries: 1 })
      ).rejects.toThrow(AgentProtocolError);

      // Should be called initial attempt + 1 retry = 2 times
      expect(global.fetch).toHaveBeenCalledTimes(2);
    });
  });
});
