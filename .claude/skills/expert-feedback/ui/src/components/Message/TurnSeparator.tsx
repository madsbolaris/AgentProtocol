import React from 'react'

interface TurnSeparatorProps {
  turnNumber: number
}

export function TurnSeparator({ turnNumber }: TurnSeparatorProps) {
  return (
    <div className="turn-separator">
      <div className="turn-separator-line" />
      <div className="turn-separator-label">Turn {turnNumber}</div>
      <div className="turn-separator-line" />
    </div>
  )
}
