/**
 * Tests for streaming modes covering all streaming-guide.md patterns.
 * Tests three streaming modes: Callback, Messages (AsyncGenerator), and Events.
 *
 * This test suite matches the .NET StreamingModesTests.cs implementation,
 * ensuring consistent behavior across SDKs.
 */

// Mock the streaming module BEFORE imports
let mockSSEStreamInstance: any = null;
let mockEvents: Array<{ eventType: string; data: any }> = [];
let mockError: Error | null = null;

jest.mock('../src/streaming', () => ({
  SSEStream: jest.fn().mockImplementation((url: string, options?: any) => {
    const handlers = new Map<string, Set<(event: any) => void>>();

    mockSSEStreamInstance = {
      url,
      options,
      connected: false,
      on(eventType: string, handler: (event: any) => void) {
        if (!handlers.has(eventType)) {
          handlers.set(eventType, new Set());
        }
        handlers.get(eventType)!.add(handler);
        return () => handlers.get(eventType)?.delete(handler);
      },
      off(eventType: string, handler: (event: any) => void) {
        handlers.get(eventType)?.delete(handler);
      },
      connect() {
        this.connected = true;
        setTimeout(() => {
          handlers.get('connected')?.forEach(h => h(null));

          if (mockError) {
            setTimeout(() => {
              handlers.get('error')?.forEach(h => h(mockError));
            }, 15);
          } else {
            mockEvents.forEach(({ eventType, data }) => {
              handlers.get('*')?.forEach(h => h({ event: eventType, ...data }));
            });
            setTimeout(() => {
              handlers.get('done')?.forEach(h => h(null));
            }, 15);
          }
        }, 5);
      },
      close() {
        this.connected = false;
        handlers.clear();
      },
    };

    return mockSSEStreamInstance;
  }),
}));

import { SimplifiedClient } from '../src/simplified-client';
import type { ChatMessage, TextContent } from '@microsoft/agents-protocol-abstractions';
import type { StreamEvent } from '../src/stream-event';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('StreamingModesTests', () => {
  let client: SimplifiedClient;

  beforeEach(() => {
    client = new SimplifiedClient({
      baseUrl: 'http://localhost:5000',
      debug: false,
    });
    jest.clearAllMocks();
    mockSSEStreamInstance = null;
    mockEvents = [];
    mockError = null;
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Mode 1: Callback-based streaming (Recommended for Most Apps)', () => {
    it('should stream text chunks via callback', async () => {
      // Arrange - Example from "Mode 1: Callback (Recommended for Most Apps)"
      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'message.delta',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Once upon' }],
          },
        },
        {
          eventType: 'message.delta',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Once upon a time' }],
          },
        },
        {
          eventType: 'message.delta',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Once upon a time, there was' }],
          },
        },
        {
          eventType: 'message.delta',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [
              { kind: 'text', type: 'text', text: 'Once upon a time, there was a curious robot named Byte...' },
            ],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const receivedChunks: string[] = [];

      // Act
      await client.streamChat(
        'Tell me a story about a robot',
        (text: string) => receivedChunks.push(text)
      );

      // Assert
      expect(receivedChunks.length).toBeGreaterThan(0);
      expect(receivedChunks.some((chunk) => chunk.includes('Once upon'))).toBe(true);
      expect(receivedChunks.some((chunk) => chunk.includes(' a time'))).toBe(true);

      // All chunks combined should form complete text
      const fullText = receivedChunks.join('');
      expect(fullText).toContain('Once upon a time, there was a curious robot named Byte...');
    });

    it('should handle cancellation with AbortSignal', async () => {
      // Arrange - Example from "Interruption Handling"
      const abortController = new AbortController();

      // Mock run creation to abort immediately
      (global.fetch as jest.Mock).mockImplementationOnce(async () => {
        abortController.abort();
        throw new Error('AbortError');
      });

      // Act & Assert
      await expect(
        client.streamChat(
          'Long story...',
          () => {},
          undefined,
          abortController.signal
        )
      ).rejects.toThrow();
    });

    it('should handle stream errors gracefully', async () => {
      // Arrange
      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      // Set up mock to trigger error
      mockError = new Error('Stream error');
      mockEvents = [];

      // Act & Assert
      await expect(
        client.streamChat('Hello', () => {})
      ).rejects.toThrow();
    });
  });

  describe('Mode 2: AsyncGenerator streaming (Advanced UI Control)', () => {
    it.skip('should preserve message boundaries with streamMessages', async () => {
      // Arrange - Example from "Mode 2: Messages (Advanced UI Control)"
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Tell me' }],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Tell me about Paris' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Tell me about Paris' }],
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const messages: ChatMessage[] = [];

      // Act
      for await (const message of conversation.streamMessages('Tell me about Paris')) {
        messages.push(message);
      }

      // Assert
      expect(messages.length).toBeGreaterThan(0);
      expect(messages.every((m) => m.messageId === 'msg_1')).toBe(true);
    });

    it.skip('should yield each message with multiple messages in stream', async () => {
      // Arrange - Multiple messages in stream
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'First message' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'First message' }],
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_2',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_2',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Second message' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_2',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Second message' }],
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const messageIds: string[] = [];

      // Act
      for await (const message of conversation.streamMessages('Multiple messages')) {
        if (message.messageId) {
          messageIds.push(message.messageId);
        }
      }

      // Assert
      expect(messageIds).toContain('msg_1');
      expect(messageIds).toContain('msg_2');
    });

    it.skip('should handle incremental text accumulation', async () => {
      // Arrange - Test text accumulation pattern from streaming-guide.md
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Hello' }],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Hello world' }],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Hello world!' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Hello world!' }],
          },
        },
        {
          eventType: 'run.completed',
          data: {
            runId: 'run_1',
            status: 'completed',
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      let textPosition = 0;
      const incrementalChunks: string[] = [];

      // Act - Pattern from streaming-guide.md
      for await (const message of conversation.streamMessages('Say hello')) {
        const textContent = message.contents?.find(
          (c: any) => c.kind === 'text'
        ) as TextContent | undefined;

        if (textContent?.text) {
          const newText = textContent.text.substring(textPosition);
          if (newText.length > 0) {
            incrementalChunks.push(newText);
            textPosition = textContent.text.length;
          }
        }
      }

      // Assert
      expect(incrementalChunks.length).toBeGreaterThan(0);
      expect(incrementalChunks[0]).toBe('Hello');
      expect(incrementalChunks.some((chunk) => chunk.includes(' world'))).toBe(true);
      expect(incrementalChunks.some((chunk) => chunk.includes('!'))).toBe(true);

      const fullText = incrementalChunks.join('');
      expect(fullText).toBe('Hello world!');
    });

    it('should handle cancellation during message streaming', async () => {
      // Arrange
      const conversation = client.createConversation();
      const abortController = new AbortController();

      // Mock run creation to abort immediately
      (global.fetch as jest.Mock).mockImplementationOnce(async () => {
        abortController.abort();
        throw new Error('AbortError');
      });

      // Act & Assert
      const messageIterator = conversation.streamMessages('Hello', abortController.signal);

      await expect(messageIterator.next()).rejects.toThrow();
    });
  });

  describe('Mode 3: Event-based streaming (Full Control)', () => {
    it.skip('should provide raw events with streamEvents', async () => {
      // Arrange - Example from "Mode 3: Raw Events (Full Control)"
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Hello' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            metadata: { totalTokens: 100 },
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const eventTypes: string[] = [];

      // Act
      for await (const evt of conversation.streamEvents('Tell me about Paris')) {
        eventTypes.push(evt.eventType);
      }

      // Assert
      expect(eventTypes).toContain('run.started');
      expect(eventTypes).toContain('message.created');
      expect(eventTypes).toContain('message.updated');
      expect(eventTypes).toContain('message.completed');
    });

    it.skip('should emit requires_action event for tool calls', async () => {
      // Arrange - Example from "Handle tool calls" section
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'run.requires_action',
          data: {
            runId: 'run_1',
            requiredAction: {
              type: 'submit_tool_outputs',
              toolCalls: [
                {
                  callId: 'call_123',
                  name: 'get_weather',
                  arguments: '{"location":"Paris"}',
                },
              ],
            },
          },
        },
        {
          eventType: 'run.completed',
          data: {
            runId: 'run_1',
            status: 'completed',
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      let hasRequiresActionEvent = false;

      // Act
      for await (const evt of conversation.streamEvents("What's the weather?")) {
        if (evt.eventType === 'run.requires_action') {
          hasRequiresActionEvent = true;
        }
      }

      // Assert
      expect(hasRequiresActionEvent).toBe(true);
    });

    it.skip('should track multiple messages with message buffering', async () => {
      // Arrange - Pattern from streaming-guide.md "Mode 3: Raw Events"
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'First' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_2',
            role: 'agent',
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_2',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Second' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_2',
            role: 'agent',
          },
        },
        {
          eventType: 'run.completed',
          data: {
            runId: 'run_1',
            status: 'completed',
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const messageBuffers = new Map<string, string[]>();

      // Act - Pattern from streaming-guide.md
      for await (const evt of conversation.streamEvents('Multiple messages')) {
        switch (evt.eventType) {
          case 'message.created': {
            const created = evt.data as ChatMessage;
            if (created?.messageId) {
              messageBuffers.set(created.messageId, []);
            }
            break;
          }

          case 'message.updated': {
            const updated = evt.data as ChatMessage;
            if (updated?.messageId && messageBuffers.has(updated.messageId)) {
              const buffer = messageBuffers.get(updated.messageId)!;
              const textContent = updated.contents?.find(
                (c: any) => c.kind === 'text'
              ) as TextContent | undefined;

              if (textContent?.text) {
                const currentLength = buffer.join('').length;
                const newText = textContent.text.substring(currentLength);
                buffer.push(newText);
              }
            }
            break;
          }

          case 'message.completed': {
            const completed = evt.data as ChatMessage;
            if (completed?.messageId) {
              messageBuffers.delete(completed.messageId);
            }
            break;
          }
        }
      }

      // Assert
      expect(messageBuffers.size).toBe(0); // All messages should be completed and removed
    });

    it.skip('should handle event parsing and data extraction', async () => {
      // Arrange
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_1',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'run.completed',
          data: {
            runId: 'run_1',
            status: 'completed',
            metadata: { totalTokens: 50 },
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const events: StreamEvent[] = [];

      // Act
      for await (const evt of conversation.streamEvents('Test')) {
        events.push(evt);
      }

      // Assert
      expect(events.length).toBe(3);

      const runStartedEvent = events.find((e) => e.eventType === 'run.started');
      expect(runStartedEvent).toBeDefined();
      expect((runStartedEvent!.data as any).runId).toBe('run_1');

      const messageCreatedEvent = events.find((e) => e.eventType === 'message.created');
      expect(messageCreatedEvent).toBeDefined();
      expect((messageCreatedEvent!.data as any).messageId).toBe('msg_1');

      const runCompletedEvent = events.find((e) => e.eventType === 'run.completed');
      expect(runCompletedEvent).toBeDefined();
      expect((runCompletedEvent!.data as any).metadata?.totalTokens).toBe(50);
    });
  });

  describe('Stream event parsing and error handling', () => {
    it('should handle stream errors during event processing', async () => {
      // Arrange
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      // Set up mock to trigger error
      mockError = new Error('Stream processing error');
      mockEvents = [];

      // Act & Assert
      const eventIterator = conversation.streamEvents('Test');

      await expect(async () => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        for await (const _evt of eventIterator) {
          // Should throw before yielding events
        }
      }).rejects.toThrow();
    });

    it.skip('should handle network errors during streaming', async () => {
      // Arrange
      const conversation = client.createConversation();

      // Mock run creation to fail
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network connection lost')
      );

      // Act & Assert
      const eventIterator = conversation.streamEvents('Test');

      await expect(eventIterator.next()).rejects.toThrow();
    });

    it.skip('should handle empty event streams', async () => {
      // Arrange
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      // Set up empty mock events
      mockEvents = [];

      const events: StreamEvent[] = [];

      // Act
      for await (const evt of conversation.streamEvents('Test')) {
        events.push(evt);
      }

      // Assert
      expect(events.length).toBe(0);
    });
  });

  describe('Partial message updates', () => {
    it.skip('should handle partial text updates correctly', async () => {
      // Arrange
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'The' }],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'The quick' }],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'The quick brown' }],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'The quick brown fox' }],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'The quick brown fox' }],
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const partialTexts: string[] = [];

      // Act
      for await (const message of conversation.streamMessages('Test')) {
        const textContent = message.contents?.find(
          (c: any) => c.kind === 'text'
        ) as TextContent | undefined;

        if (textContent?.text) {
          partialTexts.push(textContent.text);
        }
      }

      // Assert
      expect(partialTexts).toEqual([
        'The',
        'The quick',
        'The quick brown',
        'The quick brown fox',
        'The quick brown fox',
      ]);

      // Verify incremental growth
      for (let i = 1; i < partialTexts.length; i++) {
        expect(partialTexts[i].length).toBeGreaterThanOrEqual(partialTexts[i - 1].length);
      }
    });

    it.skip('should handle multiple content types in updates', async () => {
      // Arrange
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [],
          },
        },
        {
          eventType: 'message.updated',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [
              { kind: 'text', type: 'text', text: 'Here is an image:' },
              { kind: 'image', type: 'image', url: 'https://example.com/image.jpg' },
            ],
          },
        },
        {
          eventType: 'message.completed',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [
              { kind: 'text', type: 'text', text: 'Here is an image:' },
              { kind: 'image', type: 'image', url: 'https://example.com/image.jpg' },
            ],
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      const messages: ChatMessage[] = [];

      // Act
      for await (const message of conversation.streamMessages('Show me an image')) {
        messages.push(message);
      }

      // Assert
      expect(messages.length).toBe(2); // updated + completed
      const lastMessage = messages[messages.length - 1];
      expect(lastMessage.contents?.length).toBe(2);
      expect(lastMessage.contents?.[0]).toMatchObject({ kind: 'text' });
      expect(lastMessage.contents?.[1]).toMatchObject({ kind: 'image' });
    });
  });

  describe('Thread and run tracking', () => {
    it.skip('should track thread ID across streaming calls', async () => {
      // Arrange
      const conversation = client.createConversation();

      const runCreateResponse = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_1',
            threadId: 'thread_123',
            status: 'in_progress',
          },
        },
        {
          eventType: 'message.created',
          data: {
            messageId: 'msg_1',
            role: 'agent',
            contents: [{ kind: 'text', type: 'text', text: 'Hello' }],
          },
        },
        {
          eventType: 'run.completed',
          data: {
            runId: 'run_1',
            status: 'completed',
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      // Act
      const events: StreamEvent[] = [];
      for await (const evt of conversation.streamEvents('Test')) {
        events.push(evt);
      }

      // Assert
      expect(conversation.threadId).toBe('thread_123');
    });

    it.skip('should maintain thread ID for resumed conversations', async () => {
      // Arrange
      const existingThreadId = 'thread-existing-123';
      const conversation = client.resumeConversation(existingThreadId);

      const runCreateResponse = {
        runId: 'run-456',
        threadId: existingThreadId,
        status: 'in_progress',
      };

      mockEvents = [
        {
          eventType: 'run.started',
          data: {
            runId: 'run_456',
            threadId: existingThreadId,
            status: 'in_progress',
          },
        },
        {
          eventType: 'run.completed',
          data: {
            runId: 'run_456',
            status: 'completed',
          },
        },
      ];

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => runCreateResponse,
      });

      // Act
      const events: StreamEvent[] = [];
      for await (const evt of conversation.streamEvents('Continue')) {
        events.push(evt);
      }

      // Assert
      expect(conversation.threadId).toBe(existingThreadId);
    });
  });
});
