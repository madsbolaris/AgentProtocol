/**
 * Hook for composing messages with multi-modal content
 */

import { useState, useCallback } from 'react';
import type { AIContent } from '@microsoft/agents-protocol-abstractions';

export interface UseMessageComposerResult {
  content: AIContent[];
  text: string;

  // Text operations
  setText: (text: string) => void;
  addText: (text: string) => void;

  // Content operations
  addContent: (content: AIContent) => void;
  removeContent: (index: number) => void;
  clear: () => void;

  // File operations
  addImage: (file: File | string) => Promise<void>;
  addFile: (file: File) => Promise<void>;

  // State
  isEmpty: boolean;
  hasFiles: boolean;
}

export function useMessageComposer(): UseMessageComposerResult {
  const [content, setContent] = useState<AIContent[]>([]);
  const [text, setText] = useState('');

  const addText = useCallback((newText: string) => {
    setText((prev) => prev + newText);
  }, []);

  const addContent = useCallback((newContent: AIContent) => {
    setContent((prev) => [...prev, newContent]);
  }, []);

  const removeContent = useCallback((index: number) => {
    setContent((prev) => prev.filter((_, i) => i !== index));
  }, []);

  const clear = useCallback(() => {
    setContent([]);
    setText('');
  }, []);

  const addImage = useCallback(async (file: File | string) => {
    let imageUrl: string;

    if (typeof file === 'string') {
      imageUrl = file;
    } else {
      // Convert File to data URL
      imageUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      });
    }

    addContent({
      kind: 'image',
      uri: imageUrl,
      mimeType: typeof file === 'string' ? 'image/png' : file.type,
    } as AIContent);
  }, [addContent]);

  const addFile = useCallback(
    async (file: File) => {
      // Convert File to data URL
      const fileUrl = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onloadend = () => resolve(reader.result as string);
        reader.readAsDataURL(file);
      });

      addContent({
        kind: 'file',
        uri: fileUrl,
        filename: file.name,
        mimeType: file.type,
      } as AIContent);
    },
    [addContent]
  );

  const isEmpty = text.length === 0 && content.length === 0;
  const hasFiles = content.some((c) => c.kind === 'image' || c.kind === 'file');

  return {
    content,
    text,
    setText,
    addText,
    addContent,
    removeContent,
    clear,
    addImage,
    addFile,
    isEmpty,
    hasFiles,
  };
}
