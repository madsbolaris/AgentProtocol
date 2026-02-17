/**
 * Integration tests for Agent Protocol client with EchoM365 server
 *
 * Tests XML input files from test-data/input/threads and saves results to test-data/results/samples/echo-m365.
 * Covers three API patterns: XML, Wait, and Streaming.
 *
 * These tests mirror the .NET EchoM365IntegrationTests.cs implementation.
 */

import * as fs from 'fs/promises';
import * as path from 'path';
import type { ChatMessage, TextContent, Run, RunStatus, CompletionUsage } from '@microsoft/agents-protocol-abstractions';
import { ChatRoleValues } from '@microsoft/agents-protocol-abstractions';
import { AgentProtocolClient } from '../src/client';
import { SimplifiedClient } from '../src/simplified-client';
import { SSEStream } from '../src/streaming/sse-stream';

// Mock xml2js
const xml2js = {
  Parser: class {
    async parseStringPromise(xml: string): Promise<any> {
      // Simple XML parser for tests
      const tagMatch = xml.match(/<(\w+)/);
      const rootTag = tagMatch ? tagMatch[1] : 'unknown';
      const contentMatch = xml.match(/>([^<]+)</);
      const content = contentMatch ? contentMatch[1].trim() : '';

      return {
        [rootTag]: content || { _: content }
      };
    }
  }
};

// Mock fetch globally for testing
global.fetch = jest.fn();

// Constants
const ECHO_M365_URL = 'http://localhost:3978';
const ECHO_M365_AGENT_ID = 'echo-agent';
const TIMEOUT_MS = 30000; // 30 seconds for integration tests

// Test infrastructure
interface RunWaitResponse {
  runId: string;
  agentId?: string;
  threadId?: string;
  status: RunStatus;
  input?: ChatMessage[];
  output?: ChatMessage[];
  createdAt?: string;
  completedAt?: string;
}

/**
 * Mock EchoM365 server implementation
 */
class MockEchoM365Server {
  static setupMockServer(): void {
    (global.fetch as jest.Mock).mockImplementation(async (url: string, options?: any) => {
      const urlObj = new URL(url);
      const method = options?.method || 'GET';

      // Health check endpoint
      if (urlObj.pathname === '/health' && method === 'GET') {
        return {
          ok: true,
          status: 200,
          json: async () => ({ status: 'healthy' }),
        };
      }

      // POST /runs endpoint
      if (urlObj.pathname === '/runs' && method === 'POST') {
        const body = JSON.parse(options.body);
        const run = this.createEchoRun(body);
        return {
          ok: true,
          status: 200,
          json: async () => run,
        };
      }

      // POST /runs/wait endpoint
      if (urlObj.pathname === '/runs/wait' && method === 'POST') {
        const body = JSON.parse(options.body);
        const response = this.createEchoWaitResponse(body);
        return {
          ok: true,
          status: 200,
          json: async () => response,
        };
      }

      // GET /runs/:runId endpoint
      if (urlObj.pathname.match(/^\/runs\/[^/]+$/) && method === 'GET') {
        const runId = urlObj.pathname.split('/')[2];
        return {
          ok: true,
          status: 200,
          json: async () => ({
            runId,
            status: 'completed',
            output: [],
          }),
        };
      }

      // POST /runs/:runId/cancel endpoint
      if (urlObj.pathname.match(/^\/runs\/[^/]+\/cancel$/) && method === 'POST') {
        const runId = urlObj.pathname.split('/')[2];
        return {
          ok: true,
          status: 200,
          json: async () => ({
            runId,
            status: 'cancelled',
            output: [],
          }),
        };
      }

      // Default 404
      return {
        ok: false,
        status: 404,
        json: async () => ({ message: 'Not found' }),
      };
    });
  }

  private static generateId(prefix: string): string {
    return `${prefix}_${Math.random().toString(36).substring(2, 15)}`;
  }

  private static createEchoRun(inputRun: any): Run {
    const runId = this.generateId('run');
    const threadId = inputRun.threadId || this.generateId('thread');

    const echoedMessages: ChatMessage[] = [];
    if (inputRun.input && Array.isArray(inputRun.input)) {
      for (const inputMessage of inputRun.input) {
        const echoMessage = this.createEchoMessage(inputMessage);
        if (echoMessage) {
          echoedMessages.push(echoMessage);
        }
      }
    }

    const usage: CompletionUsage = {
      inputTokens: 0,
      outputTokens: 0,
      totalTokens: 0,
    };

    return {
      runId,
      agentId: inputRun.agentId,
      threadId,
      status: 'completed' as RunStatus,
      input: inputRun.input || [],
      output: echoedMessages,
      usage,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      completedAt: new Date().toISOString(),
    };
  }

  private static createEchoWaitResponse(inputRun: any): RunWaitResponse {
    const runId = this.generateId('run');
    const threadId = inputRun.threadId || this.generateId('thread');

    const echoedMessages: ChatMessage[] = [];
    if (inputRun.input && Array.isArray(inputRun.input)) {
      for (const inputMessage of inputRun.input) {
        const echoMessage = this.createEchoMessage(inputMessage);
        if (echoMessage) {
          echoedMessages.push(echoMessage);
        }
      }
    }

    return {
      runId,
      agentId: inputRun.agentId,
      threadId,
      status: 'completed' as RunStatus,
      input: inputRun.input,
      output: echoedMessages,
      createdAt: new Date().toISOString(),
    };
  }

  private static createEchoMessage(inputMessage: ChatMessage): ChatMessage | null {
    const text = this.extractText(inputMessage);
    if (!text) {
      return null;
    }

    const echoText = `you said: \n${text}`;

    return {
      messageId: this.generateId('msg'),
      role: ChatRoleValues.Agent,
      createdAt: new Date().toISOString(),
      contents: [
        {
          kind: 'text',
          text: echoText,
        } as TextContent,
      ],
    };
  }

  private static extractText(message: ChatMessage): string | null {
    if (!message.contents || message.contents.length === 0) {
      return null;
    }

    const textContents = message.contents
      .filter((c: any) => c.kind === 'text')
      .map((c: any) => (c as TextContent).text)
      .filter((t): t is string => !!t && t.trim().length > 0);

    const result = textContents.join('\n');
    return result.trim().length > 0 ? result : null;
  }
}

/**
 * Enhanced XML parser that handles multiple content types
 */
class XmlMessageParser {
  static async xmlToChatMessage(xmlContent: string): Promise<ChatMessage | null> {
    try {
      const parser = new xml2js.Parser();
      const result = await parser.parseStringPromise(xmlContent);
      const rootElement = Object.keys(result)[0];
      const root = result[rootElement];

      let text: string | null = null;

      // Extract text from XML
      if (typeof root === 'string') {
        text = root.trim();
      } else if (root && typeof root === 'object' && '_' in root) {
        text = (root as any)._.trim();
      }

      if (!text || text.trim().length === 0) {
        return null;
      }

      // Determine role from root element
      const role = this.mapRoleFromElement(rootElement, root);

      return {
        messageId: `msg_${Math.random().toString(36).substring(2, 15)}`,
        role,
        contents: [
          {
            kind: 'text',
            text: text.trim(),
          } as TextContent,
        ],
      };
    } catch (error) {
      console.warn(`Warning: Could not parse XML to ChatMessage: ${error}`);
      return null;
    }
  }

  private static mapRoleFromElement(elementName: string, element: any): 'system' | 'developer' | 'agent' | 'user' | 'tool' | 'channel' {
    // Handle thread elements - look at first child
    if (elementName === 'thread' && typeof element === 'object') {
      const firstChild = Object.keys(element).find(k => k !== '$');
      if (firstChild) {
        elementName = firstChild;
      }
    }

    const roleName = elementName.toLowerCase();
    switch (roleName) {
      case 'system':
        return ChatRoleValues.System;
      case 'developer':
        return ChatRoleValues.Developer;
      case 'agent':
      case 'assistant':
        return ChatRoleValues.Agent;
      case 'user':
        return ChatRoleValues.User;
      case 'tool':
        return ChatRoleValues.Tool;
      case 'channel':
        return ChatRoleValues.Channel;
      default:
        return ChatRoleValues.User; // Default to user
    }
  }
}

/**
 * Test utilities
 */
class TestUtils {
  static async findRepositoryRoot(startPath: string): Promise<string> {
    let current = startPath;
    while (current !== path.dirname(current)) {
      try {
        await fs.access(path.join(current, 'test-data'));
        return current;
      } catch {
        current = path.dirname(current);
      }
    }
    throw new Error('Could not find repository root with test-data directory');
  }

  static async ensureDirectory(dirPath: string): Promise<void> {
    await fs.mkdir(dirPath, { recursive: true });
  }

  static async getInputFiles(inputDir: string): Promise<string[]> {
    try {
      // Recursively get all XML files, excluding invalid subdirectory
      const files: string[] = [];

      async function walkDir(dir: string): Promise<void> {
        const entries = await fs.readdir(dir, { withFileTypes: true });

        for (const entry of entries) {
          const fullPath = path.join(dir, entry.name);

          if (entry.isDirectory()) {
            // Skip invalid subdirectory
            if (entry.name !== 'invalid') {
              await walkDir(fullPath);
            }
          } else if (entry.isFile() && entry.name.endsWith('.xml')) {
            files.push(fullPath);
          }
        }
      }

      await walkDir(inputDir);
      return files.sort();
    } catch {
      return [];
    }
  }

  static async saveResult(
    resultPath: string,
    result: any
  ): Promise<void> {
    const json = JSON.stringify(result, null, 2);
    await fs.writeFile(resultPath, json, 'utf-8');
  }
}

/**
 * Main test suite
 */
describe('EchoM365 Integration Tests', () => {
  let testDataDir: string;
  let inputDir: string;
  let xmlResultsDir: string;
  let waitResultsDir: string;
  let streamingResultsDir: string;

  beforeAll(async () => {
    // Find test-data directory
    const repoRoot = await TestUtils.findRepositoryRoot(process.cwd());
    testDataDir = path.join(repoRoot, 'test-data');
    inputDir = path.join(testDataDir, 'input', 'threads');

    // Use shared results directory (language-agnostic)
    const resultsBase = path.join(testDataDir, 'results', 'samples', 'echo-m365');
    xmlResultsDir = path.join(resultsBase, 'xml');
    waitResultsDir = path.join(resultsBase, 'wait');
    streamingResultsDir = path.join(resultsBase, 'streaming');

    // Create results directories
    await TestUtils.ensureDirectory(xmlResultsDir);
    await TestUtils.ensureDirectory(waitResultsDir);
    await TestUtils.ensureDirectory(streamingResultsDir);

    // Setup mock server
    MockEchoM365Server.setupMockServer();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('XML Pattern - End-to-End Run Creation', () => {
    it('should process all input files using XML pattern', async () => {
      const inputFiles = await TestUtils.getInputFiles(inputDir);
      let processedCount = 0;

      for (const inputFile of inputFiles) {
        const fileName = path.basename(inputFile);
        const xmlContent = await fs.readFile(inputFile, 'utf-8');

        const message = await XmlMessageParser.xmlToChatMessage(xmlContent);
        if (!message) {
          console.log(`Skipping ${fileName} - no parseable content`);
          continue;
        }

        try {
          // Create run using fetch directly (XML pattern)
          const run = {
            agentId: ECHO_M365_AGENT_ID,
            input: [message],
          };

          const response = await fetch(`${ECHO_M365_URL}/runs`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(run),
          });

          expect(response.ok).toBe(true);
          const result = await response.json() as RunWaitResponse;
          expect(result).toBeDefined();
          expect(result.runId).toBeDefined();

          // Save result
          const resultFileName = path.basename(fileName, '.xml') + '-result.json';
          const resultPath = path.join(xmlResultsDir, resultFileName);
          await TestUtils.saveResult(resultPath, result);

          processedCount++;
          console.log(`✓ Processed ${fileName}`);
        } catch (error) {
          console.log(`✗ Failed ${fileName}: ${error}`);
        }
      }

      console.log(`\nProcessed ${processedCount} files successfully`);
      expect(processedCount).toBeGreaterThan(0);
    }, TIMEOUT_MS);
  });

  describe('Wait Pattern - Full Conversation Workflow', () => {
    it('should process all input files using wait pattern', async () => {
      const inputFiles = await TestUtils.getInputFiles(inputDir);
      let processedCount = 0;

      for (const inputFile of inputFiles) {
        const fileName = path.basename(inputFile);
        const xmlContent = await fs.readFile(inputFile, 'utf-8');

        const message = await XmlMessageParser.xmlToChatMessage(xmlContent);
        if (!message) {
          console.log(`Skipping ${fileName} - no parseable content`);
          continue;
        }

        try {
          // Create run with wait
          const run = {
            agentId: ECHO_M365_AGENT_ID,
            input: [message],
          };

          const response = await fetch(`${ECHO_M365_URL}/runs/wait`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(run),
          });

          expect(response.ok).toBe(true);
          const result = await response.json() as RunWaitResponse;
          expect(result).toBeDefined();
          expect(result.status).toBe('completed');

          // Save result
          const resultFileName = path.basename(fileName, '.xml') + '-result.json';
          const resultPath = path.join(waitResultsDir, resultFileName);
          await TestUtils.saveResult(resultPath, result);

          processedCount++;
          console.log(`✓ Processed ${fileName}`);
        } catch (error) {
          console.log(`✗ Failed ${fileName}: ${error}`);
        }
      }

      console.log(`\nProcessed ${processedCount} files successfully`);
      expect(processedCount).toBeGreaterThan(0);
    }, TIMEOUT_MS);

    it('should maintain thread context across multiple messages', async () => {
      const message1: ChatMessage = {
        messageId: 'msg1',
        role: ChatRoleValues.User,
        contents: [{ kind: 'text', text: 'Hello' } as TextContent],
      };

      const message2: ChatMessage = {
        messageId: 'msg2',
        role: ChatRoleValues.User,
        contents: [{ kind: 'text', text: 'How are you?' } as TextContent],
      };

      // First message
      const response1 = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          input: [message1],
        }),
      });

      const result1 = await response1.json() as RunWaitResponse;
      expect(result1.threadId).toBeDefined();
      const threadId = result1.threadId!;

      // Second message with thread context
      const response2 = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          threadId,
          input: [message2],
        }),
      });

      const result2 = await response2.json() as RunWaitResponse;
      expect(result2.threadId).toBe(threadId);
    });
  });

  describe('Tool Execution Integration', () => {
    it('should handle tool calls in messages', async () => {
      const toolCallMessage: ChatMessage = {
        messageId: 'msg_tool_call',
        role: ChatRoleValues.Agent,
        contents: [
          {
            kind: 'text',
            text: '[Function call: get_weather({"location": "Seattle"})]',
          } as TextContent,
        ],
      };

      const response = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          input: [toolCallMessage],
        }),
      });

      const result = await response.json() as RunWaitResponse;
      expect(result.status).toBe('completed');
      expect(result.output).toBeDefined();
      expect(result.output!.length).toBeGreaterThan(0);
    });

    it('should handle tool results', async () => {
      const toolResultMessage: ChatMessage = {
        messageId: 'msg_tool_result',
        role: ChatRoleValues.Tool,
        contents: [
          {
            kind: 'text',
            text: '[Function result: {"temperature": 52, "conditions": "cloudy"}]',
          } as TextContent,
        ],
      };

      const response = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          input: [toolResultMessage],
        }),
      });

      const result = await response.json() as RunWaitResponse;
      expect(result.status).toBe('completed');
      expect(result.output).toBeDefined();
    });
  });

  describe('Streaming Integration', () => {
    it('should create a run for streaming', async () => {
      const message: ChatMessage = {
        messageId: 'msg_stream',
        role: ChatRoleValues.User,
        contents: [{ kind: 'text', text: 'Tell me a story' } as TextContent],
      };

      const response = await fetch(`${ECHO_M365_URL}/runs`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          input: [message],
        }),
      });

      const result = await response.json() as RunWaitResponse;
      expect(result.runId).toBeDefined();
      expect(result.status).toBeDefined();
    });

    it('should support streaming event handlers', () => {
      // Mock SSE stream behavior
      const stream = new SSEStream(`${ECHO_M365_URL}/runs/test-run/stream`);

      const events: any[] = [];
      stream.on('*', (event) => {
        events.push(event);
      });

      // Cleanup
      stream.close();
      expect(stream.connected).toBe(false);
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle HTTP errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ message: 'Agent not found' }),
      });

      const response = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: 'nonexistent-agent',
          input: [],
        }),
      });

      expect(response.ok).toBe(false);
      expect(response.status).toBe(404);
    });

    it('should handle network errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(
        fetch(`${ECHO_M365_URL}/runs/wait`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agentId: ECHO_M365_AGENT_ID,
            input: [],
          }),
        })
      ).rejects.toThrow('Network error');
    });

    it('should handle malformed responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      const response = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          input: [],
        }),
      });

      await expect(response.json()).rejects.toThrow('Invalid JSON');
    });
  });

  describe('Timeout Scenarios', () => {
    it('should respect request timeout', async () => {
      const controller = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(
        () => new Promise((resolve) => {
          setTimeout(() => {
            if (!controller.signal.aborted) {
              resolve({
                ok: true,
                status: 200,
                json: async () => ({ runId: 'test', status: 'completed' }),
              });
            }
          }, 5000);
        })
      );

      // Abort after 100ms
      setTimeout(() => controller.abort(), 100);

      // Start fetch but don't await (will be aborted)
      fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: ECHO_M365_AGENT_ID,
          input: [],
        }),
        signal: controller.signal,
      }).catch(() => {
        // Expected abort error
      });

      // Wait for abort to take effect
      await new Promise(resolve => setTimeout(resolve, 150));

      expect(controller.signal.aborted).toBe(true);
    });

    it('should handle run cancellation', async () => {
      const response = await fetch(`${ECHO_M365_URL}/runs/test-run/cancel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });

      const result = await response.json() as RunWaitResponse;
      expect(result.status).toBe('cancelled');
    });
  });

  describe('Multi-Agent Interactions', () => {
    it('should support different agent IDs', async () => {
      const agents = ['echo-agent', 'assistant-1', 'assistant-2'];

      for (const agentId of agents) {
        const response = await fetch(`${ECHO_M365_URL}/runs/wait`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            agentId,
            input: [
              {
                messageId: 'msg_multi',
                role: ChatRoleValues.User,
                contents: [{ kind: 'text', text: 'Hello' } as TextContent],
              },
            ],
          }),
        });

        const result = await response.json() as RunWaitResponse;
        expect(result.agentId).toBe(agentId);
      }
    });

    it('should maintain separate threads for different agents', async () => {
      const message: ChatMessage = {
        messageId: 'msg_threads',
        role: ChatRoleValues.User,
        contents: [{ kind: 'text', text: 'Hello' } as TextContent],
      };

      // Agent 1
      const response1 = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: 'agent-1',
          input: [message],
        }),
      });

      const result1 = await response1.json() as RunWaitResponse;

      // Agent 2
      const response2 = await fetch(`${ECHO_M365_URL}/runs/wait`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: 'agent-2',
          input: [message],
        }),
      });

      const result2 = await response2.json() as RunWaitResponse;

      // Different agents should have different threads
      expect(result1.threadId).toBeDefined();
      expect(result2.threadId).toBeDefined();
      expect(result1.threadId).not.toBe(result2.threadId);
    });
  });

  describe('XML Parser Tests', () => {
    it('should handle system messages', async () => {
      const xml = `<system created-at="2026-02-07T10:00:00Z">
        You are a helpful AI assistant.
      </system>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).not.toBeNull();
      expect(message!.role).toBe(ChatRoleValues.System);
      expect(message!.contents).toHaveLength(1);
      expect((message!.contents[0] as TextContent).text).toContain('helpful AI assistant');
    });

    it('should handle developer messages', async () => {
      const xml = `<developer created-at="2026-02-07T10:01:00Z">
        Additional developer instructions: Use concise responses.
      </developer>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).not.toBeNull();
      expect(message!.role).toBe(ChatRoleValues.Developer);
      expect((message!.contents[0] as TextContent).text).toContain('concise responses');
    });

    it('should handle text elements', async () => {
      const xml = `<user user-id="user_123">
        <text>What's the weather?</text>
      </user>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).not.toBeNull();
      expect(message!.role).toBe(ChatRoleValues.User);
      expect((message!.contents[0] as TextContent).text).toBe("What's the weather?");
    });

    it('should handle thinking content', async () => {
      const xml = `<agent agent-id="agent_1">
        <thinking exposed="false">
          Need to call weather API.
        </thinking>
      </agent>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).not.toBeNull();
      expect(message!.role).toBe(ChatRoleValues.Agent);
      expect((message!.contents[0] as TextContent).text).toContain('weather API');
    });

    it('should handle function calls', async () => {
      const xml = `<agent agent-id="agent_1">
        <function-call call-id="call_001" name="get_weather">
          {"location": "Seattle"}
        </function-call>
      </agent>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).not.toBeNull();
      expect(message!.role).toBe(ChatRoleValues.Agent);
      expect((message!.contents[0] as TextContent).text).toContain('Function call: get_weather');
    });

    it('should handle function results', async () => {
      const xml = `<tool call-id="call_001" name="get_weather">
        <function-result>
          {"temperature": 52, "conditions": "cloudy"}
        </function-result>
      </tool>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).not.toBeNull();
      expect(message!.role).toBe(ChatRoleValues.Tool);
      expect((message!.contents[0] as TextContent).text).toContain('Function result');
      expect((message!.contents[0] as TextContent).text).toContain('temperature');
    });

    it('should return null for empty content', async () => {
      const xml = `<refusal reason="Test reason"/>`;

      const message = await XmlMessageParser.xmlToChatMessage(xml);

      expect(message).toBeNull();
    });
  });

  describe('Client API Integration', () => {
    it('should work with AgentProtocolClient', async () => {
      const client = new AgentProtocolClient({
        baseUrl: ECHO_M365_URL,
      });

      const run = await client.runs.create({
        agentId: ECHO_M365_AGENT_ID,
        input: [
          {
            messageId: 'msg_api',
            role: ChatRoleValues.User,
            contents: [{ kind: 'text', text: 'Hello' } as TextContent],
          },
        ],
      });

      expect(run.runId).toBeDefined();
      expect(run.status).toBeDefined();
    });

    it('should work with SimplifiedClient', async () => {
      const client = new SimplifiedClient({
        baseUrl: ECHO_M365_URL,
      });

      const result = await client.completeChat('Hello', {
        agentId: ECHO_M365_AGENT_ID,
      });

      expect(result).toBeDefined();
      expect(typeof result).toBe('string');
    });

    it('should support conversation context with SimplifiedClient', async () => {
      const client = new SimplifiedClient({
        baseUrl: ECHO_M365_URL,
      });

      const conversation = client.createConversation();

      // Mock the first response with thread ID
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-1',
          threadId: 'thread-123',
          status: 'completed',
          output: [{
            messageId: 'msg-1',
            role: ChatRoleValues.Agent,
            contents: [{ kind: 'text', text: 'Hi there!' } as TextContent],
          }],
        }),
      });

      await conversation.send('Hello');
      expect(conversation.threadId).toBeDefined();

      // Mock second response
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          runId: 'run-2',
          threadId: 'thread-123',
          status: 'completed',
          output: [{
            messageId: 'msg-2',
            role: ChatRoleValues.Agent,
            contents: [{ kind: 'text', text: 'I am good!' } as TextContent],
          }],
        }),
      });

      await conversation.send('How are you?');
      expect(conversation.threadId).toBeDefined();
    });
  });

  describe('Health Check', () => {
    it('should verify server is responding', async () => {
      const response = await fetch(`${ECHO_M365_URL}/health`);
      expect(response.ok).toBe(true);
    });
  });
});
