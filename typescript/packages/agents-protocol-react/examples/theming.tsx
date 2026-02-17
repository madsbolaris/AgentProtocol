/**
 * Theming Example
 *
 * This example demonstrates how to customize the appearance of the chat
 * interface using CSS variables and custom themes.
 */

import React, { useState } from 'react';
import { AgentProvider, ChatThread } from '@microsoft/agents-react-ui';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

// Import default styles
import '@microsoft/agents-react-ui/dist/styles/default-theme.css';

const client = new AgentProtocolClient({
  baseUrl: 'https://your-agent-api.com',
  apiKey: process.env.AGENT_API_KEY,
});

// Example 1: Dark Mode Toggle
export function DarkModeExample() {
  const [isDark, setIsDark] = useState(false);

  return (
    <div data-theme={isDark ? 'dark' : 'light'}>
      <div style={{ padding: '16px' }}>
        <button onClick={() => setIsDark(!isDark)}>
          Toggle {isDark ? 'Light' : 'Dark'} Mode
        </button>
      </div>

      <AgentProvider client={client}>
        <ChatThread
          threadId="thread_123"
          agentId="agent_456"
          userId="user_789"
          enableStreaming={true}
        />
      </AgentProvider>
    </div>
  );
}

// Example 2: Custom Color Scheme
export function CustomColorSchemeExample() {
  return (
    <div
      style={{
        // Override CSS variables for custom colors
        '--agent-primary': '#7c3aed',
        '--agent-secondary': '#6d28d9',
        '--agent-user-bubble': '#7c3aed',
        '--agent-agent-bubble': '#f3e8ff',
        '--agent-background': '#faf5ff',
      } as React.CSSProperties}
    >
      <AgentProvider client={client}>
        <ChatThread
          threadId="thread_123"
          agentId="agent_456"
          userId="user_789"
          enableStreaming={true}
        />
      </AgentProvider>
    </div>
  );
}

// Example 3: Multiple Theme Presets
const themes = {
  default: {
    '--agent-primary': '#0078d4',
    '--agent-user-bubble': '#0078d4',
    '--agent-agent-bubble': '#f3f2f1',
    '--agent-background': '#ffffff',
  },
  ocean: {
    '--agent-primary': '#0891b2',
    '--agent-user-bubble': '#0891b2',
    '--agent-agent-bubble': '#cffafe',
    '--agent-background': '#ecfeff',
  },
  forest: {
    '--agent-primary': '#059669',
    '--agent-user-bubble': '#059669',
    '--agent-agent-bubble': '#d1fae5',
    '--agent-background': '#ecfdf5',
  },
  sunset: {
    '--agent-primary': '#dc2626',
    '--agent-user-bubble': '#dc2626',
    '--agent-agent-bubble': '#fee2e2',
    '--agent-background': '#fef2f2',
  },
};

export function ThemePresetsExample() {
  const [currentTheme, setCurrentTheme] = useState<keyof typeof themes>('default');

  return (
    <div style={themes[currentTheme] as React.CSSProperties}>
      <div style={{ padding: '16px', display: 'flex', gap: '8px' }}>
        {Object.keys(themes).map((themeName) => (
          <button
            key={themeName}
            onClick={() => setCurrentTheme(themeName as keyof typeof themes)}
            style={{
              padding: '8px 16px',
              border: currentTheme === themeName ? '2px solid #000' : '1px solid #ccc',
              borderRadius: '4px',
              background: currentTheme === themeName ? '#f0f0f0' : 'white',
              cursor: 'pointer',
              textTransform: 'capitalize',
            }}
          >
            {themeName}
          </button>
        ))}
      </div>

      <AgentProvider client={client}>
        <ChatThread
          threadId="thread_123"
          agentId="agent_456"
          userId="user_789"
          enableStreaming={true}
        />
      </AgentProvider>
    </div>
  );
}

// Example 4: Custom CSS with theme extension
export function ExtendedThemeExample() {
  return (
    <>
      <style>{`
        /* Extend the default theme with custom styles */
        .chat-thread {
          font-family: 'Comic Sans MS', cursive;
        }

        .message-bubble--user {
          border-radius: 20px;
          box-shadow: 0 4px 12px rgba(0, 120, 212, 0.3);
        }

        .message-bubble--agent {
          border-radius: 20px;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }

        .input-textarea {
          border-radius: 24px;
          border: 2px solid var(--agent-primary);
        }

        .input-btn--send {
          border-radius: 24px;
          font-weight: bold;
          text-transform: uppercase;
        }
      `}</style>

      <AgentProvider client={client}>
        <ChatThread
          threadId="thread_123"
          agentId="agent_456"
          userId="user_789"
          enableStreaming={true}
        />
      </AgentProvider>
    </>
  );
}

// Example 5: Compact/Mobile Theme
export function CompactThemeExample() {
  return (
    <div
      style={{
        '--agent-space-xs': '2px',
        '--agent-space-sm': '4px',
        '--agent-space-md': '8px',
        '--agent-space-lg': '12px',
        '--agent-font-size-sm': '11px',
        '--agent-font-size-md': '13px',
        '--agent-font-size-lg': '14px',
      } as React.CSSProperties}
    >
      <AgentProvider client={client}>
        <ChatThread
          threadId="thread_123"
          agentId="agent_456"
          userId="user_789"
          enableStreaming={true}
        />
      </AgentProvider>
    </div>
  );
}
