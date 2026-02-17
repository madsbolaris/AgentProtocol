import React from 'react'
import { useUIStore } from '../../store/useUIStore'
import { PhaseSelector } from '../PhaseSelector/PhaseSelector'

export function Header() {
  const darkMode = useUIStore((s) => s.darkMode)
  const toggleDarkMode = useUIStore((s) => s.toggleDarkMode)
  const projectName = useUIStore((s) => s.projectName)
  const projectBadgeCount = useUIStore((s) => s.projectBadgeCount)
  const iterationMetadata = useUIStore((s) => s.iterationMetadata)

  const formatTokens = (tokens: number): string => {
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(0)}K`
    }
    return `${tokens}`
  }

  return (
    <header className="header">
      <div className="header-left">
        <h1>{projectName}</h1>
        {projectBadgeCount > 0 && (
          <span className="project-badge">{projectBadgeCount}</span>
        )}
        <PhaseSelector />
      </div>

      <div className="header-center">
        <span className="header-stat">{formatTokens(iterationMetadata.tokens)} tokens</span>
        <span className="header-stat-separator">•</span>
        <span className="header-stat">${iterationMetadata.cost.toFixed(2)}</span>
        <span className="header-stat-separator">•</span>
        <span className="header-stat">{iterationMetadata.duration}</span>
      </div>

      <div className="header-actions">
        <button
          className="theme-toggle"
          onClick={toggleDarkMode}
          aria-label="Toggle dark mode"
        >
          {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
        </button>
      </div>
    </header>
  )
}
