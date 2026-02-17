import {
  FunctionDefinition,
  LLMOptions,
  UserMessageHandler,
  ReactionHandler,
  HandlerErrorConfig
} from '../core/types.js';
import { FunctionBuilder } from './FunctionBuilder.js';

/**
 * Configuration for a built agent.
 * @internal
 */
export interface AgentConfiguration {
  llmModel?: string;
  llmInstructions?: string;
  llmOptions?: LLMOptions;
  functions: FunctionDefinition[];
  userMessageHandlers: Array<{ handler: UserMessageHandler; config: HandlerErrorConfig }>;
  reactionHandlers: Array<{ handler: ReactionHandler; config: HandlerErrorConfig }>;
}

/**
 * Builder for configuring individual agent behavior.
 *
 * @example
 * ```typescript
 * const agent = new AgentBuilder()
 *   .useLLM('gpt-4', 'You are helpful.', { streaming: true })
 *   .addFunctions(f => f
 *     .add('getTime@v1', 'Gets time', {}, (): string => new Date().toISOString(),
 *          { trustLevel: 'trusted' })
 *   )
 *   .onUserMessage(async (msg: ChatMessage, ctx: IAgentContext): Promise<TurnResult> => {
 *     await ctx.logAsync(`User said: ${msg.text}`);
 *     return TurnResult.Continue;
 *   });
 * ```
 */
export class AgentBuilder {
  private llmModel?: string;
  private llmInstructions?: string;
  private llmOptions?: LLMOptions;
  private functions: FunctionDefinition[] = [];
  private userMessageHandlers: Array<{ handler: UserMessageHandler; config: HandlerErrorConfig }> = [];
  private reactionHandlers: Array<{ handler: ReactionHandler; config: HandlerErrorConfig }> = [];

  /**
   * Creates a new agent builder.
   *
   * @param services - Service container for dependency injection
   */
  constructor(private services?: Map<symbol, unknown>) {}

  /**
   * Configures the LLM to use for this agent.
   *
   * @param model - Model identifier (e.g., "gpt-4", "claude-3-5-sonnet-20241022")
   * @param instructions - System instructions for the agent
   * @param options - Optional LLM configuration (streaming, temperature, etc.)
   * @returns A new AgentBuilder with LLM configured
   * @throws {TypeError} If model or instructions is null/undefined
   * @throws {Error} If model or instructions is empty string
   *
   * @example
   * ```typescript
   * agent.useLLM('gpt-4', 'You are a helpful assistant.', {
   *   streaming: true,
   *   temperature: 0.7,
   *   maxTokens: 2000
   * });
   * ```
   */
  useLLM(model: string, instructions: string, options?: LLMOptions): AgentBuilder {
    if (model === null || model === undefined) {
      throw new TypeError('model cannot be null or undefined');
    }

    if (instructions === null || instructions === undefined) {
      throw new TypeError('instructions cannot be null or undefined');
    }

    if (model.trim().length === 0) {
      throw new Error('model cannot be empty');
    }

    if (instructions.trim().length === 0) {
      throw new Error('instructions cannot be empty');
    }

    const newBuilder = new AgentBuilder(this.services);
    newBuilder.llmModel = model;
    newBuilder.llmInstructions = instructions;
    newBuilder.llmOptions = options;
    newBuilder.functions = [...this.functions];
    newBuilder.userMessageHandlers = [...this.userMessageHandlers];
    newBuilder.reactionHandlers = [...this.reactionHandlers];
    return newBuilder;
  }

  /**
   * Adds functions/tools that the agent can call.
   *
   * Functions can be added using type inference or explicit schemas.
   *
   * @param configure - Function that configures a FunctionBuilder
   * @returns A new AgentBuilder with functions added
   *
   * @example
   * ```typescript
   * agent.addFunctions(f => f
   *   .add('getTime@v1', 'Gets current time', {}, (): string => new Date().toISOString(),
   *        { trustLevel: 'trusted' })
   *   .add('sum@v1', 'Adds two numbers',
   *     {
   *       type: 'object',
   *       properties: {
   *         a: { type: 'number' },
   *         b: { type: 'number' }
   *       },
   *       required: ['a', 'b']
   *     },
   *     ({ a, b }: { a: number; b: number }): string => (a + b).toString(),
   *     { trustLevel: 'trusted' })
   * );
   * ```
   */
  addFunctions(configure: (builder: FunctionBuilder) => FunctionBuilder): AgentBuilder {
    const functionBuilder = new FunctionBuilder();
    const configuredBuilder = configure(functionBuilder);
    const newFunctions = configuredBuilder.build();

    const newBuilder = new AgentBuilder(this.services);
    newBuilder.llmModel = this.llmModel;
    newBuilder.llmInstructions = this.llmInstructions;
    newBuilder.llmOptions = this.llmOptions;
    newBuilder.functions = [...this.functions, ...newFunctions];
    newBuilder.userMessageHandlers = [...this.userMessageHandlers];
    newBuilder.reactionHandlers = [...this.reactionHandlers];
    return newBuilder;
  }

  /**
   * Registers a handler for user messages.
   *
   * Handlers execute in registration order until one returns Consumed or Replied.
   *
   * @param handler - The message handler function
   * @param config - Optional error handling configuration
   * @returns A new AgentBuilder with the handler registered
   *
   * @example
   * ```typescript
   * async function onMessage(
   *   msg: ChatMessage,
   *   ctx: IAgentContext,
   *   signal?: AbortSignal
   * ): Promise<TurnResult> {
   *   await ctx.logAsync(`User said: ${msg.text}`);
   *
   *   if (msg.text.startsWith('/help')) {
   *     await ctx.respondAsync('Available commands: /help, /about');
   *     return TurnResult.Replied;
   *   }
   *
   *   return TurnResult.Continue;
   * }
   *
   * agent.onUserMessage(onMessage, { onError: 'throw' });
   * ```
   */
  onUserMessage(handler: UserMessageHandler, config?: HandlerErrorConfig): AgentBuilder {
    const errorConfig: HandlerErrorConfig = config || { onError: 'continue' };

    const newBuilder = new AgentBuilder(this.services);
    newBuilder.llmModel = this.llmModel;
    newBuilder.llmInstructions = this.llmInstructions;
    newBuilder.llmOptions = this.llmOptions;
    newBuilder.functions = [...this.functions];
    newBuilder.userMessageHandlers = [...this.userMessageHandlers, { handler, config: errorConfig }];
    newBuilder.reactionHandlers = [...this.reactionHandlers];
    return newBuilder;
  }

  /**
   * Registers a handler for reactions (emoji, likes, etc.).
   *
   * @param handler - The reaction handler function
   * @param config - Optional error handling configuration
   * @returns A new AgentBuilder with the handler registered
   *
   * @example
   * ```typescript
   * async function onReaction(
   *   reaction: ReactionContent,
   *   ctx: IAgentContext,
   *   signal?: AbortSignal
   * ): Promise<TurnResult> {
   *   if (reaction.emoji === '👍') {
   *     await ctx.respondAsync('Thanks for the feedback!');
   *     return TurnResult.Replied;
   *   }
   *   return TurnResult.Consumed;
   * }
   *
   * agent.onReaction(onReaction);
   * ```
   */
  onReaction(handler: ReactionHandler, config?: HandlerErrorConfig): AgentBuilder {
    const errorConfig: HandlerErrorConfig = config || { onError: 'continue' };

    const newBuilder = new AgentBuilder(this.services);
    newBuilder.llmModel = this.llmModel;
    newBuilder.llmInstructions = this.llmInstructions;
    newBuilder.llmOptions = this.llmOptions;
    newBuilder.functions = [...this.functions];
    newBuilder.userMessageHandlers = [...this.userMessageHandlers];
    newBuilder.reactionHandlers = [...this.reactionHandlers, { handler, config: errorConfig }];
    return newBuilder;
  }

  /**
   * Builds the agent configuration (internal use).
   *
   * @internal
   */
  build(): AgentConfiguration {
    return {
      llmModel: this.llmModel,
      llmInstructions: this.llmInstructions,
      llmOptions: this.llmOptions,
      functions: this.functions,
      userMessageHandlers: this.userMessageHandlers,
      reactionHandlers: this.reactionHandlers
    };
  }
}
