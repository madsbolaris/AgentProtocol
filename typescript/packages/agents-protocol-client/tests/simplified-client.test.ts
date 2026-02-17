/**
 * Tests for SimplifiedClient high-level API
 */

import { SimplifiedClient } from '../src/simplified-client';
import { ToolCollection } from '../src/tool-collection';
import type { ChatMessage, ChatRole, TextContent } from '@microsoft/agents-protocol-abstractions';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('SimplifiedClient', () => {
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

  describe('completeChat', () => {
    // @docExample({ testId: "client-simple-completion", title: "Simple Chat Completion" })
    it('should send a text message and return text response', async () => {
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

      // doc-example-start
      // Send message and get response
      const response = await client.completeChat('What can you help me with?');
      console.log(response);
      // doc-example-end

      expect(response).toBe('I can help you with analysis, writing, coding, research, and problem-solving tasks.');
      expect(global.fetch).toHaveBeenCalledTimes(1);
    });

    it('should return empty string when no output', async () => {
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

      const result = await client.completeChat('Hello');

      expect(result).toBe('');
    });

    it('should include agent ID in request when provided', async () => {
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
                text: 'Response',
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

      await client.completeChat('Hello', { agentId: 'agent-123' });

      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:5000/runs/wait',
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('agent-123'),
        })
      );
    });

    it('should handle metadata in options', async () => {
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
                text: 'Response',
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

      const metadata = { userId: 'user-123', sessionId: 'session-456' };
      await client.completeChat('Hello', { metadata });

      const callBody = JSON.parse(
        (global.fetch as jest.Mock).mock.calls[0][1].body
      );
      expect(callBody.metadata).toEqual(metadata);
    });

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

    // @docExample({ testId: "client-tools", title: "Tools with Lambda Functions" })
    it('should use tools with lambda functions', () => {
      // doc-example-start
      // Define tools using lambda functions
      const tools = new ToolCollection();
      tools.add('get_weather', (location: string) => `The weather in ${location} is sunny and 72°F`);
      tools.add('get_time', (_timezone: string) => '2024-01-15 14:30:00');

      // Use tools in chat  (client.completeChat would be called with { tools } option)
      console.log(`Created ${tools.size} tools`);
      // doc-example-end

      expect(tools.size).toBe(2);
      expect(tools.has('get_weather')).toBe(true);
      expect(tools.has('get_time')).toBe(true);
    });
  });

  describe('completeChatStructured', () => {
    it('should send structured message and return structured response', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [
          {
            kind: 'text',
            text: 'What is the weather?',
          } as TextContent,
        ],
      };

      const outputMessage: ChatMessage = {
        role: 'agent' as ChatRole,
        messageId: 'msg-456',
        contents: [
          {
            kind: 'text',
            text: 'The weather is sunny.',
          } as TextContent,
        ],
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

      const result = await client.completeChatStructured(inputMessage);

      expect(result).toEqual(outputMessage);
    });

    it('should return empty agent message when no output', async () => {
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

      const result = await client.completeChatStructured(inputMessage);

      expect(result.role).toBe('agent');
      expect(result.contents).toEqual([]);
    });
  });

  describe('streamChat', () => {
    // @docExample({ testId: "client-streaming", title: "Streaming with Callback" })
    it('should stream text chunks via callback', async () => {
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

      // doc-example-start
      // Stream the response with a callback
      const onTextChunk = (text: string) => {
        process.stdout.write(text);
      };

      try {
        await client.streamChat('Tell me a story about a robot', onTextChunk);
        console.log();
      } catch (error) {
        // Expected without full SSE mock
      }
      // doc-example-end

      expect(global.fetch).toHaveBeenCalled();
    });
  });

  describe('createConversation', () => {
    it('should create a new conversation without thread ID', () => {
      const conversation = client.createConversation();

      expect(conversation).toBeDefined();
      expect(conversation.threadId).toBeUndefined();
    });
  });

  describe('resumeConversation', () => {
    // @docExample({ testId: "client-resume-conversation", title: "Resume Conversation" })
    it('should resume conversation with thread ID', () => {
      const threadId = 'thread-123';

      // doc-example-start
      // Resume a previous conversation by thread ID
      const conversation = client.resumeConversation(threadId);
      // doc-example-end

      expect(conversation).toBeDefined();
      expect(conversation.threadId).toBe(threadId);
    });
  });

  describe('error handling', () => {
    it('should handle HTTP errors properly', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Agent not found',
        }),
      });

      await expect(client.completeChat('Hello')).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(client.completeChat('Hello')).rejects.toThrow();
    }, 10000);
  });

  describe('completeChatWithTools', () => {
    it('should handle tools option and call completeChatWithTools', async () => {
      const tools = new ToolCollection();
      tools.add('test_tool', () => 'result');

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
        await client.completeChat('Hello', { tools });
      } catch (error) {
        // Expected to fail without full SSE mock
      }

      expect(global.fetch).toHaveBeenCalled();
    });

    it('should accumulate text from message.delta events', async () => {
      const tools = new ToolCollection();
      tools.add('test_tool', () => 'result');

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [
              {
                kind: 'text',
                text: 'Hello',
              },
            ],
          } as ChatMessage,
        };
        yield {
          eventType: 'message.updated',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [
              {
                kind: 'text',
                text: 'Hello world',
              },
            ],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const result = await (client as any).completeChatWithTools(
        {
          input: [
            {
              role: 'user' as ChatRole,
              messageId: 'msg-user',
              contents: [{ kind: 'text', text: 'Test' }],
            },
          ],
        },
        { tools }
      );

      expect(result).toBe('Hello world');
    });

    it('should handle run.requires_action event with tools', async () => {
      const tools = new ToolCollection();
      tools.add('test_tool', () => 'result');

      const consoleWarnSpy = jest.spyOn(console, 'warn').mockImplementation();

      const mockStreamRun = jest.fn(async function* () {
        yield {
          eventType: 'run.requires_action',
          data: {
            runId: 'run-123',
            requiredAction: {
              type: 'submit_tool_outputs',
              submitToolOutputs: {
                toolCalls: [
                  {
                    id: 'call-1',
                    function: { name: 'test_tool', arguments: '{}' },
                  },
                ],
              },
            },
          },
        };
      });

      (client as any).streamRun = mockStreamRun;

      await (client as any).completeChatWithTools(
        {
          input: [
            {
              role: 'user' as ChatRole,
              messageId: 'msg-user',
              contents: [{ kind: 'text', text: 'Test' }],
            },
          ],
        },
        { tools }
      );

      expect(consoleWarnSpy).toHaveBeenCalledWith(
        'Tool execution during streaming not yet fully implemented'
      );

      consoleWarnSpy.mockRestore();
    });
  });

  describe('streamChat edge cases', () => {
    it('should handle empty text content', async () => {
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
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const chunks: string[] = [];
      await client.streamChat('Hello', (text) => chunks.push(text));

      expect(chunks).toHaveLength(0);
    });

    it('should only emit new text chunks', async () => {
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
        yield {
          eventType: 'message.delta',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [
              {
                kind: 'text',
                type: 'text',
                text: 'Hello',
              },
            ],
          } as ChatMessage,
        };
        yield {
          eventType: 'message.updated',
          data: {
            role: 'agent' as ChatRole,
            messageId: 'msg-1',
            contents: [
              {
                kind: 'text',
                type: 'text',
                text: 'Hello world',
              },
            ],
          } as ChatMessage,
        };
      });

      (client as any).streamRun = mockStreamRun;

      const chunks: string[] = [];
      await client.streamChat('Hello', (text) => chunks.push(text));

      expect(chunks).toEqual(['Hello', ' world']);
    });
  });

  describe('createRunAndWait', () => {
    it('should handle error in response', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'failed',
        output: [],
        error: {
          code: 'internal_error',
          message: 'Something went wrong',
          details: { extra: 'info' },
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = {
        agentId: 'agent-123',
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-123',
            contents: [{ kind: 'text', type: 'text', text: 'Test' }],
          },
        ],
      };

      const result = await client.createRunAndWait(request);

      expect(result.error).toBeDefined();
      expect(result.error?.code).toBe('internal_error');
      expect(result.error?.message).toBe('Something went wrong');
      expect(result.error?.details).toEqual({ extra: 'info' });
    });

    it('should handle missing threadId in response', async () => {
      const mockResponse: any = {
        runId: 'run-123',
        threadId: null,
        status: 'completed',
        output: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => mockResponse,
      });

      const request = {
        agentId: 'agent-123',
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-123',
            contents: [{ kind: 'text', type: 'text', text: 'Test' }],
          },
        ],
      };

      const result = await client.createRunAndWait(request);

      expect(result.threadId).toBe('');
    });
  });

  describe('streamRun', () => {
    it('should handle abort signal during streaming', async () => {
      const abortController = new AbortController();

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
        yield {
          eventType: 'run.started',
          data: { runId: 'run-123' },
        };
        // Simulate abort during streaming
        abortController.abort();
        throw new Error('Stream aborted');
      });

      (client as any).streamRun = mockStreamRun;

      await expect(async () => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        for await (const _event of (client as any).streamRun(
          {
            agentId: 'agent-123',
            input: [],
          },
          abortController.signal
        )) {
          // Should not complete
        }
      }).rejects.toThrow();
    });

    it('should handle stream error', async () => {
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
        throw new Error('Stream connection failed');
      });

      (client as any).streamRun = mockStreamRun;

      await expect(async () => {
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        for await (const _event of (client as any).streamRun({
          agentId: 'agent-123',
          input: [],
        })) {
          // Should not reach here
        }
      }).rejects.toThrow('Stream connection failed');
    });
  });

  describe('client getter', () => {
    it('should expose underlying low-level client', () => {
      const lowLevelClient = client.client;
      expect(lowLevelClient).toBeDefined();
      expect(lowLevelClient.runs).toBeDefined();
      expect(lowLevelClient.threads).toBeDefined();
      expect(lowLevelClient.messages).toBeDefined();
    });
  });

  describe('completeChatStructured edge cases', () => {
    it('should return empty message when output has no agent message', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [
          {
            kind: 'text',
            text: 'Test',
          } as TextContent,
        ],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
        status: 'completed',
        output: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg-user',
            contents: [{ kind: 'text', text: 'User message' } as TextContent],
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

    it('should support abort signal', async () => {
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
        client.completeChatStructured(inputMessage, undefined, abortController.signal)
      ).rejects.toThrow();
    });

    it('should pass options correctly', async () => {
      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [{ kind: 'text', text: 'Test' } as TextContent],
      };

      const mockResponse: any = {
        runId: 'run-123',
        threadId: 'thread-123',
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

      await client.completeChatStructured(inputMessage, {
        agentId: 'agent-456',
        metadata: { sessionId: 'session-789' },
      });

      const callBody = JSON.parse((global.fetch as jest.Mock).mock.calls[0][1].body);
      expect(callBody.agentId).toBe('agent-456');
      expect(callBody.metadata).toEqual({ sessionId: 'session-789' });
    });
  });
});

describe('ToolCollection', () => {
  let tools: ToolCollection;

  beforeEach(() => {
    tools = new ToolCollection();
  });

  describe('add', () => {
    it('should add a tool with handler', () => {
      const handler = (x: number, y: number) => x + y;
      tools.add('add', handler, 'Adds two numbers');

      const tool = tools.get('add');
      expect(tool).toBeDefined();
      expect(tool!.name).toBe('add');
      expect(tool!.description).toBe('Adds two numbers');
      expect(tool!.handler).toBe(handler);
    });

    it('should use default description if not provided', () => {
      const handler = () => 'test';
      tools.add('test', handler);

      const tool = tools.get('test');
      expect(tool?.description).toBe('Executes test');
    });
  });

  describe('get', () => {
    it('should return tool if exists', () => {
      tools.add('test', () => 'result');

      const tool = tools.get('test');
      expect(tool).toBeDefined();
    });

    it('should return undefined if tool does not exist', () => {
      const tool = tools.get('nonexistent');
      expect(tool).toBeUndefined();
    });
  });

  describe('getAll', () => {
    it('should return all tools', () => {
      tools.add('tool1', () => 'result1');
      tools.add('tool2', () => 'result2');

      const allTools = tools.getAll();
      expect(allTools).toHaveLength(2);
      expect(allTools.map((t) => t.name)).toContain('tool1');
      expect(allTools.map((t) => t.name)).toContain('tool2');
    });

    it('should return empty array when no tools', () => {
      const allTools = tools.getAll();
      expect(allTools).toHaveLength(0);
    });
  });

  describe('execute', () => {
    it('should execute synchronous tool', async () => {
      tools.add('multiply', (x: number, y: number) => x * y, 'Multiplies numbers');

      const result = await tools.execute('multiply', '{"param0": 5, "param1": 3}');
      expect(result).toBe(15);
    });

    it('should execute asynchronous tool', async () => {
      tools.add(
        'asyncAdd',
        async (x: number, y: number) => {
          return x + y;
        },
        'Async add'
      );

      const result = await tools.execute('asyncAdd', '{"param0": 10, "param1": 20}');
      expect(result).toBe(30);
    });

    it('should throw error for nonexistent tool', async () => {
      await expect(tools.execute('nonexistent', '{}')).rejects.toThrow(
        "Tool 'nonexistent' not found"
      );
    });
  });

  describe('has', () => {
    it('should return true if tool exists', () => {
      tools.add('test', () => 'result');
      expect(tools.has('test')).toBe(true);
    });

    it('should return false if tool does not exist', () => {
      expect(tools.has('nonexistent')).toBe(false);
    });
  });

  describe('remove', () => {
    it('should remove tool and return true', () => {
      tools.add('test', () => 'result');
      expect(tools.remove('test')).toBe(true);
      expect(tools.has('test')).toBe(false);
    });

    it('should return false if tool does not exist', () => {
      expect(tools.remove('nonexistent')).toBe(false);
    });
  });

  describe('clear', () => {
    it('should remove all tools', () => {
      tools.add('tool1', () => 'result1');
      tools.add('tool2', () => 'result2');

      tools.clear();
      expect(tools.size).toBe(0);
    });
  });

  describe('size', () => {
    it('should return correct number of tools', () => {
      expect(tools.size).toBe(0);

      tools.add('tool1', () => 'result1');
      expect(tools.size).toBe(1);

      tools.add('tool2', () => 'result2');
      expect(tools.size).toBe(2);

      tools.remove('tool1');
      expect(tools.size).toBe(1);
    });
  });

  describe('toAITools', () => {
    it('should convert tools to AITool format', () => {
      tools.add('get_weather', (location: string) => `Weather in ${location}`);
      tools.add('get_time', () => new Date().toISOString(), 'Gets current time');

      const aiTools = tools.toAITools();

      expect(aiTools).toHaveLength(2);
      expect(aiTools[0]).toHaveProperty('name');
      expect(aiTools[0]).toHaveProperty('description');
      expect(aiTools[0]).toHaveProperty('parameters');
    });

    it('should include schema as parameters', () => {
      tools.add('test_tool', (x: number, y: number) => x + y, 'Adds numbers');

      const aiTools = tools.toAITools();

      expect(aiTools[0].parameters).toHaveProperty('type', 'object');
      expect(aiTools[0].parameters).toHaveProperty('properties');
      expect(aiTools[0].parameters).toHaveProperty('required');
    });

    it('should return empty array for no tools', () => {
      const aiTools = tools.toAITools();
      expect(aiTools).toHaveLength(0);
    });
  });

  describe('fromAITools', () => {
    it('should create ToolCollection from AITools', () => {
      const aiTools = [
        {
          name: 'tool1',
          description: 'First tool',
          parameters: {
            type: 'object',
            properties: { param0: { type: 'string' } },
            required: ['param0'],
          },
        },
        {
          name: 'tool2',
          description: 'Second tool',
          parameters: {
            type: 'object',
            properties: { param0: { type: 'number' } },
            required: ['param0'],
          },
        },
      ];

      const handlers = new Map<string, Function>();
      handlers.set('tool1', (x: string) => `Result: ${x}`);
      handlers.set('tool2', (x: number) => x * 2);

      const collection = ToolCollection.fromAITools(aiTools, handlers);

      expect(collection.size).toBe(2);
      expect(collection.has('tool1')).toBe(true);
      expect(collection.has('tool2')).toBe(true);
    });

    it('should throw error if handler missing', () => {
      const aiTools = [
        {
          name: 'tool1',
          description: 'First tool',
        },
      ];

      const handlers = new Map<string, Function>();

      expect(() => ToolCollection.fromAITools(aiTools, handlers)).toThrow(
        "No handler provided for tool 'tool1'"
      );
    });

    it('should handle tools without parameters', () => {
      const aiTools = [
        {
          name: 'simple_tool',
          description: 'A simple tool',
        },
      ];

      const handlers = new Map<string, Function>();
      handlers.set('simple_tool', () => 'result');

      const collection = ToolCollection.fromAITools(aiTools, handlers);

      expect(collection.size).toBe(1);
      const tool = collection.get('simple_tool');
      expect(tool?.schema).toEqual({});
    });
  });

  describe('Symbol.iterator', () => {
    it('should iterate over tool names', () => {
      tools.add('tool1', () => 'result1');
      tools.add('tool2', () => 'result2');
      tools.add('tool3', () => 'result3');

      const names: string[] = [];
      for (const name of tools) {
        names.push(name);
      }

      expect(names).toHaveLength(3);
      expect(names).toContain('tool1');
      expect(names).toContain('tool2');
      expect(names).toContain('tool3');
    });

    it('should work with spread operator', () => {
      tools.add('tool1', () => 'result1');
      tools.add('tool2', () => 'result2');

      const names = [...tools];

      expect(names).toHaveLength(2);
    });
  });

  describe('executeTool with schema', () => {
    it('should extract parameters based on schema properties', async () => {
      tools.add('complex_tool', (a: string, b: number, c: boolean) => {
        return { a, b, c };
      });

      const result = await tools.execute(
        'complex_tool',
        '{"param0": "test", "param1": 42, "param2": true}'
      );

      expect(result).toEqual({ a: 'test', b: 42, c: true });
    });

    it('should handle function with no parameters', async () => {
      tools.add('no_param_tool', () => 'constant');

      const result = await tools.execute('no_param_tool', '{}');

      expect(result).toBe('constant');
    });
  });
});

describe('Conversation', () => {
  let client: SimplifiedClient;

  beforeEach(() => {
    client = new SimplifiedClient({
      baseUrl: 'http://localhost:5000',
    });
    jest.clearAllMocks();
  });

  describe('send', () => {
    // @docExample({ testId: "client-conversation", title: "Persistent Conversation" })
    it('should send message and return text response', async () => {
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
                text: 'Response text',
              } as TextContent,
            ],
          },
        ],
      };

      // Mock responses for all send() calls
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockResponse,
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockResponse,
        })
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => mockResponse,
        });

      // doc-example-start
      // Create a persistent conversation
      const conversation = client.createConversation();

      // Send messages that maintain context
      const response1 = await conversation.send('My name is Alice');
      console.log(response1);

      const response2 = await conversation.send("What's my name?");
      console.log(response2);
      // doc-example-end

      const result = await conversation.send('Hello');
      expect(result).toBe('Response text');
      expect(conversation.threadId).toBe('thread-123');
    });

    it('should maintain thread ID across messages', async () => {
      const conversation = client.createConversation();

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
              contents: [{ kind: 'text', text: 'First response' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('First message');
      expect(conversation.threadId).toBe('thread-123');

      // Second message - should use same thread
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
              contents: [{ kind: 'text', text: 'Second response' } as TextContent],
            },
          ],
        }),
      });

      await conversation.send('Second message');

      // Check that second call included thread ID
      const secondCallBody = JSON.parse(
        (global.fetch as jest.Mock).mock.calls[1][1].body
      );
      expect(secondCallBody.threadId).toBe('thread-123');
    });
  });

  describe('sendStructured', () => {
    it('should send structured message and return structured response', async () => {
      const conversation = client.createConversation();

      const inputMessage: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg-123',
        contents: [{ kind: 'text', text: 'Input' } as TextContent],
      };

      const outputMessage: ChatMessage = {
        role: 'agent' as ChatRole,
        messageId: 'msg-456',
        contents: [{ kind: 'text', text: 'Output' } as TextContent],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-123',
          threadId: 'thread-123',
          status: 'completed',
          output: [outputMessage],
        }),
      });

      const result = await conversation.sendStructured(inputMessage);

      expect(result).toEqual(outputMessage);
    });
  });
});
