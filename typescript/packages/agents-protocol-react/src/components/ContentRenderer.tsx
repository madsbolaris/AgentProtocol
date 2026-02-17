/**
 * Content renderer - routes content to appropriate renderer
 */

import React from 'react';
import type { AIContent, ChatMessage } from '@microsoft/agents';
import { useAgentContext } from '../context/AgentProvider';
import { ContentRendererProps } from '../types';

// Import default renderers
import { TextContentRenderer } from '../renderers/TextContentRenderer';
import { ImageContentRenderer } from '../renderers/ImageContentRenderer';
import { FunctionCallRenderer } from '../renderers/FunctionCallRenderer';
import { FunctionResultRenderer } from '../renderers/FunctionResultRenderer';
import { ErrorContentRenderer } from '../renderers/ErrorContentRenderer';

interface ContentRendererComponentProps {
  content: AIContent;
  message: ChatMessage;
  isStreaming?: boolean;
}

export function ContentRenderer({
  content,
  message,
  isStreaming,
}: ContentRendererComponentProps) {
  const { contentRenderers } = useAgentContext();

  // Check for custom renderer
  const customRenderer = contentRenderers?.[content.kind];
  if (customRenderer) {
    return <>{customRenderer({ content, message, isStreaming })}</>;
  }

  // Use default renderer based on kind
  switch (content.kind) {
    case 'text':
      return <TextContentRenderer content={content} message={message} isStreaming={isStreaming} />;

    case 'image':
      return <ImageContentRenderer content={content} message={message} />;

    case 'functionCall':
      return <FunctionCallRenderer content={content} message={message} />;

    case 'functionResult':
      return <FunctionResultRenderer content={content} message={message} />;

    case 'error':
      return <ErrorContentRenderer content={content} message={message} />;

    // Add more default renderers as needed
    default:
      return <DefaultRenderer content={content} />;
  }
}

function DefaultRenderer({ content }: { content: AIContent }) {
  return (
    <div className="content-default">
      <div className="content-kind-badge">{content.kind}</div>
      <pre>{JSON.stringify(content, null, 2)}</pre>
    </div>
  );
}
