import React from 'react'
import { AgentListItem } from './AgentListItem'
import { type AgentStatus } from '../../types/workspace'
import { useUIStore } from '../../store/useUIStore'
import { groupAgents } from '../../utils/agentHelpers'

interface AgentListProps {
  agents: Record<string, AgentStatus>
}

export function AgentList({ agents }: AgentListProps) {
  const selectedAgent = useUIStore((s) => s.selectedAgent)
  const selectAgent = useUIStore((s) => s.selectAgent)
  const markAgentReviewed = useUIStore((s) => s.markAgentReviewed)

  const handleAgentClick = (agentId: string) => {
    selectAgent(agentId)
    markAgentReviewed(agentId)
  }

  const { experts, aggregators, artifactGenerators } = groupAgents(agents)

  return (
    <>
      {experts.length > 0 && (
        <div className="agent-group">
          <div className="agent-group-header">Experts</div>
          {experts.map(([id, status]) => (
            <AgentListItem
              key={id}
              id={id}
              name={id}
              status={status}
              isSelected={selectedAgent === id}
              onClick={() => handleAgentClick(id)}
            />
          ))}
        </div>
      )}

      {aggregators.length > 0 && (
        <div className="agent-group">
          <div className="agent-group-header">Consolidator</div>
          {aggregators.map(([id, status]) => (
            <AgentListItem
              key={id}
              id={id}
              name={id}
              status={status}
              isSelected={selectedAgent === id}
              onClick={() => handleAgentClick(id)}
            />
          ))}
        </div>
      )}

      {artifactGenerators.length > 0 && (
        <div className="agent-group">
          <div className="agent-group-header">Artifact Generators</div>
          {artifactGenerators.map(([id, status]) => (
            <AgentListItem
              key={id}
              id={id}
              name={id}
              status={status}
              isSelected={selectedAgent === id}
              onClick={() => handleAgentClick(id)}
            />
          ))}
        </div>
      )}
    </>
  )
}
