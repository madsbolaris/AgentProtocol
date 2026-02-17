import React from 'react'
import { EmptyPanel } from './EmptyPanel'
import { QuestionsPanel } from './QuestionsPanel'
import { ConcernReviewPanel } from './ConcernReviewPanel'
import { ApprovalPanel } from './ApprovalPanel'
import { type Question, type Concern, type ApprovalSummary, type ActionPaneType } from '../../types/workspace'

interface ActionPanelProps {
  type: ActionPaneType
  title: string
  content?: any
  onSubmit?: (data: any) => void
  convergencePercent?: number
  convergenceTarget?: number
  consensusReached?: boolean
}

export function ActionPanel({ type, title, content, onSubmit, convergencePercent, convergenceTarget, consensusReached }: ActionPanelProps) {
  const showConvergence = convergencePercent !== undefined && convergenceTarget !== undefined

  return (
    <aside className="actions-panel">
      <div className="panel-header">
        <h3>{title}</h3>
        {showConvergence && (
          <div className="convergence-badge">
            <span>Convergence:</span>
            <div className="convergence-bar">
              <div
                className="convergence-fill"
                data-converged={consensusReached ? 'true' : 'false'}
                style={{ width: `${convergencePercent}%` }}
              />
            </div>
            <span style={{ fontWeight: 600 }}>{convergencePercent}%</span>
          </div>
        )}
      </div>

      <div className="panel-content">
        {type === 'empty' && (
          <EmptyPanel
            title={content?.title}
            description={content?.description}
            icon={content?.icon}
            message={content?.message}
          />
        )}

        {type === 'questions' && content?.questions && (
          <QuestionsPanel
            questions={content.questions}
            onSubmit={onSubmit || (() => {})}
            statusLabel={content.statusLabel}
            showHeader={content.showHeader}
          />
        )}

        {type === 'concern-review' && content?.concerns && (
          <ConcernReviewPanel
            concerns={content.concerns}
            onSubmit={onSubmit || (() => {})}
          />
        )}

        {type === 'approval' && content?.summary && (
          <ApprovalPanel
            summary={content.summary}
            onSubmit={onSubmit || (() => {})}
          />
        )}
      </div>
    </aside>
  )
}
