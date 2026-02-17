import React, { useState } from 'react'
import { type Question } from '../../types/workspace'

interface QuestionsPanelProps {
  questions: Question[]
  onSubmit: (answers: Record<string, string | string[]>) => void
  statusLabel?: string
  showHeader?: boolean
}

export function QuestionsPanel({ questions, onSubmit, statusLabel, showHeader = true }: QuestionsPanelProps) {
  const [answers, setAnswers] = useState<Record<string, string | string[]>>({})
  const [otherValues, setOtherValues] = useState<Record<string, string>>({})
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [touched, setTouched] = useState<Record<string, boolean>>({})

  const handleTextAnswer = (questionId: string, value: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
    clearError(questionId)
  }

  const handleRadioAnswer = (questionId: string, value: string) => {
    setAnswers(prev => ({ ...prev, [questionId]: value }))
    clearError(questionId)
  }

  const handleCheckboxAnswer = (questionId: string, value: string, checked: boolean) => {
    setAnswers(prev => {
      const current = (prev[questionId] || []) as string[]
      if (checked) {
        return { ...prev, [questionId]: [...current, value] }
      } else {
        return { ...prev, [questionId]: current.filter(v => v !== value) }
      }
    })
    clearError(questionId)
  }

  const handleOtherValue = (questionId: string, value: string) => {
    setOtherValues(prev => ({ ...prev, [questionId]: value }))
    clearError(questionId)
  }

  const clearError = (questionId: string) => {
    if (errors[questionId]) {
      setErrors(prev => {
        const next = { ...prev }
        delete next[questionId]
        return next
      })
    }
  }

  const handleBlur = (questionId: string) => {
    setTouched(prev => ({ ...prev, [questionId]: true }))

    // Validate on blur
    const answer = answers[questionId]
    if (!answer || (typeof answer === 'string' && answer.trim().length === 0) ||
        (Array.isArray(answer) && answer.length === 0)) {
      setErrors(prev => ({ ...prev, [questionId]: 'This answer is required' }))
    } else if (typeof answer === 'string' && answer.trim().length < 10) {
      setErrors(prev => ({ ...prev, [questionId]: 'Please provide a more detailed answer (at least 10 characters)' }))
    }
  }

  const handleSubmit = async () => {
    // Validate all fields
    const newErrors: Record<string, string> = {}
    questions.forEach(q => {
      const questionId = `${q.expert}-${q.question}`
      const answer = answers[questionId]

      if (!answer || (typeof answer === 'string' && answer.trim().length === 0) ||
          (Array.isArray(answer) && answer.length === 0)) {
        newErrors[questionId] = 'This answer is required'
      } else if (q.type === 'text' && typeof answer === 'string' && answer.trim().length < 10) {
        newErrors[questionId] = 'Please provide a more detailed answer (at least 10 characters)'
      }
    })

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      setTouched(
        questions.reduce((acc, q) => {
          acc[`${q.expert}-${q.question}`] = true
          return acc
        }, {} as Record<string, boolean>)
      )
      return
    }

    setIsSubmitting(true)
    try {
      // Merge "other" values into answers
      const finalAnswers = { ...answers }
      Object.keys(otherValues).forEach(qid => {
        if (otherValues[qid].trim()) {
          const answer = finalAnswers[qid]
          if (Array.isArray(answer) && answer.includes('__other__')) {
            finalAnswers[qid] = [...answer.filter(v => v !== '__other__'), otherValues[qid]]
          } else if (answer === '__other__') {
            finalAnswers[qid] = otherValues[qid]
          }
        }
      })
      await onSubmit(finalAnswers)
    } finally {
      setIsSubmitting(false)
    }
  }

  const isQuestionAnswered = (q: Question) => {
    const questionId = `${q.expert}-${q.question}`
    const answer = answers[questionId]

    if (!answer) return false

    if (q.type === 'text' || !q.type) {
      return typeof answer === 'string' && answer.trim().length >= 10
    } else if (q.type === 'radio') {
      return typeof answer === 'string' && answer.length > 0
    } else if (q.type === 'checkbox') {
      return Array.isArray(answer) && answer.length > 0
    }

    return false
  }

  const allQuestionsAnswered = questions.every(q => isQuestionAnswered(q))

  const renderQuestionInput = (q: Question, questionId: string) => {
    const questionType = q.type || 'text'

    // Text input (default)
    if (questionType === 'text') {
      return (
        <div className="question-answer">
          <textarea
            value={(answers[questionId] as string) || ''}
            onChange={(e) => handleTextAnswer(questionId, e.target.value)}
            onBlur={() => handleBlur(questionId)}
            placeholder="Type your answer here..."
            rows={3}
            className={`question-textarea ${touched[questionId] && errors[questionId] ? 'error' : ''}`}
          />
          {touched[questionId] && errors[questionId] && (
            <div className="field-error">{errors[questionId]}</div>
          )}
        </div>
      )
    }

    // Radio buttons (single choice)
    if (questionType === 'radio' && q.options) {
      return (
        <div className="question-answer">
          <div className="question-options">
            {q.options.map(option => {
              // Use option-label structure if description exists, otherwise use simpler question-option
              const hasDescription = option.description && option.description.trim().length > 0
              const className = hasDescription ? 'option-label' : 'question-option'

              return (
                <label key={option.value} className={className}>
                  <input
                    type="radio"
                    name={questionId}
                    value={option.value}
                    checked={answers[questionId] === option.value}
                    onChange={(e) => handleRadioAnswer(questionId, e.target.value)}
                  />
                  {hasDescription ? (
                    <div className="option-text">
                      <strong>{option.label}</strong>
                      <div className="option-description">{option.description}</div>
                    </div>
                  ) : (
                    <span>{option.label}</span>
                  )}
                </label>
              )
            })}
            {q.allowOther && (
              <label className="question-option">
                <input
                  type="radio"
                  name={questionId}
                  value="__other__"
                  checked={answers[questionId] === '__other__'}
                  onChange={(e) => handleRadioAnswer(questionId, e.target.value)}
                />
                <span>Other:</span>
                {answers[questionId] === '__other__' && (
                  <input
                    type="text"
                    className="other-input"
                    value={otherValues[questionId] || ''}
                    onChange={(e) => handleOtherValue(questionId, e.target.value)}
                    placeholder="Please specify..."
                  />
                )}
              </label>
            )}
          </div>
          {touched[questionId] && errors[questionId] && (
            <div className="field-error">{errors[questionId]}</div>
          )}
        </div>
      )
    }

    // Checkboxes (multiple choice)
    if (questionType === 'checkbox' && q.options) {
      const selectedValues = (answers[questionId] as string[]) || []
      return (
        <div className="question-answer">
          <div className="question-options">
            {q.options.map(option => (
              <label key={option.value} className="question-option">
                <input
                  type="checkbox"
                  value={option.value}
                  checked={selectedValues.includes(option.value)}
                  onChange={(e) => handleCheckboxAnswer(questionId, e.target.value, e.target.checked)}
                />
                <span>{option.label}</span>
              </label>
            ))}
            {q.allowOther && (
              <label className="question-option">
                <input
                  type="checkbox"
                  value="__other__"
                  checked={selectedValues.includes('__other__')}
                  onChange={(e) => handleCheckboxAnswer(questionId, '__other__', e.target.checked)}
                />
                <span>Other:</span>
                {selectedValues.includes('__other__') && (
                  <input
                    type="text"
                    className="other-input"
                    value={otherValues[questionId] || ''}
                    onChange={(e) => handleOtherValue(questionId, e.target.value)}
                    placeholder="Please specify..."
                  />
                )}
              </label>
            )}
          </div>
          {touched[questionId] && errors[questionId] && (
            <div className="field-error">{errors[questionId]}</div>
          )}
        </div>
      )
    }

    return null
  }

  return (
    <div className="questions-panel">
      {showHeader && (
        <div className="questions-header">
          {statusLabel && <div className="questions-header-label">{statusLabel}</div>}
          <div className="questions-header-title">
            {questions.length} Question{questions.length !== 1 ? 's' : ''} Need Your Input
          </div>
        </div>
      )}

      {!showHeader && (
        <div className="questions-intro">
          <p>Experts have questions that need your input before proceeding.</p>
        </div>
      )}

      <div className="questions-list">
        {questions.map((q, idx) => {
          const questionId = `${q.expert}-${q.question}`
          return (
            <div key={questionId} className="question-card">
              <div className="question-expert">
                <strong>{q.expert}</strong>
              </div>
              <div className="question-text">{q.question}</div>
              {q.context && (
                <div className="question-context">{q.context}</div>
              )}
              {renderQuestionInput(q, questionId)}
            </div>
          )
        })}
      </div>

      <div className="questions-actions">
        <button
          onClick={handleSubmit}
          disabled={!allQuestionsAnswered || isSubmitting}
          className={`submit-button ${isSubmitting ? 'loading' : ''}`}
        >
          {isSubmitting ? (
            <>
              <span className="spinner"></span>
              Submitting...
            </>
          ) : (
            `Submit Answers (${questions.filter(q => isQuestionAnswered(q)).length}/${questions.length})`
          )}
        </button>
      </div>
    </div>
  )
}
