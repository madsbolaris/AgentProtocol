import React from 'react'
import { useUIStore } from '../../store/useUIStore'

export function ConvergenceBadge() {
  const convergencePercent = useUIStore((s) => s.convergencePercent)
  const convergenceThreshold = useUIStore((s) => s.convergenceThreshold)

  const isConverged = convergencePercent >= convergenceThreshold

  return (
    <div className="convergence-badge">
      <div className="convergence-label">
        <span>Expert Convergence:</span>
        <span className={`convergence-value ${isConverged ? 'converged' : 'not-converged'}`}>
          {convergencePercent}% <span className="threshold">(threshold: {convergenceThreshold}%)</span>
        </span>
      </div>
      <div className="convergence-bar">
        <div
          className="convergence-fill"
          style={{ width: `${convergencePercent}%` }}
          data-converged={isConverged}
        />
      </div>
    </div>
  )
}
