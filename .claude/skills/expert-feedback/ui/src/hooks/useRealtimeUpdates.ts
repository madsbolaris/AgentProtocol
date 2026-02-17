/**
 * Hook for managing real-time updates via WebSocket
 * Falls back to polling when WebSocket unavailable
 */

import { useUIStore } from '@/store/useUIStore'
import { useWebSocket } from './useWebSocket'
import type { ConnectionStatus } from './useWebSocket'

export interface RealtimeUpdatesResult {
  isConnected: boolean
  isRealtimeEnabled: boolean
  connectionStatus: ConnectionStatus
  lastUpdate: unknown | null
  error: Error | null
  toggleRealtime: () => void
  reconnect: () => void
}

export const useRealtimeUpdates = (): RealtimeUpdatesResult => {
  const wsEnabled = useUIStore((s) => s.websocketEnabled)
  const setWsEnabled = useUIStore((s) => s.setWebSocketEnabled)

  const { status, lastMessage, error, reconnect } = useWebSocket({
    enabled: wsEnabled,
    onMessage: (data) => {
      // Log received messages in development
      if (import.meta.env.DEV) {
        console.log('WebSocket message received:', data)
      }
    },
    onError: (err) => {
      // Log errors in development
      if (import.meta.env.DEV) {
        console.error('WebSocket error:', err)
      }
    },
  })

  const toggleRealtime = () => {
    setWsEnabled(!wsEnabled)
  }

  return {
    isConnected: status === 'connected',
    isRealtimeEnabled: wsEnabled,
    connectionStatus: status,
    lastUpdate: lastMessage,
    error,
    toggleRealtime,
    reconnect,
  }
}
