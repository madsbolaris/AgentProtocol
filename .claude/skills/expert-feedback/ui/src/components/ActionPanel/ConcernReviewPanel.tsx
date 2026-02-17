import React, { useState } from 'react'
import { type Concern } from '../../types/workspace'

interface ConcernReviewPanelProps {
  concerns: Concern[]
  onSubmit: (feedback: Record<string, 'agree' | 'disagree'>) => void
}

export function ConcernReviewPanel({ concerns, onSubmit }: ConcernReviewPanelProps) {
  const [feedback, setFeedback] = useState<Record<string, 'agree' | 'disagree'>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleFeedback = (concernId: string, decision: 'agree' | 'disagree') => {
    setFeedback(prev => ({ ...prev, [concernId]: decision }))
  }

  const handleSubmit = async () => {
    setIsSubmitting(true)
    try {
      await onSubmit(feedback)
    } finally {
      setIsSubmitting(false)
    }
  }

  const allConcernsReviewed = concerns.every(c => feedback[c.id])
  const agreedCount = Object.values(feedback).filter(f => f === 'agree').length

  return (
    <div className="concern-review-panel">
      <div className="concern-review-intro">
        <p>Review concerns raised by experts and decide which to address.</p>
      </div>

      <div className="concerns-list">
        {concerns.map(concern => (
          <div key={concern.id} className="concern-card">
            <div className="concern-expert">
              <strong>{concern.expert}</strong>
            </div>
            <div className="concern-text">{concern.text}</div>
            {concern.context && (
              <div className="concern-context">{concern.context}</div>
            )}

            <div className="concern-options">
              <label className="concern-option">
                <input
                  type="radio"
                  name={concern.id}
                  checked={feedback[concern.id] === 'agree'}
                  onChange={() => handleFeedback(concern.id, 'agree')}
                />
                <span className="concern-option-label">
                  <span className="concern-option-icon">✓</span>
                  <span>Agree - Address this concern</span>
                </span>
              </label>

              <label className="concern-option">
                <input
                  type="radio"
                  name={concern.id}
                  checked={feedback[concern.id] === 'disagree'}
                  onChange={() => handleFeedback(concern.id, 'disagree')}
                />
                <span className="concern-option-label">
                  <span className="concern-option-icon">✗</span>
                  <span>Disagree - Do not address</span>
                </span>
              </label>
            </div>
          </div>
        ))}
      </div>

      <div className="concern-review-summary">
        <div className="summary-stats">
          <div className="summary-stat">
            <strong>{concerns.length}</strong> Total Concerns
          </div>
          <div className="summary-stat">
            <strong>{agreedCount}</strong> To Address
          </div>
        </div>
      </div>

      <div className="concern-review-actions">
        <button
          onClick={handleSubmit}
          disabled={!allConcernsReviewed || isSubmitting}
          className={`submit-button ${isSubmitting ? 'loading' : ''}`}
        >
          {isSubmitting ? (
            <>
              <span className="spinner"></span>
              Submitting...
            </>
          ) : (
            `Submit Review (${Object.keys(feedback).length}/${concerns.length})`
          )}
        </button>
      </div>
    </div>
  )
}
