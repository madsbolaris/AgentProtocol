/**
 * Hook for WebSocket connection management
 * Gracefully handles when backend doesn't support WebSocket yet
 */

import { useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { WebSocketClient, WebSocketState } from '@/api/websocket'

export type ConnectionStatus = 'connected' | 'disconnected' | 'connecting' | 'error'

interface UseWebSocketOptions {
  enabled?: boolean
  url?: string
  onMessage?: (data: unknown) => void
  onError?: (error: Error) => void
}

interface UseWebSocketResult {
  status: ConnectionStatus
  lastMessage: unknown | null
  error: Error | null
  send: (data: unknown) => void
  disconnect: () => void
  reconnect: () => void
}

export const useWebSocket = (options: UseWebSocketOptions = {}): UseWebSocketResult => {
  const { enabled = false, url, onMessage, onError } = options

  const [status, setStatus] = useState<ConnectionStatus>('disconnected')
  const [lastMessage, setLastMessage] = useState<unknown | null>(null)
  const [error, setError] = useState<Error | null>(null)

  const wsRef = useRef<WebSocketClient | null>(null)
  const queryClient = useQueryClient()

  useEffect(() => {
    // Don't connect if not enabled
    if (!enabled) {
      setStatus('disconnected')
      return
    }

    // Create WebSocket client
    const wsUrl = url || (import.meta.env.DEV ? 'ws://localhost:8765/ws' : '/ws')

    const ws = new WebSocketClient({
      url: wsUrl,
      onOpen: () => {
        setStatus('connected')
        setError(null)
      },
      onClose: () => {
        setStatus('disconnected')
      },
      onMessage: (data) => {
        setLastMessage(data)
        onMessage?.(data)

        // Invalidate queries to refetch data
        queryClient.invalidateQueries({ queryKey: ['state'] })
      },
      onError: (err) => {
        const error = new Error(`WebSocket error: ${err.message || 'Unknown error'}`)
        setError(error)
        setStatus('error')
        onError?.(error)
      },
    })

    // Connect
    setStatus('connecting')
    ws.connect()
    wsRef.current = ws

    // Cleanup on unmount
    return () => {
      ws.disconnect()
      wsRef.current = null
    }
  }, [enabled, url, onMessage, onError, queryClient])

  // Send message
  const send = (data: unknown) => {
    if (wsRef.current && status === 'connected') {
      wsRef.current.send(data)
    } else {
      console.warn('WebSocket not connected, cannot send message')
    }
  }

  // Disconnect manually
  const disconnect = () => {
    wsRef.current?.disconnect()
    setStatus('disconnected')
  }

  // Reconnect manually
  const reconnect = () => {
    wsRef.current?.reconnect()
    setStatus('connecting')
  }

  return {
    status,
    lastMessage,
    error,
    send,
    disconnect,
    reconnect,
  }
}
