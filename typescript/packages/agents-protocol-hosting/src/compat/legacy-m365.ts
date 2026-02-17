/**
 * Legacy M365 Agents SDK Compatibility Layer
 *
 * This module provides backwards-compatible exports for legacy M365 SDK samples.
 * These are stub implementations to allow legacy samples to compile.
 *
 * For new applications, use the modern API:
 * - AgentHostBuilder instead of AgentApplication
 * - IAgentContext instead of TurnContext
 * - InMemoryStorage instead of MemoryStorage
 */

// Legacy type aliases
export type TurnState<T = any> = T;
export type TurnContext = any;
export type Request = any;
export type AuthConfiguration = any;

// Legacy class stubs
export class AgentApplication<T = any> {
  constructor(options?: any) {
    throw new Error('AgentApplication is deprecated. Use AgentHostBuilder instead.');
  }
}

export class MemoryStorage {
  constructor() {
    throw new Error('MemoryStorage is deprecated. Use InMemoryStorage instead.');
  }
}

export class AttachmentDownloader {
  constructor() {
    throw new Error('AttachmentDownloader is deprecated.');
  }
}

export class CloudAdapter {
  constructor() {
    throw new Error('CloudAdapter is deprecated.');
  }
}

// Legacy functions
export function authorizeJWT(): void {
  throw new Error('authorizeJWT is deprecated.');
}

export function loadAuthConfigFromEnv(): any {
  throw new Error('loadAuthConfigFromEnv is deprecated.');
}
