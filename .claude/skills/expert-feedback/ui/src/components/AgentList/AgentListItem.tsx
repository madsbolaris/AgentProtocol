import React from 'react'
import { useUIStore } from '../../store/useUIStore'
import { type AgentStatus } from '../../types/workspace'

interface AgentListItemProps {
  id: string
  name: string
  status: AgentStatus
  isSelected: boolean
  onClick: () => void
}

export function AgentListItem({ id, name, status, isSelected, onClick }: AgentListItemProps) {
  const newContentAgents = useUIStore((s) => s.newContentAgents)
  const hasNewContent = newContentAgents.includes(id)

  const classes = [
    'agent-item',
    isSelected && 'active',
    status.status === 'disabled' && 'disabled'
  ].filter(Boolean).join(' ')

  return (
    <div className={classes} onClick={onClick}>
      <div className="agent-info">
        <span className="agent-name">{name}</span>
      </div>
      <div className="agent-indicators">
        {status.status === 'running' && (
          <>
            <button
              className="agent-stop-button"
              title="Stop agent"
              onClick={(e) => {
                e.stopPropagation()
                // TODO: Implement stop functionality
              }}
            >
              <i className="fa-solid fa-stop"></i>
            </button>
            <span className="agent-status running">
              <i className="fa-solid fa-circle-notch fa-spin"></i>
            </span>
          </>
        )}
        {status.status === 'completed' && (
          <span className="agent-status completed">
            <i className="fa-solid fa-circle-check"></i>
          </span>
        )}
        {status.status === 'converged' && (
          <span className="agent-status converged">
            <i className="fa-solid fa-circle-check"></i>
          </span>
        )}
        {status.status === 'disabled' && (
          <span className="agent-status disabled">
            <i className="fa-regular fa-circle"></i>
          </span>
        )}
        {status.status === 'waiting' && (
          <span className="agent-status waiting">
            <i className="fa-solid fa-pause"></i>
          </span>
        )}
        {status.status === 'pending' && (
          <span className="agent-status pending"></span>
        )}
        {status.hasConcerns && (
          <span className="concern-badge">
            <i className="fa-solid fa-circle-exclamation"></i>
          </span>
        )}
        {hasNewContent && <div className="new-content-dot"></div>}
      </div>
    </div>
  )
}
