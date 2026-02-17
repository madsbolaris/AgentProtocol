import React, { useState } from 'react'
import { SyntaxHighlighter } from '../Code/SyntaxHighlighter'
import { CopyButton } from '../Common/CopyButton'
import { type ToolCall } from '../../types/workspace'

interface ToolCallBlockProps {
  calls: ToolCall[]
}

export function ToolCallBlock({ calls }: ToolCallBlockProps) {
  const [expandedCalls, setExpandedCalls] = useState<Set<string>>(new Set())

  const toggleCall = (id: string) => {
    setExpandedCalls(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const getResultSummary = (call: ToolCall): string => {
    if (!call.output) return ''
    if (typeof call.output === 'string') {
      return call.output.length > 100
        ? call.output.substring(0, 100) + '...'
        : call.output
    }
    // Check for summary field in output object
    if (call.output && typeof call.output === 'object' && 'summary' in call.output) {
      return (call.output as any).summary || ''
    }
    return ''
  }

  const formatInput = (input: unknown): string => {
    if (typeof input === 'string') return input
    if (!input || typeof input !== 'object') return ''
    // Format as simple key: value pairs (like prototype)
    return Object.entries(input)
      .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
      .join('\n')
  }

  return (
    <div className="tool-calls-block">
      <div className="tool-calls-header">
        <i className="fa-solid fa-wrench"></i> Tool Calls ({calls.length})
      </div>
      {calls.map(call => {
        const inputFormatted = formatInput(call.input)
        const resultSummary = getResultSummary(call)

        return (
          <div key={call.id} className="tool-call">
            <div className="tool-call-header">
              <span className="tool-name">
                <i className="fa-solid fa-wrench tool-icon"></i>
                {call.name}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <span className="tool-status success">Success • 0.1s</span>
                <button className="copy-button" onClick={(e) => { e.stopPropagation(); navigator.clipboard.writeText(resultSummary || inputFormatted) }}>
                  <i className="fa-regular fa-copy"></i>
                </button>
              </div>
            </div>
            <div className="tool-params">
              {inputFormatted}
            </div>
            {resultSummary && (
              <div className="tool-result-summary">
                {resultSummary}
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}
