/**
 * Microsoft Agents Protocol Client
 * API client for interacting with Agent Protocol-compliant services
 */

// Low-level API
export * from './client';
export * from './streaming';
export * from './types';
export * from './errors';

// High-level API
export * from './simplified-client';
export * from './conversation';
export * from './tool-collection';
export * from './chat-options';
export { StreamEvent, StreamEventImpl, createStreamEvent } from './stream-event';
