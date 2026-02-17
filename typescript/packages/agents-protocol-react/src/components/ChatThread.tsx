/**
 * ChatThread component - main chat interface
 */

import React, { useEffect } from 'react';
import { MessageList } from './MessageList';
import { InputBox } from './InputBox';
import { ThreadHeader } from './ThreadHeader';
import { useThread } from '../hooks/useThread';
import { useAgent } from '../hooks/useAgent';
import { useStreaming } from '../hooks/useStreaming';
import { ThemeConfig, MessageComponentProps } from '../types';
import '../styles/default-theme.css';

export interface ChatThreadProps {
  /** Thread ID */
  threadId: string;

  /** Agent ID for execution */
  agentId: string;

  /** Current user ID */
  userId: string;

  /** Enable real-time streaming */
  enableStreaming?: boolean;

  /** Enable reactions */
  enableReactions?: boolean;

  /** Enable typing indicators */
  enableTypingIndicators?: boolean;

  /** Enable file upload */
  enableFileUpload?: boolean;

  /** Theme configuration */
  theme?: ThemeConfig;

  /** Custom class name */
  className?: string;

  /** Message component props */
  messageProps?: Partial<MessageComponentProps>;

  /** Callbacks */
  onMessageSent?: (message: string) => void;
  onRunCompleted?: (runId: string) => void;
  onError?: (error: Error) => void;

  /** Show header */
  showHeader?: boolean;
}

export function ChatThread({
  threadId,
  agentId,
  userId,
  enableStreaming = true,
  enableReactions = false,
  enableTypingIndicators = true,
  enableFileUpload = true,
  theme,
  className,
  messageProps,
  onMessageSent,
  onRunCompleted,
  onError,
  showHeader = true,
}: ChatThreadProps) {
  const { messages, isLoading, error, sendMessage, refresh } = useThread(threadId);
  const { createRun, isRunning } = useAgent();
  const streaming = useStreaming(threadId, 'thread', {
    autoConnect: enableStreaming,
    onError: (err) => onError?.(err),
  });

  // Handle streaming updates
  useEffect(() => {
    if (streaming.lastEvent) {
      const event = streaming.lastEvent;

      if (event.event === 'message.completed' || event.event === 'run.completed') {
        refresh();
      }

      if (event.event === 'run.completed' && event.runId) {
        onRunCompleted?.(event.runId);
      }
    }
  }, [streaming.lastEvent, refresh, onRunCompleted]);

  // Handle errors
  useEffect(() => {
    if (error) {
      onError?.(error);
    }
  }, [error, onError]);

  const handleSend = async (text: string) => {
    try {
      await sendMessage(text);
      onMessageSent?.(text);

      // Execute agent
      await createRun({
        agentId,
        threadId,
      });
    } catch (err) {
      onError?.(err as Error);
    }
  };

  const containerClass = `chat-thread ${className || ''}`;

  return (
    <div className={containerClass} data-theme={theme?.darkMode ? 'dark' : 'light'}>
      {showHeader && (
        <ThreadHeader threadId={threadId} isStreaming={streaming.isConnected} />
      )}

      <MessageList
        messages={messages}
        isLoading={isLoading || isRunning}
        messageProps={{
          showReactions: enableReactions,
          ...messageProps,
        }}
      />

      <InputBox
        threadId={threadId}
        onSend={handleSend}
        disabled={isLoading || isRunning}
        enableFileUpload={enableFileUpload}
      />

      {error && (
        <div className="chat-thread-error">
          <span className="error-icon">⚠️</span>
          {error.message}
        </div>
      )}
    </div>
  );
}
