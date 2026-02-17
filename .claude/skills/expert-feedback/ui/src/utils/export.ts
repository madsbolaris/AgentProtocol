/**
 * Export utilities for session data
 */

import type { WorkspaceState } from '@/types/workspace'
import { formatDuration, formatCost } from './formatting'

/**
 * Download a file to the user's computer
 */
const downloadFile = (content: string, filename: string, mimeType: string): void => {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<boolean> => {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch (error) {
    console.error('Failed to copy to clipboard:', error)
    return false
  }
}

/**
 * Export session data as JSON
 */
export const exportToJSON = (state: WorkspaceState, pretty: boolean = true): void => {
  const json = pretty ? JSON.stringify(state, null, 2) : JSON.stringify(state)
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `expert-feedback-session-${timestamp}.json`
  downloadFile(json, filename, 'application/json')
}

/**
 * Export session data as CSV
 */
export const exportToCSV = (state: WorkspaceState): void => {
  const headers = [
    'Expert',
    'Status',
    'Duration (s)',
    'Duration (formatted)',
    'Input Tokens',
    'Output Tokens',
    'Cache Created',
    'Cache Read',
    'Total Tokens',
    'Cost (USD)',
    'Error',
  ]

  const rows = (state.experts || []).map((expert) => {
    const result = state.expert_progress[expert]

    return [
      expert,
      result?.status || 'pending',
      result?.duration_seconds || 0,
      result ? formatDuration(result.duration_seconds) : '',
      result?.input_tokens || 0,
      result?.output_tokens || 0,
      result?.cache_creation_tokens || 0,
      result?.cache_read_tokens || 0,
      result?.tokens_used || 0,
      result ? formatCost(result.accurate_cost, 4) : '0.0000',
      result?.error ? `"${result.error.replace(/"/g, '""')}"` : '',
    ]
  })

  // Add summary row
  const summaryRow = [
    'TOTAL',
    '',
    state.total_duration_seconds,
    formatDuration(state.total_duration_seconds),
    state.total_input_tokens,
    state.total_output_tokens,
    state.total_cache_creation_tokens,
    state.total_cache_read_tokens,
    state.total_tokens,
    formatCost(state.total_cost, 4),
    '',
  ]

  const csv = [headers, ...rows, [], summaryRow].map((row) => row.join(',')).join('\n')

  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `expert-feedback-session-${timestamp}.csv`
  downloadFile(csv, filename, 'text/csv')
}

/**
 * Export session summary as text
 */
export const exportToText = (state: WorkspaceState): void => {
  const lines: string[] = []

  lines.push('=' .repeat(60))
  lines.push('EXPERT FEEDBACK SESSION SUMMARY')
  lines.push('='.repeat(60))
  lines.push('')

  // Session info
  lines.push('SESSION INFORMATION')
  lines.push('-'.repeat(60))
  lines.push(`Workspace: ${state.workspace_path}`)
  lines.push(`Topic: ${state.topic || 'N/A'}`)
  lines.push(`Phase: ${state.phase || 'N/A'}`)
  lines.push(`Iteration: ${state.current_iteration}/${state.max_iterations}`)
  lines.push(`Convergence: ${state.convergence_percent}%`)
  lines.push(`Start Time: ${state.start_time || 'N/A'}`)
  lines.push(`End Time: ${state.end_time || 'N/A'}`)
  lines.push('')

  // Overall metrics
  lines.push('OVERALL METRICS')
  lines.push('-'.repeat(60))
  lines.push(`Total Duration: ${formatDuration(state.total_duration_seconds || 0)}`)
  lines.push(`Total Cost: $${formatCost(state.total_cost || 0, 4)}`)
  lines.push(`Total Tokens: ${(state.total_tokens || 0).toLocaleString()}`)
  lines.push(`  - Input: ${(state.total_input_tokens || 0).toLocaleString()}`)
  lines.push(`  - Output: ${(state.total_output_tokens || 0).toLocaleString()}`)
  if (state.cache_enabled) {
    lines.push(`  - Cache Created: ${(state.total_cache_creation_tokens || 0).toLocaleString()}`)
    lines.push(`  - Cache Read: ${(state.total_cache_read_tokens || 0).toLocaleString()}`)
    const cacheRead = state.total_cache_read_tokens || 0
    const inputTokens = state.total_input_tokens || 0
    const hitRate =
      ((cacheRead / (inputTokens + cacheRead)) * 100).toFixed(1)
    lines.push(`  - Cache Hit Rate: ${hitRate}%`)
  }
  lines.push('')

  // Expert results
  lines.push('EXPERT RESULTS')
  lines.push('-'.repeat(60))

  ;(state.experts || []).forEach((expert) => {
    const result = state.expert_progress[expert]
    lines.push(`\n${expert}:`)

    if (!result) {
      lines.push('  Status: Pending')
    } else {
      lines.push(`  Status: ${result.status}`)
      lines.push(`  Duration: ${formatDuration(result.duration_seconds)}`)
      lines.push(`  Tokens: ${result.tokens_used.toLocaleString()}`)
      lines.push(`  Cost: $${formatCost(result.accurate_cost, 4)}`)

      if (result.cache_read_tokens > 0) {
        lines.push(`  Cache: ${result.cache_read_tokens.toLocaleString()} tokens read`)
      }

      if (result.error) {
        lines.push(`  Error: ${result.error}`)
      }
    }
  })

  lines.push('')
  lines.push('='.repeat(60))
  lines.push(`Generated: ${new Date().toISOString()}`)
  lines.push('='.repeat(60))

  const text = lines.join('\n')
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
  const filename = `expert-feedback-summary-${timestamp}.txt`
  downloadFile(text, filename, 'text/plain')
}

/**
 * Export filtered experts (for use with filtered view)
 */
export const exportFilteredToCSV = (
  state: WorkspaceState,
  expertNames: string[]
): void => {
  // Create a filtered state with only selected experts
  const filteredState: WorkspaceState = {
    ...state,
    experts: expertNames,
    expert_progress: Object.fromEntries(
      expertNames
        .filter((name) => state.expert_progress[name])
        .map((name) => [name, state.expert_progress[name]])
    ),
  }

  // Recalculate totals
  const results = Object.values(filteredState.expert_progress)
  filteredState.total_duration_seconds = results.reduce(
    (sum, r) => sum + (r.duration_seconds || 0),
    0
  )
  filteredState.total_cost = results.reduce((sum, r) => sum + (r.accurate_cost || 0), 0)
  filteredState.total_tokens = results.reduce((sum, r) => sum + (r.tokens_used || 0), 0)
  filteredState.total_input_tokens = results.reduce(
    (sum, r) => sum + (r.input_tokens || 0),
    0
  )
  filteredState.total_output_tokens = results.reduce(
    (sum, r) => sum + (r.output_tokens || 0),
    0
  )
  filteredState.total_cache_creation_tokens = results.reduce(
    (sum, r) => sum + (r.cache_creation_tokens || 0),
    0
  )
  filteredState.total_cache_read_tokens = results.reduce(
    (sum, r) => sum + (r.cache_read_tokens || 0),
    0
  )

  exportToCSV(filteredState)
}
