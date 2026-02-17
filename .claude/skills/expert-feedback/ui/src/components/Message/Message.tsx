import React, { useState, useRef, useEffect } from 'react'
import { type Message as MessageType } from '../../types/workspace'
import { ToolCallBlock } from './ToolCallBlock'
import { ThinkingBlock } from './ThinkingBlock'
import { CopyButton } from '../Common/CopyButton'

interface MessageProps {
  message: MessageType
}

export function Message({ message }: MessageProps) {
  const [expanded, setExpanded] = useState(false)
  const [needsExpansion, setNeedsExpansion] = useState(false)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (contentRef.current) {
      const scrollHeight = contentRef.current.scrollHeight
      const clientHeight = contentRef.current.clientHeight
      setNeedsExpansion(scrollHeight > clientHeight + 10)
    }
  }, [message.content])

  const formatTime = (timestamp: number) => {
    const now = Date.now()
    const diff = now - timestamp

    const seconds = Math.floor(diff / 1000)
    const minutes = Math.floor(seconds / 60)
    const hours = Math.floor(minutes / 60)

    if (hours > 0) return `${hours}h ${minutes % 60}m`
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`
    return `${seconds}s`
  }

  return (
    <div className={`message ${message.role}`}>
      <div className="message-header">
        <div className="message-header-left">
          <span className="message-role">
            {message.role === 'assistant' ? 'Agent' :
             message.role === 'user' ? 'User' :
             'System'}
          </span>
        </div>
        <div className="message-header-right">
          <span className="message-time">{formatTime(message.timestamp)}</span>
          <CopyButton text={message.content} />
        </div>
      </div>

      {message.content && (
        <div
          ref={contentRef}
          className={`message-content ${!expanded ? 'truncated' : ''}`}
        >
          {message.content.split('\n').map((line, index) => (
            <p key={index}>{line || '\u00A0'}</p>
          ))}
        </div>
      )}

      {needsExpansion && (
        <button
          className="expand-button"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? (
            <>Show less <i className="fa-solid fa-chevron-up"></i></>
          ) : (
            <>Show more <i className="fa-solid fa-chevron-down"></i></>
          )}
        </button>
      )}

      {message.metadata?.thinking && (
        <ThinkingBlock content={message.metadata.thinking} />
      )}

      {message.metadata?.toolCalls && message.metadata.toolCalls.length > 0 && (
        <ToolCallBlock calls={message.metadata.toolCalls} />
      )}
    </div>
  )
}
