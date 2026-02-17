/**
 * Hook to get filtered and sorted experts
 */

import { useMemo } from 'react'
import { useWorkspaceState } from '@/api'
import { useUIStore } from '@/store/useUIStore'
import type { ExpertResult } from '@/types/workspace'

export interface FilteredExpert {
  name: string
  result?: ExpertResult
  index: number
}

export const useFilteredExperts = (): FilteredExpert[] => {
  const { data: state } = useWorkspaceState()
  const filter = useUIStore((s) => s.expertStatusFilter)
  const sortBy = useUIStore((s) => s.expertSortBy)
  const sortOrder = useUIStore((s) => s.expertSortOrder)

  return useMemo(() => {
    if (!state || !state.experts || state.experts.length === 0) return []

    // Map experts to FilteredExpert objects
    let experts: FilteredExpert[] = state.experts.map((name, index) => ({
      name,
      result: state.expert_progress?.[name],
      index,
    }))

    // Apply filter
    if (filter !== 'all') {
      experts = experts.filter((expert) => {
        const status = expert.result?.status || 'pending'
        return status === filter
      })
    }

    // Apply sort
    experts.sort((a, b) => {
      let comparison = 0

      switch (sortBy) {
        case 'index':
          comparison = a.index - b.index
          break

        case 'name':
          comparison = a.name.localeCompare(b.name)
          break

        case 'duration':
          comparison =
            (a.result?.duration_seconds || 0) - (b.result?.duration_seconds || 0)
          break

        case 'cost':
          comparison = (a.result?.accurate_cost || 0) - (b.result?.accurate_cost || 0)
          break

        case 'status': {
          const statusOrder = { complete: 0, running: 1, failed: 2, timeout: 3, cancelled: 4, pending: 5 }
          const aStatus = a.result?.status || 'pending'
          const bStatus = b.result?.status || 'pending'
          comparison = statusOrder[aStatus] - statusOrder[bStatus]
          break
        }
      }

      return sortOrder === 'asc' ? comparison : -comparison
    })

    return experts
  }, [state, filter, sortBy, sortOrder])
}
