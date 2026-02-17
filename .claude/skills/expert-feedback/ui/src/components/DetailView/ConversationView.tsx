import { useRef, useEffect } from 'react'
import { Message } from '../Message/Message'
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

  return (
    <div className="messages-container" ref={scrollRef}>
      {messages.length === 0 && (
        <div className="empty-state">
          <p>No messages yet. Select an agent to view their conversation.</p>
        </div>
      )}

      {messages.map(msg => (
        <Message key={msg.id} message={msg} />
      ))}

      {isTyping && (
        <div className="typing-indicator">
          <span className="typing-indicator-text">Agent is thinking</span>
          <div className="typing-dots">
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
            <span className="typing-dot"></span>
          </div>
        </div>
      )}
    </div>
  )
}
