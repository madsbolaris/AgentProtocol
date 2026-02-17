import React, { useState, useRef, useEffect } from 'react'

interface MessageInputProps {
  onSend: (content: string) => void
  onStop?: () => void
  isRunning?: boolean
}

export function MessageInput({ onSend, onStop, isRunning = false }: MessageInputProps) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [value])

  const handleSubmit = () => {
    if (value.trim() && !isRunning) {
      onSend(value.trim())
      setValue('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="message-input-container">
      <div className="message-input-wrapper">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Send a message to the agent..."
          rows={1}
          disabled={isRunning}
          className="message-input"
        />

        <div className="message-input-actions">
          {isRunning && onStop ? (
            <button
              onClick={onStop}
              className="stop-button"
              title="Stop generation"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <rect x="4" y="4" width="8" height="8" rx="1"/>
              </svg>
              Stop
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={!value.trim()}
              className="send-button"
              title="Send message (Enter)"
            >
              <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                <path d="M15.964.686a.5.5 0 0 0-.65-.65L.767 5.855H.766l-.452.18a.5.5 0 0 0-.082.887l.41.26.001.002 4.995 3.178 3.178 4.995.002.002.26.41a.5.5 0 0 0 .886-.083l6-15Zm-1.833 1.89L6.637 10.07l-.215-.338a.5.5 0 0 0-.154-.154l-.338-.215 7.494-7.494 1.178-.471-.47 1.178Z"/>
              </svg>
              Send
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
