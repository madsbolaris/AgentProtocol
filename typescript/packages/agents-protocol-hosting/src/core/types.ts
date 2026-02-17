import { TurnResult } from './TurnResult.js';
import { IAgentContext } from './IAgentContext.js';

// Import generated types from @microsoft/agents
import type { AIContent as GeneratedAIContent } from '@microsoft/agents-protocol-abstractions';

// Re-export AIContent from generated package
// This is a discriminated union with proper 'kind' discriminator
export type AIContent = GeneratedAIContent;

/**
 * Represents a handler message.
 *
 * NOTE: This is a simplified hosting-specific type for handler interfaces.
 * The full protocol ChatMessage type from @microsoft/agents has more fields
 * (messageId, contents[], role, etc.) for wire-level communication.
 *
 * Renamed from ChatMessage to HandlerMessage to avoid confusion with the
 * protocol-level ChatMessage type.
 */
export interface HandlerMessage {
  /** The message content */
  text: string;
  /** Message type (optional) */
  type?: string;
  /** Who sent it (if authenticated) */
  userId?: string;
  /** When it was sent */
  timestamp: Date;
  /** Custom metadata */
  metadata?: Record<string, unknown>;
}

/**
 * @deprecated Use HandlerMessage instead. Will be removed in next major version.
 */
export type ChatMessage = HandlerMessage;

/**
 * Represents a reaction to a message.
 */
export interface ReactionContent {
  /** The emoji or reaction identifier (e.g., '👍', '❤️') */
  emoji: string;
  /** Which message was reacted to */
  messageId?: string;
  /** Who reacted */
  userId?: string;
  /** When the reaction occurred */
  timestamp: Date;
}

/**
 * Handler for user messages.
 *
 * @param message - The incoming handler message
 * @param context - Agent context for responding and logging
 * @param cancellationToken - Optional abort signal
 * @returns A TurnResult indicating how to proceed
 */
export type UserMessageHandler = (
  message: HandlerMessage,
  context: IAgentContext,
  cancellationToken?: AbortSignal
) => Promise<TurnResult>;

/**
 * Handler for reactions (emoji, likes, etc.).
 *
 * @param reaction - The reaction content
 * @param context - Agent context for responding and logging
 * @param cancellationToken - Optional abort signal
 * @returns A TurnResult indicating how to proceed
 */
export type ReactionHandler = (
  reaction: ReactionContent,
  context: IAgentContext,
  cancellationToken?: AbortSignal
) => Promise<TurnResult>;

/**
 * Configuration for handler error behavior.
 */
export interface HandlerErrorConfig {
  /**
   * What to do when a handler throws an error.
   *
   * - 'continue': Log error and continue to next handler (silent failure)
   * - 'stop': Log error and stop processing (no response sent)
   * - 'throw': Re-throw error (let caller handle)
   *
   * @default 'continue'
   */
  onError: 'continue' | 'stop' | 'throw';
}

/**
 * JSON Schema type for function parameters.
 *
 * NOTE: We define our own JSONSchema here instead of importing from @microsoft/agents
 * because the hosting SDK requires 'type' field for validation, while the generated
 * JSONSchema is more permissive for protocol compatibility.
 */
export interface JSONSchema {
  type: string;
  properties?: Record<string, JSONSchema>;
  items?: JSONSchema;
  required?: string[];
  description?: string;
  enum?: unknown[];
  minimum?: number;
  maximum?: number;
  minLength?: number;
  maxLength?: number;
  pattern?: string;
}

/**
 * Options for function execution with security controls.
 */
export interface FunctionExecutionOptions {
  /**
   * Trust level for this function.
   *
   * - 'trusted': Function is from trusted source, runs without sandbox
   * - 'untrusted': Function may be unsafe, runs in sandbox
   *
   * SECURITY: Always use 'untrusted' for user-provided code or
   * functions from untrusted sources.
   *
   * @required - Must be explicitly set for all functions
   */
  trustLevel: 'trusted' | 'untrusted';

  /**
   * Timeout in milliseconds.
   *
   * @default 30000 (30 seconds)
   */
  timeoutMs?: number;

  /**
   * Maximum memory in bytes (sandbox only).
   * Only enforced when trustLevel is 'untrusted'.
   *
   * @default 100MB for untrusted functions
   */
  maxMemoryBytes?: number;

  /**
   * Allow network access (sandbox only).
   * Only enforced when trustLevel is 'untrusted'.
   *
   * @default false for untrusted functions
   */
  allowNetwork?: boolean;

  /**
   * Allow filesystem access (sandbox only).
   * Only enforced when trustLevel is 'untrusted'.
   *
   * @default false for untrusted functions
   */
  allowFilesystem?: boolean;
}

/**
 * Represents a function/tool definition with type information.
 */
export interface FunctionDefinition<TParams = Record<string, unknown>> {
  /** Function name (should include version suffix like @v1) */
  name: string;
  /** Human-readable description for the LLM */
  description: string;
  /** The function implementation */
  implementation: (params: TParams) => string | Promise<string>;
  /** JSON schema for parameters */
  parametersSchema: JSONSchema;
  /** Execution options including sandboxing */
  executionOptions: FunctionExecutionOptions;
}

/**
 * Configuration options for LLM behavior.
 */
export interface LLMOptions {
  /**
   * Enable streaming responses.
   * When true, tokens are sent to the user as they're generated.
   *
   * @default false
   */
  streaming?: boolean;

  /**
   * Callback invoked for each token in streaming mode.
   *
   * @param token - The token text
   * @param context - Agent context for streaming
   */
  onToken?: (token: string, context: IAgentContext) => Promise<void>;

  /**
   * Temperature for response generation (0.0 to 2.0).
   * Higher values make output more random.
   *
   * @default 0.7
   */
  temperature?: number;

  /**
   * Maximum tokens in the response.
   *
   * @default 2000
   */
  maxTokens?: number;

  /**
   * Stop sequences that end generation.
   */
  stopSequences?: string[];

  /**
   * Timeout for LLM API calls in milliseconds.
   *
   * @default 30000 (30 seconds)
   */
  timeoutMs?: number;
}

/**
 * Retry policy configuration.
 */
export interface RetryPolicy {
  /** Maximum number of retry attempts */
  maxAttempts: number;
  /** Backoff strategy */
  backoff: 'fixed' | 'exponential';
  /** Initial delay in milliseconds */
  initialDelayMs: number;
  /** Maximum delay in milliseconds */
  maxDelayMs: number;
}

/**
 * Rate limiting configuration.
 */
export interface RateLimitingConfig {
  /** Global rate limits */
  global?: {
    windowMs: number;
    maxRequests: number;
  };
  /** Per-thread rate limits */
  perThread?: {
    windowMs: number;
    maxRequests: number;
  };
  /** Per-function rate limits */
  perFunction?: Record<string, {
    windowMs: number;
    maxRequests: number;
  }>;
}

/**
 * Logging configuration.
 */
export interface LoggingConfig {
  /** Log level filter */
  level: 'debug' | 'info' | 'warn' | 'error';
  /** Log output format */
  format: 'json' | 'text';
  /** Log destination */
  destination: 'console' | 'file' | 'cloudwatch' | 'stackdriver' | 'custom';
  /** Include stack traces for errors */
  includeStackTraces: boolean;
  /** Automatically redact secrets from logs */
  redactSecrets: boolean;
  /** Additional structured fields to include in all logs */
  structuredFields: string[];
  /** File path for file-based logging */
  filePath?: string;
  /** Custom log transport function */
  customTransport?: (log: LogEntry) => Promise<void>;
}

/**
 * Structured log entry.
 */
export interface LogEntry {
  timestamp: Date;
  level: 'debug' | 'info' | 'warn' | 'error';
  message: string;
  threadId?: string;
  runId?: string;
  traceId?: string;
  error?: Error;
  metadata?: Record<string, unknown>;
}
