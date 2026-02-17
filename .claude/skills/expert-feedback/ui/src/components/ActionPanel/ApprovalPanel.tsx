import React, { useState } from 'react'
import { type ApprovalSummary } from '../../types/workspace'

interface ApprovalPanelProps {
  summary: ApprovalSummary
  onSubmit: (decision: 'approve' | 'revise', feedback?: string) => void
}

export function ApprovalPanel({ summary, onSubmit }: ApprovalPanelProps) {
  const [decision, setDecision] = useState<'approve' | 'revise' | null>(null)
  const [feedback, setFeedback] = useState('')

  const handleSubmit = () => {
    if (decision) {
      onSubmit(decision, feedback || undefined)
    }
  }

  return (
    <div className="approval-panel">
      <div className="approval-summary">
        <h4>REVIEW SUMMARY</h4>
        <table className="summary-table">
          <tbody>
            <tr>
              <td>Iterations Completed</td>
              <td><strong>{summary.iterations}</strong></td>
            </tr>
            <tr>
              <td>Concerns Addressed</td>
              <td><strong>{summary.concernsAddressed}</strong></td>
            </tr>
            <tr>
              <td>Total Duration</td>
              <td><strong>{summary.totalTime}</strong></td>
            </tr>
            {summary.tokensUsed && (
              <tr>
                <td>Tokens Used</td>
                <td><strong>{summary.tokensUsed.toLocaleString()}</strong></td>
              </tr>
            )}
            {summary.cost !== undefined && (
              <tr>
                <td>Estimated Cost</td>
                <td><strong>${summary.cost.toFixed(2)}</strong></td>
              </tr>
            )}
            {summary.expertCount && (
              <tr>
                <td>Experts Consulted</td>
                <td><strong>{summary.expertCount}</strong></td>
              </tr>
            )}
            {summary.convergencePercent !== undefined && (
              <tr>
                <td>Expert Convergence</td>
                <td><strong>{summary.convergencePercent}%</strong></td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="approval-decision">
        <h4>DECISION</h4>

        <label className="decision-option">
          <input
            type="radio"
            name="decision"
            checked={decision === 'approve'}
            onChange={() => setDecision('approve')}
          />
          <div className="decision-content">
            <div className="decision-title">
              <span className="decision-icon">✓</span>
              <strong>Approve Artifact</strong>
            </div>
            <p className="decision-description">
              Accept the artifact as final and complete the review process.
            </p>
          </div>
        </label>

        <label className="decision-option">
          <input
            type="radio"
            name="decision"
            checked={decision === 'revise'}
            onChange={() => setDecision('revise')}
          />
          <div className="decision-content">
            <div className="decision-title">
              <span className="decision-icon">↻</span>
              <strong>Request Revisions</strong>
            </div>
            <p className="decision-description">
              Request changes for another iteration.
            </p>
          </div>
        </label>

        {decision === 'revise' && (
          <div className="revision-feedback">
            <label>
              <strong>Describe the changes you'd like to see:</strong>
              <textarea
                value={feedback}
                onChange={(e) => setFeedback(e.target.value)}
                placeholder="Enter your feedback here..."
                rows={6}
                className="feedback-textarea"
              />
            </label>
          </div>
        )}
      </div>

      <div className="approval-actions">
        <button
          onClick={handleSubmit}
          disabled={!decision || (decision === 'revise' && !feedback.trim())}
          className="submit-button"
        >
          {decision === 'approve' ? 'Approve & Complete' : 'Submit Revisions'}
        </button>
      </div>
    </div>
  )
}
