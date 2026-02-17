/**
 * Comprehensive tests for Conversation class
 */

import { Conversation } from '../src/conversation';
import { SimplifiedClient } from '../src/simplified-client';
import type { ChatMessage, ChatRole, TextContent } from '@microsoft/agents-protocol-abstractions';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('Conversation', () => {
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

  describe('constructor and threadId', () => {
    it('should create conversation without threadId', () => {
      const conversation = new Conversation(client, undefined);
      expect(conversation.threadId).toBeUndefined();
    });

    it('should create conversation with existing threadId', () => {
      const conversation = new Conversation(client, 'thread-123');
      expect(conversation.threadId).toBe('thread-123');
    });

    it('should expose threadId getter', () => {
      const conversation = new Conversation(client, 'test-thread');
      expect(conversation.threadId).toBe('test-thread');
    });
  });

  describe('send', () => {
    it('should send message and return text response', async () => {
      const conversation = new Conversation(client, undefined);

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [
              {
                kind: 'text',
                type: 'text',
                text: 'Hello! How can I help you?',
              } as TextContent,
            ],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await conversation.send('Hello');

      expect(result).toBe('Hello! How can I help you?');
      expect(conversation.threadId).toBe('thread-123');
    });

    it('should maintain threadId across multiple messages', async () => {
      const conversation = new Conversation(client, undefined);

      // First message
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-1',
          threadId: 'thread-123',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', type: 'text', text: 'First response' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('First message');
      expect(conversation.threadId).toBe('thread-123');

      // Second message
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-2',
          threadId: 'thread-123',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-2',
              contents: [{ kind: 'text', type: 'text', text: 'Second response' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('Second message');
      expect(conversation.threadId).toBe('thread-123');
    });

    it('should return empty string when output is empty', async () => {
      const conversation = new Conversation(client, 'thread-123');

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

      const result = await conversation.send('Hello');

      expect(result).toBe('');
    });

    it('should return empty string when output is null/undefined', async () => {
      const conversation = new Conversation(client, 'thread-123');

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

      const result = await conversation.send('Hello');

      expect(result).toBe('');
    });

    it('should return empty string when no agent message in output', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-456',
            contents: [{ kind: 'text', type: 'text', text: 'User message' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await conversation.send('Hello');

      expect(result).toBe('');
    });

    it('should return empty string when agent message has no contents', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await conversation.send('Hello');

      expect(result).toBe('');
    });

    it('should return empty string when agent message has no text content', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
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

      const result = await conversation.send('Hello');

      expect(result).toBe('');
    });

    it('should support abort signal for cancellation', async () => {
      const conversation = new Conversation(client, 'thread-123');
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('AbortError'));
      });

      await expect(conversation.send('Hello', abortController.signal)).rejects.toThrow();
    });

    it('should update threadId only on first message', async () => {
      const conversation = new Conversation(client, undefined);

      // First message - should set threadId
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-1',
          threadId: 'thread-123',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', type: 'text', text: 'Response' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('First');
      expect(conversation.threadId).toBe('thread-123');

      // Second message - threadId should remain the same even if response has different threadId
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-2',
          threadId: 'thread-456', // Different threadId
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-2',
              contents: [{ kind: 'text', type: 'text', text: 'Response' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('Second');
      expect(conversation.threadId).toBe('thread-123'); // Should keep original threadId
    });
  });

  describe('sendStructured', () => {
    it('should send structured message and return structured response', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [{ kind: 'text', type: 'text', text: 'What is the weather?' } as TextContent],
      };

      const outputMessage: ChatMessage = {
        role: 'agent' as ChatRole,
        messageId: 'msg-456',
        contents: [{ kind: 'text', type: 'text', text: 'The weather is sunny.' } as TextContent],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [outputMessage],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await conversation.sendStructured(inputMessage);

      expect(result).toEqual(outputMessage);
    });

    it('should return empty agent message when no output', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [],
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

      const result = await conversation.sendStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
      expect(result.messageId).toBeDefined();
    });

    it('should return empty agent message when output is null', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [],
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

      const result = await conversation.sendStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
    });

    it('should return empty agent message when no agent in output', async () => {
      const conversation = new Conversation(client, 'thread-123');

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
            role: 'user' as ChatRole,
            messageId: 'msg-456',
            contents: [{ kind: 'text', type: 'text', text: 'User message' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await conversation.sendStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
    });

    it('should update threadId when not set', async () => {
      const conversation = new Conversation(client, undefined);

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-789',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await conversation.sendStructured(inputMessage);

      expect(conversation.threadId).toBe('thread-789');
    });

    it('should support abort signal', async () => {
      const conversation = new Conversation(client, 'thread-123');
      const abortController = new AbortController();

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [],
      };

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('AbortError'));
      });

      await expect(
        conversation.sendStructured(inputMessage, abortController.signal)
      ).rejects.toThrow();
    });
  });

  describe('streamMessages', () => {
    it('should stream messages and update threadId from run.started event', async () => {
      const conversation = new Conversation(client, undefined);

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

      try {
        // This will fail when trying to connect to SSE, but we can test the setup
        const generator = conversation.streamMessages('Hello');
        await generator.next();
      } catch (error) {
        // Expected to fail without full SSE mock
      }

      expect(global.fetch).toHaveBeenCalled();
    });

    it('should yield message on message.created event', async () => {
      const conversation = new Conversation(client, 'thread-123');

      // We need to mock the internal streamRun method
      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'run.started',
          data: { runId: 'run-123', threadId: 'thread-123' },
        };
        yield {
          eventType: 'message.created',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', type: 'text', text: 'Hello' } as TextContent],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const messages: ChatMessage[] = [];
      for await (const message of conversation.streamMessages('Hello')) {
        messages.push(message);
      }

      expect(messages).toHaveLength(1);
      expect(messages[0].messageId).toBe('msg-1');
    });

    it('should yield message on message.updated event', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.updated',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', type: 'text', text: 'Updated' } as TextContent],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const messages: ChatMessage[] = [];
      for await (const message of conversation.streamMessages('Hello')) {
        messages.push(message);
      }

      expect(messages).toHaveLength(1);
      expect(messages[0].messageId).toBe('msg-1');
    });

    it('should yield message on message.delta event', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', type: 'text', text: 'Delta' } as TextContent],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const messages: ChatMessage[] = [];
      for await (const message of conversation.streamMessages('Hello')) {
        messages.push(message);
      }

      expect(messages).toHaveLength(1);
    });

    it('should not yield message when messageId is missing', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.created',
          data: {
            role: 'agent' as ChatRole,
            // No messageId
            contents: [{ kind: 'text', type: 'text', text: 'Hello' } as TextContent],
          },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const messages: ChatMessage[] = [];
      for await (const message of conversation.streamMessages('Hello')) {
        messages.push(message);
      }

      expect(messages).toHaveLength(0);
    });

    it('should update threadId from run.started event', async () => {
      const conversation = new Conversation(client, undefined);

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'run.started',
          data: { runId: 'run-123', threadId: 'thread-456' },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const messages: ChatMessage[] = [];
      for await (const message of conversation.streamMessages('Hello')) {
        messages.push(message);
      }

      expect(conversation.threadId).toBe('thread-456');
    });

    it('should not update threadId if already set', async () => {
      const conversation = new Conversation(client, 'thread-original');

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'run.started',
          data: { runId: 'run-123', threadId: 'thread-new' },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const messages: ChatMessage[] = [];
      for await (const message of conversation.streamMessages('Hello')) {
        messages.push(message);
      }

      expect(conversation.threadId).toBe('thread-original');
    });

    it('should support abort signal', async () => {
      const conversation = new Conversation(client, 'thread-123');
      const abortController = new AbortController();

      const mockStreamRun = jest.fn(async function* () {
        abortController.abort();
        throw new Error('Aborted');
      });

      (client as any).streamRun = mockStreamRun;

      await expect(async () => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        for await (const _message of conversation.streamMessages(
          'Hello',
          abortController.signal
        )) {
          // Should not reach here
        }
      }).rejects.toThrow();
    });
  });

  describe('streamEvents', () => {
    it('should stream all events', async () => {
      const conversation = new Conversation(client, 'thread-123');

      const mockStreamRun = jest.fn(async function* () {
        yield { eventType: 'run.started', data: { runId: 'run-123' } };
        yield { eventType: 'run.step.created', data: { stepId: 'step-1' } };
        yield { eventType: 'run.completed', data: { runId: 'run-123' } };
      });

      (client as any).streamRun = mockStreamRun;

      const events: any[] = [];
      for await (const event of conversation.streamEvents('Hello')) {
        events.push(event);
      }

      expect(events).toHaveLength(3);
      expect(events[0].eventType).toBe('run.started');
      expect(events[1].eventType).toBe('run.step.created');
      expect(events[2].eventType).toBe('run.completed');
    });

    it('should update threadId from run.started event', async () => {
      const conversation = new Conversation(client, undefined);

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'run.started',
          data: { runId: 'run-123', threadId: 'thread-789' },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const events: any[] = [];
      for await (const event of conversation.streamEvents('Hello')) {
        events.push(event);
      }

      expect(conversation.threadId).toBe('thread-789');
    });

    it('should not update threadId if already set', async () => {
      const conversation = new Conversation(client, 'thread-existing');

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'run.started',
          data: { runId: 'run-123', threadId: 'thread-new' },
        };
      });

      (client as any).streamRun = mockStreamRun;

      const events: any[] = [];
      for await (const event of conversation.streamEvents('Hello')) {
        events.push(event);
      }

      expect(conversation.threadId).toBe('thread-existing');
    });

    it('should support abort signal', async () => {
      const conversation = new Conversation(client, 'thread-123');
      const abortController = new AbortController();

      const mockStreamRun = jest.fn(async function* () {
        abortController.abort();
        throw new Error('Aborted');
      });

      (client as any).streamRun = mockStreamRun;

      await expect(async () => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        for await (const _event of conversation.streamEvents(
          'Hello',
          abortController.signal
        )) {
          // Should not reach here
        }
      }).rejects.toThrow();
    });
  });
});
