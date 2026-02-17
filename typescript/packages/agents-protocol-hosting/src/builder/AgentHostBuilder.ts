import { AgentBuilder } from './AgentBuilder.js';
import { AgentHost } from '../hosting/AgentHost.js';
import { IStorage } from '../storage/IStorage.js';
import { InMemoryStorage } from '../storage/InMemoryStorage.js';
import { IQueue } from '../queue/IQueue.js';
import { InMemoryQueue } from '../queue/InMemoryQueue.js';
import { RetryPolicy, RateLimitingConfig, LoggingConfig, ChatMessage } from '../core/types.js';

/**
 * Configuration for agent routing.
 */
export interface RoutingBuilder {
  /**
   * Route based on HTTP header value.
   *
   * @param header - Header name to inspect
   * @returns Updated routing builder
   */
  byHeader(header: string): RoutingBuilder;

  /**
   * Route based on URL path parameter.
   *
   * @param pattern - Path pattern with parameters
   * @returns Updated routing builder
   */
  byPath(pattern: string): RoutingBuilder;

  /**
   * Route based on message content analysis.
   *
   * @param fn - Function that determines agent name from message
   * @returns Updated routing builder
   */
  byContent(fn: (msg: ChatMessage) => Promise<string>): RoutingBuilder;

  /**
   * Specifies fallback agent when routing fails.
   *
   * @param agentName - Name of fallback agent
   * @returns Updated routing builder
   */
  withFallback(agentName: string): RoutingBuilder;
}

/**
 * Builder for configuring Agent Protocol host services.
 *
 * @example
 * ```typescript
 * const host = new AgentHostBuilder()
 *   .addDefaultAgent(agent => agent
 *     .useLLM('gpt-4', 'You are helpful.')
 *   )
 *   .build();
 * ```
 */
export class AgentHostBuilder {
  private readonly agentConfigurations: Map<string, (builder: AgentBuilder) => AgentBuilder> = new Map();
  private readonly services: Map<symbol, unknown> = new Map();
  private storage?: IStorage;
  private queue?: IQueue;
  private retryPolicy?: RetryPolicy;
  private rateLimiting?: RateLimitingConfig;
  private logging?: LoggingConfig;
  private routing?: RoutingBuilder;

  /**
   * Creates a new agent host builder.
   */
  constructor() {}

  /**
   * Adds a default agent with the specified configuration.
   *
   * @param configure - Function that configures an AgentBuilder
   * @returns A new AgentHostBuilder with the agent added
   *
   * @example
   * ```typescript
   * builder.addDefaultAgent(agent => agent
   *   .useLLM('gpt-4', 'You are a helpful assistant.')
   *   .addFunctions(f => f
   *     .add('getTime@v1', 'Gets current time', {}, (): string => new Date().toISOString(),
   *          { trustLevel: 'trusted' })
   *   )
   * );
   * ```
   */
  addDefaultAgent(configure: (builder: AgentBuilder) => AgentBuilder): AgentHostBuilder {
    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.agentConfigurations.set('default', configure);
    return newBuilder;
  }

  /**
   * Adds a named agent with routing configuration.
   *
   * @param name - Unique name for this agent
   * @param configure - Function that configures an AgentBuilder
   * @returns A new AgentHostBuilder with the agent added
   *
   * @example
   * ```typescript
   * builder
   *   .addAgent('sales', agent => agent.useLLM('gpt-4', 'Sales agent'))
   *   .addAgent('support', agent => agent.useLLM('gpt-4', 'Support agent'));
   * ```
   */
  addAgent(name: string, configure: (builder: AgentBuilder) => AgentBuilder): AgentHostBuilder {
    if (!name || name.trim().length === 0) {
      throw new Error('Agent name is required');
    }

    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.agentConfigurations.set(name, configure);
    return newBuilder;
  }

  /**
   * Configures storage for conversation state and history.
   *
   * @param storage - Storage implementation (InMemoryStorage, PostgresStorage, etc.)
   * @returns A new AgentHostBuilder with storage configured
   *
   * @example
   * ```typescript
   * import { PostgresStorage } from '@microsoft/agents-hosting/storage';
   *
   * builder.useStorage(new PostgresStorage({
   *   connectionString: process.env.DATABASE_URL,
   *   pool: { min: 2, max: 10 }
   * }));
   * ```
   */
  useStorage(storage: IStorage): AgentHostBuilder {
    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.storage = storage;
    return newBuilder;
  }

  /**
   * Configures message queue for distributed processing.
   *
   * @param queue - Queue implementation (InMemoryQueue, RedisQueue, etc.)
   * @returns A new AgentHostBuilder with queue configured
   *
   * @example
   * ```typescript
   * import { RedisQueue } from '@microsoft/agents-hosting/queue';
   *
   * builder.useQueue(new RedisQueue({
   *   host: process.env.REDIS_HOST,
   *   port: 6379
   * }));
   * ```
   */
  useQueue(queue: IQueue): AgentHostBuilder {
    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.queue = queue;
    return newBuilder;
  }

  /**
   * Configures retry policy for LLM API calls and functions.
   *
   * @param policy - Retry policy configuration
   * @returns A new AgentHostBuilder with retry policy configured
   *
   * @example
   * ```typescript
   * builder.useRetryPolicy({
   *   maxAttempts: 3,
   *   backoff: 'exponential',
   *   initialDelayMs: 1000,
   *   maxDelayMs: 10000
   * });
   * ```
   */
  useRetryPolicy(policy: RetryPolicy): AgentHostBuilder {
    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.retryPolicy = policy;
    return newBuilder;
  }

  /**
   * Configures rate limiting to prevent abuse.
   *
   * @param config - Rate limiting configuration
   * @returns A new AgentHostBuilder with rate limiting configured
   *
   * @example
   * ```typescript
   * builder.useRateLimiting({
   *   global: { windowMs: 60_000, maxRequests: 1000 },
   *   perThread: { windowMs: 60_000, maxRequests: 100 },
   *   perFunction: {
   *     'expensive@v1': { windowMs: 60_000, maxRequests: 10 }
   *   }
   * });
   * ```
   */
  useRateLimiting(config: RateLimitingConfig): AgentHostBuilder {
    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.rateLimiting = config;
    return newBuilder;
  }

  /**
   * Configures logging behavior.
   *
   * @param config - Logging configuration
   * @returns A new AgentHostBuilder with logging configured
   *
   * @example
   * ```typescript
   * builder.useLogging({
   *   level: 'info',
   *   format: 'json',
   *   destination: 'console',
   *   includeStackTraces: true,
   *   redactSecrets: true,
   *   structuredFields: ['userId', 'threadId', 'runId']
   * });
   * ```
   */
  useLogging(config: LoggingConfig): AgentHostBuilder {
    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.logging = config;
    return newBuilder;
  }

  /**
   * Configures agent routing strategy.
   *
   * @param configure - Function that configures routing
   * @returns A new AgentHostBuilder with routing configured
   *
   * @example Basic routing
   * ```typescript
   * builder.useRouting(routing => routing
   *   .byHeader('X-Agent-Type')
   *   .byPath('/agents/:agentId')
   *   .withFallback('default')
   * );
   * ```
   */
  useRouting(configure: (routing: RoutingBuilder) => RoutingBuilder): AgentHostBuilder {
    const routingBuilder = this.createRoutingBuilder();
    const configured = configure(routingBuilder);

    const newBuilder = new AgentHostBuilder();
    this.copyTo(newBuilder);
    newBuilder.routing = configured;
    return newBuilder;
  }

  /**
   * Builds the configured agent host.
   *
   * @returns An AgentHost instance ready to run
   * @throws {Error} If no agents are configured
   * @throws {Error} If required dependencies are missing
   *
   * @example
   * ```typescript
   * const host = builder.build();
   * await host.start();
   * ```
   */
  build(): AgentHost {
    if (this.agentConfigurations.size === 0) {
      throw new Error('At least one agent must be configured');
    }

    // Build agent configurations
    const agents = new Map<string, any>();
    for (const [name, configure] of this.agentConfigurations.entries()) {
      const agentBuilder = new AgentBuilder(this.services);
      const configuredBuilder = configure(agentBuilder);
      agents.set(name, configuredBuilder.build());
    }

    // Use default implementations if not specified
    const storage = this.storage || new InMemoryStorage();
    const queue = this.queue || new InMemoryQueue();

    return new AgentHost(
      agents,
      storage,
      queue,
      this.retryPolicy,
      this.rateLimiting,
      this.logging,
      this.routing
    );
  }

  private copyTo(target: AgentHostBuilder): void {
    for (const [name, configure] of this.agentConfigurations.entries()) {
      target.agentConfigurations.set(name, configure);
    }
    for (const [key, value] of this.services.entries()) {
      target.services.set(key, value);
    }
    target.storage = this.storage;
    target.queue = this.queue;
    target.retryPolicy = this.retryPolicy;
    target.rateLimiting = this.rateLimiting;
    target.logging = this.logging;
    target.routing = this.routing;
  }

  private createRoutingBuilder(): RoutingBuilder {
    const builder: any = {
      byHeader: (_header: string) => builder,
      byPath: (_pattern: string) => builder,
      byContent: (_fn: (msg: ChatMessage) => Promise<string>) => builder,
      withFallback: (_agentName: string) => builder
    };
    return builder as RoutingBuilder;
  }
}
