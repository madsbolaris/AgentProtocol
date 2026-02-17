import React, { useEffect, useRef, useState } from 'react'

interface ResizeHandleProps {
  onResize: (delta: number) => void
  orientation?: 'vertical' | 'horizontal'
}

export function ResizeHandle({ onResize, orientation = 'vertical' }: ResizeHandleProps) {
  const [isDragging, setIsDragging] = useState(false)
  const startPosRef = useRef(0)

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      const delta = orientation === 'vertical'
        ? e.clientX - startPosRef.current
        : e.clientY - startPosRef.current

      startPosRef.current = orientation === 'vertical' ? e.clientX : e.clientY
      onResize(delta)
    }

    const handleMouseUp = () => {
      setIsDragging(false)
    }

    document.addEventListener('mousemove', handleMouseMove)
    document.addEventListener('mouseup', handleMouseUp)

    return () => {
      document.removeEventListener('mousemove', handleMouseMove)
      document.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, onResize, orientation])

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    startPosRef.current = orientation === 'vertical' ? e.clientX : e.clientY
  }

  return (
    <div
      className={`resize-handle resize-handle-${orientation} ${isDragging ? 'dragging' : ''}`}
      onMouseDown={handleMouseDown}
      role="separator"
      aria-orientation={orientation}
    >
      <div className="resize-handle-indicator" />
    </div>
  )
}
