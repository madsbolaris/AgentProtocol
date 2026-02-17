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
    const date = new Date(timestamp)
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    })
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
          <span className="message-time">{formatTime(message.timestamp)}</span>
        </div>
        <CopyButton text={message.content} />
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
