/**
 * Types for workspace state and expert results.
 * These types mirror the Python WorkspaceState dataclass.
 */

export type ExpertStatus = 'pending' | 'running' | 'complete' | 'failed' | 'timeout' | 'cancelled'

export type Phase =
  | 'idle'
  | 'init'
  | 'spawning_experts'
  | 'consolidating'
  | 'questions'
  | 'generating'
  | 'reviewing'
  | 'complete'
  | 'error'

export interface ExpertResult {
  expert: string
  status: ExpertStatus
  duration_seconds: number
  tokens_used: number
  input_tokens: number
  output_tokens: number
  cache_creation_tokens: number
  cache_read_tokens: number
  accurate_cost: number
  session_id: string
  output_file: string | null
  error: string | null
}

export interface WorkspaceState {
  // Phase metadata - phase is optional during initial loading
  phase?: Phase
  current_iteration: number
  max_iterations: number

  // Session metadata
  session_start: string | null
  session_end: string | null
  duration_seconds: number

  // Topic
  topic: string

  // Expert tracking
  experts: string[]
  expert_progress: Record<string, ExpertResult>

  // Convergence
  convergence_percent: number
  convergence_target: number
  consensus_reached: boolean

  // Token usage & costs
  total_tokens: number
  total_cost: number
  total_input_tokens: number
  total_output_tokens: number

  // Phase 1.1: Cache metrics
  total_cache_creation_tokens: number
  total_cache_read_tokens: number
  cache_enabled: boolean

  // Recommendations
  recommendations: unknown[] // To be refined later

  // Files
  workspace_path: string
  start_time: string | null
  complete_time: string | null

  // Artifact review (optional)
  artifact_review: unknown | null
  consolidated_concerns: unknown | null
  concerns_feedback: unknown | null

  // Questions (optional)
  questions: {
    questions: Question[]
  } | null
}

export interface QuestionOption {
  value: string
  label: string
}

export interface Question {
  question: string
  context: string
  expert: string
  type?: 'text' | 'radio' | 'checkbox'  // Default to 'text' for backwards compatibility
  options?: QuestionOption[]  // For radio/checkbox questions
  allowOther?: boolean  // Whether to show "Other" option
}

/**
 * Derived metrics for display
 */
export interface CacheMetrics {
  hitRate: number // Percentage (0-100)
  tokensCreated: number
  tokensRead: number
  savings: number // USD
}

/**
 * Expert progress summary for display
 */
export interface ExpertProgressSummary {
  total: number
  completed: number
  running: number
  failed: number
  pending: number
}

/**
 * UI Phase types for the conversational interface
 */
export type UIPhase =
  | 'phase-01' | 'phase-02' | 'phase-03'
  | 'phase-04' | 'phase-05' | 'phase-06'
  | 'phase-07' | 'phase-08' | 'phase-09'
  | 'phase-10' | 'phase-11' | 'phase-12'
  | 'phase-13'

export type ViewType = 'loading' | 'conversation' | 'document' | 'concern-review'
export type ActionPaneType =
  | 'empty'
  | 'questions'
  | 'concern-review'
  | 'approval'
  | 'implementation-progress'
  | 'implementation-questions'
  | 'implementation-complete'
  | 'test-coverage-status'
  | 'test-coverage-progress'
  | 'test-coverage-complete'

/**
 * Message types for conversation view
 */
export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: number
  metadata?: {
    toolCalls?: ToolCall[]
    thinking?: string
    citations?: Citation[]
  }
}

export interface ToolCall {
  id: string
  name: string
  input: unknown
  output?: unknown
}

export interface Citation {
  id: string
  source: string
  text: string
}

/**
 * Agent definition with ID and display name
 */
export interface Agent {
  id: string // lowercase-with-hyphens (e.g., "typescript-expert")
  displayName: string // Capitalized with spaces (e.g., "TypeScript Expert")
  group: 'experts' | 'consolidator' | 'artifact-generators'
}

/**
 * Agent status for UI display
 */
export interface AgentStatus {
  status: 'completed' | 'running' | 'pending' | 'failed' | 'converged' | 'disabled' | 'waiting'
  hasConcerns?: boolean
  hasNewContent?: boolean
}

/**
 * Phase configuration for UI rendering
 */
export interface PhaseConfig {
  name: string
  description: string
  agentStatuses: Record<string, AgentStatus>
  detailView: {
    type: ViewType
    title: string
    content?: string
  }
  actionPane: {
    type: ActionPaneType
    title: string
    content?: unknown
  }
}

/**
 * Implementation progress content for action pane
 */
export interface ImplementationProgressContent {
  status: string
  elapsed: string
  filesModified: number
  totalFiles: number
  linesAdded: number
  linesRemoved: number
  currentTask: string
  deferredQuestions: number
}

/**
 * Test coverage content for action pane
 */
export interface TestCoverageContent {
  status: string
  currentCoverage: number
  targetCoverage: number
  gap: number
  filesAnalyzed?: number
  totalFiles?: number
  testsWritten?: number
  coverageGain?: number
  priorityAreas?: string[]
}

/**
 * Concern types
 */
export interface Concern {
  id: string
  expert: string
  text: string
  context?: string
}

/**
 * Approval summary types
 */
export interface ApprovalSummary {
  iterations: number
  concernsAddressed: number
  totalTime: string
  tokensUsed?: number
  cost?: number
  expertCount?: number
  convergencePercent?: number
}

/**
 * Implementation progress content types
 */