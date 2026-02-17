/**
 * Hook to get pre-calculated expert summary statistics
 */

import { useMemo } from 'react'
import { useWorkspaceState } from '@/api'
import { getExpertProgressSummary } from '@/utils/calculations'
import type { ExpertProgressSummary } from '@/utils/calculations'

export const useExpertSummary = (): ExpertProgressSummary | null => {
  const { data: state } = useWorkspaceState()

  return useMemo(() => {
    if (!state) return null
    return getExpertProgressSummary(state)
  }, [state])
}
