import { useEffect } from 'react'
import { useUIStore } from '../store/useUIStore'
import { phaseConfigs } from '../config/phases'

/**
 * Hook that manages phase-based rendering logic
 * Updates document title and handles phase-specific setup
 */
export function usePhaseRendering() {
  const currentPhase = useUIStore((s) => s.currentPhase)
  const setCurrentView = useUIStore((s) => s.setCurrentView)

  useEffect(() => {
    const config = phaseConfigs[currentPhase]
    if (config) {
      // Update document title to match prototype
      document.title = 'Expert Feedback UI - Prototype'

      // Only set view from phase config if URL doesn't explicitly specify a view
      // This allows URL parameters to override phase-based view defaults
      const urlParams = new URLSearchParams(window.location.search)
      const urlHasViewParam = urlParams.has('view')

      if (config.detailView.type && !urlHasViewParam) {
        setCurrentView(config.detailView.type)
      }
    }
  }, [currentPhase, setCurrentView])

  return {
    currentPhaseConfig: phaseConfigs[currentPhase]
  }
}
