import React from 'react'
import { useUIStore } from '../../store/useUIStore'
import { phaseConfigs } from '../../config/phases'

interface DocumentViewProps {
  title: string
  content: string
  showDiff?: boolean
}

export function DocumentView({ title, content, showDiff = false }: DocumentViewProps) {
  const iterationMetadata = useUIStore((s) => s.iterationMetadata)
  const selectedAgent = useUIStore((s) => s.selectedAgent)
  const currentPhase = useUIStore((s) => s.currentPhase)

  // Check if agent is running (for loading state)
  const phaseConfig = phaseConfigs[currentPhase]
  const agentStatus = selectedAgent && phaseConfig?.agentStatuses?.[selectedAgent]
  const isLoading = agentStatus?.status === 'running' && !content

  // Agent-specific loading messages
  const getLoadingMessage = () => {
    switch (selectedAgent) {
      case 'synthesis-agent':
        return {
          title: 'Synthesizing expert feedback...',
          description: 'synthesis-agent is consolidating recommendations and calculating convergence'
        }
      case 'artifact-generator':
        return {
          title: 'Generating artifact...',
          description: 'artifact-generator is creating deliverables from expert feedback'
        }
      default:
        return {
          title: 'Analyzing simple-calculator codebase...',
          description: `${selectedAgent} is reviewing the code for production readiness`
        }
    }
  }

  const loadingMessage = getLoadingMessage()

  const formatTokens = (tokens: number) => {
    if (tokens >= 1000) {
      return `${Math.floor(tokens / 1000)}K`
    }
    return tokens.toString()
  }

  return (
    <div className="document-view active">
      <div className="document-header">
        <div className="document-title-group">
          <h2>{title}</h2>
          <div className="iteration-metadata">
            <span className="metadata-item">{formatTokens(iterationMetadata.tokens)} tokens</span>
            <span className="metadata-separator">•</span>
            <span className="metadata-item">${iterationMetadata.cost.toFixed(2)}</span>
            <span className="metadata-separator">•</span>
            <span className="metadata-item">{iterationMetadata.duration}</span>
          </div>
        </div>
        {showDiff && (
          <button className="view-diff-button" title="View diff">
            📊 View Diff
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="iteration-content">
          <div className="loading-state">
            <div className="loading-spinner">
              <i className="fa-solid fa-circle-notch fa-spin"></i>
            </div>
            <h3 className="loading-title">{loadingMessage.title}</h3>
            <p className="loading-description">{loadingMessage.description}</p>

            <div className="loading-skeleton">
              <div className="skeleton-line w-80"></div>
              <div className="skeleton-line w-100"></div>
              <div className="skeleton-line w-90"></div>
              <div className="skeleton-line w-70"></div>
            </div>
          </div>
        </div>
      ) : content ? (
        <div className="document-content">
          <pre className="document-text">{content}</pre>
        </div>
      ) : (
        <div className="document-content">
          <div className="empty-state">
            <p>No document content available yet.</p>
          </div>
        </div>
      )}
    </div>
  )
}
