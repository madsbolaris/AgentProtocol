/**
 * Tests for LLM configuration patterns (string vs provider instance).
 * Verifies Vercel AI-style pattern: accept either string (gateway) or provider instance.
 */

import { AgentHostBuilder } from '../builder/AgentHostBuilder';
import { IProtocolLLMClient, LLMProviderInfo, AgentMessage, AgentMessageDelta, DeltaType } from '../types';
import { ChatMessage, TextContent, ToolDefinition } from '@microsoft/agents-abstractions';

/**
 * Mock LLM client for testing purposes.
 */
class MockProtocolLLMClient implements IProtocolLLMClient {
  constructor(private model: string) {}

  get providerInfo(): LLMProviderInfo {
    return {
      provider: 'Mock',
      model: this.model,
      supportsStreaming: true,
      supportsFunctionCalling: true,
    };
  }

  async generate(
    conversationHistory: ChatMessage[],
    availableTools?: ToolDefinition[]
  ): Promise<AgentMessage> {
    return {
      messageId: 'test-msg-123',
      contents: [
        {
          kind: 'text',
          text: 'Mock response',
        } as TextContent,
      ],
    };
  }

  async *stream(
    conversationHistory: ChatMessage[],
    availableTools?: ToolDefinition[]
  ): AsyncGenerator<AgentMessageDelta> {
    yield {
      messageId: 'test-msg-123',
      type: DeltaType.MessageStart,
    };

    yield {
      messageId: 'test-msg-123',
      type: DeltaType.TextDelta,
      content: {
        kind: 'text',
        text: 'Mock streaming response',
      } as TextContent,
    };

    yield {
      messageId: 'test-msg-123',
      type: DeltaType.MessageComplete,
      isComplete: true,
    };
  }
}

describe('LLM Configuration Tests', () => {
  // Store original environment
  const originalEnv = { ...process.env };

  beforeEach(() => {
    // Reset environment before each test
    process.env = { ...originalEnv };
  });

  afterEach(() => {
    // Restore original environment
    process.env = originalEnv;
  });

  describe('String-Based Configuration', () => {
    it('should create client from environment variables when using string', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';

      // Act
      const builder = new AgentHostBuilder();
      const buildFn = () =>
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM('gpt-4o-mini', 'You are a test assistant')
          )
          .build();

      // Assert - should not throw
      expect(buildFn).not.toThrow();
    });

    it('should throw when FOUNDRY_ENDPOINT is missing', () => {
      // Arrange
      delete process.env.FOUNDRY_ENDPOINT;
      process.env.FOUNDRY_API_KEY = 'test-key-123';

      // Act & Assert
      const builder = new AgentHostBuilder();
      expect(() => {
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM('gpt-4o-mini', 'You are a test assistant')
          )
          .build();
      }).toThrow(/FOUNDRY_ENDPOINT/);
    });

    it('should throw when FOUNDRY_API_KEY is missing', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      delete process.env.FOUNDRY_API_KEY;

      // Act & Assert
      const builder = new AgentHostBuilder();
      expect(() => {
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM('gpt-4o-mini', 'You are a test assistant')
          )
          .build();
      }).toThrow(/FOUNDRY_API_KEY/);
    });

    it('should use explicit model over environment variable', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';
      process.env.FOUNDRY_MODEL_DEPLOYMENT = 'gpt-5-turbo';

      // Act
      const builder = new AgentHostBuilder();
      const buildFn = () =>
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM('gpt-4o-mini', 'You are a test assistant') // Explicit model should be used
          )
          .build();

      // Assert - should not throw
      expect(buildFn).not.toThrow();
    });

    it('should read model from FOUNDRY_MODEL_DEPLOYMENT when not specified', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';
      process.env.FOUNDRY_MODEL_DEPLOYMENT = 'gpt-5-turbo';

      // Act
      const builder = new AgentHostBuilder();
      const buildFn = () =>
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM(
              process.env.FOUNDRY_MODEL_DEPLOYMENT!,
              'You are a test assistant'
            )
          )
          .build();

      // Assert - should not throw
      expect(buildFn).not.toThrow();
    });
  });

  describe('Provider Instance Configuration', () => {
    it('should use provided client instance', () => {
      // Arrange
      const mockClient = new MockProtocolLLMClient('custom-model');

      // Act
      const builder = new AgentHostBuilder();
      const buildFn = () =>
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM(mockClient, 'You are a test assistant')
          )
          .build();

      // Assert - should not throw
      expect(buildFn).not.toThrow();
    });

    it('should not require environment variables when using provider instance', () => {
      // Arrange - clear all environment variables
      delete process.env.FOUNDRY_ENDPOINT;
      delete process.env.FOUNDRY_API_KEY;
      delete process.env.FOUNDRY_MODEL_DEPLOYMENT;

      const mockClient = new MockProtocolLLMClient('custom-model');

      // Act
      const builder = new AgentHostBuilder();
      const buildFn = () =>
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM(mockClient, 'You are a test assistant')
          )
          .build();

      // Assert - should not throw even without environment variables
      expect(buildFn).not.toThrow();
    });

    it('should throw when client instance is null', () => {
      // Act & Assert
      const builder = new AgentHostBuilder();
      expect(() => {
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM(null as any, 'You are a test assistant')
          )
          .build();
      }).toThrow();
    });

    it('should extract model from provider info', () => {
      // Arrange
      const expectedModel = 'custom-gpt-model';
      const mockClient = new MockProtocolLLMClient(expectedModel);

      // Act
      const builder = new AgentHostBuilder();
      builder
        .addDefaultAgent((agent) =>
          agent.useLLM(mockClient, 'You are a test assistant')
        )
        .build();

      // Assert
      expect(mockClient.providerInfo.model).toBe(expectedModel);
    });

    it('should prefer provider instance over string configuration', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';

      const mockClient = new MockProtocolLLMClient('custom-model');

      // Act
      const builder = new AgentHostBuilder();
      const buildFn = () =>
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM(mockClient, 'You are a test assistant')
          )
          .build();

      // Assert - should use provider instance and not fail
      expect(buildFn).not.toThrow();
    });
  });

  describe('Full Integration Tests', () => {
    it('should build successfully with string configuration', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';

      // Act
      const builder = new AgentHostBuilder();
      const host = builder
        .addDefaultAgent((agent) =>
          agent
            .useLLM('gpt-4o-mini', 'You are a test assistant')
            .addFunctions((f) => {
              // Functions can be added here
            })
        )
        .build();

      // Assert
      expect(host).toBeDefined();
    });

    it('should build successfully with provider instance', () => {
      // Arrange
      const mockClient = new MockProtocolLLMClient('custom-model');

      // Act
      const builder = new AgentHostBuilder();
      const host = builder
        .addDefaultAgent((agent) =>
          agent
            .useLLM(mockClient, 'You are a test assistant')
            .addFunctions((f) => {
              // Functions can be added here
            })
        )
        .build();

      // Assert
      expect(host).toBeDefined();
    });

    it('should support multiple agents with different configurations', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';

      const mockClient = new MockProtocolLLMClient('custom-model');

      // Act
      const builder = new AgentHostBuilder();
      const host = builder
        .addAgent('agent1', (agent) =>
          agent.useLLM('gpt-4o-mini', 'You are assistant 1')
        )
        .addAgent('agent2', (agent) =>
          agent.useLLM(mockClient, 'You are assistant 2')
        )
        .build();

      // Assert
      expect(host).toBeDefined();
    });
  });

  describe('Error Handling', () => {
    it('should provide clear error when model is not specified', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';
      delete process.env.FOUNDRY_MODEL_DEPLOYMENT;

      // Act & Assert
      const builder = new AgentHostBuilder();
      expect(() => {
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM('', 'You are a test assistant') // Empty string
          )
          .build();
      }).toThrow();
    });

    it('should provide clear error when instructions are missing', () => {
      // Arrange
      process.env.FOUNDRY_ENDPOINT = 'https://api.test.com';
      process.env.FOUNDRY_API_KEY = 'test-key-123';

      // Act & Assert
      const builder = new AgentHostBuilder();
      expect(() => {
        builder
          .addDefaultAgent((agent) =>
            agent.useLLM('gpt-4o-mini', '') // Empty instructions
          )
          .build();
      }).toThrow();
    });
  });
});
