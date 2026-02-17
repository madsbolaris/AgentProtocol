import React, { useRef, useEffect } from 'react'
import { Message } from '../Message/Message'
import { TurnSeparator } from '../Message/TurnSeparator'
import { type Message as MessageType } from '../../types/workspace'

interface ConversationViewProps {
  messages: MessageType[]
  isTyping?: boolean
}

export function ConversationView({
  messages,
  isTyping = false
}: ConversationViewProps) {
  const scrollRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      })
    }
  }, [messages, isTyping])

  // Group messages by turns (for turn separator display)
  const groupedMessages: { turnNumber: number; messages: MessageType[] }[] = []
  let currentTurn: MessageType[] = []
  let turnNumber = 1

  messages.forEach((msg, idx) => {
    currentTurn.push(msg)

    // Start new turn when we see a user message (unless it's the first message)
    if (msg.role === 'user' && idx < messages.length - 1) {
      groupedMessages.push({ turnNumber, messages: [...currentTurn] })
      currentTurn = []
      turnNumber++
    }
  })

  // Add any remaining messages
  if (currentTurn.length > 0) {
    groupedMessages.push({ turnNumber, messages: currentTurn })
  }

  return (
    <div className="messages-container" ref={scrollRef}>
      {groupedMessages.length === 0 && (
        <div className="empty-state">
          <p>No messages yet. Select an agent to view their conversation.</p>
        </div>
      )}

      {groupedMessages.map((group, idx) => (
        <React.Fragment key={group.turnNumber}>
          {idx > 0 && <TurnSeparator turnNumber={group.turnNumber} />}
          {group.messages.map(msg => (
            <Message key={msg.id} message={msg} />
          ))}
        </React.Fragment>
      ))}

      {isTyping && (
        <div className="typing-indicator">
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
          <span className="typing-dot"></span>
        </div>
      )}
    </div>
  )
}
