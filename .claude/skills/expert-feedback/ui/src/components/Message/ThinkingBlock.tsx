import React, { useState } from 'react'

interface ThinkingBlockProps {
  content: string
  agentName?: string
}

export function ThinkingBlock({ content, agentName }: ThinkingBlockProps) {
  const [isExpanded, setIsExpanded] = useState(false)

  const label = agentName ? `${agentName} (Thinking)` : 'Thinking'

  return (
    <div className="thinking-block">
      <div
        className="thinking-header"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <div className="thinking-header-content">
          <span className="thinking-icon">💭</span>
          <span className="thinking-label">{label}</span>
        </div>
        <span className="thinking-toggle">
          {isExpanded ? '▼' : '▶'}
        </span>
      </div>

      {isExpanded && (
        <div className="thinking-content">
          <pre className="thinking-text">{content}</pre>
        </div>
      )}
    </div>
  )
}
