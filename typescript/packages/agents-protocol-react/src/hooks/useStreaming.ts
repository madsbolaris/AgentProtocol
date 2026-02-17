/**
 * Hook for SSE streaming
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { createRunStream, createThreadStream, SSEStream } from '@microsoft/agents-protocol-client';
import type { StreamEvent } from '@microsoft/agents-protocol-client';
import { useAgentContext } from '../context/AgentProvider';

export type StreamType = 'run' | 'thread';

export interface UseStreamingOptions {
  /** Auto-connect on mount */
  autoConnect?: boolean;

  /** Event handlers */
  onEvent?: (event: StreamEvent) => void;
  onError?: (error: Error) => void;
  onConnected?: () => void;
}

export interface UseStreamingResult {
  events: StreamEvent[];
  isConnected: boolean;
  error: Error | null;
  lastEvent: StreamEvent | null;

  // Actions
  connect: () => void;
  disconnect: () => void;
  clearEvents: () => void;
}

export function useStreaming(
  resourceId: string,
  streamType: StreamType,
  options: UseStreamingOptions = {}
): UseStreamingResult {
  const { client } = useAgentContext();
  const { autoConnect = true, onEvent, onError, onConnected } = options;

  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [lastEvent, setLastEvent] = useState<StreamEvent | null>(null);

  const streamRef = useRef<SSEStream | null>(null);

  const connect = useCallback(() => {
    if (streamRef.current) {
      return; // Already connected
    }

    try {
      // Create stream based on type
      const stream =
        streamType === 'run'
          ? createRunStream(client['baseUrl'], resourceId, {
              authToken: client['authToken'],
            })
          : createThreadStream(client['baseUrl'], resourceId, {
              authToken: client['authToken'],
            });

      // Listen to all events
      stream.on('*', (event) => {
        setEvents((prev) => [...prev, event]);
        setLastEvent(event);
        onEvent?.(event);
      });

      stream.on('connected', () => {
        setIsConnected(true);
        onConnected?.();
      });

      stream.on('error', (err) => {
        setError(err);
        setIsConnected(false);
        onError?.(err);
      });

      streamRef.current = stream;
    } catch (err) {
      setError(err as Error);
      onError?.(err as Error);
    }
  }, [client, resourceId, streamType, onEvent, onError, onConnected]);

  const disconnect = useCallback(() => {
    if (streamRef.current) {
      streamRef.current.close();
      streamRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const clearEvents = useCallback(() => {
    setEvents([]);
    setLastEvent(null);
  }, []);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    events,
    isConnected,
    error,
    lastEvent,
    connect,
    disconnect,
    clearEvents,
  };
}
