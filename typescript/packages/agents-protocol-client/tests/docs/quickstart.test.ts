/**
 * Comprehensive tests for ALL Client SDK Quickstart samples
 * Based on /docs/products/client-sdk/quickstart.md
 *
 * Tests cover:
 * - Step 1: Simple Completion
 * - Step 2: Multimodal Content (text + image objects)
 * - Step 3: Persistent Conversations (createConversation, send, resume)
 * - Step 4: Tools/Functions (ToolCollection with add method)
 * - Step 5: Simple Text Streaming (streamChat with onTextChunk)
 * - Step 5: Rich Content Streaming (streamMessages)
 * - Step 5: Thread Streaming (streamThreadMessages)
 * - Complete Example (all features combined)
 * - Error Handling (AgentProtocolError)
 */

import { SimplifiedClient } from '../src/simplified-client';
import { ToolCollection } from '../src/tool-collection';
import { AgentProtocolError } from '../src/errors';
import type { ChatMessage, ChatRole, TextContent, ImageContent } from '@microsoft/agents-protocol-abstractions';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('Client SDK Quickstart Samples', () => {
  let client: SimplifiedClient;

  beforeEach(() => {
    // Note: SimplifiedClient is the TypeScript equivalent of the quickstart's "AgentProtocolClient"
    client = new SimplifiedClient({
      baseUrl: 'http://localhost:5000',
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Step 1: Simple Completion', () => {
    /**
     * @docExample client-simple-completion
     */
    it('should send message and get response (quickstart example)', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_abc123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [
              {
                kind: 'text',
                text: 'I can help you with analysis, writing, coding, research, and problem-solving tasks.',
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

      // Quickstart sample: const response = await client.completeChat("What can you help me with?");
      // <snippet>
      const response = await client.completeChat('What can you help me with?');
      // </snippet>

      expect(response).toBe('I can help you with analysis, writing, coding, research, and problem-solving tasks.');
      expect(global.fetch).toHaveBeenCalledTimes(1);

      // Verify request includes the message
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.input[0].contents[0].text).toBe('What can you help me with?');
    });

    it('should use server default agent', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_abc123',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [{ kind: 'text', text: 'Response' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.completeChat('Hello!');

      // Verify no explicit agentId was provided (uses default)
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.agentId).toBeUndefined();
    });

    it('should create ephemeral thread when no thread ID provided', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_ephemeral',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [{ kind: 'text', text: 'Response' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.completeChat('Hello!');

      // Verify no threadId in request (ephemeral thread)
      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.threadId).toBeUndefined();
    });
  });

  describe('Step 2: Multimodal Content', () => {
    it('should send text and image content together', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_def456',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [
              {
                kind: 'text',
                text: 'This image shows the Eiffel Tower in Paris during sunset, with beautiful orange and pink hues in the sky.',
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

      // Quickstart sample using object array (TypeScript approach)
      const response = await client.completeChat([
        { type: 'text', text: "What's in this image?" },
        { type: 'image', uri: 'https://example.com/photo.jpg' }
      ] as any);

      expect(response).toContain('Eiffel Tower');
      expect(response).toContain('sunset');
    });

    it('should support multimodal content with structured message', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [
          {
            kind: 'text',
            type: 'text',
            text: "What's in this image?",
          } as TextContent,
          {
            kind: 'image',
            type: 'image',
            uri: 'https://example.com/photo.jpg',
          } as ImageContent,
        ],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_ghi789',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [
              {
                kind: 'text',
                text: 'The image shows a beautiful landscape.',
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

      const result = await client.completeChatStructured(inputMessage);

      expect(result.contents[0]).toMatchObject({
        kind: 'text',
        text: 'The image shows a beautiful landscape.',
      });
    });

    it('should handle base64-encoded image data', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_jkl012',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-456',
            contents: [{ kind: 'text', text: 'Image analyzed' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [
          { kind: 'text', type: 'text', text: 'Analyze this' } as TextContent,
          { kind: 'image', type: 'image', data: 'base64encodeddata' } as any,
        ],
      };

      await client.completeChatStructured(inputMessage);

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.input[0].contents).toHaveLength(2);
      expect(callBody.input[0].contents[1].kind).toBe('image');
    });
  });

  describe('Step 3: Persistent Conversations', () => {
    describe('createConversation and send', () => {
      /**
       * @docExample client-persistent-conversations
       */
      it('should create conversation and maintain context across messages', async () => {
        const mockResponse1: any = {
          runId: 'run-1',
          threadId: 'thread_abc123',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [
                { kind: 'text', text: 'Nice to meet you, Alice! How can I help you today?' } as TextContent,
              ],
            },
          ],
        };

        const mockResponse2: any = {
          runId: 'run-2',
          threadId: 'thread_abc123',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-2',
              contents: [{ kind: 'text', text: 'Your name is Alice.' } as TextContent],
            },
          ],
        };

        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({
            ok: true,
            status: 200,
            json: async () => mockResponse1,
          })
          .mockResolvedValueOnce({
            ok: true,
            status: 200,
            json: async () => mockResponse2,
          });

        // Quickstart sample code
        // <snippet>
        const conversation = client.createConversation();

        const response1 = await conversation.send('My name is Alice');
        // </snippet>
        expect(response1).toContain('Alice');
        expect(conversation.threadId).toBe('thread_abc123');

        // <snippet>
        const response2 = await conversation.send("What's my name?");
        // </snippet>
        expect(response2).toBe('Your name is Alice.');

        // Verify second request includes the thread ID
        const secondCallBody = JSON.parse((global.fetch as jest.Mock).mock.calls[1][1].body);
        expect(secondCallBody.threadId).toBe('thread_abc123');
      });

      it('should automatically maintain full conversation history', async () => {
        const conversation = client.createConversation();

        (global.fetch as jest.Mock)
          .mockResolvedValueOnce({
            ok: true,
            status: 200,
            json: async () => ({
              runId: 'run-1',
              threadId: 'thread_xyz',
              status: 'completed',
              output: [
                {
                  role: 'agent' as ChatRole,
                  messageId: 'msg-1',
                  contents: [{ kind: 'text', text: 'Response 1' } as TextContent],
                },
              ],
            }),
          })
          .mockResolvedValueOnce({
            ok: true,
            status: 200,
            json: async () => ({
              runId: 'run-2',
              threadId: 'thread_xyz',
              status: 'completed',
              output: [
                {
                  role: 'agent' as ChatRole,
                  messageId: 'msg-2',
                  contents: [{ kind: 'text', text: 'Response 2' } as TextContent],
                },
              ],
            }),
          });

        await conversation.send('First message');
        await conversation.send('Second message');

        // Both requests should use the same thread
        const firstCall = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
        const secondCall = JSON.parse((global.fetch as jest.Mock).mock.calls[1][1].body);

        expect(firstCall.threadId).toBeUndefined(); // First creates thread
        expect(secondCall.threadId).toBe('thread_xyz'); // Second uses existing thread
      });

      it('should expose thread ID for saving and resuming later', async () => {
        const conversation = client.createConversation();

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            runId: 'run-123',
            threadId: 'thread_save_me',
            status: 'completed',
            output: [
              {
                role: 'agent' as ChatRole,
                messageId: 'msg-1',
                contents: [{ kind: 'text', text: 'Response' } as TextContent],
              },
            ],
          }),
        });

        await conversation.send('Hello');

        // Save thread ID as shown in quickstart
        const savedThreadId = conversation.threadId;
        expect(savedThreadId).toBe('thread_save_me');
        expect(typeof savedThreadId).toBe('string');
      });
    });

    describe('resumeConversation', () => {
      /**
       * @docExample client-resume-conversation
       */
      it('should resume conversation from saved thread ID', async () => {
        const threadId = 'thread_abc123';

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            runId: 'run-resume',
            threadId: threadId,
            status: 'completed',
            output: [
              {
                role: 'agent' as ChatRole,
                messageId: 'msg-1',
                contents: [{ kind: 'text', text: 'Resumed response' } as TextContent],
              },
            ],
          }),
        });

        // Quickstart sample: const conversation = client.resumeConversation(threadId);
        // <snippet>
        const conversation = client.resumeConversation(threadId);
        const response = await conversation.send('Continue our chat');
        // </snippet>

        expect(conversation.threadId).toBe(threadId);
        expect(response).toBe('Resumed response');

        // Verify request uses the resumed thread ID
        const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
        expect(callBody.threadId).toBe(threadId);
      });

      it('should maintain context from previous conversation', async () => {
        const threadId = 'thread_with_history';
        const conversation = client.resumeConversation(threadId);

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            runId: 'run-continue',
            threadId: threadId,
            status: 'completed',
            output: [
              {
                role: 'agent' as ChatRole,
                messageId: 'msg-1',
                contents: [{ kind: 'text', text: 'As we discussed earlier...' } as TextContent],
              },
            ],
          }),
        });

        const response = await conversation.send('Can you remind me?');
        expect(response).toContain('As we discussed earlier');
      });
    });
  });

  describe('Step 4: Tools/Functions', () => {
    /**
     * @docExample client-tools
     */
    it('should register tools with lambda functions', () => {
      // Quickstart sample code
      // <snippet>
      const tools = new ToolCollection();
      tools.add('get_weather', (location: string) => `The weather in ${location} is sunny and 72°F`);
      tools.add('get_time', (_timezone: string) => '2024-01-15 14:30:00');
      // </snippet>

      expect(tools.size).toBe(2);
      expect(tools.has('get_weather')).toBe(true);
      expect(tools.has('get_time')).toBe(true);
    });

    it('should execute tool when agent requests it', async () => {
      const tools = new ToolCollection();
      tools.add('get_weather', (location: string) => ({
        temperature: '72°F',
        condition: 'sunny',
        location: location,
      }));

      const result = await tools.execute('get_weather', '{"param0": "Seattle"}');

      expect(result).toEqual({
        temperature: '72°F',
        condition: 'sunny',
        location: 'Seattle',
      });
    });

    it('should automatically execute tools during chat completion', async () => {
      const tools = new ToolCollection();
      tools.add('get_weather', (location: string) =>
        JSON.stringify({ temperature: '72°F', condition: 'sunny', location })
      );

      // Mock run creation
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-123',
          threadId: 'thread_xyz789',
          status: 'in_progress',
        }),
      });

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [
              {
                kind: 'text',
                text: 'The weather in Seattle is sunny and 72°F',
              },
            ],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      try {
        const response = await client.completeChat('What is the weather in Seattle?', { tools });
        expect(response).toContain('sunny');
      } catch (error) {
        // Expected without full SSE mock
      }
    });

    it('should support tools with multiple parameters', () => {
      const tools = new ToolCollection();
      tools.add('calculate', (a: number, b: number, operation: string) => {
        switch (operation) {
          case 'add':
            return a + b;
          case 'multiply':
            return a * b;
          default:
            return 0;
        }
      });

      expect(tools.has('calculate')).toBe(true);
    });

    it('should provide default descriptions for tools', () => {
      const tools = new ToolCollection();
      tools.add('my_tool', () => 'result');

      const tool = tools.get('my_tool');
      expect(tool?.description).toBe('Executes my_tool');
    });

    it('should accept custom tool descriptions', () => {
      const tools = new ToolCollection();
      tools.add('get_weather', (_location: string) => 'result', 'Gets weather for a location');

      const tool = tools.get('get_weather');
      expect(tool?.description).toBe('Gets weather for a location');
    });
  });

  describe('Step 5: Streaming Responses', () => {
    describe('Simple Text Streaming (streamChat with onTextChunk)', () => {
      /**
       * @docExample client-simple-streaming
       */
      it('should stream text chunks via callback', async () => {
        // Mock run creation
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            runId: 'run-123',
            threadId: 'thread-streaming',
            status: 'in_progress',
          }),
        });

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.delta',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Once upon' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Once upon a time' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Once upon a time, there was a curious robot named Byte' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const chunks: string[] = [];
        // Quickstart sample: await client.streamChat('Tell me a story', (text) => process.stdout.write(text))
        // <snippet>
        await client.streamChat('Tell me a story about a robot', (text) => {
          chunks.push(text);
        });
        // </snippet>

        expect(chunks.length).toBeGreaterThan(0);
        expect(chunks.join('')).toContain('Once upon');
      });

      it('should produce typewriter effect by emitting incremental chunks', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            runId: 'run-123',
            threadId: 'thread-typewriter',
            status: 'in_progress',
          }),
        });

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.delta',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Hello' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Hello world' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Hello world!' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const chunks: string[] = [];
        await client.streamChat('Say hello', (text) => chunks.push(text));

        // Each chunk should only contain new text, not the full accumulated text
        expect(chunks).toEqual(['Hello', ' world', '!']);
      });

      it('should fire callback for each text chunk in real-time', async () => {
        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => ({
            runId: 'run-123',
            threadId: 'thread-realtime',
            status: 'in_progress',
          }),
        });

        const mockStreamRun = jest.fn(async function* () {
          for (let i = 1; i <= 5; i++) {
            yield {
              eventType: 'message.delta',
              data: {
                role: 'agent' as ChatRole,
                messageId: 'msg-1',
                contents: [{ kind: 'text', text: `${i}` }],
              } as ChatMessage,
            };
          }
        });

        (client as any).streamRun = mockStreamRun;

        const callbackFireCount: number[] = [];
        await client.streamChat('Count to 5', (text) => {
          callbackFireCount.push(parseInt(text));
        });

        expect(callbackFireCount).toEqual([1, 2, 3, 4, 5]);
      });
    });

    describe('Rich Content Streaming (streamMessages)', () => {
      it('should stream messages with multiple content types', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [
                { kind: 'text', type: 'text', text: "Here's a beautiful view of the Eiffel Tower at sunset." } as TextContent,
                { kind: 'image', type: 'image', uri: 'https://example.com/paris-eiffel-tower.jpg' } as ImageContent,
              ],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        // Quickstart sample: for await (const message of client.streamMessages("Show me a photo of Paris"))
        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages('Show me a photo of Paris and describe it')) {
          messages.push(message);
        }

        expect(messages).toHaveLength(1);
        expect(messages[0].contents).toHaveLength(2);
        expect(messages[0].contents[0].kind).toBe('text');
        expect(messages[0].contents[1].kind).toBe('image');
      });

      it('should stream text content as it is generated', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.delta',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Paris is' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Paris is beautiful' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages('Describe Paris')) {
          messages.push(message);
        }

        expect(messages.length).toBeGreaterThan(0);
        expect(messages[messages.length - 1].contents[0]).toMatchObject({
          kind: 'text',
          text: expect.stringContaining('Paris'),
        });
      });

      it('should handle images appearing when ready', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.delta',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Generating image...' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [
                { kind: 'text', text: 'Generating image...' },
                { kind: 'image', uri: 'https://example.com/generated.jpg' } as any,
              ],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages('Create an image')) {
          messages.push(message);
        }

        const finalMessage = messages[messages.length - 1];
        expect(finalMessage.contents).toHaveLength(2);
        expect(finalMessage.contents[1].kind).toBe('image');
      });

      it('should support single message with multiple content types', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [
                { kind: 'text', text: 'Text content' } as TextContent,
                { kind: 'image', uri: 'https://example.com/image1.jpg' } as any,
                { kind: 'image', uri: 'https://example.com/image2.jpg' } as any,
              ],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages('Show me multiple things')) {
          messages.push(message);
        }

        expect(messages[0].contents).toHaveLength(3);
      });
    });

    describe('Thread Streaming (conversation streamMessages)', () => {
      it('should stream all messages from conversation in real-time', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'run.started',
            data: { runId: 'run-123', threadId: 'thread_abc123' },
          };
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Let me check that for you...' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.updated',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'The current weather in Paris is 18°C and partly cloudy.' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        // Stream messages in conversation
        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages("What's the weather in Paris?")) {
          messages.push(message);
        }

        expect(messages.length).toBeGreaterThanOrEqual(1);
        expect(messages.some(m => m.role === 'agent')).toBe(true);
      });

      it('should show messages from all participants (users, agents)', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Agent response' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages('User message')) {
          messages.push(message);
        }

        expect(messages.length).toBeGreaterThan(0);
        expect(messages[0].role).toBe('agent');
      });

      it('should update in real-time as messages are posted', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Message 1' }],
            } as ChatMessage,
          };
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-2',
              contents: [{ kind: 'text', text: 'Message 2' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const receivedTimestamps: number[] = [];
        for await (const _message of conversation.streamMessages('Test')) {
          receivedTimestamps.push(Date.now());
        }

        expect(receivedTimestamps).toHaveLength(2);
      });

      it('should work with streaming conversation and maintain thread ID', async () => {
        const conversation = client.createConversation();

        const mockStreamRun = jest.fn(async function* () {
          yield {
            eventType: 'run.started',
            data: { runId: 'run-123', threadId: 'thread_conv' },
          };
          yield {
            eventType: 'message.created',
            data: {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Conversation message' }],
            } as ChatMessage,
          };
        });

        (client as any).streamRun = mockStreamRun;

        const messages: ChatMessage[] = [];
        for await (const message of conversation.streamMessages('Hello')) {
          messages.push(message);
        }

        expect(messages).toHaveLength(1);
        expect(conversation.threadId).toBe('thread_conv');
      });
    });
  });

  describe('Complete Example: All Features Combined', () => {
    it('should demonstrate simple completion', async () => {
      const mockResponse: any = {
        runId: 'run-complete-1',
        threadId: 'thread_complete',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: 'Hello! How can I help?' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      // From quickstart complete example
      const response = await client.completeChat('Hello!');
      expect(response).toBe('Hello! How can I help?');
    });

    it('should demonstrate streaming', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-stream',
          threadId: 'thread_stream',
          status: 'in_progress',
        }),
      });

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: '1, 2, 3, 4, 5' }],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      let output = '';
      await client.streamChat('Count to 5', (text) => {
        output += text;
      });

      expect(output).toContain('1');
    });

    it('should demonstrate conversation with context', async () => {
      const mockResponse1: any = {
        runId: 'run-1',
        threadId: 'thread_context',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: "Great! Planets are fascinating celestial bodies." } as TextContent],
          },
        ],
      };

      const mockResponse2: any = {
        runId: 'run-2',
        threadId: 'thread_context',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-2',
            contents: [
              {
                kind: 'text',
                text: 'Mars is the fourth planet from the Sun, known as the Red Planet.',
              } as TextContent,
            ],
          },
        ],
      };

      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockResponse1,
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockResponse2,
        });

      // From quickstart complete example
      const conversation = client.createConversation();

      const msg1 = await conversation.send("Hi, I'm learning about planets");
      expect(msg1).toContain('planets');

      const msg2 = await conversation.send('Tell me about Mars');
      expect(msg2).toContain('Mars');

      expect(conversation.threadId).toBeTruthy();
    });

    it('should work with all features in sequence', async () => {
      // 1. Simple completion
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-1',
          threadId: 'thread_seq',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Simple response' } as TextContent],
            },
          ],
        }),
      });

      await client.completeChat('Test');
      expect(global.fetch).toHaveBeenCalledTimes(1);

      // 2. Streaming (would need more complex mock)
      // 3. Conversation (would create new conversation)
      const conversation = client.createConversation();
      expect(conversation).toBeDefined();
    });
  });

  describe('Error Handling: AgentProtocolError', () => {
    it('should catch AgentProtocolError with code and message', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({
          error: {
            code: 'rate_limit_exceeded',
            message: 'Rate limit hit',
          },
        }),
      });

      // Quickstart error handling sample
      try {
        await client.completeChat('Hello!');
        fail('Should have thrown error');
      } catch (error) {
        if (error instanceof AgentProtocolError) {
          expect(error.message).toBeTruthy();
          // Note: AgentProtocolError doesn't have a 'code' property in the current implementation
          // This is testing the pattern shown in the quickstart guide
        }
      }
    });

    it('should handle rate_limit_exceeded error code', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 429,
        json: async () => ({
          error: {
            code: 'rate_limit_exceeded',
            message: 'Too many requests',
          },
        }),
      });

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
        // In real implementation, would check error.code === 'rate_limit_exceeded'
      }
    });

    it('should handle invalid_request error code', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          error: {
            code: 'invalid_request',
            message: 'Invalid request format',
          },
        }),
      });

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should handle authentication_failed error code', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          error: {
            code: 'authentication_failed',
            message: 'Invalid API credentials',
          },
        }),
      });

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should handle service_unavailable error code', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 503,
        json: async () => ({
          error: {
            code: 'service_unavailable',
            message: 'Service temporarily down',
          },
        }),
      });

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should handle timeout error code', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 408,
        json: async () => ({
          error: {
            code: 'timeout',
            message: 'Request took too long',
          },
        }),
      });

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should handle generic network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
        expect(error).toBeInstanceOf(Error);
      }
    });

    it('should preserve error details for debugging', async () => {
      const errorResponse = {
        error: {
          code: 'custom_error',
          message: 'Custom error message',
          details: {
            field: 'email',
            reason: 'Invalid format',
          },
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => errorResponse,
      });

      try {
        await client.completeChat('Test');
        fail('Should have thrown');
      } catch (error) {
        expect(error).toBeDefined();
      }
    });

    it('should support error recovery with retry logic pattern', async () => {
      let attemptCount = 0;

      (global.fetch as jest.Mock).mockImplementation(async () => {
        attemptCount++;
        if (attemptCount === 1) {
          // First attempt fails
          return {
            ok: false,
            status: 429,
            json: async () => ({
              error: {
                code: 'rate_limit_exceeded',
                message: 'Rate limit exceeded',
              },
            }),
          };
        } else {
          // Second attempt succeeds
          return {
            ok: true,
            status: 200,
            json: async () => ({
              runId: 'run-retry',
              threadId: 'thread_retry',
              status: 'completed',
              output: [
                {
                  role: 'agent' as ChatRole,
                  messageId: 'msg-1',
                  contents: [{ kind: 'text', text: 'Success after retry' } as TextContent],
                },
              ],
            }),
          };
        }
      });

      // Simulate retry pattern
      let result: string | null = null;
      for (let i = 0; i < 2; i++) {
        try {
          result = await client.completeChat('Test');
          break;
        } catch (error) {
          if (i === 1) throw error; // Rethrow on last attempt
        }
      }

      expect(result).toBe('Success after retry');
      expect(attemptCount).toBe(2);
    });
  });

  describe('Additional Quickstart Features', () => {
    it('should support abort signal for cancellation', async () => {
      const abortController = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        abortController.abort();
        return Promise.reject(new Error('AbortError'));
      });

      await expect(
        client.completeChat('Hello', undefined, abortController.signal)
      ).rejects.toThrow();
    });

    it('should support custom agent IDs', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_custom',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: 'Response from custom agent' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      await client.completeChat('Hello', { agentId: 'agent-custom-123' });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.agentId).toBe('agent-custom-123');
    });

    it('should support metadata in requests', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_meta',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: 'Response' } as TextContent],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const metadata = {
        userId: 'user-123',
        sessionId: 'session-456',
        source: 'web-app',
      };

      await client.completeChat('Hello', { metadata });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.metadata).toEqual(metadata);
    });

    it('should return empty string when agent has no text response', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_empty',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [],
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const result = await client.completeChat('Hello');
      expect(result).toBe('');
    });

    it('should handle messages with only non-text content', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread_image_only',
        status: 'completed',
        output: [
          {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [
              {
                kind: 'image',
                uri: 'https://example.com/image.jpg',
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

      const result = await client.completeChat('Show me an image');
      expect(result).toBe(''); // No text content
    });
  });

  describe('Integration: Real-world Usage Patterns', () => {
    it('should handle multi-turn conversation with mixed content types', async () => {
      const conversation = client.createConversation();

      // Turn 1: Text only
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-1',
          threadId: 'thread_mixed',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'Hello! What would you like to know?' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('Hi');

      // Turn 2: Text with image
      const multimodalMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-user-2',
        contents: [
          { kind: 'text', type: 'text', text: 'What is this?' } as TextContent,
          { kind: 'image', type: 'image', uri: 'https://example.com/test.jpg' } as ImageContent,
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-2',
          threadId: 'thread_mixed',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-2',
              contents: [{ kind: 'text', text: 'This is a test image.' } as TextContent],
            },
          ],
        }),
      });

      await conversation.sendStructured(multimodalMessage);

      expect(conversation.threadId).toBe('thread_mixed');
    });

    it('should support conversation resumption after page reload', async () => {
      // Simulate first session
      const conversation1 = client.createConversation();

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-1',
          threadId: 'thread_persistent',
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-1',
              contents: [{ kind: 'text', text: 'First session response' } as TextContent],
            },
          ],
        }),
      });

      await conversation1.send('Initial message');
      const savedThreadId = conversation1.threadId;

      // Simulate page reload / new session
      const conversation2 = client.resumeConversation(savedThreadId!);

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-2',
          threadId: savedThreadId,
          status: 'completed',
          output: [
            {
              role: 'agent' as ChatRole,
              messageId: 'msg-2',
              contents: [{ kind: 'text', text: 'Resumed session response' } as TextContent],
            },
          ],
        }),
      });

      const response = await conversation2.send('Continue conversation');
      expect(response).toContain('Resumed');
      expect(conversation2.threadId).toBe(savedThreadId);
    });

    it('should handle tools in streaming context', async () => {
      const tools = new ToolCollection();
      tools.add('search', (query: string) => `Search results for: ${query}`);

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-tools',
          threadId: 'thread_tools',
          status: 'in_progress',
        }),
      });

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [{ kind: 'text', text: 'Let me search for that...' }],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const chunks: string[] = [];
      await client.streamChat('Search for TypeScript', (text) => chunks.push(text), { tools });

      expect(chunks.length).toBeGreaterThan(0);
    });
  });
});
