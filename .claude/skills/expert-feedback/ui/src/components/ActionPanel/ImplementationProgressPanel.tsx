import React from 'react'
import { type ImplementationProgressContent } from '../../types/workspace'

interface Props {
  content: ImplementationProgressContent
}

export function ImplementationProgressPanel({ content }: Props) {
  const progressPercent = (content.filesModified / content.totalFiles) * 100

  return (
    <div className="implementation-progress-panel">
      <div className="progress-status">
        <span className="status-badge">{content.status}</span>
        <span className="elapsed-time">{content.elapsed}</span>
      </div>

      <div className="progress-bar">
        <div
          className="progress-fill"
          style={{ width: `${progressPercent}%` }}
        />
        <span className="progress-label">
          {content.filesModified} / {content.totalFiles} files
        </span>
      </div>

      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Lines Added</div>
          <div className="metric-value">{content.linesAdded.toLocaleString()}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Lines Removed</div>
          <div className="metric-value">{content.linesRemoved.toLocaleString()}</div>
        </div>
      </div>

      <div className="current-task">
        <div className="task-label">Current Task</div>
        <div className="task-text">{content.currentTask}</div>
      </div>

      {content.deferredQuestions > 0 && (
        <div className="deferred-questions">
          <span className="question-icon">❓</span>
          {content.deferredQuestions} question(s) deferred
        </div>
      )}
    </div>
  )
}
