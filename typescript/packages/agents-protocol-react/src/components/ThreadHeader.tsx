/**
 * ThreadHeader component - displays thread info
 */

import React from 'react';

export interface ThreadHeaderProps {
  threadId: string;
  title?: string;
  subtitle?: string;
  isStreaming?: boolean;
  onClose?: () => void;
}

export function ThreadHeader({
  threadId,
  title,
  subtitle,
  isStreaming,
  onClose,
}: ThreadHeaderProps) {
  return (
    <div className="thread-header">
      <div className="thread-header-info">
        <div className="thread-header-title">{title || 'Chat'}</div>
        {subtitle && <div className="thread-header-subtitle">{subtitle}</div>}
        {isStreaming && (
          <div className="thread-header-status">
            <span className="status-indicator status-indicator--connected"></span>
            Connected
          </div>
        )}
      </div>

      {onClose && (
        <button className="thread-header-close" onClick={onClose} title="Close">
          ✕
        </button>
      )}
    </div>
  );
}
