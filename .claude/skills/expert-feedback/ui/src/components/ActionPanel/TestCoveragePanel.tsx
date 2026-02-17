import React from 'react'
import { type TestCoverageContent } from '../../types/workspace'

interface Props {
  content: TestCoverageContent
}

export function TestCoveragePanel({ content }: Props) {
  const progressPercent = (content.currentCoverage / content.targetCoverage) * 100

  return (
    <div className="test-coverage-panel">
      <div className="coverage-status">
        <span className="status-badge">{content.status}</span>
      </div>

      <div className="coverage-display">
        <div className="coverage-number">{content.currentCoverage}%</div>
        <div className="coverage-label">Current Coverage</div>
      </div>

      <div className="coverage-bar">
        <div
          className="coverage-fill"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="coverage-target">
        Target: {content.targetCoverage}% • Gap: {content.gap}%
      </div>

      {content.testsWritten !== undefined && (
        <div className="test-metrics">
          <div className="metric">
            <div className="metric-label">Tests Written</div>
            <div className="metric-value">{content.testsWritten}</div>
          </div>
          {content.coverageGain !== undefined && (
            <div className="metric">
              <div className="metric-label">Coverage Gain</div>
              <div className="metric-value">+{content.coverageGain}%</div>
            </div>
          )}
        </div>
      )}

      {content.priorityAreas && content.priorityAreas.length > 0 && (
        <div className="priority-areas">
          <div className="priority-label">Priority Areas</div>
          <div className="priority-list">
            {content.priorityAreas.map((area, i) => (
              <span key={i} className="priority-badge">{area}</span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
