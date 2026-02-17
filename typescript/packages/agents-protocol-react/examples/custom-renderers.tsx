/**
 * Custom Content Renderers Example
 *
 * This example shows how to create custom renderers for specific content types
 * to match your application's design or add special functionality.
 */

import React from 'react';
import {
  AgentProvider,
  ChatThread,
  ContentRenderer,
  ContentRendererProps,
} from '@microsoft/agents-react-ui';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import type { TextContent, ImageContent, FunctionCallContent } from '@microsoft/agents-protocol-types';

const client = new AgentProtocolClient({
  baseUrl: 'https://your-agent-api.com',
  apiKey: process.env.AGENT_API_KEY,
});

// Custom text renderer with markdown support
function CustomTextRenderer({ content }: ContentRendererProps<TextContent>) {
  const textContent = content as TextContent;

  // You could use a markdown library here
  return (
    <div className="custom-text-content">
      <p style={{ fontFamily: 'Georgia, serif', lineHeight: 1.8 }}>
        {textContent.text}
      </p>
      {textContent.annotations && (
        <div className="text-annotations">
          {textContent.annotations.map((annotation, idx) => (
            <span key={idx} className="annotation-badge">
              {annotation}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}

// Custom image renderer with lightbox
function CustomImageRenderer({ content }: ContentRendererProps<ImageContent>) {
  const imageContent = content as ImageContent;
  const [isLightboxOpen, setIsLightboxOpen] = React.useState(false);

  return (
    <>
      <div className="custom-image-content">
        <img
          src={imageContent.uri}
          alt={imageContent.altText || 'Image'}
          onClick={() => setIsLightboxOpen(true)}
          style={{ cursor: 'pointer', maxWidth: '100%', borderRadius: '8px' }}
        />
        {imageContent.altText && (
          <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            {imageContent.altText}
          </p>
        )}
      </div>

      {/* Simple lightbox */}
      {isLightboxOpen && (
        <div
          className="lightbox"
          onClick={() => setIsLightboxOpen(false)}
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.9)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
          }}
        >
          <img
            src={imageContent.uri}
            alt={imageContent.altText || 'Image'}
            style={{ maxWidth: '90%', maxHeight: '90%' }}
          />
        </div>
      )}
    </>
  );
}

// Custom function call renderer with execution status
function CustomFunctionCallRenderer({ content }: ContentRendererProps<FunctionCallContent>) {
  const functionCall = content as FunctionCallContent;
  const [showDetails, setShowDetails] = React.useState(false);

  return (
    <div
      className="custom-function-call"
      style={{
        background: '#f0f7ff',
        border: '1px solid #0078d4',
        borderRadius: '8px',
        padding: '12px',
        margin: '8px 0',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '20px' }}>⚙️</span>
        <strong>{functionCall.name}</strong>
        <button
          onClick={() => setShowDetails(!showDetails)}
          style={{
            marginLeft: 'auto',
            background: 'transparent',
            border: 'none',
            cursor: 'pointer',
          }}
        >
          {showDetails ? '▼' : '▶'}
        </button>
      </div>

      {showDetails && (
        <div style={{ marginTop: '8px', fontSize: '14px' }}>
          {functionCall.callId && (
            <div style={{ color: '#666', marginBottom: '4px' }}>
              ID: <code>{functionCall.callId}</code>
            </div>
          )}
          <details>
            <summary style={{ cursor: 'pointer', fontWeight: 600 }}>
              Arguments
            </summary>
            <pre
              style={{
                background: '#fff',
                padding: '8px',
                borderRadius: '4px',
                overflow: 'auto',
                fontSize: '12px',
              }}
            >
              {JSON.stringify(
                typeof functionCall.arguments === 'string'
                  ? JSON.parse(functionCall.arguments)
                  : functionCall.arguments,
                null,
                2
              )}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

// Mapping custom renderers to content types
const customRenderers = {
  text: CustomTextRenderer,
  image: CustomImageRenderer,
  functionCall: CustomFunctionCallRenderer,
};

export function CustomRenderersExample() {
  return (
    <AgentProvider client={client}>
      <ChatThread
        threadId="thread_123"
        agentId="agent_456"
        userId="user_789"
        customRenderers={customRenderers}
        enableStreaming={true}
      />
    </AgentProvider>
  );
}

// Example: Override just one renderer while keeping the rest default
export function PartialCustomRenderersExample() {
  return (
    <AgentProvider client={client}>
      <ChatThread
        threadId="thread_123"
        agentId="agent_456"
        userId="user_789"
        customRenderers={{
          text: CustomTextRenderer, // Only override text rendering
        }}
        enableStreaming={true}
      />
    </AgentProvider>
  );
}
