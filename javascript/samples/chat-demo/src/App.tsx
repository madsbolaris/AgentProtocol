import React, { useState, useEffect } from 'react';
import { AgentProvider, ChatThread } from '@microsoft/agents-react-ui';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import '@microsoft/agents-react-ui/dist/styles/default-theme.css';
import './App.css';

type BotImplementation = 'dotnet' | 'python' | 'typescript' | 'dotnet-emoji-chat' | 'dotnet-function-tools';
type Theme = 'light' | 'dark';

interface BotConfig {
  name: string;
  description: string;
  baseUrl: string;
  port: number;
  language: string;
}

interface AgentConfig {
  bots: Record<string, {
    name: string;
    baseUrl: string;
    port: number;
  }>;
}

// Default bot configurations (used as fallback if config file not loaded)
const DEFAULT_BOT_CONFIGS: Record<BotImplementation, BotConfig> = {
  dotnet: {
    name: 'EchoBot (.NET)',
    description: 'C# implementation using ASP.NET Core',
    baseUrl: 'http://localhost',
    port: 3978,
    language: 'C#',
  },
  python: {
    name: 'EchoBot (Python)',
    description: 'Python implementation using aiohttp',
    baseUrl: 'http://localhost',
    port: 3979,
    language: 'Python',
  },
  typescript: {
    name: 'EchoBot (TypeScript)',
    description: 'TypeScript implementation using Express',
    baseUrl: 'http://localhost',
    port: 3980,
    language: 'TypeScript',
  },
  'dotnet-function-tools': {
    name: 'FunctionToolsAgent (.NET)',
    description: 'Agent with function calling capabilities',
    baseUrl: 'http://localhost',
    port: 3981,
    language: 'C#',
  },
  'dotnet-emoji-chat': {
    name: 'EmojiChatBot (.NET)',
    description: 'Chatbot with emoji reactions and event handling',
    baseUrl: 'http://localhost',
    port: 3984,
    language: 'C#',
  },
};

function App() {
  const [selectedBot, setSelectedBot] = useState<BotImplementation>('dotnet');
  const [theme, setTheme] = useState<Theme>('light');
  const [client, setClient] = useState<AgentProtocolClient | null>(null);
  const [threadId] = useState<string>('demo-thread-' + Date.now());
  const [userId] = useState<string>('demo-user-' + Math.random().toString(36).substring(7));
  const [isConnected, setIsConnected] = useState(false);
  const [botConfigs, setBotConfigs] = useState<Record<BotImplementation, BotConfig>>(DEFAULT_BOT_CONFIGS);

  // Load configuration from agent-config.json
  useEffect(() => {
    const loadConfig = async () => {
      try {
        const response = await fetch('/agent-config.json');
        if (response.ok) {
          const config: AgentConfig = await response.json();

          // Merge loaded config with defaults
          const mergedConfigs: Record<BotImplementation, BotConfig> = {
            dotnet: {
              ...DEFAULT_BOT_CONFIGS.dotnet,
              name: config.bots.dotnet?.name || DEFAULT_BOT_CONFIGS.dotnet.name,
              baseUrl: config.bots.dotnet?.baseUrl || DEFAULT_BOT_CONFIGS.dotnet.baseUrl,
              port: config.bots.dotnet?.port || DEFAULT_BOT_CONFIGS.dotnet.port,
            },
            python: {
              ...DEFAULT_BOT_CONFIGS.python,
              name: config.bots.python?.name || DEFAULT_BOT_CONFIGS.python.name,
              baseUrl: config.bots.python?.baseUrl || DEFAULT_BOT_CONFIGS.python.baseUrl,
              port: config.bots.python?.port || DEFAULT_BOT_CONFIGS.python.port,
            },
            typescript: {
              ...DEFAULT_BOT_CONFIGS.typescript,
              name: config.bots.typescript?.name || DEFAULT_BOT_CONFIGS.typescript.name,
              baseUrl: config.bots.typescript?.baseUrl || DEFAULT_BOT_CONFIGS.typescript.baseUrl,
              port: config.bots.typescript?.port || DEFAULT_BOT_CONFIGS.typescript.port,
            },
            'dotnet-function-tools': {
              ...DEFAULT_BOT_CONFIGS['dotnet-function-tools'],
              name: config.bots['dotnet-function-tools']?.name || DEFAULT_BOT_CONFIGS['dotnet-function-tools'].name,
              baseUrl: config.bots['dotnet-function-tools']?.baseUrl || DEFAULT_BOT_CONFIGS['dotnet-function-tools'].baseUrl,
              port: config.bots['dotnet-function-tools']?.port || DEFAULT_BOT_CONFIGS['dotnet-function-tools'].port,
            },
            'dotnet-emoji-chat': {
              ...DEFAULT_BOT_CONFIGS['dotnet-emoji-chat'],
              name: config.bots['dotnet-emoji-chat']?.name || DEFAULT_BOT_CONFIGS['dotnet-emoji-chat'].name,
              baseUrl: config.bots['dotnet-emoji-chat']?.baseUrl || DEFAULT_BOT_CONFIGS['dotnet-emoji-chat'].baseUrl,
              port: config.bots['dotnet-emoji-chat']?.port || DEFAULT_BOT_CONFIGS['dotnet-emoji-chat'].port,
            },
          };

          setBotConfigs(mergedConfigs);
          console.log('Loaded configuration from agent-config.json');
        }
      } catch (error) {
        console.warn('Could not load agent-config.json, using defaults:', error);
      }
    };

    loadConfig();
  }, []);

  const currentConfig = botConfigs[selectedBot];

  // Update client when bot selection changes
  useEffect(() => {
    const newClient = new AgentProtocolClient({
      baseUrl: `${currentConfig.baseUrl}:${currentConfig.port}`,
    });

    setClient(newClient);
    setIsConnected(false);

    // Test connection
    const testConnection = async () => {
      try {
        await fetch(`${currentConfig.baseUrl}:${currentConfig.port}/`, {
          method: 'GET',
        });
        setIsConnected(true);
      } catch (error) {
        console.error('Failed to connect to bot:', error);
        setIsConnected(false);
      }
    };

    testConnection();
  }, [selectedBot]);

  return (
    <div className={`app ${theme}`} data-theme={theme}>
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <h1>🤖 Agent Protocol Chat Demo</h1>
          <p className="header-subtitle">
            Interactive demo with multiple bots and emoji reactions
          </p>
        </div>
      </header>

      {/* Configuration Panel */}
      <div className="config-panel">
        <div className="config-section">
          <h3>Bot Implementation</h3>
          <div className="bot-selector">
            {(Object.keys(botConfigs) as BotImplementation[]).map((bot) => {
              const config = botConfigs[bot];
              return (
                <button
                  key={bot}
                  className={`bot-option ${selectedBot === bot ? 'active' : ''}`}
                  onClick={() => setSelectedBot(bot)}
                >
                  <div className="bot-option-header">
                    <span className="bot-name">{config.name}</span>
                    {selectedBot === bot && isConnected && (
                      <span className="status-badge connected">Connected</span>
                    )}
                    {selectedBot === bot && !isConnected && (
                      <span className="status-badge disconnected">Disconnected</span>
                    )}
                  </div>
                  <span className="bot-description">{config.description}</span>
                  <div className="bot-details">
                    <span className="bot-language">{config.language}</span>
                    <span className="bot-port">Port: {config.port}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {!isConnected && (
            <div className="connection-warning">
              ⚠️ Cannot connect to {currentConfig.name}. Make sure the bot is running on port{' '}
              {currentConfig.port}.
            </div>
          )}
        </div>

        <div className="config-section">
          <h3>Theme</h3>
          <div className="theme-selector">
            <button
              className={`theme-option ${theme === 'light' ? 'active' : ''}`}
              onClick={() => setTheme('light')}
            >
              ☀️ Light
            </button>
            <button
              className={`theme-option ${theme === 'dark' ? 'active' : ''}`}
              onClick={() => setTheme('dark')}
            >
              🌙 Dark
            </button>
          </div>
        </div>

        <div className="config-section info-section">
          <h3>ℹ️ About This Demo</h3>
          <ul>
            <li>
              <strong>Thread ID:</strong> <code>{threadId}</code>
            </li>
            <li>
              <strong>User ID:</strong> <code>{userId}</code>
            </li>
            <li>
              <strong>API Endpoint:</strong>{' '}
              <code>
                {currentConfig.baseUrl}:{currentConfig.port}/api/messages
              </code>
            </li>
          </ul>
        </div>
      </div>

      {/* Chat Interface */}
      <div className="chat-container">
        {client ? (
          <AgentProvider client={client}>
            <ChatThread
              threadId={threadId}
              agentId="echo-bot"
              userId={userId}
              enableStreaming={false}
              placeholder="Type a message to the echo bot..."
              emptyStateMessage="👋 Start chatting! The bot will echo your messages back."
              onError={(error) => {
                console.error('Chat error:', error);
              }}
            />
          </AgentProvider>
        ) : (
          <div className="loading-state">Initializing chat client...</div>
        )}
      </div>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Built with{' '}
          <a
            href="https://github.com/microsoft/agent-protocol"
            target="_blank"
            rel="noopener noreferrer"
          >
            Microsoft Agent Protocol
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
