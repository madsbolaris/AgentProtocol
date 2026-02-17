/**
 * Renderer for text content
 */

import React from 'react';
import type { TextContent } from '@microsoft/agents';
import { ContentRendererProps } from '../types';

export function TextContentRenderer({
  content,
  isStreaming,
}: ContentRendererProps<TextContent>) {
  const textContent = content as TextContent;

  return (
    <div className={`content-text ${isStreaming ? 'content-text--streaming' : ''}`}>
      {textContent.text}
    </div>
  );
}
