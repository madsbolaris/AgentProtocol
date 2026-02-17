/**
 * Renderer for error content
 */

import React, { useState } from 'react';
import type { ErrorContent } from '@microsoft/agents';
import { ContentRendererProps } from '../types';

export function ErrorContentRenderer({ content }: ContentRendererProps<ErrorContent>) {
  const error = content as ErrorContent;
  const [showDetails, setShowDetails] = useState(false);

  return (
    <div className="content-error">
      <div className="error-header">
        <span className="error-icon">⚠️</span>
        <span className="error-message">{error.message}</span>
      </div>

      {(error.code || error.stackTrace) && (
        <>
          <button
            className="error-details-toggle"
            onClick={() => setShowDetails(!showDetails)}
          >
            {showDetails ? 'Hide' : 'Show'} details
          </button>

          {showDetails && (
            <div className="error-details">
              {error.code && (
                <div className="error-code">
                  <strong>Code:</strong> {error.code}
                </div>
              )}
              {error.stackTrace && (
                <div className="error-stack">
                  <strong>Stack Trace:</strong>
                  <pre>{error.stackTrace}</pre>
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}
