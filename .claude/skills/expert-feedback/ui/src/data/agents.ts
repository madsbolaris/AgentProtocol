import { type Agent } from '../types/workspace'

/**
 * All agents in the expert feedback system
 */
export const agents: Agent[] = [
  // Experts
  {
    id: 'typescript-expert',
    displayName: 'TypeScript Expert',
    group: 'experts'
  },
  {
    id: 'python-expert',
    displayName: 'Python Expert',
    group: 'experts'
  },
  {
    id: 'csharp-expert',
    displayName: 'C# Expert',
    group: 'experts'
  },
  {
    id: 'frontend-expert',
    displayName: 'Frontend Expert',
    group: 'experts'
  },
  {
    id: 'security-expert',
    displayName: 'Security Expert',
    group: 'experts'
  },
  // Consolidator
  {
    id: 'synthesis-agent',
    displayName: 'Synthesis',
    group: 'consolidator'
  },
  // Artifact Generator
  {
    id: 'artifact-generator',
    displayName: 'Finalization',
    group: 'artifact-generators'
  },
  // Test Agent
  {
    id: 'Test Agent',
    displayName: 'Test Agent',
    group: 'experts'
  }
]

/**
 * Get agent by ID
 */
export function getAgentById(id: string): Agent | undefined {
  return agents.find(agent => agent.id === id)
}

/**
 * Get agent display name by ID
 */
export function getAgentDisplayName(id: string): string {
  const agent = getAgentById(id)
  return agent?.displayName || id
}

/**
 * Get agents by group
 */
export function getAgentsByGroup(group: Agent['group']): Agent[] {
  return agents.filter(agent => agent.group === group)
}
