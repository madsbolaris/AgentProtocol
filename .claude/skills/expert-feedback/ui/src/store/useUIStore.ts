/**
 * Zustand store for conversational UI state
 * Persists to localStorage automatically
 */

import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { type UIPhase, type Message } from '../types/workspace'
import {
  loadPhase01MockData,
  loadPhase02MockData,
  loadPhase03MockData,
  loadPhase04MockData,
  loadPhase05MockData
} from '../data/mockPhaseData'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  message: string
  duration?: number
}

interface UIState {
  // Conversational UI state
  currentPhase: UIPhase
  selectedAgent: string | null
  currentView: 'conversation' | 'document'
  darkMode: boolean
  messageHistory: Record<string, Message[]>
  convergencePercent: number
  convergenceThreshold: number
  newContentAgents: string[]
  // Project metadata
  projectName: string
  projectBadgeCount: number
  iterationMetadata: {
    tokens: number
    cost: number
    duration: string
  }
  notifications: Notification[]

  // Actions
  setPhase: (phase: UIPhase) => void
  selectAgent: (agentId: string | null) => void
  setCurrentView: (view: 'conversation' | 'document') => void
  toggleView: () => void
  toggleDarkMode: () => void
  addMessage: (agentId: string, message: Message) => void
  clearMessages: (agentId: string) => void
  setConvergence: (percent: number) => void
  markAgentReviewed: (agentId: string) => void
  markAgentHasNewContent: (agentId: string) => void
  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
  setProjectName: (name: string) => void
  setProjectBadgeCount: (count: number) => void
  resetToDefaults: () => void
  loadPhase01Data: () => void
}

// Helper function to load mock data for any phase
function loadPhaseData(phase: UIPhase) {
  switch (phase) {
    case 'phase-01': return loadPhase01MockData()
    case 'phase-02': return loadPhase02MockData()
    case 'phase-03': return loadPhase03MockData()
    case 'phase-04': return loadPhase04MockData()
    case 'phase-05': return loadPhase05MockData()
    default: return loadPhase01MockData() // Fallback to phase-01
  }
}

// Load phase-01 mock data for initial state
const phase01Data = loadPhase01MockData()

const defaultState = {
  currentPhase: 'phase-01' as UIPhase,
  selectedAgent: null,
  currentView: 'conversation' as 'conversation' | 'document',
  darkMode: false,
  messageHistory: phase01Data.messageHistory,
  convergencePercent: phase01Data.convergencePercent,
  convergenceThreshold: 60,
  newContentAgents: phase01Data.newContentAgents,
  projectName: 'UX Update Review',
  projectBadgeCount: 2,
  iterationMetadata: {
    tokens: 125000,
    cost: 0.42,
    duration: '8m 34s',
  },
  notifications: [],
}

export const useUIStore = create<UIState>()(
  persist(
    (set, get) => ({
      ...defaultState,

      // Phase management
      setPhase: (phase) => {
        // Load mock data for the selected phase
        const phaseData = loadPhaseData(phase)
        set({
          currentPhase: phase,
          convergencePercent: phaseData.convergencePercent,
          newContentAgents: phaseData.newContentAgents,
          messageHistory: phaseData.messageHistory
        })
      },

      // Agent selection
      selectAgent: (agentId) => set({ selectedAgent: agentId }),

      // View management
      setCurrentView: (view) => set({ currentView: view }),

      toggleView: () =>
        set((state) => ({
          currentView: state.currentView === 'conversation' ? 'document' : 'conversation',
        })),

      // Dark mode
      toggleDarkMode: () => {
        set((state) => {
          const newMode = !state.darkMode
          // Apply dark mode class to body
          if (typeof document !== 'undefined') {
            document.body.classList.toggle('dark-mode', newMode)
          }
          return { darkMode: newMode }
        })
      },

      // Message management
      addMessage: (agentId, message) =>
        set((state) => ({
          messageHistory: {
            ...state.messageHistory,
            [agentId]: [...(state.messageHistory[agentId] || []), message],
          },
        })),

      clearMessages: (agentId) =>
        set((state) => ({
          messageHistory: {
            ...state.messageHistory,
            [agentId]: [],
          },
        })),

      // Convergence management
      setConvergence: (percent) => set({ convergencePercent: percent }),

      // New content management
      markAgentReviewed: (agentId) =>
        set((state) => ({
          newContentAgents: state.newContentAgents.filter((id) => id !== agentId),
        })),

      markAgentHasNewContent: (agentId) =>
        set((state) => ({
          newContentAgents: state.newContentAgents.includes(agentId)
            ? state.newContentAgents
            : [...state.newContentAgents, agentId],
        })),

      // Notification management
      addNotification: (notification) => {
        const id = Date.now().toString()
        const newNotification: Notification = {
          ...notification,
          id,
          duration: notification.duration || 5000,
        }

        set((state) => ({
          notifications: [...state.notifications, newNotification],
        }))

        // Auto-remove after duration
        if (newNotification.duration) {
          setTimeout(() => {
            useUIStore.getState().removeNotification(id)
          }, newNotification.duration)
        }
      },

      removeNotification: (id) =>
        set((state) => ({
          notifications: state.notifications.filter((n) => n.id !== id),
        })),

      // Load phase 01 mock data
      loadPhase01Data: () => {
        const mockData = loadPhase01MockData()
        set({
          convergencePercent: mockData.convergencePercent,
          newContentAgents: mockData.newContentAgents,
          messageHistory: mockData.messageHistory
        })
      },

      // Project management
      setProjectName: (name) => set({ projectName: name }),
      setProjectBadgeCount: (count) => set({ projectBadgeCount: count }),

      // Reset to defaults
      resetToDefaults: () => set(defaultState),
    }),
    {
      name: 'expert-feedback-conversational-ui',
      onRehydrateStorage: () => (state) => {
        // Apply dark mode class on rehydration
        if (state?.darkMode && typeof document !== 'undefined') {
          document.body.classList.add('dark-mode')
        }
        // Load phase-01 mock data if on phase-01 and no messages
        if (state?.currentPhase === 'phase-01' && Object.keys(state.messageHistory || {}).length === 0) {
          useUIStore.getState().loadPhase01Data()
        }
      },
    }
  )
)
