/**
 * API request and response types
 */

import type { WorkspaceState } from '../types/workspace'

/**
 * API Response wrapper
 */
export interface ApiResponse<T> {
  data: T
  error?: string
  timestamp: string
}

/**
 * GET /api/state response
 */
export type StateResponse = WorkspaceState

/**
 * GET /api/experts response
 */
export interface ExpertsResponse {
  experts: string[]
  expert_results: Record<string, unknown>
}

/**
 * GET /api/history response
 */
export interface HistoricalSession {
  workspace_path: string
  topic: string
  date: string
  duration_seconds: number
  total_cost: number
  convergence_percent: number
  consensus_reached: boolean
  experts_count: number
}

export interface HistoryResponse {
  sessions: HistoricalSession[]
  total: number
}

/**
 * POST /api/cancel request
 */
export interface CancelRequest {
  expert: string
}

/**
 * WebSocket message types
 */
export type WebSocketMessageType = 'state_update' | 'expert_update' | 'phase_change' | 'error'

export interface WebSocketMessage {
  type: WebSocketMessageType
  data: unknown
  timestamp: string
}
