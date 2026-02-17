/**
 * Renderer for typing indicator content
 */

import React from 'react';
import type { TypingIndicatorContent } from '@microsoft/agents';
import { ContentRendererProps } from '../types';

export function TypingIndicatorRenderer({
  content,
}: ContentRendererProps<TypingIndicatorContent>) {
  const typing = content as TypingIndicatorContent;

  const statusText = {
    typing: 'typing',
    thinking: 'thinking',
    processing: 'processing',
  }[typing.status || 'typing'];

  return (
    <div className="content-typing-indicator">
      <div className="typing-indicator-dots">
        <span className="typing-dot"></span>
        <span className="typing-dot"></span>
        <span className="typing-dot"></span>
      </div>
      <span className="typing-indicator-text">{statusText}...</span>
    </div>
  );
}
