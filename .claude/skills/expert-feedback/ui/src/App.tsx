import React, { useEffect } from 'react'
import { Header } from './components/Layout/Header'
import { ConversationalLayout } from './components/Layout/ConversationalLayout'
import { PhaseSelector } from './components/PhaseSelector/PhaseSelector'
import { NotificationCenter } from './components/Notifications/NotificationCenter'
import { usePhaseRendering } from './hooks/usePhaseRendering'
import { useDeepLinking } from './hooks/useDeepLinking'
import { useUIStore } from './store/useUIStore'
import './styles/variables.css'
import './styles/global.css'
import './styles/components.css'

export function App() {
  usePhaseRendering()
  useDeepLinking()
  const darkMode = useUIStore((s) => s.darkMode)

  // Apply dark mode on mount
  useEffect(() => {
    if (darkMode) {
      document.body.classList.add('dark-mode')
    } else {
      document.body.classList.remove('dark-mode')
    }
  }, [darkMode])

  return (
    <div className="app-container">
      <Header />
      <ConversationalLayout />
      <PhaseSelector />
      <NotificationCenter />
    </div>
  )
}
