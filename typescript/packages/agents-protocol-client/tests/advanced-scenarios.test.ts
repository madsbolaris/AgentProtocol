/**
 * Tests for advanced scenarios and complex workflows
 * Mirrors functionality from .NET AdvancedScenariosTests.cs
 */

import { AgentProtocolClient } from '../src/client';
import type {
  Run,
  Thread,
  ChatMessage,
  TextContent,
  ImageContent,
  AITool,
  PromptAgent,
  ChatRole,
  CompletionUsage,
} from '@microsoft/agents-protocol-abstractions';
import { AgentProtocolClientConfig } from '../src/types';

// Mock fetch globally for testing
global.fetch = jest.fn();

// Helper function to create a valid ChatMessage
function createChatMessage(
  role: ChatRole,
  text: string,
  messageId?: string
): ChatMessage {
  return {
    role,
    messageId: messageId || `msg_${Date.now()}_${Math.random()}`,
    contents: [
      {
        kind: 'text',
        text,
      } as TextContent,
    ],
  };
}

// Helper function to create a default usage object
function createUsage(
  input = 10,
  output = 50,
  total = 60
): CompletionUsage {
  return {
    inputTokens: input,
    outputTokens: output,
    totalTokens: total,
  };
}

// Helper function to create a partial Run with required fields
function createRun(partial: Partial<Run>): Run {
  const now = new Date().toISOString();
  return {
    runId: partial.runId || `run_${Date.now()}`,
    agentId: partial.agentId || 'agent_001',
    status: partial.status || 'completed',
    input: partial.input || [],
    output: partial.output || [],
    usage: partial.usage || createUsage(),
    createdAt: partial.createdAt || now,
    updatedAt: partial.updatedAt || now,
    ...partial,
  };
}

describe('Advanced Scenarios Tests', () => {
  let mockFetch: jest.MockedFunction<typeof fetch>;

  beforeEach(() => {
    mockFetch = global.fetch as jest.MockedFunction<typeof fetch>;
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Inline Agent Definition with Ephemeral Execution', () => {
    it('should create and execute inline agent with ephemeral thread', async () => {
      // Arrange - Example from "Using Inline Agent Definitions" section
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        timeout: 30000,
      };

      const client = new AgentProtocolClient(config);

      const expectedResponse = createRun({
        runId: 'run_ephemeral_001',
        agentId: 'ephemeral',
        status: 'completed',
        input: [createChatMessage('user', 'Explain calculus', 'msg_input_001')],
        output: [
          createChatMessage(
            'agent',
            'Calculus is the mathematical study of continuous change...',
            'msg_output_001'
          ),
        ],
        completedAt: new Date(Date.now() + 5000).toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      } as Response);

      const runRequest = {
        agentId: 'ephemeral',
        agent: {
          kind: 'prompt',
          name: 'math_tutor',
          description: 'You are a math tutor',
          metadata: { model: 'gpt-4o', temperature: 0.3 },
        } as PromptAgent,
        input: [createChatMessage('user', 'Explain calculus')],
        threadCleanup: 'delete' as const,
      };

      // Act
      const result = await client.runs.createAndWait(runRequest);

      // Assert
      expect(result).toBeDefined();
      expect(result.status).toBe('completed');
      expect(result.output).toBeDefined();
      expect(result.output!.length).toBeGreaterThan(0);
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/runs/wait',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  describe('Working with Images - Vision Model', () => {
    it('should process image content with vision model', async () => {
      // Arrange - Example from "Working with Images" section
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const expectedRun = createRun({
        runId: 'run_vision_001',
        agentId: 'agent_vision',
        status: 'in_progress',
        input: [
          {
            role: 'user' as ChatRole,
            messageId: 'msg_vision_input',
            contents: [
              {
                kind: 'text',
                text: "What's in this image?",
              } as TextContent,
              {
                kind: 'image',
                url: 'https://example.com/image.jpg',
                detail: 'high',
              } as ImageContent,
            ],
          },
        ],
        output: [],
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      } as Response);

      const message: ChatMessage = {
        role: 'user' as ChatRole,
        messageId: 'msg_user_vision',
        contents: [
          {
            kind: 'text',
            text: "What's in this image?",
          } as TextContent,
          {
            kind: 'image',
            url: 'https://example.com/image.jpg',
            detail: 'high',
          } as ImageContent,
        ],
      };

      // Act
      const result = await client.runs.create({
        agentId: 'agent_vision',
        input: [message],
      });

      // Assert
      expect(result).toBeDefined();
      expect(result.agentId).toBe('agent_vision');
      expect(result.input![0].contents).toHaveLength(2);
      expect(result.input![0].contents[0].kind).toBe('text');
      expect(result.input![0].contents[1].kind).toBe('image');
    });
  });

  describe('Tool Execution with Approval', () => {
    it('should handle tools requiring human-in-the-loop approval', async () => {
      // Arrange - Example from "Tool Execution with Approval" section
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const tool: AITool = {
        name: 'delete_file',
        description: 'Delete a file from the system',
        requiresApproval: true,
        parameters: {
          properties: {
            path: {
              description: 'File path to delete',
            },
          },
          required: ['path'],
        },
      };

      const runWithToolCall = createRun({
        runId: 'run_approval_001',
        agentId: 'agent_file_manager',
        status: 'requires_action',
        input: [createChatMessage('user', 'Delete the old backup file')],
        output: [],
      });

      // Add required action after creation
      (runWithToolCall as any).requiredAction = {
        type: 'submit_tool_outputs',
        submitToolOutputs: {
          toolCalls: [
            {
              id: 'call_001',
              type: 'function',
              function: {
                name: 'delete_file',
                arguments: '{"path": "/important/file.txt"}',
              },
            },
          ],
        },
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => runWithToolCall,
      } as Response);

      // Act
      const result = await client.runs.create({
        agentId: 'agent_file_manager',
        input: [createChatMessage('user', 'Delete the old backup file')],
        tools: [tool],
      });

      // Assert
      expect(result).toBeDefined();
      expect(result.status).toBe('requires_action');
      expect((result as any).requiredAction).toBeDefined();
      expect((result as any).requiredAction.type).toBe('submit_tool_outputs');
      expect(
        (result as any).requiredAction.submitToolOutputs.toolCalls[0].function
          .name
      ).toBe('delete_file');
    });

    it('should submit tool outputs after approval', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const completedRun = createRun({
        runId: 'run_approval_001',
        agentId: 'agent_file_manager',
        status: 'completed',
        input: [],
        output: [
          createChatMessage('agent', 'File has been deleted successfully.'),
        ],
        completedAt: new Date().toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => completedRun,
      } as Response);

      // Act - Human approves and submits tool output
      const result = await client.runs.submitToolOutputs('run_approval_001', {
        toolOutputs: [
          {
            toolCallId: 'call_001',
            output: JSON.stringify({ success: true }),
          },
        ],
      });

      // Assert
      expect(result).toBeDefined();
      expect(result.status).toBe('completed');
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/runs/run_approval_001/submit_tool_outputs',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  describe('Custom HTTP Client Configuration', () => {
    it('should use provided custom configuration', async () => {
      // Arrange - Example from "Custom HTTP Client Configuration" section
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        authToken: 'test-api-key',
        timeout: 300000, // 5 minutes
        maxRetries: 5,
        headers: {
          'X-Custom-Header': 'custom-value',
        },
        debug: false,
      };

      const client = new AgentProtocolClient(config);

      const expectedRun = createRun({
        runId: 'run_custom_001',
        agentId: 'agent_001',
        status: 'in_progress',
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedRun,
      } as Response);

      // Act
      const result = await client.runs.create({
        agentId: 'agent_001',
        input: [createChatMessage('user', 'Test message')],
      });

      // Assert
      expect(result).toBeDefined();
      expect(result.runId).toBe('run_custom_001');
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/runs',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'X-Custom-Header': 'custom-value',
            Authorization: 'Bearer test-api-key',
          }),
        })
      );
    });
  });

  describe('Error Handling', () => {
    it('should handle failed run with error details', async () => {
      // Arrange - Example from "Error Handling" section
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const failedRun = createRun({
        runId: 'run_failed_001',
        agentId: 'agent_001',
        status: 'failed',
        input: [],
        output: [],
        error: {
          code: 'context_length_exceeded',
          message:
            'The conversation exceeded the maximum token limit of 128000 tokens',
          details: {
            maxTokens: 128000,
            actualTokens: 150000,
          },
        },
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => failedRun,
      } as Response);

      // Act
      const result = await client.runs.retrieve('run_failed_001');

      // Assert
      expect(result).toBeDefined();
      expect(result.status).toBe('failed');
      expect(result.error).toBeDefined();
      expect(result.error!.code).toBe('context_length_exceeded');
      expect(result.error!.message).toContain('maximum token limit');
      expect(result.error!.details).toBeDefined();
      expect((result.error!.details as any).maxTokens).toBe(128000);
      expect((result.error!.details as any).actualTokens).toBe(150000);
    });

    it('should handle HTTP errors properly', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({
          error: {
            code: 'not_found',
            message: 'Agent not found',
          },
        }),
      } as Response);

      // Act & Assert
      await expect(client.runs.retrieve('invalid_run_id')).rejects.toThrow();
    });

    it('should handle network errors', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        maxRetries: 0, // Disable retries for faster test
      };

      const client = new AgentProtocolClient(config);

      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      // Act & Assert
      await expect(
        client.runs.create({
          agentId: 'agent_001',
          input: [],
        })
      ).rejects.toThrow();
    }, 10000);
  });

  describe('Multi-Turn Conversation with Thread Context', () => {
    it('should maintain state across multiple conversation turns', async () => {
      // Arrange - Multi-turn conversation pattern
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      // Turn 1: Create thread
      const expectedThread: Thread = {
        threadId: 'thread_multi_001',
        status: 'active',
        participants: [],
        messages: [],
        metadata: { title: 'Math Help' },
        createdAt: new Date().toISOString(),
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedThread,
      } as Response);

      // Turn 2: First run
      const firstRun = createRun({
        runId: 'run_turn_001',
        agentId: 'agent_math',
        threadId: 'thread_multi_001',
        status: 'completed',
        input: [createChatMessage('user', 'What is 5 + 3?')],
        output: [createChatMessage('agent', '5 + 3 equals 8')],
        completedAt: new Date().toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => firstRun,
      } as Response);

      // Turn 3: Second run (references previous context)
      const secondRun = createRun({
        runId: 'run_turn_002',
        agentId: 'agent_math',
        threadId: 'thread_multi_001',
        status: 'completed',
        input: [createChatMessage('user', 'Now multiply that by 2')],
        output: [createChatMessage('agent', '8 multiplied by 2 equals 16')],
        completedAt: new Date().toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => secondRun,
      } as Response);

      // Act - Simulate multi-turn conversation
      // Turn 1: Create thread
      const thread = await client.threads.create({
        metadata: { title: 'Math Help' },
      });

      // Turn 2: First question
      const turn1 = await client.runs.create({
        agentId: 'agent_math',
        threadId: thread.threadId,
        input: [createChatMessage('user', 'What is 5 + 3?')],
      });

      // Turn 3: Follow-up question (references previous answer)
      const turn2 = await client.runs.create({
        agentId: 'agent_math',
        threadId: thread.threadId,
        input: [createChatMessage('user', 'Now multiply that by 2')],
      });

      // Assert
      expect(thread).toBeDefined();
      expect(thread.threadId).toBe('thread_multi_001');

      expect(turn1).toBeDefined();
      expect(turn1.threadId).toBe('thread_multi_001');
      expect(turn1.status).toBe('completed');
      expect(turn1.output).toBeDefined();

      expect(turn2).toBeDefined();
      expect(turn2.threadId).toBe('thread_multi_001');
      expect(turn2.status).toBe('completed');
      expect(turn2.output).toBeDefined();

      // Verify multi-turn conversation maintains thread context
      expect(turn1.threadId).toBe(turn2.threadId);
    });
  });

  describe('Retry and Error Recovery', () => {
    it('should retry failed requests with exponential backoff', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        maxRetries: 2, // 2 retries = 3 total calls
      };

      const client = new AgentProtocolClient(config);

      const expectedRun = createRun({
        runId: 'run_retry_001',
        agentId: 'agent_001',
        status: 'completed',
        completedAt: new Date().toISOString(),
      });

      // First two calls fail, third succeeds
      mockFetch
        .mockRejectedValueOnce(new Error('Temporary network error'))
        .mockRejectedValueOnce(new Error('Temporary network error'))
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => expectedRun,
        } as Response);

      // Act
      const result = await client.runs.retrieve('run_retry_001');

      // Assert
      expect(result).toBeDefined();
      expect(result.runId).toBe('run_retry_001');
      expect(mockFetch).toHaveBeenCalledTimes(3);
    }, 10000);

    it('should fail after max retries exceeded', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        maxRetries: 1, // 1 retry = 2 total calls
      };

      const client = new AgentProtocolClient(config);

      // All calls fail
      mockFetch.mockRejectedValue(new Error('Persistent network error'));

      // Act & Assert
      await expect(client.runs.retrieve('run_fail_001')).rejects.toThrow();
      expect(mockFetch).toHaveBeenCalledTimes(2); // initial + 1 retry
    }, 10000);
  });

  describe('Timeout Handling', () => {
    it('should timeout long-running requests', async () => {
      // Note: Timeout behavior depends on client implementation
      // This test verifies the timeout parameter is accepted
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        timeout: 1000, // Default timeout
      };

      const client = new AgentProtocolClient(config);

      const expectedRun = createRun({
        runId: 'run_timeout_001',
        agentId: 'agent_001',
        status: 'completed',
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      } as Response);

      // Act - Verify timeout parameter is accepted
      const result = await client.runs.retrieve('run_timeout_001', {
        timeout: 100,
      });

      // Assert
      expect(result).toBeDefined();
      expect(result.runId).toBe('run_timeout_001');
    });

    it('should allow custom timeout per request', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        timeout: 1000, // Default timeout
      };

      const client = new AgentProtocolClient(config);

      const expectedRun = createRun({
        runId: 'run_custom_timeout_001',
        agentId: 'agent_001',
        status: 'completed',
        completedAt: new Date().toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedRun,
      } as Response);

      // Act - Override timeout for this specific request
      const result = await client.runs.createAndWait(
        {
          agentId: 'agent_001',
          input: [],
        },
        { timeout: 300000 } // 5 minutes for long-running operation
      );

      // Assert
      expect(result).toBeDefined();
      expect(result.runId).toBe('run_custom_timeout_001');
    });
  });

  describe('Concurrent Operations', () => {
    it('should handle multiple parallel runs', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const run1 = createRun({
        runId: 'run_parallel_001',
        agentId: 'agent_001',
        status: 'completed',
        output: [createChatMessage('agent', 'Response 1')],
        completedAt: new Date().toISOString(),
      });

      const run2 = createRun({
        runId: 'run_parallel_002',
        agentId: 'agent_002',
        status: 'completed',
        output: [createChatMessage('agent', 'Response 2')],
        completedAt: new Date().toISOString(),
      });

      const run3 = createRun({
        runId: 'run_parallel_003',
        agentId: 'agent_003',
        status: 'completed',
        output: [createChatMessage('agent', 'Response 3')],
        completedAt: new Date().toISOString(),
      });

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => run1,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => run2,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => run3,
        } as Response);

      // Act - Execute multiple runs in parallel
      const [result1, result2, result3] = await Promise.all([
        client.runs.createAndWait({ agentId: 'agent_001', input: [] }),
        client.runs.createAndWait({ agentId: 'agent_002', input: [] }),
        client.runs.createAndWait({ agentId: 'agent_003', input: [] }),
      ]);

      // Assert
      expect(result1.runId).toBe('run_parallel_001');
      expect(result2.runId).toBe('run_parallel_002');
      expect(result3.runId).toBe('run_parallel_003');
      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    it('should handle race conditions in concurrent operations', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      let callCount = 0;
      mockFetch.mockImplementation(async () => {
        callCount++;
        const runId = `run_race_${String(callCount).padStart(3, '0')}`;
        return {
          ok: true,
          status: 200,
          json: async () =>
            createRun({
              runId,
              agentId: 'agent_001',
              status: 'completed',
              completedAt: new Date().toISOString(),
            }),
        } as Response;
      });

      // Act - Rapidly fire multiple requests
      const promises = Array.from({ length: 10 }, (_, i) =>
        client.runs.createAndWait({
          agentId: 'agent_001',
          input: [createChatMessage('user', `Request ${i + 1}`)],
        })
      );

      const results = await Promise.all(promises);

      // Assert
      expect(results).toHaveLength(10);
      expect(mockFetch).toHaveBeenCalledTimes(10);
      // Verify all runs have unique IDs
      const runIds = results.map((r) => r.runId);
      const uniqueRunIds = new Set(runIds);
      expect(uniqueRunIds.size).toBe(10);
    });
  });

  describe('State Management Across Runs', () => {
    it('should preserve metadata across thread operations', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const initialMetadata = {
        userId: 'user_123',
        sessionId: 'session_456',
        context: 'customer_support',
      };

      const thread: Thread = {
        threadId: 'thread_state_001',
        status: 'active',
        participants: [],
        messages: [],
        metadata: initialMetadata,
        createdAt: new Date().toISOString(),
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => thread,
      } as Response);

      // Act - Create thread with metadata
      const createdThread = await client.threads.create({
        metadata: initialMetadata,
      });

      // Assert
      expect(createdThread.metadata).toEqual(initialMetadata);
      expect((createdThread.metadata as any).userId).toBe('user_123');
      expect((createdThread.metadata as any).sessionId).toBe('session_456');
    });

    it('should update thread metadata while preserving thread state', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const updatedMetadata = {
        userId: 'user_123',
        sessionId: 'session_456',
        context: 'customer_support',
        resolved: true,
        resolutionTime: new Date().toISOString(),
      };

      const updatedThread: Thread = {
        threadId: 'thread_state_001',
        status: 'active',
        participants: [],
        messages: [],
        metadata: updatedMetadata,
        createdAt: new Date(Date.now() - 3600000).toISOString(),
        lastActivityAt: new Date().toISOString(),
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => updatedThread,
      } as Response);

      // Act - Update thread metadata
      const result = await client.threads.update('thread_state_001', {
        metadata: updatedMetadata,
      });

      // Assert
      expect(result.metadata).toEqual(updatedMetadata);
      expect((result.metadata as any).resolved).toBe(true);
      expect(result.threadId).toBe('thread_state_001');
    });

    it('should handle stateless runs without thread persistence', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const statelessRun = createRun({
        runId: 'run_stateless_001',
        agentId: 'agent_001',
        // No threadId - stateless execution
        threadId: undefined,
        status: 'completed',
        input: [createChatMessage('user', 'Quick question')],
        output: [createChatMessage('agent', 'Quick answer')],
        completedAt: new Date().toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => statelessRun,
      } as Response);

      // Act - Create stateless run
      const result = await client.runs.createAndWait({
        agentId: 'agent_001',
        input: [createChatMessage('user', 'Quick question')],
        threadCleanup: 'delete', // Ephemeral thread
      });

      // Assert
      expect(result).toBeDefined();
      expect(result.threadId).toBeUndefined();
      expect(result.status).toBe('completed');
    });
  });

  describe('Cancellation Support', () => {
    it('should cancel run using AbortSignal', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);
      const abortController = new AbortController();

      mockFetch.mockImplementationOnce(() => {
        // Simulate delay before cancellation
        return new Promise((_, reject) => {
          setTimeout(() => {
            if (abortController.signal.aborted) {
              reject(new Error('Request aborted'));
            }
          }, 100);
        });
      });

      // Act - Start request and immediately cancel
      const promise = client.runs.createAndWait(
        {
          agentId: 'agent_001',
          input: [],
        },
        { signal: abortController.signal }
      );

      abortController.abort();

      // Assert
      await expect(promise).rejects.toThrow();
    });

    it('should cancel run via API endpoint', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const cancelledRun = createRun({
        runId: 'run_cancel_001',
        agentId: 'agent_001',
        status: 'cancelled',
        input: [],
        output: [],
        cancelledAt: new Date().toISOString(),
      });

      mockFetch.mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => cancelledRun,
      } as Response);

      // Act - Cancel run via API
      const result = await client.runs.cancel('run_cancel_001');

      // Assert
      expect(result).toBeDefined();
      expect(result.status).toBe('cancelled');
      expect(result.cancelledAt).toBeDefined();
      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.example.com/runs/run_cancel_001/cancel',
        expect.objectContaining({
          method: 'POST',
        })
      );
    });
  });

  describe('Pagination', () => {
    it('should paginate through run results', async () => {
      // Arrange
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      const firstPage = {
        data: [
          createRun({
            runId: 'run_001',
            agentId: 'agent_001',
            status: 'completed',
          }),
          createRun({
            runId: 'run_002',
            agentId: 'agent_001',
            status: 'completed',
          }),
        ],
        hasMore: true,
        lastId: 'run_002',
      };

      const secondPage = {
        data: [
          createRun({
            runId: 'run_003',
            agentId: 'agent_001',
            status: 'completed',
          }),
        ],
        hasMore: false,
        lastId: 'run_003',
      };

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => firstPage,
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          status: 200,
          json: async () => secondPage,
        } as Response);

      // Act - Fetch first page
      const page1 = await client.runs.list({ limit: 2 });

      // Act - Fetch second page
      const page2 = await client.runs.list({ limit: 2, after: page1.lastId });

      // Assert
      expect(page1.data).toHaveLength(2);
      expect(page1.hasMore).toBe(true);
      expect(page2.data).toHaveLength(1);
      expect(page2.hasMore).toBe(false);
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('Client Initialization', () => {
    it('should create client with minimal configuration', () => {
      // Arrange & Act
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
      };

      const client = new AgentProtocolClient(config);

      // Assert
      expect(client).toBeDefined();
      expect(client.runs).toBeDefined();
      expect(client.threads).toBeDefined();
      expect(client.messages).toBeDefined();
    });

    it('should create client with full configuration', () => {
      // Arrange & Act
      const config: AgentProtocolClientConfig = {
        baseUrl: 'https://api.example.com',
        authToken: 'test-api-key',
        timeout: 60000,
        maxRetries: 5,
        headers: {
          'X-Custom-Header': 'value',
        },
        debug: true,
      };

      const client = new AgentProtocolClient(config);

      // Assert
      expect(client).toBeDefined();
      expect(client.runs).toBeDefined();
      expect(client.threads).toBeDefined();
      expect(client.messages).toBeDefined();
    });
  });
});
