/**
 * Hook for managing typing indicators
 */

import { useState, useCallback, useEffect } from 'react';

export interface UseTypingIndicatorResult {
  isTyping: boolean;
  startTyping: () => void;
  stopTyping: () => void;
}

export function useTypingIndicator(
  threadId: string,
  debounceMs: number = 1000
): UseTypingIndicatorResult {
  const [isTyping, setIsTyping] = useState(false);
  const [timeoutId, setTimeoutId] = useState<NodeJS.Timeout | null>(null);

  const startTyping = useCallback(() => {
    setIsTyping(true);

    // Clear existing timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    // Auto-stop typing after debounce period
    const newTimeoutId = setTimeout(() => {
      setIsTyping(false);
    }, debounceMs);

    setTimeoutId(newTimeoutId);
  }, [timeoutId, debounceMs]);

  const stopTyping = useCallback(() => {
    if (timeoutId) {
      clearTimeout(timeoutId);
      setTimeoutId(null);
    }
    setIsTyping(false);
  }, [timeoutId]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [timeoutId]);

  return {
    isTyping,
    startTyping,
    stopTyping,
  };
}
