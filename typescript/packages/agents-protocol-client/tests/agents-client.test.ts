/**
 * Tests for AgentsClient covering all agent management operations
 * Matches the .NET AgentsClientTests.cs implementation
 */

import { AgentProtocolClient } from '../src/client';
import type {
  AgentCard,
  PromptAgent,
  AITool,
} from '@microsoft/agents-protocol-abstractions';
import {
  AuthenticationError,
  NotFoundError,
  ValidationError,
} from '../src/errors';

// Mock fetch globally for testing
global.fetch = jest.fn();

describe('AgentsClient', () => {
  let client: AgentProtocolClient;
  const mockBaseUrl = 'https://api.example.com';

  beforeEach(() => {
    client = new AgentProtocolClient({
      baseUrl: mockBaseUrl,
      debug: false,
    });
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('getCard', () => {
    it('should retrieve agent card with capabilities and tools', async () => {
      const expectedCard: AgentCard = {
        agentId: 'agent_001',
        name: 'Support Agent',
        description: 'A helpful customer support agent',
        capabilities: {
          vision: true,
          thinking: false,
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 128000,
          maxInputTokens: 120000,
          maxOutputTokens: 8000,
          supportedContentTypes: ['text', 'image'],
          provider: 'openai',
          modelFamily: 'gpt-4',
        },
        inputModes: ['text', 'image'],
        outputModes: ['text'],
        version: '1.0.0',
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedCard,
      });

      const result = await client.agents.getCard('agent_001');

      expect(result).toEqual(expectedCard);
      expect(result.agentId).toBe('agent_001');
      expect(result.name).toBe('Support Agent');
      expect(result.capabilities?.vision).toBe(true);
      expect(result.capabilities?.maxTokens).toBe(128000);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/agents/agent_001/card`,
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should retrieve agent card with tools', async () => {
      const searchOrdersTool: AITool = {
        name: 'search_orders',
        description: 'Search customer orders by customer ID',
        parameters: {
          properties: {
            customerId: {
              description: 'Customer ID',
            },
          },
          required: ['customerId'],
        },
      };

      const expectedCard: AgentCard = {
        agentId: 'agent_001',
        name: 'Support Agent',
        description: 'A helpful customer support agent',
        capabilities: {
          vision: true,
          thinking: false,
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 128000,
          maxInputTokens: 120000,
          maxOutputTokens: 8000,
          supportedContentTypes: ['text', 'image'],
          provider: 'openai',
          modelFamily: 'gpt-4',
        },
        metadata: {
          tools: [searchOrdersTool],
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedCard,
      });

      const result = await client.agents.getCard('agent_001');

      expect(result).toEqual(expectedCard);
      expect(result.metadata?.tools).toBeDefined();
      expect(Array.isArray(result.metadata?.tools)).toBe(true);
      const tools = result.metadata?.tools as AITool[];
      expect(tools[0].name).toBe('search_orders');
    });

    it('should throw error for null or empty agent ID', async () => {
      await expect(client.agents.getCard('')).rejects.toThrow(
        'Agent ID cannot be null or empty'
      );
      await expect(client.agents.getCard('   ')).rejects.toThrow(
        'Agent ID cannot be null or empty'
      );
    });

    it('should handle agent not found error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Agent not found',
          resource: 'agent_999',
        }),
      });

      await expect(client.agents.getCard('agent_999')).rejects.toThrow(
        NotFoundError
      );
    });

    it('should handle authentication error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          message: 'Unauthorized',
        }),
      });

      await expect(client.agents.getCard('agent_001')).rejects.toThrow(
        AuthenticationError
      );
    });

    it('should validate required agentId parameter', async () => {
      await expect(client.agents.getCard('')).rejects.toThrow();
    });
  });

  describe('inspect', () => {
    it('should inspect agent definition and return capabilities', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'weather-agent',
        description: 'Weather information assistant',
        tools: [
          {
            name: 'get_weather',
            description: 'Get current weather for a location',
            parameters: {
              properties: {
                location: {
                  description: 'City name',
                },
              },
              required: ['location'],
            },
          },
        ],
      };

      const expectedCard: AgentCard = {
        agentId: '', // Ephemeral - not persisted
        name: 'Ephemeral Agent',
        description: 'Temporary agent for inspection',
        capabilities: {
          vision: true,
          thinking: false,
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 128000,
          maxInputTokens: 120000,
          maxOutputTokens: 8000,
          supportedContentTypes: ['text'],
          provider: 'openai',
          modelFamily: 'gpt-4',
        },
        metadata: {
          tools: agent.tools,
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedCard,
      });

      const result = await client.agents.inspect(agent);

      expect(result).toEqual(expectedCard);
      expect(result.agentId).toBe(''); // Not persisted
      expect(result.capabilities?.functionCalling).toBe(true);
      expect(result.capabilities?.maxTokens).toBe(128000);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/agents/inspect`,
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('weather-agent'),
        })
      );
    });

    it('should inspect agent with model capabilities', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'claude-agent',
        description: 'Research analyst powered by Claude',
        metadata: {
          model: 'claude-3-sonnet',
        },
      };

      const expectedCard: AgentCard = {
        agentId: '',
        name: 'Claude 3 Sonnet',
        description: 'Research analyst',
        capabilities: {
          vision: true,
          thinking: true, // Extended thinking support
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 200000,
          maxInputTokens: 196000,
          maxOutputTokens: 4096,
          supportedContentTypes: ['text', 'image'],
          provider: 'anthropic',
          modelFamily: 'claude-3',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedCard,
      });

      const result = await client.agents.inspect(agent);

      expect(result.capabilities?.thinking).toBe(true); // Extended thinking
      expect(result.capabilities?.maxTokens).toBe(200000);
      expect(result.capabilities?.provider).toBe('anthropic');
    });

    it('should inspect agent with tool definitions and validate tool support', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'file-manager',
        description: 'File management assistant',
        tools: [
          {
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
          },
        ],
      };

      const expectedCard: AgentCard = {
        agentId: '',
        name: 'File Manager Agent',
        description: 'Manages file operations',
        capabilities: {
          vision: false,
          thinking: false,
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 128000,
          maxInputTokens: 120000,
          maxOutputTokens: 8000,
          supportedContentTypes: ['text'],
          provider: 'openai',
          modelFamily: 'gpt-4',
        },
        metadata: {
          tools: agent.tools,
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedCard,
      });

      const result = await client.agents.inspect(agent);

      expect(result.capabilities?.functionCalling).toBe(true);
      expect(result.metadata?.tools).toBeDefined();
      const tools = result.metadata?.tools as AITool[];
      expect(tools[0].name).toBe('delete_file');
      expect(tools[0].requiresApproval).toBe(true);
    });

    it('should validate required agent parameter', async () => {
      await expect(client.agents.inspect(null as any)).rejects.toThrow(
        'Agent definition cannot be null'
      );
    });

    it('should throw error for null agent in validate', async () => {
      await expect(client.agents.validate(null as any)).rejects.toThrow(
        'Agent definition cannot be null'
      );
    });

    it('should throw error for null agent in register', async () => {
      await expect(client.agents.register(null as any)).rejects.toThrow(
        'Agent definition cannot be null'
      );
    });

    it('should handle validation errors from inspect', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: '', // Invalid - empty name
        description: 'Test agent',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({
          message: 'Validation failed',
          errors: {
            name: 'Name is required',
          },
        }),
      });

      await expect(client.agents.inspect(agent)).rejects.toThrow(
        ValidationError
      );
    });
  });

  describe('register', () => {
    it('should register a new agent and return agent card', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'customer-support',
        displayName: 'Customer Support Agent',
        description: 'Handles customer inquiries',
        tools: [
          {
            name: 'search_kb',
            description: 'Search knowledge base',
            parameters: {
              properties: {
                query: {
                  description: 'Search query',
                },
              },
              required: ['query'],
            },
          },
        ],
      };

      const expectedCard: AgentCard = {
        agentId: 'agent_new_123',
        name: 'customer-support',
        displayName: 'Customer Support Agent',
        description: 'Handles customer inquiries',
        capabilities: {
          vision: false,
          thinking: false,
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 128000,
          maxInputTokens: 120000,
          maxOutputTokens: 8000,
          supportedContentTypes: ['text'],
          provider: 'openai',
          modelFamily: 'gpt-4',
        },
        version: '1.0.0',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        metadata: {
          tools: agent.tools,
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 201,
        json: async () => expectedCard,
      });

      const result = await client.agents.register(agent);

      expect(result).toEqual(expectedCard);
      expect(result.agentId).toBe('agent_new_123');
      expect(result.name).toBe('customer-support');
      expect(result.displayName).toBe('Customer Support Agent');
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/agents`,
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should handle duplicate agent registration error', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'duplicate-agent',
        description: 'Test agent',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 409,
        statusText: 'Conflict',
        json: async () => ({
          message: 'Agent already exists',
          code: 'DUPLICATE_AGENT',
        }),
      });

      await expect(client.agents.register(agent)).rejects.toThrow();
    }, 10000);
  });

  describe('update', () => {
    it('should update existing agent configuration', async () => {
      const agentId = 'agent_001';
      const updates: Partial<PromptAgent> = {
        description: 'Updated description',
        metadata: {
          version: '2.0.0',
          updated: true,
        },
      };

      const expectedCard: AgentCard = {
        agentId: 'agent_001',
        name: 'support-agent',
        description: 'Updated description',
        capabilities: {
          vision: true,
          thinking: false,
          functionCalling: true,
          structuredOutput: true,
          streaming: true,
          parallelToolCalls: true,
          maxTokens: 128000,
          maxInputTokens: 120000,
          maxOutputTokens: 8000,
          supportedContentTypes: ['text', 'image'],
          provider: 'openai',
          modelFamily: 'gpt-4',
        },
        version: '2.0.0',
        updatedAt: new Date().toISOString(),
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedCard,
      });

      const result = await client.agents.update(agentId, updates);

      expect(result).toEqual(expectedCard);
      expect(result.description).toBe('Updated description');
      expect(result.version).toBe('2.0.0');
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/agents/${agentId}`,
        expect.objectContaining({
          method: 'PATCH',
          body: expect.stringContaining('Updated description'),
        })
      );
    });

    it('should throw error for null or empty agent ID', async () => {
      const updates: Partial<PromptAgent> = { description: 'Updated' };

      await expect(client.agents.update('', updates)).rejects.toThrow(
        'Agent ID cannot be null or empty'
      );
      await expect(client.agents.update('   ', updates)).rejects.toThrow(
        'Agent ID cannot be null or empty'
      );
    });

    it('should throw error for null updates', async () => {
      await expect(client.agents.update('agent_001', null as any)).rejects.toThrow(
        'Updates cannot be null'
      );
    });

    it('should handle update of non-existent agent', async () => {
      const agentId = 'agent_999';
      const updates: Partial<PromptAgent> = {
        description: 'Updated description',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Agent not found',
          resource: agentId,
        }),
      });

      await expect(client.agents.update(agentId, updates)).rejects.toThrow(
        NotFoundError
      );
    });
  });

  describe('delete', () => {
    it('should delete an agent successfully', async () => {
      const agentId = 'agent_to_delete';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 204,
      });

      await client.agents.remove(agentId);

      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/agents/${agentId}`,
        expect.objectContaining({
          method: 'DELETE',
        })
      );
    });

    it('should throw error for null or empty agent ID', async () => {
      await expect(client.agents.remove('')).rejects.toThrow(
        'Agent ID cannot be null or empty'
      );
      await expect(client.agents.remove('   ')).rejects.toThrow(
        'Agent ID cannot be null or empty'
      );
    });

    it('should handle deletion of non-existent agent', async () => {
      const agentId = 'agent_999';

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({
          message: 'Agent not found',
          resource: agentId,
        }),
      });

      await expect(client.agents.remove(agentId)).rejects.toThrow(
        NotFoundError
      );
    });

    it('should validate required agentId parameter for delete', async () => {
      await expect(client.agents.remove('')).rejects.toThrow();
    });
  });

  describe('list', () => {
    it('should list all agents with pagination', async () => {
      const expectedResponse = {
        data: [
          {
            agentId: 'agent_001',
            name: 'support-agent',
            description: 'Customer support',
            version: '1.0.0',
          },
          {
            agentId: 'agent_002',
            name: 'sales-agent',
            description: 'Sales assistant',
            version: '1.0.0',
          },
        ],
        hasMore: false,
        firstId: 'agent_001',
        lastId: 'agent_002',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.agents.list({ limit: 10 });

      expect(result.data).toHaveLength(2);
      expect(result.data[0].agentId).toBe('agent_001');
      expect(result.data[1].agentId).toBe('agent_002');
      expect(result.hasMore).toBe(false);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`${mockBaseUrl}/agents`),
        expect.objectContaining({
          method: 'GET',
        })
      );
    });

    it('should list agents with pagination cursor', async () => {
      const expectedResponse = {
        data: [
          {
            agentId: 'agent_003',
            name: 'marketing-agent',
            description: 'Marketing assistant',
            version: '1.0.0',
          },
        ],
        hasMore: true,
        firstId: 'agent_003',
        lastId: 'agent_003',
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.agents.list({
        limit: 1,
        after: 'agent_002',
      });

      expect(result.data).toHaveLength(1);
      expect(result.hasMore).toBe(true);
      expect(result.data[0].agentId).toBe('agent_003');
    });

    it('should return empty list when no agents exist', async () => {
      const expectedResponse = {
        data: [],
        hasMore: false,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => expectedResponse,
      });

      const result = await client.agents.list();

      expect(result.data).toHaveLength(0);
      expect(result.hasMore).toBe(false);
    });
  });

  describe('validation', () => {
    it('should validate agent with valid configuration', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'valid-agent',
        description: 'A valid agent configuration',
        tools: [
          {
            name: 'test_tool',
            description: 'Test tool',
            parameters: {
              properties: {
                param1: {
                  description: 'Parameter 1',
                },
              },
              required: ['param1'],
            },
          },
        ],
      };

      const validationResult = {
        valid: true,
        errors: [],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => validationResult,
      });

      const result = await client.agents.validate(agent);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(global.fetch).toHaveBeenCalledWith(
        `${mockBaseUrl}/agents/validate`,
        expect.objectContaining({
          method: 'POST',
        })
      );
    });

    it('should return validation errors for invalid agent', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: '', // Invalid - empty name
        description: '', // Invalid - empty description
      };

      const validationResult = {
        valid: false,
        errors: [
          {
            field: 'name',
            message: 'Name cannot be empty',
          },
          {
            field: 'description',
            message: 'Description cannot be empty',
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => validationResult,
      });

      const result = await client.agents.validate(agent);

      expect(result.valid).toBe(false);
      expect(result.errors).toHaveLength(2);
      expect(result.errors[0].field).toBe('name');
      expect(result.errors[1].field).toBe('description');
    });

    it('should validate agent with invalid tool parameters', async () => {
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'agent-with-bad-tool',
        description: 'Agent with invalid tool',
        tools: [
          {
            name: '', // Invalid - empty name
            description: 'Tool without name',
            parameters: {
              properties: {},
              required: ['nonexistent'], // Invalid - required param not in properties
            },
          },
        ],
      };

      const validationResult = {
        valid: false,
        errors: [
          {
            field: 'tools[0].name',
            message: 'Tool name cannot be empty',
          },
          {
            field: 'tools[0].parameters.required',
            message: 'Required parameter "nonexistent" not found in properties',
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => validationResult,
      });

      const result = await client.agents.validate(agent);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });
  });

  describe('error handling', () => {
    it('should handle network errors gracefully', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(
        new Error('Network error')
      );

      await expect(client.agents.getCard('agent_001')).rejects.toThrow();
    }, 10000);

    it('should handle timeout errors', async () => {
      (global.fetch as jest.Mock).mockRejectedValue(
        new Error('Timeout')
      );

      await expect(client.agents.getCard('agent_001')).rejects.toThrow();
    }, 10000);

    it('should handle malformed JSON responses', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => {
          throw new Error('Invalid JSON');
        },
      });

      await expect(client.agents.getCard('agent_001')).rejects.toThrow();
    }, 10000);

    it('should include error details in error objects', async () => {
      const errorDetails = {
        message: 'Validation failed',
        code: 'VALIDATION_ERROR',
        details: {
          field: 'name',
          reason: 'Name is required',
        },
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => errorDetails,
      });

      try {
        await client.agents.inspect({
          kind: 'prompt',
          name: '',
          description: 'Test',
        });
        fail('Should have thrown an error');
      } catch (error) {
        expect(error).toBeInstanceOf(ValidationError);
        const validationError = error as ValidationError;
        expect(validationError.message).toContain('Validation failed');
      }
    });
  });

  describe('AbortController support', () => {
    it('should support request cancellation with AbortSignal', async () => {
      const controller = new AbortController();

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        controller.abort();
        return Promise.reject(new Error('AbortError'));
      });

      await expect(
        client.agents.getCard('agent_001', { signal: controller.signal })
      ).rejects.toThrow();
    });

    it('should cancel inspect operation with AbortSignal', async () => {
      const controller = new AbortController();
      const agent: PromptAgent = {
        kind: 'prompt',
        name: 'test-agent',
        description: 'Test agent',
      };

      (global.fetch as jest.Mock).mockImplementationOnce(() => {
        controller.abort();
        return Promise.reject(new Error('AbortError'));
      });

      await expect(
        client.agents.inspect(agent, { signal: controller.signal })
      ).rejects.toThrow();
    });
  });

  describe('retry logic', () => {
    it('should retry failed requests up to max retries', async () => {
      let attempts = 0;

      (global.fetch as jest.Mock).mockImplementation(() => {
        attempts++;
        if (attempts < 4) {
          return Promise.reject(new Error('Temporary failure'));
        }
        return Promise.resolve({
          ok: true,
          status: 200,
          json: async () => ({
            agentId: 'agent_001',
            name: 'test-agent',
            description: 'Test agent',
          }),
        });
      });

      const result = await client.agents.getCard('agent_001');

      expect(attempts).toBe(4); // Initial attempt + 3 retries
      expect(result.agentId).toBe('agent_001');
    }, 10000);

    it('should not retry on authentication errors', async () => {
      let attempts = 0;

      (global.fetch as jest.Mock).mockImplementation(() => {
        attempts++;
        return Promise.resolve({
          ok: false,
          status: 401,
          json: async () => ({
            message: 'Unauthorized',
          }),
        });
      });

      await expect(client.agents.getCard('agent_001')).rejects.toThrow(
        AuthenticationError
      );

      expect(attempts).toBe(1); // Should not retry
    });

    it('should not retry on not found errors', async () => {
      let attempts = 0;

      (global.fetch as jest.Mock).mockImplementation(() => {
        attempts++;
        return Promise.resolve({
          ok: false,
          status: 404,
          json: async () => ({
            message: 'Not found',
          }),
        });
      });

      await expect(client.agents.getCard('agent_999')).rejects.toThrow(
        NotFoundError
      );

      expect(attempts).toBe(1); // Should not retry
    });
  });
});
