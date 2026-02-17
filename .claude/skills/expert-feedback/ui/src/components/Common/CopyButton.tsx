import React, { useState } from 'react'

interface CopyButtonProps {
  text: string
  className?: string
  onCopy?: () => void
}

export function CopyButton({ text, className = '', onCopy }: CopyButtonProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      onCopy?.()
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <button
      className={`copy-button ${className}`}
      onClick={handleCopy}
      title={copied ? 'Copied!' : 'Copy to clipboard'}
      type="button"
    >
      {copied ? (
        <>✓ Copied</>
      ) : (
        <i className="fa-regular fa-copy"></i>
      )}
    </button>
  )
}
