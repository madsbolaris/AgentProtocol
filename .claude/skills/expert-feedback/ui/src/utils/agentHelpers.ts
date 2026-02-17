/**
 * Helper functions for agent display and formatting
 */

import { getAgentById, getAgentDisplayName as getDisplayName } from '../data/agents'

/**
 * Get agent display name from ID
 */
export function getAgentDisplayName(agentId: string): string {
  return getDisplayName(agentId)
}

/**
 * Get agent type (expert, aggregator, artifact-generator)
 */
export function getAgentType(agentId: string): 'expert' | 'aggregator' | 'artifact-generator' {
  const agent = getAgentById(agentId)
  if (!agent) return 'expert'

  if (agent.group === 'consolidator') {
    return 'aggregator'
  }
  if (agent.group === 'artifact-generators') {
    return 'artifact-generator'
  }
  return 'expert'
}

/**
 * Group agents by type for display
 */
export function groupAgents(agents: Record<string, any>): {
  experts: Array<[string, any]>
  aggregators: Array<[string, any]>
  artifactGenerators: Array<[string, any]>
} {
  const entries = Object.entries(agents)

  return {
    experts: entries.filter(([id]) => getAgentType(id) === 'expert'),
    aggregators: entries.filter(([id]) => getAgentType(id) === 'aggregator'),
    artifactGenerators: entries.filter(([id]) => getAgentType(id) === 'artifact-generator')
  }
}
