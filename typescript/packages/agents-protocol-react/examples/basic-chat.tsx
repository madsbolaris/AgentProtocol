/**
 * Basic Chat Example
 *
 * This example shows the simplest way to integrate the Agent Protocol chat
 * into your React application using the pre-built ChatThread component.
 */

import React from 'react';
import { AgentProvider, ChatThread } from '@microsoft/agents-react-ui';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

// Import default styles
import '@microsoft/agents-react-ui/dist/styles/default-theme.css';

const client = new AgentProtocolClient({
  baseUrl: 'https://your-agent-api.com',
  apiKey: process.env.AGENT_API_KEY,
});

export function BasicChatExample() {
  return (
    <AgentProvider client={client}>
      <div style={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
        <ChatThread
          threadId="thread_123"
          agentId="agent_456"
          userId="user_789"
          enableStreaming={true}
          onError={(error) => console.error('Chat error:', error)}
        />
      </div>
    </AgentProvider>
  );
}

// With custom configuration
export function ConfiguredChatExample() {
  return (
    <AgentProvider client={client}>
      <ChatThread
        threadId="thread_123"
        agentId="agent_456"
        userId="user_789"
        enableStreaming={true}
        maxMessageLength={1000}
        placeholder="Ask me anything..."
        showTimestamps={true}
        enableReactions={true}
        emptyStateMessage="Start a conversation!"
        loadingMessage="Thinking..."
      />
    </AgentProvider>
  );
}
