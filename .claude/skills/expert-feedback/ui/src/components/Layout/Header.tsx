import React from 'react'
import { useUIStore } from '../../store/useUIStore'
import { PhaseSelector } from '../PhaseSelector/PhaseSelector'
import { ProjectSelector } from '../ProjectSelector/ProjectSelector'
import { type ProjectConfig } from '../../config/projects'

export function Header() {
  const darkMode = useUIStore((s) => s.darkMode)
  const toggleDarkMode = useUIStore((s) => s.toggleDarkMode)
  const projectName = useUIStore((s) => s.projectName)
  const projectBadgeCount = useUIStore((s) => s.projectBadgeCount)
  const setProjectName = useUIStore((s) => s.setProjectName)
  const setProjectBadgeCount = useUIStore((s) => s.setProjectBadgeCount)
  const iterationMetadata = useUIStore((s) => s.iterationMetadata)

  const formatTokens = (tokens: number): string => {
    if (tokens >= 1000) {
      return `${(tokens / 1000).toFixed(0)}K`
    }
    return `${tokens}`
  }

  const handleProjectSelect = (project: ProjectConfig) => {
    setProjectName(project.name)
    setProjectBadgeCount(project.badgeCount || 0)
  }

  return (
    <header className="header">
      <div className="header-left" style={{ position: 'relative' }}>
        <ProjectSelector
          currentProject={projectName}
          currentBadgeCount={projectBadgeCount}
          onProjectSelect={handleProjectSelect}
        />
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
