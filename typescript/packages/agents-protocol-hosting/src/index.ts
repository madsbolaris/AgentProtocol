/**
 * Microsoft Agents Protocol Hosting SDK
 *
 * This package provides a complete hosting solution for building agent applications
 * with LLM-powered assistants, tools, and event processing.
 */

// Core types and enums
export { TurnResult } from './core/TurnResult.js';
export { IAgentContext } from './core/IAgentContext.js';
export { HealthStatus } from './core/HealthStatus.js';
export {
  ChatMessage,
  ReactionContent,
  AIContent,
  UserMessageHandler,
  ReactionHandler,
  HandlerErrorConfig,
  JSONSchema,
  FunctionExecutionOptions,
  FunctionDefinition,
  LLMOptions,
  RetryPolicy,
  RateLimitingConfig,
  LoggingConfig,
  LogEntry
} from './core/types.js';

// Builder classes
export { AgentHostBuilder, RoutingBuilder } from './builder/AgentHostBuilder.js';
export { AgentBuilder, AgentConfiguration } from './builder/AgentBuilder.js';
export { FunctionBuilder } from './builder/FunctionBuilder.js';

// Hosting
export { AgentHost } from './hosting/AgentHost.js';
export { IOutOfBandPublisher } from './hosting/IOutOfBandPublisher.js';

// Storage
export { IStorage, PostgresStorageConfig } from './storage/IStorage.js';
export { InMemoryStorage } from './storage/InMemoryStorage.js';

// Queue
export { IQueue, QueueMessage, ConcurrencyConfig } from './queue/IQueue.js';
export { InMemoryQueue } from './queue/InMemoryQueue.js';

// LLM utilities
export { LLMClient, LLMClientOptions } from './llm/llm-client.js';
export { LLMRecorder, LLMRequest, LLMResponse } from './llm/llm-recorder.js';
export { LLMPlayer } from './llm/llm-player.js';

// Legacy M365 SDK compatibility (for reference samples only)
export {
  TurnState,
  TurnContext,
  Request,
  AuthConfiguration,
  AgentApplication,
  MemoryStorage,
  AttachmentDownloader,
  CloudAdapter,
  authorizeJWT,
  loadAuthConfigFromEnv
} from './compat/legacy-m365.js';

// M365 Agent Protocol extension
export { mapAgentProtocol } from './compat/mapAgentProtocol.js';
