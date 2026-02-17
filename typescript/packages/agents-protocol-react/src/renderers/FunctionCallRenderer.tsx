/**
 * Renderer for function call content
 */

import React, { useState } from 'react';
import type { FunctionCallContent } from '@microsoft/agents';
import { ContentRendererProps } from '../types';

export function FunctionCallRenderer({ content }: ContentRendererProps<FunctionCallContent>) {
  const functionCall = content as FunctionCallContent;
  const [isExpanded, setIsExpanded] = useState(false);

  let parsedArgs;
  try {
    parsedArgs =
      typeof functionCall.arguments === 'string'
        ? JSON.parse(functionCall.arguments)
        : functionCall.arguments;
  } catch {
    parsedArgs = functionCall.arguments;
  }

  return (
    <div className="content-function-call">
      <div className="function-call-header">
        <span className="function-call-icon">🔧</span>
        <span className="function-call-name">{functionCall.name}</span>
        <button
          className="function-call-toggle"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className="function-call-details">
          {functionCall.callId && (
            <div className="function-call-id">
              <strong>Call ID:</strong> {functionCall.callId}
            </div>
          )}
          <div className="function-call-arguments">
            <strong>Arguments:</strong>
            <pre>{JSON.stringify(parsedArgs, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
