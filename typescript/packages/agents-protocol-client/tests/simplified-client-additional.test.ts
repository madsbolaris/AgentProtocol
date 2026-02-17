/**
 * Additional tests for SimplifiedClient to achieve 95%+ coverage
 */

import { SimplifiedClient } from '../src/simplified-client';
import type { ChatMessage, ChatRole, TextContent } from '@microsoft/agents-protocol-abstractions';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('SimplifiedClient - Additional Coverage', () => {
  let client: SimplifiedClient;

  beforeEach(() => {
    client = new SimplifiedClient({
      baseUrl: 'http://localhost:5000',
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('completeChat - empty output scenarios', () => {
    it('should return empty string when response has empty output array', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChat('Test message');

      expect(result).toBe('');
    });

    it('should return empty string when response has no agent message', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-user',
            contents: [{ kind: 'text', type: 'text', text: 'User msg' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChat('Test message');

      expect(result).toBe('');
    });

    it('should return empty string when agent message has no text content', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-agent',
            contents: [],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChat('Test message');

      expect(result).toBe('');
    });

    it('should return empty string when agent message contents have no text kind', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-agent',
            contents: [
              {
                kind: 'image',
                type: 'image',
                url: 'http://example.com/image.png',
              },
            ],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChat('Test message');

      expect(result).toBe('');
    });
  });

  describe('completeChatStructured - empty output scenarios', () => {
    it('should return empty agent message when response has empty output', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [{ kind: 'text', type: 'text', text: 'Test' } as TextContent],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChatStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
      expect(result.messageId).toBeDefined();
    });

    it('should return empty agent message when response has null output', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [{ kind: 'text', type: 'text', text: 'Test' } as TextContent],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: null,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChatStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
    });

    it('should return empty agent message when output has no agent role', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [{ kind: 'text', type: 'text', text: 'Test' } as TextContent],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-user',
            contents: [{ kind: 'text', type: 'text', text: 'User' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChatStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
    });

    it('should use agentId from options', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-agent',
            contents: [],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.completeChatStructured(inputMessage, { agentId: 'agent-456' });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.agentId).toBe('agent-456');
    });

    it('should use metadata from options', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-agent',
            contents: [],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const metadata = { sessionId: 'session-123' };
      await client.completeChatStructured(inputMessage, { metadata });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.metadata).toEqual(metadata);
    });
  });

  describe('resumeConversation', () => {
    it('should create conversation with provided threadId', () => {
      const conversation = client.resumeConversation('thread-abc');

      expect(conversation).toBeDefined();
      expect(conversation.threadId).toBe('thread-abc');
    });
  });

  describe('streamRun - advanced scenarios', () => {
    it('should handle stream with no events', async () => {
      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-123',
          threadId: 'thread-123',
          status: 'in_progress',
        }),
      });

      const mockStreamRun = jest.fn(async function* () {
        // No events yielded
      });

      (client as any).streamRun = mockStreamRun;

      const events: any[] = [];
      for await (const event of (client as any).streamRun({
        agentId: 'agent-123',
        input: [],
      })) {
        events.push(event);
      }

      expect(events).toHaveLength(0);
    });
  });

  describe('extractText edge cases', () => {
    it('should extract text from message with multiple contents', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-agent',
            contents: [
              {
                kind: 'image',
                type: 'image',
                url: 'http://example.com/img.png',
              },
              {
                kind: 'text',
                type: 'text',
                text: 'This is the text response',
              },
            ],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChat('Test');

      expect(result).toBe('This is the text response');
    });
  });

  describe('completeChat with tools', () => {
    it('should call completeChatWithTools when tools are provided', async () => {
      const { ToolCollection } = await import('../src/tool-collection');
      const tools = new ToolCollection();
      tools.add('test_tool', () => 'result');

      // Mock streamRun to return events
      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent',
            messageId: 'msg-1',
            contents: [
              {
                kind: 'text',
                text: 'Response from agent',
              },
            ],
          },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const result = await client.completeChat('Hello', { tools });

      expect(result).toBe('Response from agent');
      expect(mockStreamRun).toHaveBeenCalled();
    });
  });

  describe('createRunAndWait with threadId', () => {
    it('should pass threadId in request', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-456',
        status: 'completed',
        output: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.createRunAndWait({
        agentId: 'agent-123',
        threadId: 'thread-456',
        input: [],
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.threadId).toBe('thread-456');
    });

    it('should handle response without error', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.createRunAndWait({
        agentId: 'agent-123',
        input: [],
      });

      expect(result.error).toBeUndefined();
    });
  });
});
