/**
 * Hook to get pre-calculated cache metrics
 */

import { useMemo } from 'react'
import { useWorkspaceState } from '@/api'
import { getCacheMetrics } from '@/utils/calculations'
import type { CacheMetrics } from '@/utils/calculations'

export const useCacheMetrics = (): CacheMetrics | null => {
  const { data: state } = useWorkspaceState()

  return useMemo(() => {
    if (!state?.cache_enabled) return null
    if (state.total_cache_creation_tokens === 0 && state.total_cache_read_tokens === 0) {
      return null
    }
    return getCacheMetrics(state)
  }, [state])
}
