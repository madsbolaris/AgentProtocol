/**
 * Hook to get overall session progress information
 */

import { useMemo } from 'react'
import { useWorkspaceState } from '@/api'
import { getExpertProgressSummary } from '@/utils/calculations'
import type { Phase } from '@/types/workspace'
import type { ExpertProgressSummary } from '@/utils/calculations'

export interface SessionProgress {
  phase: Phase
  iteration: string
  iterationCurrent: number
  iterationMax: number
  convergence: number
  isComplete: boolean
  hasErrors: boolean
  isRunning: boolean
  expertProgress: ExpertProgressSummary
  totalDuration: number
  totalCost: number
  totalTokens: number
}

export const useSessionProgress = (): SessionProgress | null => {
  const { data: state } = useWorkspaceState()

  return useMemo(() => {
    if (!state) return null

    const expertProgress = getExpertProgressSummary(state)
    const phase = state.phase || 'idle'

    return {
      phase,
      iteration: `${state.current_iteration || 0}/${state.max_iterations || 0}`,
      iterationCurrent: state.current_iteration || 0,
      iterationMax: state.max_iterations || 0,
      convergence: state.convergence_percent || 0,
      isComplete: phase === 'complete',
      hasErrors: phase === 'error',
      isRunning: phase === 'spawning_experts' || phase === 'consolidating',
      expertProgress,
      totalDuration: state.total_duration_seconds || 0,
      totalCost: state.total_cost || 0,
      totalTokens: state.total_tokens || 0,
    }
  }, [state])
}
