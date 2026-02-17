import React, { useState } from 'react'
import { projects, type ProjectConfig } from '../../config/projects'

interface ProjectSelectorProps {
  currentProject: string
  currentBadgeCount: number
  onProjectSelect: (project: ProjectConfig) => void
}

export function ProjectSelector({ currentProject, currentBadgeCount, onProjectSelect }: ProjectSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)

  const handleProjectSelect = (project: ProjectConfig) => {
    onProjectSelect(project)
    setIsOpen(false)
  }

  return (
    <>
      <div
        className="project-title-dropdown"
        onClick={() => setIsOpen(!isOpen)}
        style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
      >
        <h1>{currentProject}</h1>
        {currentBadgeCount > 0 && (
          <span className="project-badge">{currentBadgeCount}</span>
        )}
        <svg
          width="16"
          height="16"
          viewBox="0 0 24 24"
          fill="currentColor"
          style={{ opacity: 0.5 }}
        >
          <path d="M7 10l5 5 5-5z" />
        </svg>
      </div>

      {isOpen && (
        <>
          <div
            className="project-selector-overlay"
            onClick={() => setIsOpen(false)}
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 999
            }}
          />
          <div
            className="project-selector-menu"
            style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              marginTop: '0.5rem',
              background: 'var(--bg-primary)',
              border: '1px solid var(--border-color)',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              minWidth: '250px',
              zIndex: 1000
            }}
          >
            <div
              style={{
                padding: '0.75rem 1rem',
                borderBottom: '1px solid var(--border-color)',
                fontWeight: 600,
                fontSize: '0.875rem',
                color: 'var(--text-secondary)'
              }}
            >
              Switch Project
            </div>

            <div style={{ padding: '0.5rem 0' }}>
              {projects.map((project) => (
                <div
                  key={project.id}
                  className={`project-item ${currentProject === project.name ? 'active' : ''}`}
                  onClick={() => handleProjectSelect(project)}
                  style={{
                    padding: '0.75rem 1rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    transition: 'background 0.2s',
                    background: currentProject === project.name ? 'var(--bg-tertiary)' : 'transparent'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'var(--bg-tertiary)'
                  }}
                  onMouseLeave={(e) => {
                    if (currentProject !== project.name) {
                      e.currentTarget.style.background = 'transparent'
                    }
                  }}
                >
                  <span style={{ fontSize: '0.875rem' }}>{project.name}</span>
                  {project.badgeCount && (
                    <span
                      style={{
                        background: 'var(--accent-blue)',
                        color: 'white',
                        borderRadius: '0.75rem',
                        padding: '0.125rem 0.5rem',
                        fontSize: '0.75rem',
                        fontWeight: 600
                      }}
                    >
                      {project.badgeCount}
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </>
  )
}
