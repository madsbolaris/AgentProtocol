/**
 * Message component - renders individual messages with content
 */

import React from 'react';
import type { ChatMessage } from '@microsoft/agents';
import { filterContentByAudience } from '@microsoft/agents';
import { ContentRenderer } from './ContentRenderer';
import { MessageComponentProps } from '../types';
import { useAgentContext } from '../context/AgentProvider';

export function Message({
  message,
  showAvatar = true,
  showTimestamp = true,
  showReactions = false,
  compactMode = false,
  onReact,
  onCopy,
  onDelete,
  renderAvatar,
  renderTimestamp,
}: MessageComponentProps) {
  const { theme } = useAgentContext();

  // Filter content by audience (hide agent-only content from users)
  const visibleContent = filterContentByAudience(message.contents || [], 'user');

  const bubbleClass = `message-bubble message-bubble--${message.role}`;
  const containerClass = compactMode ? 'message-container--compact' : 'message-container';

  return (
    <div className={containerClass} data-role={message.role}>
      {showAvatar && (
        <div className="message-avatar">
          {renderAvatar ? renderAvatar(message) : <DefaultAvatar role={message.role} />}
        </div>
      )}

      <div className="message-content">
        <div className={bubbleClass}>
          {visibleContent.map((content, index) => (
            <ContentRenderer key={index} content={content} message={message} />
          ))}
        </div>

        {showTimestamp && (
          <div className="message-timestamp">
            {renderTimestamp
              ? renderTimestamp(message)
              : formatTimestamp(message.createdAt)}
          </div>
        )}

        {showReactions && (
          <div className="message-actions">
            <button onClick={onCopy} className="message-action-btn" title="Copy">
              📋
            </button>
            {onReact && (
              <button onClick={() => onReact('👍')} className="message-action-btn">
                👍
              </button>
            )}
            {onDelete && (
              <button
                onClick={onDelete}
                className="message-action-btn message-action-btn--danger"
                title="Delete"
              >
                🗑️
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function DefaultAvatar({ role }: { role: string }) {
  const avatarMap: Record<string, string> = {
    user: '👤',
    agent: '🤖',
    system: '⚙️',
    tool: '🔧',
    developer: '👨‍💻',
    channel: '📡',
  };

  return <div className="avatar-icon">{avatarMap[role] || '💬'}</div>;
}

function formatTimestamp(timestamp?: string): string {
  if (!timestamp) return '';

  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);

  if (diffMins < 1) return 'Just now';
  if (diffMins < 60) return `${diffMins}m ago`;

  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;

  return date.toLocaleDateString();
}
