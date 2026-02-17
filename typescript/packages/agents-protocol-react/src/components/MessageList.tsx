/**
 * MessageList component - scrollable list of messages
 */

import React, { useEffect, useRef } from 'react';
import type { ChatMessage } from '@microsoft/agents';
import { Message } from './Message';
import { MessageComponentProps } from '../types';

export interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  autoScroll?: boolean;
  messageProps?: Partial<MessageComponentProps>;
  renderEmpty?: () => React.ReactNode;
  renderLoading?: () => React.ReactNode;
}

export function MessageList({
  messages,
  isLoading,
  autoScroll = true,
  messageProps,
  renderEmpty,
  renderLoading,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (autoScroll && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  if (messages.length === 0 && !isLoading) {
    return (
      <div className="message-list-empty">
        {renderEmpty ? renderEmpty() : <DefaultEmptyState />}
      </div>
    );
  }

  return (
    <div className="message-list">
      {messages.map((message) => (
        <Message key={message.messageId} message={message} {...messageProps} />
      ))}

      {isLoading && (
        <div className="message-list-loading">
          {renderLoading ? renderLoading() : <DefaultLoadingState />}
        </div>
      )}

      <div ref={messagesEndRef} />
    </div>
  );
}

function DefaultEmptyState() {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">💬</div>
      <p className="empty-state-text">No messages yet</p>
      <p className="empty-state-subtext">Start a conversation!</p>
    </div>
  );
}

function DefaultLoadingState() {
  return (
    <div className="loading-state">
      <div className="loading-dots">
        <span className="loading-dot"></span>
        <span className="loading-dot"></span>
        <span className="loading-dot"></span>
      </div>
    </div>
  );
}
