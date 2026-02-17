/**
 * Global context provider for Agent Protocol client and configuration
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { AgentProtocolClient } from '@microsoft/agents-protocol-client';
import { ThemeConfig, ContentRenderers } from '../types';

export interface AgentContextValue {
  client: AgentProtocolClient;
  theme?: ThemeConfig;
  contentRenderers?: ContentRenderers;
}

const AgentContext = createContext<AgentContextValue | null>(null);

export interface AgentProviderProps {
  /** Agent Protocol API base URL */
  apiBaseUrl: string;

  /** Authentication token */
  authToken?: string;

  /** Theme configuration */
  theme?: ThemeConfig;

  /** Custom content renderers */
  contentRenderers?: ContentRenderers;

  /** Request timeout */
  timeout?: number;

  /** Enable debug mode */
  debug?: boolean;

  children: ReactNode;
}

export function AgentProvider({
  apiBaseUrl,
  authToken,
  theme,
  contentRenderers,
  timeout,
  debug,
  children,
}: AgentProviderProps) {
  const client = React.useMemo(
    () =>
      new AgentProtocolClient({
        baseUrl: apiBaseUrl,
        authToken,
        timeout,
        debug,
      }),
    [apiBaseUrl, authToken, timeout, debug]
  );

  const value = React.useMemo(
    () => ({
      client,
      theme,
      contentRenderers,
    }),
    [client, theme, contentRenderers]
  );

  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>;
}

/**
 * Hook to access the Agent context
 */
export function useAgentContext(): AgentContextValue {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
}
