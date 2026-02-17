/**
 * Hook for managing thread state and operations
 */

import { useState, useEffect, useCallback } from 'react';
import type { Thread, ChatMessage } from '@microsoft/agents-protocol-abstractions';
import { useAgentContext } from '../context/AgentProvider';

export interface UseThreadOptions {
  /** Auto-load thread on mount */
  autoLoad?: boolean;

  /** Polling interval for updates (ms) */
  pollingInterval?: number;
}

export interface UseThreadResult {
  thread: Thread | null;
  messages: ChatMessage[];
  isLoading: boolean;
  error: Error | null;

  // Actions
  loadThread: () => Promise<void>;
  sendMessage: (content: string) => Promise<void>;
  addReaction: (messageId: string, reaction: string) => Promise<void>;
  deleteMessage: (messageId: string) => Promise<void>;
  refresh: () => Promise<void>;
}

export function useThread(
  threadId: string,
  options: UseThreadOptions = {}
): UseThreadResult {
  const { client } = useAgentContext();
  const { autoLoad = true, pollingInterval } = options;

  const [thread, setThread] = useState<Thread | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadThread = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);

      const [threadData, messagesData] = await Promise.all([
        client.threads.get(threadId),
        client.messages.list(threadId, { limit: 100 }),
      ]);

      setThread(threadData);
      setMessages(messagesData.data);
    } catch (err) {
      setError(err as Error);
    } finally {
      setIsLoading(false);
    }
  }, [client, threadId]);

  const sendMessage = useCallback(
    async (content: string) => {
      try {
        await client.messages.create(threadId, {
          role: 'user',
          content,
        });
        await loadThread();
      } catch (err) {
        setError(err as Error);
      }
    },
    [client, threadId, loadThread]
  );

  const addReaction = useCallback(
    async (messageId: string, reaction: string) => {
      // TODO: Implement reaction API when available
      console.log('Add reaction:', messageId, reaction);
    },
    []
  );

  const deleteMessage = useCallback(
    async (messageId: string) => {
      try {
        await client.messages.delete(threadId, messageId);
        await loadThread();
      } catch (err) {
        setError(err as Error);
      }
    },
    [client, threadId, loadThread]
  );

  const refresh = useCallback(async () => {
    await loadThread();
  }, [loadThread]);

  // Auto-load on mount
  useEffect(() => {
    if (autoLoad) {
      loadThread();
    }
  }, [autoLoad, loadThread]);

  // Polling
  useEffect(() => {
    if (pollingInterval) {
      const interval = setInterval(() => {
        loadThread();
      }, pollingInterval);

      return () => clearInterval(interval);
    }
  }, [pollingInterval, loadThread]);

  return {
    thread,
    messages,
    isLoading,
    error,
    loadThread,
    sendMessage,
    addReaction,
    deleteMessage,
    refresh,
  };
}
