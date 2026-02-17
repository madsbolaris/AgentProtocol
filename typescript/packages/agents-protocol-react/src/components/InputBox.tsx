/**
 * InputBox component - user input with file upload
 */

import React, { useState, useRef, KeyboardEvent } from 'react';
import { useMessageComposer } from '../hooks/useMessageComposer';
import { useTypingIndicator } from '../hooks/useTypingIndicator';

export interface InputBoxProps {
  threadId: string;
  onSend: (text: string) => Promise<void>;
  placeholder?: string;
  disabled?: boolean;
  enableFileUpload?: boolean;
  enableMultiline?: boolean;
  maxLength?: number;
  onTyping?: () => void;
  onStopTyping?: () => void;
}

export function InputBox({
  threadId,
  onSend,
  placeholder = 'Type a message...',
  disabled = false,
  enableFileUpload = true,
  enableMultiline = true,
  maxLength,
  onTyping,
  onStopTyping,
}: InputBoxProps) {
  const { text, setText, addImage, addFile, clear, content, hasFiles } = useMessageComposer();
  const { isTyping, startTyping, stopTyping } = useTypingIndicator(threadId);
  const [isSending, setIsSending] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setText(e.target.value);
    startTyping();
    onTyping?.();
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !enableMultiline) {
      e.preventDefault();
      handleSend();
    } else if (e.key === 'Enter' && e.ctrlKey && enableMultiline) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleSend = async () => {
    if (!text.trim() || isSending || disabled) return;

    try {
      setIsSending(true);
      stopTyping();
      onStopTyping?.();

      await onSend(text);
      clear();

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsSending(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    for (const file of Array.from(files)) {
      if (file.type.startsWith('image/')) {
        await addImage(file);
      } else {
        await addFile(file);
      }
    }

    // Reset file input
    e.target.value = '';
  };

  const handlePaste = async (e: React.ClipboardEvent) => {
    const items = e.clipboardData?.items;
    if (!items) return;

    for (const item of Array.from(items)) {
      if (item.type.startsWith('image/')) {
        const file = item.getAsFile();
        if (file) {
          e.preventDefault();
          await addImage(file);
        }
      }
    }
  };

  // Auto-resize textarea
  const handleTextareaResize = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  return (
    <div className="input-box">
      {hasFiles && (
        <div className="input-attachments">
          {content.map((item, index) => (
            <div key={index} className="attachment-preview">
              {item.kind === 'image' ? '🖼️' : '📎'}{' '}
              {item.kind === 'file' && 'filename' in item ? item.filename : 'Attachment'}
            </div>
          ))}
        </div>
      )}

      <div className="input-box-container">
        {enableFileUpload && (
          <button
            type="button"
            className="input-btn input-btn--attach"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled}
            title="Attach file"
          >
            📎
          </button>
        )}

        <textarea
          ref={textareaRef}
          className="input-textarea"
          value={text}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          onInput={handleTextareaResize}
          onPaste={handlePaste}
          placeholder={placeholder}
          disabled={disabled || isSending}
          maxLength={maxLength}
          rows={1}
        />

        <button
          type="button"
          className="input-btn input-btn--send"
          onClick={handleSend}
          disabled={!text.trim() || disabled || isSending}
          title={enableMultiline ? 'Send (Ctrl+Enter)' : 'Send (Enter)'}
        >
          {isSending ? '⏳' : '➤'}
        </button>

        <input
          ref={fileInputRef}
          type="file"
          className="input-file-hidden"
          onChange={handleFileSelect}
          accept="image/*,application/pdf,.doc,.docx,.txt"
          multiple
          style={{ display: 'none' }}
        />
      </div>

      {maxLength && (
        <div className="input-character-count">
          {text.length} / {maxLength}
        </div>
      )}
    </div>
  );
}
