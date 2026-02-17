/**
 * WebSocket client for real-time updates
 */

import type { WebSocketMessage } from './types'

/**
 * WebSocket connection states
 */
export const WebSocketState = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const

export type WebSocketState = (typeof WebSocketState)[keyof typeof WebSocketState]

/**
 * WebSocket client configuration
 */
export interface WebSocketConfig {
  url?: string
  reconnectInterval?: number
  maxReconnectAttempts?: number
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  onMessage?: (message: WebSocketMessage) => void
}

/**
 * WebSocket client with auto-reconnect
 */
export class WebSocketClient {
  private ws: WebSocket | null = null
  private config: Required<WebSocketConfig>
  private reconnectAttempts = 0
  private reconnectTimeout: number | null = null
  private isIntentionallyClosed = false

  constructor(config: WebSocketConfig = {}) {
    this.config = {
      url: config.url || 'ws://localhost:8765/ws',
      reconnectInterval: config.reconnectInterval || 3000,
      maxReconnectAttempts: config.maxReconnectAttempts || 10,
      onOpen: config.onOpen || (() => {}),
      onClose: config.onClose || (() => {}),
      onError: config.onError || (() => {}),
      onMessage: config.onMessage || (() => {}),
    }
  }

  /**
   * Connect to WebSocket server
   */
  connect(): void {
    if (this.ws && this.ws.readyState === WebSocketState.OPEN) {
      return
    }

    this.isIntentionallyClosed = false

    try {
      this.ws = new WebSocket(this.config.url)

      this.ws.onopen = () => {
        console.log('[WebSocket] Connected')
        this.reconnectAttempts = 0
        this.config.onOpen()
      }

      this.ws.onclose = () => {
        console.log('[WebSocket] Disconnected')
        this.config.onClose()

        // Auto-reconnect if not intentionally closed
        if (!this.isIntentionallyClosed && this.shouldReconnect()) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        this.config.onError(error)
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          this.config.onMessage(message)
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error)
        }
      }
    } catch (error) {
      console.error('[WebSocket] Connection error:', error)
      if (this.shouldReconnect()) {
        this.scheduleReconnect()
      }
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.isIntentionallyClosed = true

    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  /**
   * Send a message to the server
   */
  send(data: unknown): void {
    if (this.ws && this.ws.readyState === WebSocketState.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('[WebSocket] Cannot send message, not connected')
    }
  }

  /**
   * Get current connection state
   */
  get state(): WebSocketState {
    return (this.ws?.readyState ?? WebSocketState.CLOSED) as WebSocketState
  }

  /**
   * Check if connected
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocketState.OPEN
  }

  /**
   * Check if should attempt reconnect
   */
  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.config.maxReconnectAttempts
  }

  /**
   * Schedule reconnection attempt
   */
  private scheduleReconnect(): void {
    this.reconnectAttempts++

    const delay = this.config.reconnectInterval * this.reconnectAttempts

    console.log(
      `[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.config.maxReconnectAttempts})`
    )

    this.reconnectTimeout = setTimeout(() => {
      this.connect()
    }, delay)
  }
}

/**
 * Create a new WebSocket client
 */
export const createWebSocketClient = (config?: WebSocketConfig): WebSocketClient => {
  return new WebSocketClient(config)
}
