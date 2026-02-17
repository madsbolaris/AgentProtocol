/**
 * Headless Chat Example
 *
 * This example demonstrates how to use the hooks directly to build a
 * completely custom chat interface. This gives you full control over
 * the UI while still benefiting from the protocol logic.
 */

import React, { useEffect } from 'react';
import { AgentProvider, useThread, useStreaming, useAgent } from '@microsoft/agents-react-ui';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

const client = new AgentProtocolClient({
  baseUrl: 'https://your-agent-api.com',
  apiKey: process.env.AGENT_API_KEY,
});

function CustomChatUI() {
  const {
    thread,
    messages,
    isLoading,
    sendMessage,
    addReaction,
    deleteMessage,
  } = useThread('thread_123', { autoLoad: true });

  const { events, isConnected } = useStreaming('thread_123', 'thread', {
    autoConnect: true,
  });

  const { executeAgent } = useAgent('agent_456');

  // Handle new streaming events
  useEffect(() => {
    if (events.length > 0) {
      const lastEvent = events[events.length - 1];
      console.log('New event:', lastEvent);
    }
  }, [events]);

  const handleSend = async (text: string) => {
    await sendMessage(text);
    // Execute the agent after sending a user message
    await executeAgent('thread_123', 'user_789');
  };

  return (
    <div className="custom-chat">
      {/* Custom Header */}
      <header className="custom-header">
        <h1>{thread?.title || 'Chat'}</h1>
        <div className="connection-status">
          {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
        </div>
      </header>

      {/* Custom Message List */}
      <div className="custom-messages">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`custom-message custom-message--${message.role}`}
          >
            <div className="message-content">
              {message.contents?.map((content, idx) => {
                if (content.kind === 'text') {
                  return <p key={idx}>{content.text}</p>;
                }
                return <div key={idx}>[{content.kind}]</div>;
              })}
            </div>

            {/* Custom Actions */}
            <div className="message-actions">
              <button onClick={() => addReaction(message.id, '👍')}>👍</button>
              <button onClick={() => addReaction(message.id, '❤️')}>❤️</button>
              <button onClick={() => deleteMessage(message.id)}>🗑️</button>
            </div>
          </div>
        ))}

        {isLoading && <div className="custom-loading">Agent is thinking...</div>}
      </div>

      {/* Custom Input */}
      <CustomInput onSend={handleSend} disabled={isLoading} />
    </div>
  );
}

function CustomInput({ onSend, disabled }: { onSend: (text: string) => void; disabled: boolean }) {
  const [value, setValue] = React.useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSend(value);
      setValue('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="custom-input">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Type a message..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !value.trim()}>
        Send
      </button>
    </form>
  );
}

export function HeadlessChatExample() {
  return (
    <AgentProvider client={client}>
      <CustomChatUI />
    </AgentProvider>
  );
}
