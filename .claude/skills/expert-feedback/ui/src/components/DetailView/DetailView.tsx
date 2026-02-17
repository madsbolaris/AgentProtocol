import React from 'react'
import { ConversationView } from './ConversationView'
import { DocumentView } from './DocumentView'
import { MessageInput } from '../MessageInput/MessageInput'
import { useUIStore } from '../../store/useUIStore'
import { type Message } from '../../types/workspace'

interface DetailViewProps {
  viewType: 'conversation' | 'document'
  title: string
  // Conversation view props
  messages?: Message[]
  isTyping?: boolean
  onSendMessage?: (content: string) => void
  onStop?: () => void
  // Document view props
  documentContent?: string
  showDiff?: boolean
}

export function DetailView({
  viewType,
  title,
  messages = [],
  isTyping = false,
  onSendMessage = () => {},
  onStop,
  documentContent = '',
  showDiff = false
}: DetailViewProps) {
  const currentView = useUIStore((s) => s.currentView)
  const setCurrentView = useUIStore((s) => s.setCurrentView)
  const selectedAgent = useUIStore((s) => s.selectedAgent)
  const currentPhase = useUIStore((s) => s.currentPhase)

  // Get iteration number from phase (phase-01 → Iteration 1)
  const getIterationLabel = (): string => {
    const match = currentPhase.match(/phase-(\d+)/)
    if (!match) return ''
    const phaseNum = parseInt(match[1])

    // Phases 1-2 = Iteration 1, 3 = Questions, 4-5 = Iteration 2, 6-7 = Iteration 3, etc.
    if (phaseNum <= 2) return 'Iteration 1'
    if (phaseNum === 3) return 'Questions'
    if (phaseNum <= 5) return 'Iteration 2'
    if (phaseNum <= 7) return 'Iteration 3'
    return 'Artifact Phase'
  }

  return (
    <main className="detail-view">
      <div className="detail-header">
        <div className="detail-header-controls">
          {selectedAgent && (
            <>
              <h2 className="agent-heading">{selectedAgent}</h2>
              <div className="detail-header-metadata">
                <span className="metadata-time">
                  {new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </>
          )}

          <div className="view-toggle">
            <button
              className={`view-toggle-button ${currentView === 'document' ? 'active' : ''}`}
              onClick={() => setCurrentView('document')}
            >
              Documents
            </button>
            <button
              className={`view-toggle-button ${currentView === 'conversation' ? 'active' : ''}`}
              onClick={() => setCurrentView('conversation')}
            >
              Conversation
            </button>
          </div>
        </div>
      </div>

      <div className="detail-content-wrapper">
        {currentView === 'conversation' ? (
          <div className="conversation-view active">
            <ConversationView
              messages={messages}
              isTyping={isTyping}
            />
          </div>
        ) : (
          <>
            {/* Document view shows both conversation and document (matches prototype) */}
            <div className="conversation-view">
              <ConversationView
                messages={messages}
                isTyping={isTyping}
              />
            </div>
            <div className="document-view active">
              <DocumentView
                title={title}
                content={documentContent}
                showDiff={showDiff}
              />
            </div>
          </>
        )}
      </div>

      {currentView === 'conversation' && (
        <MessageInput
          onSend={onSendMessage}
          onStop={onStop}
          isRunning={isTyping}
        />
      )}
    </main>
  )
}
