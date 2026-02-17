/**
 * API module exports
 */

// HTTP Client
export { httpClient, createHttpClient, ApiError, type ClientConfig } from './client'

// Endpoints
export {
  getState,
  getExperts,
  getHistory,
  cancelExpert,
  submitAnswers,
  submitConcernFeedback,
} from './endpoints'

// TanStack Query Hooks
export {
  useWorkspaceState,
  useExperts,
  useHistory,
  useCancelExpert,
  useSubmitAnswers,
  useSubmitConcernFeedback,
  queryKeys,
} from './queries'

// WebSocket Client
export {
  WebSocketClient,
  createWebSocketClient,
  WebSocketState,
  type WebSocketConfig,
} from './websocket'

// Types
export type {
  ApiResponse,
  StateResponse,
  ExpertsResponse,
  HistoryResponse,
  HistoricalSession,
  CancelRequest,
  WebSocketMessage,
  WebSocketMessageType,
} from './types'
