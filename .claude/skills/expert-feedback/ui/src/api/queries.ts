/**
 * TanStack Query hooks for API endpoints
 */

import { useQuery, useMutation, useQueryClient, type UseQueryOptions } from '@tanstack/react-query'
import {
  getState,
  getExperts,
  getHistory,
  cancelExpert,
  submitAnswers,
  submitConcernFeedback,
} from './endpoints'
import type { StateResponse, ExpertsResponse, HistoryResponse } from './types'

/**
 * Query keys for cache management
 */
export const queryKeys = {
  state: ['workspace', 'state'] as const,
  experts: ['workspace', 'experts'] as const,
  history: (limit: number, offset: number) => ['workspace', 'history', { limit, offset }] as const,
}

/**
 * Hook to get current workspace state
 * Refetches every 2 seconds while active
 */
export const useWorkspaceState = (
  options?: Omit<UseQueryOptions<StateResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.state,
    queryFn: getState,
    refetchInterval: 2000, // Poll every 2 seconds
    refetchIntervalInBackground: false,
    staleTime: 1000, // Consider data stale after 1 second
    ...options,
  })
}

/**
 * Hook to get expert results
 */
export const useExperts = (
  options?: Omit<UseQueryOptions<ExpertsResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.experts,
    queryFn: getExperts,
    staleTime: 5000, // Consider data stale after 5 seconds
    ...options,
  })
}

/**
 * Hook to get historical sessions
 */
export const useHistory = (
  limit: number = 10,
  offset: number = 0,
  options?: Omit<UseQueryOptions<HistoryResponse>, 'queryKey' | 'queryFn'>
) => {
  return useQuery({
    queryKey: queryKeys.history(limit, offset),
    queryFn: () => getHistory(limit, offset),
    staleTime: 60000, // Historical data rarely changes, cache for 1 minute
    ...options,
  })
}

/**
 * Hook to cancel an expert
 */
export const useCancelExpert = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: cancelExpert,
    onSuccess: () => {
      // Invalidate state query to refetch with updated expert status
      queryClient.invalidateQueries({ queryKey: queryKeys.state })
      queryClient.invalidateQueries({ queryKey: queryKeys.experts })
    },
  })
}

/**
 * Hook to submit answers
 */
export const useSubmitAnswers = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: submitAnswers,
    onSuccess: () => {
      // Invalidate state query to refetch after submission
      queryClient.invalidateQueries({ queryKey: queryKeys.state })
    },
  })
}

/**
 * Hook to submit concern feedback
 */
export const useSubmitConcernFeedback = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: submitConcernFeedback,
    onSuccess: () => {
      // Invalidate state query to refetch after submission
      queryClient.invalidateQueries({ queryKey: queryKeys.state })
    },
  })
}
