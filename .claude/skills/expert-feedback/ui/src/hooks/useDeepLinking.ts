import { useEffect } from 'react'
import { useUIStore } from '../store/useUIStore'
import { phaseConfigs } from '../config/phases'
import { agents } from '../data/agents'
import type { UIPhase } from '../types/workspace'

/**
 * Hook that enables URL-based navigation and state management
 * Supports query parameters: ?phase=xxx&agent=xxx&view=xxx
 * Updates URL when state changes and vice versa
 * Validates that requested agents are accessible (not disabled) for the current phase
 */
export function useDeepLinking() {
  // Helper to find first accessible agent for a phase
  const findAccessibleAgent = (phase: UIPhase): string | null => {
    const phaseConfig = phaseConfigs[phase]
    if (!phaseConfig) return null

    // Find first agent that is not disabled
    const accessibleAgent = agents.find(agent => {
      const status = phaseConfig.agentStatuses[agent.id]
      return status && status.status !== 'disabled'
    })

    return accessibleAgent?.id || null
  }

  // Helper to check if agent is accessible in phase
  const isAgentAccessible = (agentId: string, phase: UIPhase): boolean => {
    const phaseConfig = phaseConfigs[phase]
    if (!phaseConfig) {
      console.log('[DeepLink] No phase config for:', phase)
      return false
    }

    const agentStatus = phaseConfig.agentStatuses[agentId]
    const isAccessible = agentStatus && agentStatus.status !== 'disabled'

    console.log('[DeepLink] Agent status check:', {
      agentId,
      phase,
      agentStatus: agentStatus,
      statusValue: agentStatus?.status,
      isAccessible
    })

    return isAccessible
  }

  // Read URL params on mount and update state
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const phase = params.get('phase')
    const agent = params.get('agent')
    const view = params.get('view')

    const store = useUIStore.getState()

    // Set phase first if requested
    if (phase) {
      store.setPhase(phase as UIPhase)
    }

    // Validate and set agent
    if (agent) {
      const currentPhase = phase ? (phase as UIPhase) : store.currentPhase

      console.log('[DeepLink] Checking agent accessibility:', {
        agent,
        currentPhase,
        phaseConfig: phaseConfigs[currentPhase],
        agentStatus: phaseConfigs[currentPhase]?.agentStatuses[agent]
      })

      if (isAgentAccessible(agent, currentPhase)) {
        // Agent is accessible, select it
        console.log('[DeepLink] Agent is accessible, selecting:', agent)
        store.selectAgent(agent)
      } else {
        // Agent is disabled, find an accessible alternative
        console.log('[DeepLink] Agent is disabled, finding fallback')
        const fallbackAgent = findAccessibleAgent(currentPhase)

        if (fallbackAgent) {
          console.log('[DeepLink] Selecting fallback agent:', fallbackAgent)
          store.selectAgent(fallbackAgent)

          // Notify user about the redirect
          store.addNotification({
            type: 'warning',
            message: `Agent "${agent}" is not accessible in this phase. Showing "${fallbackAgent}" instead.`,
            duration: 5000
          })
        } else {
          // No accessible agents found
          console.log('[DeepLink] No accessible agents found')
          store.selectAgent(null)
          store.addNotification({
            type: 'error',
            message: `No accessible agents found for this phase.`,
            duration: 5000
          })
        }
      }
    }

    if (view) store.setCurrentView(view as 'conversation' | 'document')

    // Listen for browser back/forward navigation
    const handlePopState = () => {
      const p = new URLSearchParams(window.location.search)
      const newPhase = p.get('phase')
      const newAgent = p.get('agent')
      const newView = p.get('view')

      const s = useUIStore.getState()

      // Set phase first if requested
      if (newPhase) {
        s.setPhase(newPhase as UIPhase)
      }

      // Validate and set agent
      if (newAgent) {
        const currentPhase = newPhase ? (newPhase as UIPhase) : s.currentPhase

        if (isAgentAccessible(newAgent, currentPhase)) {
          s.selectAgent(newAgent)
        } else {
          const fallbackAgent = findAccessibleAgent(currentPhase)
          if (fallbackAgent) {
            s.selectAgent(fallbackAgent)
            s.addNotification({
              type: 'warning',
              message: `Agent "${newAgent}" is not accessible in this phase. Showing "${fallbackAgent}" instead.`,
              duration: 5000
            })
          } else {
            s.selectAgent(null)
          }
        }
      }

      if (newView) s.setCurrentView(newView as 'conversation' | 'document')
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  // Sync state changes to URL
  useEffect(() => {
    const unsubscribe = useUIStore.subscribe((state) => {
      const params = new URLSearchParams()

      if (state.currentPhase) params.set('phase', state.currentPhase)
      if (state.selectedAgent) params.set('agent', state.selectedAgent)
      if (state.currentView) params.set('view', state.currentView)

      const newUrl = `?${params.toString()}`

      // Only update if URL actually changed
      if (window.location.search !== newUrl) {
        window.history.pushState(null, '', newUrl)
      }
    })

    return unsubscribe
  }, [])
}
