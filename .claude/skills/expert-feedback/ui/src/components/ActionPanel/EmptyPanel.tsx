import React from 'react'

interface EmptyPanelProps {
  title?: string
  description?: string
  icon?: string
  message?: string
}

export function EmptyPanel({ title, description, icon, message }: EmptyPanelProps) {
  // Support both old message format and new title/description format
  const displayTitle = title || 'Status'
  const displayDescription = description || message || 'No actions required at this time.'
  const displayIcon = icon || 'users'

  return (
    <div className="empty-state">
      <div className="empty-state-icon">
        <i className={`fa-solid fa-${displayIcon}`}></i>
      </div>
      <div className="empty-state-title">
        {displayTitle}
      </div>
      <div className="empty-state-description">
        {displayDescription}
      </div>
    </div>
  )
}
