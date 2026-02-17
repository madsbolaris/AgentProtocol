/**
 * Comprehensive tests for Hosting SDK Quickstart samples
 *
 * These tests validate all code samples from the hosting quickstart guide:
 * - Step 1: Hello World (AgentHost with config)
 * - Step 2: Adding Tools (functions array with getWeather, getTime)
 * - Tool Error Handling (fetch errors in tools)
 * - Step 3: Client-Provided Functions (allowClientFunctions: true)
 * - Step 4: Command Router Middleware (async generator function)
 * - Step 4: Reaction Handler Middleware (MessageReactionContent)
 * - Step 4: Uppercase Content Streaming Middleware (AsyncIterable<TextContent>)
 * - Step 4: Time Streaming Middleware (Before/After with next callback)
 * - Step 4: Message Middleware (Message-level timing)
 * - Step 4: Error Middleware (try/catch with next)
 * - Step 6: Persistent Conversations (In-Memory Storage)
 * - Step 6: Durable Storage (SqlStorageProvider)
 */

import { AgentHostBuilder } from '../src/builder/AgentHostBuilder.js';
import { AgentHost } from '../src/hosting/AgentHost.js';
import { InMemoryStorage } from '../src/storage/InMemoryStorage.js';
import { TurnResult } from '../src/core/TurnResult.js';
import { ChatMessage, ReactionContent } from '../src/core/types.js';
import { IAgentContext } from '../src/core/IAgentContext.js';

// Type aliases for middleware signatures
type AIContentChunk = any;
type IStreamable = any;
type Thread = any;
type TextContentChunk = any;

// Simple middleware (default case - 80%)
type Middleware<T extends IStreamable = IStreamable> = (
  stream: AsyncIterable<T>,
  thread: Thread
) => AsyncIterable<IStreamable>;

// Chained middleware (advanced case - 20%)
type ChainedMiddleware<T extends IStreamable = IStreamable> = (
  stream: AsyncIterable<T>,
  thread: Thread,
  next: (stream: AsyncIterable<IStreamable>) => Promise<AsyncIterable<T>>
) => Promise<AsyncIterable<IStreamable>>;

type MessageMiddleware = (
  message: ChatMessage,
  thread: Thread,
  next: () => Promise<void>
) => Promise<void>;

describe('Hosting SDK Quickstart Samples', () => {
  let currentPort = 4000; // Start from 4000 to avoid conflicts

  afterEach(async () => {
    // Increment port for next test
    currentPort++;
    // Add small delay to ensure port is fully released
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  describe('Step 1: Hello World', () => {
    /**
     * @docExample hosting-hello-world
     */
    it('should create basic agent with model and instructions', () => {
      // Sample from quickstart guide
      // <snippet>
      import { AgentHost, AgentConfig } from "@microsoft/agents-protocol-hosting";

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!
      };

      const agent = new AgentHost(config);
      agent.listen(5000);
      // </snippet>

      expect(agent).toBeDefined();
      expect(agent).toBeInstanceOf(AgentHost);
    });

    it('should process messages with basic configuration', async () => {
      const host = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      const response = await host.processMessage('Hello!');

      expect(response).toBeDefined();
      expect(response?.kind).toBe('text');
      if (response?.kind === 'text') {
        expect(response.text).toBe('Response from agent');
      }
    });

    it('should start and listen on specified port', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      const host = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      await host.start(currentPort);

      expect(consoleLogSpy).toHaveBeenCalledWith(`Agent host started on port ${currentPort}`);

      await host.stop();
      consoleLogSpy.mockRestore();
    });
  });

  describe('Step 2: Adding Tools', () => {
    /**
     * @docExample hosting-adding-tools
     */
    it('should support getWeather and getTime functions', () => {
      // Sample from quickstart guide
      // <snippet>
      import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';

      function getWeather(location: string): string {
          // In production, call a real weather API
          return `The weather in ${location} is sunny and 72°F`;
      }

      function getTime(): string {
          return new Date().toISOString();
      }

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          functions: [
              { name: "get_weather", description: "Get current weather for a location", fn: getWeather },
              { name: "get_time", description: "Get current time in UTC", fn: getTime }
          ]
      };

      const agent = new AgentHost(config);
      // </snippet>

      expect(agent).toBeDefined();
    });

    it('should execute weather function correctly', () => {
      function getWeather(location: string): string {
        return `The weather in ${location} is sunny and 72°F`;
      }

      const result = getWeather('Seattle');
      expect(result).toBe('The weather in Seattle is sunny and 72°F');
    });

    it('should execute time function correctly', () => {
      function getTime(): string {
        return new Date().toISOString();
      }

      const result = getTime();
      expect(result).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/);
    });
  });

  describe('Tool Error Handling', () => {
    /**
     * @docExample hosting-tool-error-handling
     */
    it('should handle fetch errors gracefully', async () => {
      // Sample from quickstart guide
      // <snippet>
      async function getWeather(location: string): Promise<string> {
        try {
          const response = await fetch(
            `https://api.weather.com/v1/current?location=${location}`
          );
          if (!response.ok) throw new Error(`HTTP ${response.status}`);
          const data = await response.json();
          return `Weather in ${location}: ${data.temp}°F`;
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          return `Sorry, couldn't fetch weather: ${errorMsg}`;
        }
      }
      // </snippet>

      // Test error handling
      const result = await getWeather('InvalidCity');
      expect(result).toContain("Sorry, couldn't fetch weather");
    });

    it('should return error message without throwing', async () => {
      async function getWeatherWithError(location: string): Promise<string> {
        try {
          throw new Error('Network timeout');
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          return `Sorry, couldn't fetch weather: ${errorMsg}`;
        }
      }

      const result = await getWeatherWithError('Seattle');
      expect(result).toBe("Sorry, couldn't fetch weather: Network timeout");
    });

    it('should handle various error types', async () => {
      async function getWeather(location: string): Promise<string> {
        try {
          if (location === 'throw_error') {
            throw new Error('Test error');
          } else if (location === 'throw_string') {
            throw 'String error';
          } else {
            return `Weather in ${location}: 72°F`;
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          return `Sorry, couldn't fetch weather: ${errorMsg}`;
        }
      }

      expect(await getWeather('throw_error')).toBe("Sorry, couldn't fetch weather: Test error");
      expect(await getWeather('throw_string')).toBe("Sorry, couldn't fetch weather: String error");
      expect(await getWeather('Seattle')).toBe("Weather in Seattle: 72°F");
    });
  });

  describe('Step 3: Client-Provided Functions', () => {
    /**
     * @docExample hosting-client-functions
     */
    it('should enable client functions with allowClientFunctions flag', () => {
      // Sample from quickstart guide
      // <snippet>
      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          allowClientFunctions: true  // Enable client functions
      };
      const agent = new AgentHost(config);
      // </snippet>

      expect(agent).toBeDefined();
    });

    it('should document client-side tool pattern', () => {
      // This test documents the client-side pattern from the quickstart
      // In practice, clients would provide tools via the protocol request

      const clientSideTools = {
        send_email: async (to: string, subject: string, body: string = '') => {
          console.log(`📧 Sending email to ${to}: ${subject}`);
          return "Email sent successfully";
        },
        get_local_files: async () => {
          return "Found 15 files: file1.txt, file2.py, README.md, config.json, package.json";
        }
      };

      expect(clientSideTools.send_email).toBeDefined();
      expect(clientSideTools.get_local_files).toBeDefined();
    });
  });

  describe('Step 4: Command Router Middleware', () => {
    /**
     * @docExample hosting-command-router
     */
    it('should route /help command without calling LLM', async () => {
      // Sample from quickstart guide

      // <snippet>
      import { TextContent, Thread } from '@microsoft/agents-protocol';

      async function* commandRouter(
          content: TextContent,
          thread: Thread
      ): AsyncIterable<IStreamable> {
          // Check if it's the /help command
          if (content.text.trim() === "/help") {
              // Handle command - return result without calling LLM
              yield new TextContent({
                  text: "Available commands:\n/help - Show this help"
              });
          } else {
              // Pass through to LLM
              yield content;
          }
      }

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          middleware: [
              [TextContent, commandRouter]
          ]
      };

      const agent = new AgentHost(config);
      // </snippet>

      // Test the router
      const helpResult: any[] = [];
      for await (const item of commandRouter({ text: '/help' })) {
        helpResult.push(item);
      }

      expect(helpResult).toHaveLength(1);
      expect(helpResult[0].text).toContain('/help - Show this help');
    });

    it('should pass through non-command messages', async () => {
      async function* commandRouter(content: any): AsyncIterable<any> {
        if (content?.text?.trim() === '/help') {
          yield {
            kind: 'text',
            text: 'Available commands:\n/help - Show this help'
          };
        } else {
          yield content;
        }
      }

      const passThrough: any[] = [];
      for await (const item of commandRouter({ text: 'Hello, how are you?' })) {
        passThrough.push(item);
      }

      expect(passThrough).toHaveLength(1);
      expect(passThrough[0].text).toBe('Hello, how are you?');
    });
  });

  describe('Step 4: Reaction Handler Middleware', () => {
    /**
     * @docExample hosting-reaction-handler
     */
    it('should convert reactions to developer messages', async () => {
      // Sample from quickstart guide
      // <snippet>
      import { MessageReactionContent, DeveloperMessage, TextContent } from '@microsoft/agents-protocol';

      async function* handleReactions(
          reaction: MessageReactionContent,
          thread: Thread
      ): AsyncIterable<IStreamable> {
          // Convert reaction to a message the agent can understand
          const developerMsg = new DeveloperMessage({
              content: [
                  new TextContent({
                      text: `User reacted with ${reaction.emoji} to a previous message.`
                  })
              ]
          });
          yield reaction;
          yield developerMsg;  // Yield so LLM can process the notification
      }

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          middleware: [
              [MessageReactionContent, handleReactions],
          ]
      };
      // </snippet>

      const results: any[] = [];
      const testReaction = { emoji: '👍', messageId: 'msg123' };

      for await (const item of handleReactions(testReaction)) {
        results.push(item);
      }

      expect(results).toHaveLength(2);
      expect(results[0]).toEqual(testReaction);
      expect(results[1].kind).toBe('developer');
      expect(results[1].content[0].text).toContain('reacted with 👍');
    });

    it('should handle different emoji types', async () => {
      async function* handleReactions(reaction: any): AsyncIterable<any> {
        const developerMsg = {
          kind: 'developer',
          content: [{
            kind: 'text',
            text: `User reacted with ${reaction.emoji} to a previous message.`
          }]
        };
        yield reaction;
        yield developerMsg;
      }

      const emojis = ['👍', '❤️', '😊', '🎉'];

      for (const emoji of emojis) {
        const results: any[] = [];
        for await (const item of handleReactions({ emoji })) {
          results.push(item);
        }

        expect(results[1].content[0].text).toContain(`reacted with ${emoji}`);
      }
    });
  });

  describe('Step 4: Uppercase Content Streaming Middleware', () => {
    /**
     * @docExample hosting-streaming-middleware
     */
    it('should uppercase streamed content chunks', async () => {
      // Sample from quickstart guide
      // <snippet>
      async function* uppercaseContent(
          stream: AsyncIterable<TextContentChunk>,
          thread: Thread
      ): AsyncIterable<IStreamable> {
          for await (const chunk of stream) {
              chunk.text = chunk.text.toUpperCase();
              yield chunk;
          }
      }

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          middleware: [
              [TextContent, uppercaseContent],
          ]
      };
      // </snippet>

      // Create test stream
      async function* testStream() {
        yield { kind: 'text', text: 'hello' };
        yield { kind: 'text', text: 'world' };
      }

      const results: any[] = [];
      for await (const chunk of uppercaseContent(testStream())) {
        results.push(chunk);
      }

      expect(results).toHaveLength(2);
      expect(results[0].text).toBe('HELLO');
      expect(results[1].text).toBe('WORLD');
    });

    it('should preserve other chunk properties', async () => {
      async function* uppercaseContent(chunks: AsyncIterable<any>): AsyncIterable<any> {
        for await (const chunk of chunks) {
          chunk.text = chunk.text.toUpperCase();
          yield chunk;
        }
      }

      async function* testStream() {
        yield { kind: 'text', text: 'test', id: '123', metadata: { foo: 'bar' } };
      }

      const results: any[] = [];
      for await (const chunk of uppercaseContent(testStream())) {
        results.push(chunk);
      }

      expect(results[0].text).toBe('TEST');
      expect(results[0].id).toBe('123');
      expect(results[0].metadata).toEqual({ foo: 'bar' });
    });
  });

  describe('Step 4: Time Streaming Middleware (Before/After with next)', () => {
    /**
     * @docExample hosting-before-after
     */
    it('should execute code before and after stream processing', async () => {
      // Sample from quickstart guide - next() callback pattern
      const logs: string[] = [];

      // <snippet>
      const timeStreaming: ChainedMiddleware<TextContentChunk> = async function (
          stream: AsyncIterable<TextContentChunk>,
          thread: Thread,
          next: (stream: AsyncIterable<IStreamable>) => Promise<AsyncIterable<TextContentChunk>>
      ): Promise<AsyncIterable<IStreamable>> {
          const start = Date.now();
          console.log("🚀 Starting stream");

          const result = await next(stream);

          console.log(`✅ Stream completed in ${Date.now() - start}ms`);

          return result;
      };

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          middleware: [
              [TextContent, timeStreaming],
          ]
      };
      // </snippet>

      // Mock next function that processes the stream
      async function mockNext(stream: AsyncIterable<any>): Promise<void> {
        for await (const chunk of stream) {
          // Process chunks
          await new Promise(resolve => setTimeout(resolve, 10));
        }
      }

      // Test stream
      async function* testStream() {
        yield { text: 'chunk1' };
        yield { text: 'chunk2' };
      }

      await timeStreaming(testStream(), mockNext);

      expect(logs).toHaveLength(2);
      expect(logs[0]).toBe('🚀 Starting stream');
      expect(logs[1]).toMatch(/✅ Stream completed in \d+ms/);
    });

    it('should measure elapsed time accurately', async () => {
      const start = Date.now();

      async function timeStreaming(
        chunks: AsyncIterable<any>,
        next: (stream: AsyncIterable<any>) => Promise<void>
      ): Promise<number> {
        const startTime = Date.now();
        await next(chunks);
        return Date.now() - startTime;
      }

      async function mockNext(stream: AsyncIterable<any>): Promise<void> {
        for await (const chunk of stream) {
          await new Promise(resolve => setTimeout(resolve, 20));
        }
      }

      async function* testStream() {
        yield { text: 'test' };
      }

      const elapsed = await timeStreaming(testStream(), mockNext);
      expect(elapsed).toBeGreaterThanOrEqual(15);
    });
  });

  describe('Step 4: Message Middleware (Message-level timing)', () => {
    /**
     * @docExample hosting-message-middleware
     */
    it('should time entire message processing', async () => {
      // Sample from quickstart guide
      const logs: string[] = [];

      // <snippet>
      const timingMiddleware: MessageMiddleware = async function (
          message: ChatMessage,
          thread: Thread,
          next: () => Promise<void>
      ): Promise<void> {
          const start = Date.now();
          console.log(`⏱️ Processing started for thread ${thread.id}`);

          await next();  // Let other middleware and LLM process

          const elapsed = Date.now() - start;
          console.log(`✅ Completed in ${elapsed}ms`);
      };

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          middleware: [timingMiddleware]
      };
      // </snippet>

      // Test implementation
      async function testTimingMiddleware(
        message: any,
        thread: any,
        next: () => Promise<void>
      ): Promise<void> {
        const start = Date.now();
        logs.push(`⏱️ Processing started for thread ${thread.id}`);

        await next();

        const elapsed = Date.now() - start;
        logs.push(`✅ Completed in ${elapsed}ms`);
      }

      // Mock next function
      async function mockNext(): Promise<void> {
        await new Promise(resolve => setTimeout(resolve, 50));
      }

      const testMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Hello' }]
      };

      const testThread = {
        id: 'thread123',
        messages: [testMessage],
        addMessage: jest.fn()
      };

      await testTimingMiddleware(testMessage, testThread, mockNext);

      expect(logs).toHaveLength(2);
      expect(logs[0]).toContain('Processing started for thread thread123');
      expect(logs[1]).toMatch(/Completed in \d+ms/);
    });

    it('should work with onUserMessage handler pattern', async () => {
      let processingStarted = false;
      let processingCompleted = false;

      async function timingWrapper(
        message: ChatMessage,
        ctx: IAgentContext
      ): Promise<TurnResult> {
        processingStarted = true;

        // Simulate processing
        await ctx.logAsync(`Processing message: ${message.text}`);

        processingCompleted = true;
        return TurnResult.Continue;
      }

      const storage = new InMemoryStorage();
      const mockContext: IAgentContext = {
        runId: 'run1',
        threadId: 'thread1',
        logAsync: jest.fn().mockResolvedValue(undefined),
        respondAsync: jest.fn().mockResolvedValue(undefined),
        streamAsync: jest.fn().mockResolvedValue(undefined),
        getStateAsync: jest.fn(),
        setStateAsync: jest.fn(),
        deleteStateAsync: jest.fn(),
        getStateKeysAsync: jest.fn(),
        pauseForApprovalAsync: jest.fn().mockResolvedValue(undefined),
        recordMetric: jest.fn(),
        addTraceAttribute: jest.fn(),
        getTraceId: jest.fn().mockReturnValue('trace-123')
      };

      const message: ChatMessage = {
        text: 'Test message',
        timestamp: new Date()
      };

      const result = await timingWrapper(message, mockContext);

      expect(processingStarted).toBe(true);
      expect(processingCompleted).toBe(true);
      expect(result).toBe(TurnResult.Continue);
      expect(mockContext.logAsync).toHaveBeenCalledWith('Processing message: Test message');
    });
  });

  describe('Step 4: Error Middleware (try/catch with next)', () => {
    /**
     * @docExample hosting-error-handling
     */
    it('should catch errors and add error message to thread', async () => {
      // Sample from quickstart guide
      const errors: string[] = [];

      // <snippet>
      async function errorMiddleware(
          message: ChatMessage,
          thread: Thread,
          next: () => Promise<void>
      ): Promise<void> {
          try {
              await next();
          } catch (error) {
              const errorMsg = error instanceof Error ? error.message : String(error);
              console.error(`❌ Error: ${errorMsg}`);
              const errorResponse = new AgentMessage({
                  content: [new TextContent({ text: "Sorry, something went wrong." })]
              });
              thread.addMessage(errorResponse);
          }
      }

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          middleware: [errorMiddleware]
      };
      // </snippet>

      // Test implementation
      async function testErrorMiddleware(
        message: any,
        thread: any,
        next: () => Promise<void>
      ): Promise<void> {
        try {
          await next();
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          errors.push(`❌ Error: ${errorMsg}`);
          const errorResponse = {
            content: [{ text: 'Sorry, something went wrong.' }]
          };
          thread.addMessage(errorResponse);
        }
      }

      // Mock next that throws
      async function throwingNext(): Promise<void> {
        throw new Error('Something went wrong');
      }

      const testMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Test' }]
      };

      const addedMessages: any[] = [];
      const testThread = {
        id: 'thread123',
        messages: [testMessage],
        addMessage: jest.fn((msg: any) => addedMessages.push(msg))
      };

      await testErrorMiddleware(testMessage, testThread, throwingNext);

      expect(errors).toHaveLength(1);
      expect(errors[0]).toContain('Something went wrong');
      expect(addedMessages).toHaveLength(1);
      expect(addedMessages[0].content[0].text).toBe('Sorry, something went wrong.');
    });

    it('should handle successful processing without errors', async () => {
      const errors: string[] = [];

      async function testErrorMiddleware(
        message: any,
        thread: any,
        next: () => Promise<void>
      ): Promise<void> {
        try {
          await next();
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          errors.push(`❌ Error: ${errorMsg}`);
        }
      }

      // Mock next that succeeds
      async function successNext(): Promise<void> {
        // Success
      }

      const testMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Test' }]
      };

      const testThread = {
        id: 'thread123',
        messages: [testMessage],
        addMessage: jest.fn()
      };

      await testErrorMiddleware(testMessage, testThread, successNext);

      expect(errors).toHaveLength(0);
    });

    it('should handle different error types', async () => {
      const errors: string[] = [];

      async function testErrorMiddleware(
        message: any,
        thread: any,
        next: () => Promise<void>
      ): Promise<void> {
        try {
          await next();
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : String(error);
          errors.push(errorMsg);
        }
      }

      const testMessage = {
        role: 'user',
        content: [{ type: 'text', text: 'Test' }]
      };

      const testThread = {
        id: 'thread123',
        messages: [testMessage],
        addMessage: jest.fn()
      };

      // Test Error instance
      await testErrorMiddleware(testMessage, testThread, async () => {
        throw new Error('Test error');
      });
      expect(errors[0]).toBe('Test error');

      // Test string
      await testErrorMiddleware(testMessage, testThread, async () => {
        throw 'String error';
      });
      expect(errors[1]).toBe('String error');

      // Test object
      await testErrorMiddleware(testMessage, testThread, async () => {
        throw { message: 'Object error' };
      });
      expect(errors[2]).toBe('[object Object]');
    });
  });

  describe('Step 6: Persistent Conversations (In-Memory Storage)', () => {
    /**
     * @docExample hosting-inmemory-storage
     */
    it('should use in-memory storage by default', () => {
      // Sample from quickstart guide
      // <snippet>
      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!
      };
      // Default: in-memory storage
      // </snippet>

      const host = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      expect(host).toBeDefined();
      // Default storage is in-memory (lost on restart)
    });

    it('should maintain conversation state across messages', async () => {
      const storage = new InMemoryStorage();

      // First message
      await storage.setAsync('thread_abc123', 'user_name', 'Alice');

      // Second message - retrieve state
      const userName = await storage.getAsync('thread_abc123', 'user_name');

      expect(userName).toBe('Alice');
    });

    it('should support thread-specific state', async () => {
      const storage = new InMemoryStorage();

      // Set state for multiple threads
      await storage.setAsync('thread1', 'name', 'Alice');
      await storage.setAsync('thread2', 'name', 'Bob');
      await storage.setAsync('thread1', 'count', 5);
      await storage.setAsync('thread2', 'count', 10);

      // Verify thread isolation
      expect(await storage.getAsync('thread1', 'name')).toBe('Alice');
      expect(await storage.getAsync('thread2', 'name')).toBe('Bob');
      expect(await storage.getAsync('thread1', 'count')).toBe(5);
      expect(await storage.getAsync('thread2', 'count')).toBe(10);
    });

    it('should list keys for a thread', async () => {
      const storage = new InMemoryStorage();

      await storage.setAsync('thread1', 'key1', 'value1');
      await storage.setAsync('thread1', 'key2', 'value2');
      await storage.setAsync('thread1', 'key3', 'value3');

      const keys = await storage.getKeysAsync('thread1');

      expect(keys).toHaveLength(3);
      expect(keys).toContain('key1');
      expect(keys).toContain('key2');
      expect(keys).toContain('key3');
    });

    it('should delete state keys', async () => {
      const storage = new InMemoryStorage();

      await storage.setAsync('thread1', 'temp_key', 'temp_value');
      expect(await storage.getAsync('thread1', 'temp_key')).toBe('temp_value');

      await storage.deleteAsync('thread1', 'temp_key');
      expect(await storage.getAsync('thread1', 'temp_key')).toBeNull();
    });
  });

  describe('Step 6: Durable Storage', () => {
    /**
     * @docExample hosting-durable-storage
     */
    it('should support custom storage provider pattern', () => {
      // Sample from quickstart guide - documents the pattern
      // Note: SqlStorageProvider is not implemented yet, but the pattern is:

      // <snippet>
      import { AgentHost, AgentConfig } from '@microsoft/agents-protocol-hosting';
      import { SqlStorageProvider } from '@microsoft/agents-protocol-storage';

      const config: AgentConfig = {
          model: "gpt-4",
          instructions: "You are helpful.",
          apiKey: process.env.OPENAI_API_KEY!,
          storage: new SqlStorageProvider(process.env.DATABASE_URL!)
      };

      const agent = new AgentHost(config);
      // </snippet>

      class MockSqlStorageProvider {
        constructor(private connectionString: string) {}

        async setAsync(threadId: string, key: string, value: any): Promise<void> {
          // SQL INSERT/UPDATE
        }

        async getAsync(threadId: string, key: string): Promise<any | null> {
          // SQL SELECT
          return null;
        }

        async deleteAsync(threadId: string, key: string): Promise<void> {
          // SQL DELETE
        }

        async getKeysAsync(threadId: string): Promise<string[]> {
          // SQL SELECT keys
          return [];
        }

        async checkHealth(): Promise<boolean> {
          return true;
        }
      }

      const sqlStorage = new MockSqlStorageProvider('postgresql://localhost/agents');
      expect(sqlStorage).toBeDefined();
    });

    it('should use custom storage in AgentHostBuilder', () => {
      const customStorage = new InMemoryStorage();

      const host = new AgentHostBuilder()
        .useStorage(customStorage)
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      expect(host).toBeDefined();
    });

    it('should persist data across host restarts with durable storage', async () => {
      const durableStorage = new InMemoryStorage();

      // First host instance
      const host1 = new AgentHostBuilder()
        .useStorage(durableStorage)
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      // Store data
      await durableStorage.setAsync('thread1', 'persistent_key', 'persistent_value');

      // Simulate restart - create new host with same storage
      const host2 = new AgentHostBuilder()
        .useStorage(durableStorage)
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      // Data should persist
      const value = await durableStorage.getAsync('thread1', 'persistent_key');
      expect(value).toBe('persistent_value');
    });
  });

  describe('Integration: Complete Agent Configuration', () => {
    it('should combine all quickstart features', async () => {
      // Complete sample combining all quickstart features
      function getWeather(location: string): string {
        return `The weather in ${location} is sunny and 72°F`;
      }

      function getTime(): string {
        return new Date().toISOString();
      }

      const storage = new InMemoryStorage();

      const host = new AgentHostBuilder()
        .useStorage(storage)
        .addDefaultAgent(agent => agent
          .useLLM('gpt-4', 'You are a helpful assistant.', {
            streaming: false,
            temperature: 0.7,
            maxTokens: 2000
          })
          .addFunctions(f => f
            .add('get_weather', 'Get current weather for a location',
              {
                type: 'object',
                properties: {
                  location: { type: 'string' }
                },
                required: ['location']
              },
              ({ location }: { location: string }): string => getWeather(location),
              { trustLevel: 'trusted' })
            .add('get_time', 'Get current time in UTC',
              { type: 'object', properties: {} },
              (): string => getTime(),
              { trustLevel: 'trusted' })
          )
        )
        .build();

      expect(host).toBeDefined();

      // Test message processing
      const response = await host.processMessage('Hello!');
      expect(response).toBeDefined();
    });

    it('should support middleware patterns with handlers', async () => {
      const logs: string[] = [];

      async function commandHandler(
        message: ChatMessage,
        ctx: IAgentContext
      ): Promise<TurnResult> {
        if (message.text.trim() === '/help') {
          await ctx.respondAsync('Available commands:\n/help - Show this help');
          return TurnResult.Replied;
        }
        return TurnResult.Continue;
      }

      async function timingHandler(
        message: ChatMessage,
        ctx: IAgentContext
      ): Promise<TurnResult> {
        const start = Date.now();
        logs.push(`⏱️ Processing: ${message.text}`);

        // Simulate processing
        await new Promise(resolve => setTimeout(resolve, 10));

        logs.push(`✅ Completed in ${Date.now() - start}ms`);
        return TurnResult.Continue;
      }

      const host = new AgentHostBuilder()
        .addDefaultAgent(agent => agent
          .useLLM('gpt-4', 'You are helpful.')
          .onUserMessage(commandHandler)
          .onUserMessage(timingHandler)
        )
        .build();

      expect(host).toBeDefined();
      expect(logs).toHaveLength(0); // No messages processed yet
    });

    it('should validate health checks', async () => {
      const consoleLogSpy = jest.spyOn(console, 'log').mockImplementation();

      const host = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'You are helpful.'))
        .build();

      await host.start(currentPort);

      const health = await host.checkHealth();
      expect(health.status).toBe('healthy');
      expect(health.checks.server).toBe(true);
      expect(health.checks.storage).toBe(true);
      expect(health.checks.queue).toBe(true);
      expect(health.checks.llmConnection).toBe(true);

      await host.stop();
      consoleLogSpy.mockRestore();
    });
  });

  describe('Error Handling Patterns', () => {
    it('should handle invalid configuration', () => {
      expect(() => {
        new AgentHostBuilder()
          .addDefaultAgent(agent => agent.useLLM('', 'Instructions'))
          .build();
      }).toThrow('model cannot be empty');
    });

    it('should handle missing instructions', () => {
      expect(() => {
        new AgentHostBuilder()
          .addDefaultAgent(agent => agent.useLLM('gpt-4', ''))
          .build();
      }).toThrow('instructions cannot be empty');
    });

    it('should validate function definitions', () => {
      const host = new AgentHostBuilder()
        .addDefaultAgent(agent => agent
          .useLLM('gpt-4', 'You are helpful.')
          .addFunctions(f => f
            .add('test_func', 'Test function',
              { type: 'object', properties: {} },
              (): string => 'result',
              { trustLevel: 'trusted' })
          )
        )
        .build();

      expect(host).toBeDefined();
    });
  });

  describe('Storage Operations', () => {
    it('should handle null values correctly', async () => {
      const storage = new InMemoryStorage();

      const nonExistent = await storage.getAsync('thread1', 'does_not_exist');
      expect(nonExistent).toBeNull();
    });

    it('should overwrite existing values', async () => {
      const storage = new InMemoryStorage();

      await storage.setAsync('thread1', 'key', 'value1');
      expect(await storage.getAsync('thread1', 'key')).toBe('value1');

      await storage.setAsync('thread1', 'key', 'value2');
      expect(await storage.getAsync('thread1', 'key')).toBe('value2');
    });

    it('should handle complex object values', async () => {
      const storage = new InMemoryStorage();

      const complexValue = {
        user: { name: 'Alice', id: 123 },
        settings: { theme: 'dark', notifications: true },
        history: ['msg1', 'msg2', 'msg3']
      };

      await storage.setAsync('thread1', 'complex', complexValue);
      const retrieved = await storage.getAsync('thread1', 'complex');

      expect(retrieved).toEqual(complexValue);
    });
  });
});
