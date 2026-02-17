/**
 * Calculation utility functions
 */

import type { WorkspaceState, CacheMetrics, ExpertProgressSummary } from '@/types/workspace'

/**
 * Calculate cache hit rate
 */
export const calculateCacheHitRate = (state: WorkspaceState): number => {
  const totalInput = (state.total_input_tokens || 0) + (state.total_cache_read_tokens || 0)

  if (totalInput === 0) return 0

  return ((state.total_cache_read_tokens || 0) / totalInput) * 100
}

/**
 * Calculate cache savings in USD
 * Formula: (cache_read_tokens / 1M) * $2.70
 * $2.70 = difference between full price ($3.00/MTok) and cache read price ($0.30/MTok)
 */
export const calculateCacheSavings = (state: WorkspaceState): number => {
  return ((state.total_cache_read_tokens || 0) / 1_000_000) * 2.7
}

/**
 * Get complete cache metrics
 */
export const getCacheMetrics = (state: WorkspaceState): CacheMetrics => {
  return {
    hitRate: calculateCacheHitRate(state),
    tokensCreated: state.total_cache_creation_tokens || 0,
    tokensRead: state.total_cache_read_tokens || 0,
    savings: calculateCacheSavings(state),
  }
}

/**
 * Get expert progress summary
 */
export const getExpertProgressSummary = (state: WorkspaceState): ExpertProgressSummary => {
  const results = state.expert_progress ? Object.values(state.expert_progress) : []
  const total = state.experts?.length || 0

  return {
    total,
    completed: results.filter((r) => r.status === 'complete').length,
    running: results.filter((r) => r.status === 'running').length,
    failed: results.filter((r) => r.status === 'failed').length,
    pending: total - results.length,
  }
}

/**
 * Calculate cache hit rate for a single expert
 */
export const calculateExpertCacheHitRate = (
  inputTokens: number,
  cacheReadTokens: number
): number => {
  const total = inputTokens + cacheReadTokens

  if (total === 0) return 0

  return (cacheReadTokens / total) * 100
}

/**
 * Check if caching is active and has data
 */
export const isCachingActive = (state: WorkspaceState): boolean => {
  return (
    (state.cache_enabled || false) &&
    ((state.total_cache_creation_tokens || 0) > 0 || (state.total_cache_read_tokens || 0) > 0)
  )
}

/**
 * Calculate average cost per expert
 */
export const calculateAverageCostPerExpert = (state: WorkspaceState): number => {
  if (!state.expert_progress) return 0

  const completedExperts = Object.values(state.expert_progress).filter(
    (r) => r.status === 'complete'
  ).length

  if (completedExperts === 0) return 0

  return (state.total_cost || 0) / completedExperts
}

/**
 * Calculate average duration per expert (in seconds)
 */
export const calculateAverageDurationPerExpert = (state: WorkspaceState): number => {
  if (!state.expert_progress) return 0

  const completedExperts = Object.values(state.expert_progress).filter(
    (r) => r.status === 'complete'
  )

  if (completedExperts.length === 0) return 0

  const totalDuration = completedExperts.reduce((sum, r) => sum + r.duration_seconds, 0)

  return Math.floor(totalDuration / completedExperts.length)
}
