import React, { useState, useEffect } from 'react'
import { AgentList } from '../AgentList/AgentList'
import { DetailView } from '../DetailView/DetailView'
import { ActionPanel } from '../ActionPanel/ActionPanel'
import { ResizeHandle } from '../Common/ResizeHandle'
import { useUIStore } from '../../store/useUIStore'
import { phaseConfigs } from '../../config/phases'

export function ConversationalLayout() {
  const currentPhase = useUIStore((s) => s.currentPhase)
  const selectedAgent = useUIStore((s) => s.selectedAgent)
  const selectAgent = useUIStore((s) => s.selectAgent)
  const messageHistory = useUIStore((s) => s.messageHistory)
  const addMessage = useUIStore((s) => s.addMessage)
  const setPhase = useUIStore((s) => s.setPhase)
  const [agentListWidth, setAgentListWidth] = useState(280)
  const [actionPaneWidth, setActionPaneWidth] = useState(400)

  const config = phaseConfigs[currentPhase]

  // If phase config doesn't exist (e.g., from old localStorage), reset to phase-01
  useEffect(() => {
    if (!config) {
      console.warn(`Phase ${currentPhase} not found in configs, resetting to phase-01`)
      setPhase('phase-01')
    }
  }, [config, currentPhase, setPhase])

  // Select first agent by default if no agent is selected
  useEffect(() => {
    if (!selectedAgent && config?.agentStatuses) {
      const firstAgentId = Object.keys(config.agentStatuses)[0]
      if (firstAgentId) {
        selectAgent(firstAgentId)
      }
    }
  }, [currentPhase, selectedAgent, config, selectAgent])

  // Guard: don't render if config is invalid
  if (!config) {
    return <div className="main-layout">Loading...</div>
  }

  // Mock handlers for now
  const handleSendMessage = (content: string) => {
    if (!selectedAgent) return

    addMessage(selectedAgent, {
      id: `msg-${Date.now()}`,
      role: 'user',
      content,
      timestamp: Date.now()
    })
  }

  const handleActionSubmit = (data: any) => {
    console.log('Action submitted:', data)
  }

  // Determine messages to display
  let messages: any[] = []

  if (selectedAgent) {
    // If an agent is selected, show their message history
    messages = messageHistory[selectedAgent] || []
  } else if (config.detailView.type === 'conversation' && config.detailView.content) {
    // If no agent selected but there's static conversation content, show it as a message
    messages = [{
      id: 'static-content',
      role: 'assistant',
      content: config.detailView.content,
      timestamp: Date.now()
    }]
  }

  const handleAgentListResize = (delta: number) => {
    setAgentListWidth(prev => {
      const newWidth = prev + delta
      return Math.max(200, Math.min(400, newWidth))
    })
  }

  const handleActionPaneResize = (delta: number) => {
    setActionPaneWidth(prev => {
      const newWidth = prev - delta
      return Math.max(300, Math.min(600, newWidth))
    })
  }

  return (
    <div className="main-layout">
      <aside className="agent-list" style={{ width: `${agentListWidth}px` }}>
        <AgentList agents={config.agentStatuses} />
      </aside>

      <ResizeHandle onResize={handleAgentListResize} orientation="vertical" />

      <DetailView
        viewType={config.detailView.type as 'conversation' | 'document'}
        title={config.detailView.title}
        messages={messages}
        isTyping={false}
        onSendMessage={handleSendMessage}
        documentContent={config.detailView.content}
      />

      <ResizeHandle onResize={handleActionPaneResize} orientation="vertical" />

      <div className="action-pane" style={{ width: `${actionPaneWidth}px` }}>
        <ActionPanel
          type={config.actionPane.type}
          title={config.actionPane.title}
          content={config.actionPane.content}
          onSubmit={handleActionSubmit}
          convergencePercent={config.actionPane.convergencePercent}
          convergenceTarget={config.actionPane.convergenceTarget}
          consensusReached={config.actionPane.consensusReached}
        />
      </div>
    </div>
  )
}
