/**
 * SSE Stream client for real-time event streaming
 */

import { StreamEvent, StreamEventType } from './event-types';
import { NetworkError } from '../errors';

export type EventHandler<T extends StreamEvent = StreamEvent> = (event: T) => void;

export interface SSEStreamOptions {
  /** Authorization token */
  authToken?: string;

  /** Custom headers */
  headers?: Record<string, string>;

  /** Auto-reconnect on disconnect */
  autoReconnect?: boolean;

  /** Maximum reconnection attempts */
  maxReconnectAttempts?: number;

  /** Reconnection delay in ms */
  reconnectDelay?: number;
}

export class SSEStream {
  private eventSource: EventSource | null = null;
  private handlers: Map<StreamEventType | '*', Set<EventHandler>> = new Map();
  private url: string;
  private options: SSEStreamOptions;
  private reconnectAttempts = 0;
  private isConnected = false;
  private isClosed = false;

  constructor(url: string, options: SSEStreamOptions = {}) {
    this.url = url;
    this.options = {
      autoReconnect: true,
      maxReconnectAttempts: 5,
      reconnectDelay: 1000,
      ...options,
    };
  }

  /**
   * Connect to the SSE stream
   */
  connect(): void {
    if (this.isConnected || this.isClosed) {
      return;
    }

    // Build URL with auth token if needed
    const url = new URL(this.url);
    if (this.options.authToken) {
      url.searchParams.set('access_token', this.options.authToken);
    }

    this.eventSource = new EventSource(url.toString());

    // Handle all event types
    this.eventSource.addEventListener('message', (e) => {
      this.handleMessage(e);
    });

    this.eventSource.addEventListener('open', () => {
      this.isConnected = true;
      this.reconnectAttempts = 0;
      this.emit('connected', null);
    });

    this.eventSource.addEventListener('error', (_error) => {
      this.isConnected = false;
      this.emit('error', new NetworkError('SSE connection error'));

      if (
        this.options.autoReconnect &&
        !this.isClosed &&
        this.reconnectAttempts < this.options.maxReconnectAttempts!
      ) {
        this.reconnectAttempts++;
        setTimeout(() => {
          if (!this.isClosed) {
            this.close();
            this.connect();
          }
        }, this.options.reconnectDelay! * this.reconnectAttempts);
      }
    });
  }

  /**
   * Handle incoming SSE message
   */
  private handleMessage(e: MessageEvent): void {
    try {
      const data = JSON.parse(e.data);

      // Extract event type
      const eventType = data.event || e.type;

      // Parse as StreamEvent
      const event: StreamEvent = {
        event: eventType,
        ...data,
      };

      // Emit to specific handlers
      this.emit(eventType, event);

      // Emit to wildcard handlers
      this.emit('*', event);
    } catch (error) {
      console.error('[SSEStream] Failed to parse event:', error);
    }
  }

  /**
   * Listen for a specific event type
   */
  on<T extends StreamEvent = StreamEvent>(
    eventType: StreamEventType | '*',
    handler: EventHandler<T>
  ): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set());
    }
    this.handlers.get(eventType)!.add(handler as EventHandler);

    // Return unsubscribe function
    return () => this.off(eventType, handler);
  }

  /**
   * Remove an event listener
   */
  off<T extends StreamEvent = StreamEvent>(
    eventType: StreamEventType | '*',
    handler: EventHandler<T>
  ): void {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      handlers.delete(handler as EventHandler);
    }
  }

  /**
   * Listen for an event once
   */
  once<T extends StreamEvent = StreamEvent>(
    eventType: StreamEventType | '*',
    handler: EventHandler<T>
  ): void {
    const wrappedHandler = (event: T) => {
      handler(event);
      this.off(eventType, wrappedHandler);
    };
    this.on(eventType, wrappedHandler);
  }

  /**
   * Emit an event to all registered handlers
   */
  private emit(eventType: string, data: any): void {
    const handlers = this.handlers.get(eventType as StreamEventType);
    if (handlers) {
      handlers.forEach((handler) => {
        try {
          handler(data);
        } catch (error) {
          console.error(`[SSEStream] Error in handler for ${eventType}:`, error);
        }
      });
    }
  }

  /**
   * Close the stream
   */
  close(): void {
    this.isClosed = true;
    this.isConnected = false;
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
    }
    this.handlers.clear();
  }

  /**
   * Check if stream is connected
   */
  get connected(): boolean {
    return this.isConnected;
  }
}

/**
 * Helper to create a stream for a run
 */
export function createRunStream(
  baseUrl: string,
  runId: string,
  options?: SSEStreamOptions
): SSEStream {
  const url = `${baseUrl}/runs/${runId}/stream`;
  const stream = new SSEStream(url, options);
  stream.connect();
  return stream;
}

/**
 * Helper to create a stream for a thread
 */
export function createThreadStream(
  baseUrl: string,
  threadId: string,
  options?: SSEStreamOptions
): SSEStream {
  const url = `${baseUrl}/threads/${threadId}/stream`;
  const stream = new SSEStream(url, options);
  stream.connect();
  return stream;
}
