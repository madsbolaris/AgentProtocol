/**
 * API endpoints for expert-feedback backend
 */

import { httpClient } from './client'
import type { StateResponse, ExpertsResponse, HistoryResponse, CancelRequest } from './types'

/**
 * Get current workspace state
 * @returns Current state including expert progress, cache metrics, etc.
 */
export const getState = async (): Promise<StateResponse> => {
  return httpClient.get<StateResponse>('/state')
}

/**
 * Get expert results
 * @returns List of experts and their results
 */
export const getExperts = async (): Promise<ExpertsResponse> => {
  return httpClient.get<ExpertsResponse>('/experts')
}

/**
 * Get historical sessions
 * @param limit - Maximum number of sessions to return (default: 10)
 * @param offset - Number of sessions to skip (default: 0)
 * @returns List of past sessions with metadata
 */
export const getHistory = async (
  limit: number = 10,
  offset: number = 0
): Promise<HistoryResponse> => {
  const params = new URLSearchParams({
    limit: limit.toString(),
    offset: offset.toString(),
  })
  return httpClient.get<HistoryResponse>(`/history?${params}`)
}

/**
 * Cancel a running expert
 * @param expert - Name of expert to cancel
 * @returns Success response
 */
export const cancelExpert = async (expert: string): Promise<{ success: boolean }> => {
  const request: CancelRequest = { expert }
  return httpClient.post<{ success: boolean }>('/cancel', request)
}

/**
 * Submit answers to questions
 * @param answers - User's answers to expert questions
 * @returns Success response
 */
export const submitAnswers = async (answers: Record<string, string>): Promise<void> => {
  return httpClient.post<void>('/answers', { answers })
}

/**
 * Submit concern feedback
 * @param feedback - User's feedback on concerns
 * @returns Success response
 */
export const submitConcernFeedback = async (feedback: Record<string, unknown>): Promise<void> => {
  return httpClient.post<void>('/concern-feedback', { feedback })
}
