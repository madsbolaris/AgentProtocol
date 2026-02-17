/**
 * Options and types for high-level chat API
 */

import type { ToolCollection } from './tool-collection';

/**
 * Options for chat completion and streaming requests
 */
export interface ChatOptions {
  /**
   * Agent ID to use (optional if only one agent registered)
   */
  agentId?: string;

  /**
   * Tools available for the agent to call
   */
  tools?: ToolCollection;

  /**
   * Additional metadata for the request
   */
  metadata?: Record<string, unknown>;

  /**
   * Callback fired when a tool call starts (for monitoring)
   */
  onToolCallStarted?: (info: ToolCallInfo) => Promise<void>;

  /**
   * Callback fired when a tool call completes (for monitoring)
   */
  onToolCallCompleted?: (info: ToolCallInfo, result: unknown) => Promise<void>;

  /**
   * Callback fired when a tool call fails (for monitoring)
   */
  onToolCallFailed?: (info: ToolCallInfo, error: Error) => Promise<void>;
}

/**
 * Information about a tool call
 */
export interface ToolCallInfo {
  /**
   * Unique identifier for this tool call
   */
  callId: string;

  /**
   * Name of the tool being called
   */
  name: string;

  /**
   * JSON-encoded arguments for the tool
   */
  arguments: string;
}
