/**
 * Color utility functions for consistent styling
 */

import type { Phase, ExpertStatus } from '@/types/workspace'

/**
 * Phase color classes
 */
export const getPhaseColor = (phase: Phase): string => {
  switch (phase) {
    case 'init':
      return 'text-gray-600'
    case 'spawning_experts':
      return 'text-blue-600'
    case 'consolidating':
      return 'text-purple-600'
    case 'questions':
      return 'text-orange-600'
    case 'generating':
      return 'text-indigo-600'
    case 'reviewing':
      return 'text-yellow-600'
    case 'complete':
      return 'text-green-600'
    case 'error':
      return 'text-red-600'
    default:
      return 'text-gray-600'
  }
}

/**
 * Expert status styling
 */
export interface StatusStyle {
  icon: string
  color: string
  bgColor: string
  borderColor: string
}

export const getStatusStyle = (status: ExpertStatus): StatusStyle => {
  switch (status) {
    case 'complete':
      return {
        icon: '✅',
        color: 'text-green-600',
        bgColor: 'bg-green-50',
        borderColor: 'border-green-200',
      }
    case 'running':
      return {
        icon: '🤖',
        color: 'text-blue-600',
        bgColor: 'bg-blue-50',
        borderColor: 'border-blue-200',
      }
    case 'failed':
      return {
        icon: '❌',
        color: 'text-red-600',
        bgColor: 'bg-red-50',
        borderColor: 'border-red-200',
      }
    case 'timeout':
      return {
        icon: '⏱️',
        color: 'text-orange-600',
        bgColor: 'bg-orange-50',
        borderColor: 'border-orange-200',
      }
    case 'cancelled':
      return {
        icon: '🚫',
        color: 'text-gray-600',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
      }
    default:
      return {
        icon: '⏳',
        color: 'text-gray-400',
        bgColor: 'bg-gray-50',
        borderColor: 'border-gray-200',
      }
  }
}

/**
 * Convergence color (based on percentage)
 */
export const getConvergenceColor = (percentage: number, target: number): string => {
  if (percentage >= target) return 'text-green-600'
  if (percentage >= target * 0.7) return 'text-yellow-600'
  return 'text-orange-600'
}

/**
 * Cache hit rate color
 */
export const getCacheHitRateColor = (hitRate: number): string => {
  if (hitRate >= 80) return 'text-green-600'
  if (hitRate >= 60) return 'text-yellow-600'
  if (hitRate >= 40) return 'text-orange-600'
  return 'text-red-600'
}
