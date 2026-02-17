import React from 'react'
import { Highlight, themes } from 'prism-react-renderer'
import { useUIStore } from '../../store/useUIStore'

interface SyntaxHighlighterProps {
  code: string
  language?: string
  showLineNumbers?: boolean
}

// Map common language aliases to Prism language identifiers
const languageMap: Record<string, string> = {
  js: 'javascript',
  ts: 'typescript',
  jsx: 'javascript',
  tsx: 'typescript',
  py: 'python',
  rb: 'ruby',
  sh: 'bash',
  yml: 'yaml',
  json: 'json',
  md: 'markdown',
  html: 'markup',
  xml: 'markup',
}

// Detect language from code content
function detectLanguage(code: string): string {
  // Simple heuristics for language detection
  if (code.includes('function') || code.includes('const') || code.includes('let')) {
    return 'javascript'
  }
  if (code.includes('def ') || code.includes('import ') || code.includes('class ')) {
    return 'python'
  }
  if (code.includes('{') && code.includes('}') && code.includes(':')) {
    return 'json'
  }
  return 'text'
}

export function SyntaxHighlighter({
  code,
  language,
  showLineNumbers = false,
}: SyntaxHighlighterProps) {
  const darkMode = useUIStore((s) => s.darkMode)

  // Normalize language
  const normalizedLang = language
    ? (languageMap[language.toLowerCase()] || language.toLowerCase())
    : detectLanguage(code)

  const theme = darkMode ? themes.vsDark : themes.vsLight

  return (
    <Highlight theme={theme} code={code.trim()} language={normalizedLang}>
      {({ className, style, tokens, getLineProps, getTokenProps }) => (
        <pre className={`syntax-highlighter ${className}`} style={style}>
          <code>
            {tokens.map((line, i) => (
              <div key={i} {...getLineProps({ line })}>
                {showLineNumbers && <span className="line-number">{i + 1}</span>}
                {line.map((token, key) => (
                  <span key={key} {...getTokenProps({ token })} />
                ))}
              </div>
            ))}
          </code>
        </pre>
      )}
    </Highlight>
  )
}
