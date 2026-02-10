/**
 * Result types for emoji chat bot operations.
 */

/**
 * Result returned by AddEmojiToMessage function.
 */
export interface AddEmojiResult {
  /** Whether the operation succeeded */
  success: boolean;
  /** ID of the message that was reacted to */
  messageId: string;
  /** The emoji that was added */
  emoji: string;
  /** Human-readable result message */
  message: string;
}

/**
 * Result returned by SuggestEmoji function.
 */
export interface EmojiSuggestion {
  /** The original message text that was analyzed */
  messageText: string;
  /** Array of suggested emojis based on sentiment */
  suggestedEmojis: string[];
}

/**
 * Context for tracking conversation state.
 */
export interface ChatContext {
  /** Number of messages received in this conversation */
  messageCount: number;
  /** Last emoji used in a reaction */
  lastEmojiUsed: string | null;
}
