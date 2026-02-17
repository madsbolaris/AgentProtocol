import { IAgentContext } from './IAgentContext.js';
import { IStorage } from '../storage/IStorage.js';
import { AIContent } from './types.js';

/**
 * Default implementation of IAgentContext.
 * @internal
 */
export class AgentContext implements IAgentContext {
  constructor(
    public readonly runId: string,
    public readonly threadId: string,
    private storage: IStorage,
    private responseCallback?: (content: string | AIContent) => Promise<void>,
    private streamCallback?: (token: string) => Promise<void>,
    private logCallback?: (message: string, level: string) => Promise<void>
  ) {}

  async respondAsync(content: string | AIContent, cancellationToken?: AbortSignal): Promise<void> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    if (this.responseCallback) {
      await this.responseCallback(content);
    }
  }

  async streamAsync(token: string, cancellationToken?: AbortSignal): Promise<void> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    if (this.streamCallback) {
      await this.streamCallback(token);
    }
  }

  async logAsync(
    message: string,
    level: 'debug' | 'info' | 'warn' | 'error' = 'info',
    cancellationToken?: AbortSignal
  ): Promise<void> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    if (this.logCallback) {
      await this.logCallback(message, level);
    } else {
      console.log(`[${level.toUpperCase()}] ${message}`);
    }
  }

  async getStateAsync<T>(key: string, cancellationToken?: AbortSignal): Promise<T | null> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    return await this.storage.getAsync<T>(this.threadId, key);
  }

  async setStateAsync<T>(key: string, value: T, cancellationToken?: AbortSignal): Promise<void> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    await this.storage.setAsync<T>(this.threadId, key, value);
  }

  async deleteStateAsync(key: string, cancellationToken?: AbortSignal): Promise<void> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    await this.storage.deleteAsync(this.threadId, key);
  }

  async getStateKeysAsync(cancellationToken?: AbortSignal): Promise<string[]> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    return await this.storage.getKeysAsync(this.threadId);
  }

  async pauseForApprovalAsync(
    summary: string,
    _metadata?: Record<string, unknown>,
    cancellationToken?: AbortSignal
  ): Promise<void> {
    if (cancellationToken?.aborted) {
      throw new Error('Operation was cancelled');
    }

    // TODO: Implement approval mechanism
    await this.logAsync(`Approval requested: ${summary}`, 'info');
  }

  recordMetric(name: string, value: number, tags?: Record<string, string>): void {
    // TODO: Implement metrics recording with OpenTelemetry
    console.log(`[METRIC] ${name}=${value}`, tags);
  }

  addTraceAttribute(key: string, value: string | number | boolean): void {
    // TODO: Implement trace attributes with OpenTelemetry
    console.log(`[TRACE] ${key}=${value}`);
  }

  getTraceId(): string {
    // TODO: Implement actual trace ID from OpenTelemetry
    return `trace-${this.runId}`;
  }
}
