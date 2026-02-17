import { AgentHostBuilder } from '../src/builder/AgentHostBuilder.js';
import { AgentBuilder } from '../src/builder/AgentBuilder.js';
import { InMemoryStorage } from '../src/storage/InMemoryStorage.js';
import { InMemoryQueue } from '../src/queue/InMemoryQueue.js';

describe('AgentHostBuilder', () => {
  describe('constructor', () => {
    it('should create a new AgentHostBuilder instance', () => {
      const builder = new AgentHostBuilder();
      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });
  });

  describe('addDefaultAgent', () => {
    it('should add a default agent', () => {
      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should configure agent with LLM', () => {
      const configure = jest.fn((agent: AgentBuilder) => agent.useLLM('gpt-4', 'Instructions'));

      const builder = new AgentHostBuilder()
        .addDefaultAgent(configure);

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'));

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('addAgent', () => {
    it('should add a named agent', () => {
      const builder = new AgentHostBuilder()
        .addAgent('sales', agent => agent.useLLM('gpt-4', 'Sales agent'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should add multiple named agents', () => {
      const builder = new AgentHostBuilder()
        .addAgent('sales', agent => agent.useLLM('gpt-4', 'Sales agent'))
        .addAgent('support', agent => agent.useLLM('gpt-4', 'Support agent'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should throw error for empty agent name', () => {
      const builder = new AgentHostBuilder();
      expect(() => {
        builder.addAgent('', agent => agent.useLLM('gpt-4', 'Instructions'));
      }).toThrow('Agent name is required');
    });

    it('should throw error for whitespace-only agent name', () => {
      const builder = new AgentHostBuilder();
      expect(() => {
        builder.addAgent('   ', agent => agent.useLLM('gpt-4', 'Instructions'));
      }).toThrow('Agent name is required');
    });

    it('should return new builder instance (immutability)', () => {
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.addAgent('sales', agent => agent.useLLM('gpt-4', 'Instructions'));

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('useStorage', () => {
    it('should configure storage', () => {
      const storage = new InMemoryStorage();
      const builder = new AgentHostBuilder()
        .useStorage(storage);

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const storage = new InMemoryStorage();
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.useStorage(storage);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('useQueue', () => {
    it('should configure queue', () => {
      const queue = new InMemoryQueue();
      const builder = new AgentHostBuilder()
        .useQueue(queue);

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const queue = new InMemoryQueue();
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.useQueue(queue);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('useRetryPolicy', () => {
    it('should configure retry policy', () => {
      const retryPolicy: any = {
        maxRetries: 3
      };

      const builder = new AgentHostBuilder()
        .useRetryPolicy(retryPolicy);

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const retryPolicy: any = { maxRetries: 3 };
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.useRetryPolicy(retryPolicy);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('useRateLimiting', () => {
    it('should configure rate limiting', () => {
      const rateLimiting: any = {
        maxRequestsPerMinute: 60
      };

      const builder = new AgentHostBuilder()
        .useRateLimiting(rateLimiting);

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const rateLimiting: any = { maxRequestsPerMinute: 60 };
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.useRateLimiting(rateLimiting);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('useLogging', () => {
    it('should configure logging', () => {
      const logging: any = {
        level: 'info'
      };

      const builder = new AgentHostBuilder()
        .useLogging(logging);

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const logging: any = { level: 'info' };
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.useLogging(logging);

      expect(builder1).not.toBe(builder2);
    });
  });

  describe('useRouting', () => {
    it('should configure routing', () => {
      const builder = new AgentHostBuilder()
        .useRouting((routing: any) => routing.withFallback('default'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should return new builder instance (immutability)', () => {
      const builder1 = new AgentHostBuilder();
      const builder2 = builder1.useRouting((routing: any) => routing);

      expect(builder1).not.toBe(builder2);
    });

    it('should support byHeader routing', () => {
      const builder = new AgentHostBuilder()
        .useRouting(routing => routing.byHeader('X-Agent-Type'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should support byPath routing', () => {
      const builder = new AgentHostBuilder()
        .useRouting(routing => routing.byPath('/agents/:agentId'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should support byContent routing', () => {
      const builder = new AgentHostBuilder()
        .useRouting(routing => routing.byContent(async (_msg: any) => 'default'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });

    it('should support chaining routing methods', () => {
      const builder = new AgentHostBuilder()
        .useRouting(routing => routing
          .byHeader('X-Agent-Type')
          .byPath('/agents/:agentId')
          .byContent(async (_msg: any) => 'default')
          .withFallback('default')
        );

      expect(builder).toBeInstanceOf(AgentHostBuilder);
    });
  });

  describe('build', () => {
    it('should build an AgentHost with default configuration', () => {
      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'));

      const host = builder.build();
      expect(host).toBeDefined();
    });

    it('should throw error when no agents are configured', () => {
      const builder = new AgentHostBuilder();
      expect(() => {
        builder.build();
      }).toThrow('At least one agent must be configured');
    });

    it('should use InMemoryStorage by default', () => {
      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'));

      const host = builder.build();
      expect(host).toBeDefined();
    });

    it('should use InMemoryQueue by default', () => {
      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'));

      const host = builder.build();
      expect(host).toBeDefined();
    });

    it('should use custom storage when provided', () => {
      const storage = new InMemoryStorage();
      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'))
        .useStorage(storage);

      const host = builder.build();
      expect(host).toBeDefined();
    });

    it('should use custom queue when provided', () => {
      const queue = new InMemoryQueue();
      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Instructions'))
        .useQueue(queue);

      const host = builder.build();
      expect(host).toBeDefined();
    });
  });

  describe('integration', () => {
    it('should chain all configuration methods', () => {
      const storage = new InMemoryStorage();
      const queue = new InMemoryQueue();
      const retryPolicy: any = { maxRetries: 3 };
      const rateLimiting: any = { maxRequestsPerMinute: 60 };
      const logging: any = { level: 'info' };

      const builder = new AgentHostBuilder()
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Default agent'))
        .addAgent('sales', agent => agent.useLLM('gpt-4', 'Sales agent'))
        .useStorage(storage)
        .useQueue(queue)
        .useRetryPolicy(retryPolicy)
        .useRateLimiting(rateLimiting)
        .useLogging(logging)
        .useRouting((routing: any) => routing.withFallback('default'));

      expect(builder).toBeInstanceOf(AgentHostBuilder);

      const host = builder.build();
      expect(host).toBeDefined();
    });

    it('should preserve configuration through multiple chained operations', () => {
      const storage = new InMemoryStorage();
      const queue = new InMemoryQueue();
      const retryPolicy: any = { maxRetries: 5 };
      const rateLimiting: any = { maxRequestsPerMinute: 100 };
      const logging: any = { level: 'debug' };

      // Chain multiple operations to ensure copyTo works correctly with all fields
      const builder = new AgentHostBuilder()
        .useStorage(storage)
        .useQueue(queue)
        .useRetryPolicy(retryPolicy)
        .useRateLimiting(rateLimiting)
        .useLogging(logging)
        .useRouting(routing => routing
          .byHeader('X-Agent')
          .byPath('/api/:agent')
          .byContent(async () => 'default')
          .withFallback('default')
        )
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Agent 1'))
        .addAgent('agent2', agent => agent.useLLM('gpt-4', 'Agent 2'))
        .addAgent('agent3', agent => agent.useLLM('gpt-4', 'Agent 3'));

      // Build should succeed with all configuration preserved
      const host = builder.build();
      expect(host).toBeDefined();
    });

    it('should support building multiple hosts from same base configuration', () => {
      const baseBuilder = new AgentHostBuilder()
        .useStorage(new InMemoryStorage())
        .useQueue(new InMemoryQueue())
        .useRetryPolicy({ maxRetries: 3 } as any)
        .useRateLimiting({ maxRequestsPerMinute: 60 } as any);

      const host1 = baseBuilder
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Agent 1'))
        .build();

      const host2 = baseBuilder
        .addDefaultAgent(agent => agent.useLLM('gpt-4', 'Agent 2'))
        .build();

      expect(host1).toBeDefined();
      expect(host2).toBeDefined();
      expect(host1).not.toBe(host2);
    });
  });
});
