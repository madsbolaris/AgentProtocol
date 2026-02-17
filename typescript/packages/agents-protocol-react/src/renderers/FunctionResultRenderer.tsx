/**
 * Renderer for function result content
 */

import React, { useState } from 'react';
import type { FunctionResultContent } from '@microsoft/agents';
import { ContentRendererProps } from '../types';

export function FunctionResultRenderer({
  content,
}: ContentRendererProps<FunctionResultContent>) {
  const result = content as FunctionResultContent;
  const [isExpanded, setIsExpanded] = useState(false);

  let parsedResult;
  try {
    parsedResult = typeof result.result === 'string' ? JSON.parse(result.result) : result.result;
  } catch {
    parsedResult = result.result;
  }

  const isError = result.isError;

  return (
    <div className={`content-function-result ${isError ? 'content-function-result--error' : ''}`}>
      <div className="function-result-header">
        <span className="function-result-icon">{isError ? '❌' : '✅'}</span>
        <span className="function-result-label">
          {isError ? 'Function Failed' : 'Function Result'}
        </span>
        <button className="function-result-toggle" onClick={() => setIsExpanded(!isExpanded)}>
          {isExpanded ? '▼' : '▶'}
        </button>
      </div>

      {isExpanded && (
        <div className="function-result-details">
          {result.callId && (
            <div className="function-result-id">
              <strong>Call ID:</strong> {result.callId}
            </div>
          )}
          <div className="function-result-output">
            <strong>Output:</strong>
            <pre>{JSON.stringify(parsedResult, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
