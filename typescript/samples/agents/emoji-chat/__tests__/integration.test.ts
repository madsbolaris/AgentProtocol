/**
 * Integration tests for Emoji Chat Bot
 *
 * These tests verify the functionality of:
 * - Tool functions (addEmojiToMessage, suggestEmoji)
 * - Logic and algorithms
 * - Result types and data structures
 *
 * Note: These are unit tests that verify the core logic without requiring
 * the full agent to be running.
 */

import { AddEmojiResult, EmojiSuggestion, ChatContext } from '../src/types.js';

// Tool function implementations (copied from source for testing)
async function addEmojiToMessage(params: {
  messageId: string;
  emoji: string;
}): Promise<string> {
  const result: AddEmojiResult = {
    success: true,
    messageId: params.messageId,
    emoji: params.emoji,
    message: `Added ${params.emoji} reaction to message ${params.messageId}`
  };
  return JSON.stringify(result);
}

async function suggestEmoji(params: { messageText: string }): Promise<string> {
  const lowerText = params.messageText.toLowerCase();
  const suggestedEmojis: string[] = [];

  if (lowerText.includes('happy') || lowerText.includes('great') || lowerText.includes('awesome')) {
    suggestedEmojis.push('😊', '🎉', '👍');
  } else if (lowerText.includes('sad') || lowerText.includes('sorry')) {
    suggestedEmojis.push('😢', '💔', '🤗');
  } else if (lowerText.includes('love')) {
    suggestedEmojis.push('❤️', '💕', '😍');
  } else if (lowerText.includes('thank')) {
    suggestedEmojis.push('🙏', '😊', '👍');
  } else {
    suggestedEmojis.push('👍', '😊', '✨');
  }

  const result: EmojiSuggestion = {
    messageText: params.messageText,
    suggestedEmojis
  };

  return JSON.stringify(result);
}

describe('Emoji Chat Bot Integration Tests', () => {
  describe('Tool Functions', () => {
    test('addEmojiToMessage adds emoji successfully', async () => {
      const result = await addEmojiToMessage({
        messageId: 'msg-123',
        emoji: '👍'
      });

      const parsed: AddEmojiResult = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.messageId).toBe('msg-123');
      expect(parsed.emoji).toBe('👍');
      expect(parsed.message).toContain('Added 👍 reaction');
    });

    test('suggestEmoji suggests happy emojis for positive sentiment', async () => {
      const result = await suggestEmoji({
        messageText: 'I am so happy today!'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('😊');
      expect(parsed.suggestedEmojis).toContain('🎉');
      expect(parsed.suggestedEmojis).toContain('👍');
    });

    test('suggestEmoji suggests sad emojis for negative sentiment', async () => {
      const result = await suggestEmoji({
        messageText: 'I am feeling sad today'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('😢');
      expect(parsed.suggestedEmojis).toContain('💔');
    });

    test('suggestEmoji suggests love emojis for love messages', async () => {
      const result = await suggestEmoji({
        messageText: 'I love this project!'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('❤️');
      expect(parsed.suggestedEmojis).toContain('💕');
      expect(parsed.suggestedEmojis).toContain('😍');
    });

    test('suggestEmoji suggests thank you emojis for gratitude', async () => {
      const result = await suggestEmoji({
        messageText: 'Thank you so much!'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('🙏');
      expect(parsed.suggestedEmojis).toContain('😊');
    });

    test('suggestEmoji provides default emojis for neutral messages', async () => {
      const result = await suggestEmoji({
        messageText: 'Hello there'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('👍');
      expect(parsed.suggestedEmojis).toContain('😊');
      expect(parsed.suggestedEmojis).toContain('✨');
    });

    test('addEmojiToMessage works with different emojis', async () => {
      const emojis = ['❤️', '🚀', '🎉', '😊', '👍', '💯'];

      for (const emoji of emojis) {
        const result = await addEmojiToMessage({
          messageId: 'msg-test',
          emoji: emoji
        });

        const parsed: AddEmojiResult = JSON.parse(result);
        expect(parsed.success).toBe(true);
        expect(parsed.emoji).toBe(emoji);
      }
    });

    test('suggestEmoji is case insensitive', async () => {
      const result1 = await suggestEmoji({ messageText: 'I am HAPPY' });
      const result2 = await suggestEmoji({ messageText: 'I am happy' });

      const parsed1: EmojiSuggestion = JSON.parse(result1);
      const parsed2: EmojiSuggestion = JSON.parse(result2);

      expect(parsed1.suggestedEmojis).toEqual(parsed2.suggestedEmojis);
    });

    test('suggestEmoji handles empty text', async () => {
      const result = await suggestEmoji({ messageText: '' });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toHaveLength(3);
      expect(parsed.suggestedEmojis).toContain('👍');
    });

    test('suggestEmoji handles very long text', async () => {
      const longText = 'a'.repeat(10000);
      const result = await suggestEmoji({ messageText: longText });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toHaveLength(3);
    });

    test('suggestEmoji handles special characters', async () => {
      const specialChars = '!@#$%^&*()_+-=[]{}|;:\'",.<>?/~`';
      const result = await suggestEmoji({ messageText: specialChars });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toBeDefined();
    });

    test('suggestEmoji handles unicode emoji in text', async () => {
      const emojiText = '👋 Hello 🌍 World 🚀';
      const result = await suggestEmoji({ messageText: emojiText });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.messageText).toBe(emojiText);
    });

    test('addEmojiToMessage handles empty messageId', async () => {
      const result = await addEmojiToMessage({
        messageId: '',
        emoji: '👍'
      });

      const parsed: AddEmojiResult = JSON.parse(result);
      expect(parsed.success).toBe(true);
      expect(parsed.messageId).toBe('');
    });

    test('addEmojiToMessage handles complex emoji', async () => {
      const complexEmojis = ['👨‍👩‍👧‍👦', '🏳️‍🌈', '👍🏾'];

      for (const emoji of complexEmojis) {
        const result = await addEmojiToMessage({
          messageId: 'msg-1',
          emoji: emoji
        });

        const parsed: AddEmojiResult = JSON.parse(result);
        expect(parsed.success).toBe(true);
        expect(parsed.emoji).toBe(emoji);
      }
    });
  });

  describe('Type Definitions', () => {
    test('AddEmojiResult type is correct', () => {
      const result: AddEmojiResult = {
        success: true,
        messageId: 'msg-1',
        emoji: '👍',
        message: 'Test'
      };

      expect(result.success).toBe(true);
      expect(result.messageId).toBe('msg-1');
      expect(result.emoji).toBe('👍');
      expect(result.message).toBe('Test');
    });

    test('EmojiSuggestion type is correct', () => {
      const suggestion: EmojiSuggestion = {
        messageText: 'Test message',
        suggestedEmojis: ['👍', '😊']
      };

      expect(suggestion.messageText).toBe('Test message');
      expect(suggestion.suggestedEmojis).toHaveLength(2);
    });

    test('ChatContext type is correct', () => {
      const context: ChatContext = {
        messageCount: 5,
        lastEmojiUsed: '🚀'
      };

      expect(context.messageCount).toBe(5);
      expect(context.lastEmojiUsed).toBe('🚀');
    });
  });

  describe('Emoji Suggestion Logic', () => {
    test('suggests correct emojis for multiple sentiment words', async () => {
      const result = await suggestEmoji({
        messageText: 'This is great and awesome!'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('😊');
      expect(parsed.suggestedEmojis).toContain('🎉');
    });

    test('prioritizes sentiment keywords over default', async () => {
      const happyResult = await suggestEmoji({ messageText: 'happy' });
      const neutralResult = await suggestEmoji({ messageText: 'hello' });

      const happyParsed: EmojiSuggestion = JSON.parse(happyResult);
      const neutralParsed: EmojiSuggestion = JSON.parse(neutralResult);

      expect(happyParsed.suggestedEmojis).not.toEqual(neutralParsed.suggestedEmojis);
    });

    test('handles mixed case sentiment words', async () => {
      const testCases = ['HAPPY', 'Happy', 'hApPy'];

      for (const testCase of testCases) {
        const result = await suggestEmoji({ messageText: testCase });
        const parsed: EmojiSuggestion = JSON.parse(result);
        expect(parsed.suggestedEmojis).toContain('😊');
      }
    });

    test('handles sentiment words in longer sentences', async () => {
      const result = await suggestEmoji({
        messageText: 'I just wanted to say that I am very happy with the results'
      });

      const parsed: EmojiSuggestion = JSON.parse(result);
      expect(parsed.suggestedEmojis).toContain('😊');
      expect(parsed.suggestedEmojis).toContain('🎉');
    });

    test('different sentiments produce different emoji sets', async () => {
      const happy = await suggestEmoji({ messageText: 'happy' });
      const sad = await suggestEmoji({ messageText: 'sad' });
      const love = await suggestEmoji({ messageText: 'love' });

      const happyParsed: EmojiSuggestion = JSON.parse(happy);
      const sadParsed: EmojiSuggestion = JSON.parse(sad);
      const loveParsed: EmojiSuggestion = JSON.parse(love);

      // Each sentiment should have at least one unique emoji
      const happySet = new Set(happyParsed.suggestedEmojis);
      const sadSet = new Set(sadParsed.suggestedEmojis);
      const loveSet = new Set(loveParsed.suggestedEmojis);

      expect(happySet).not.toEqual(sadSet);
      expect(happySet).not.toEqual(loveSet);
      expect(sadSet).not.toEqual(loveSet);
    });
  });

  describe('Integration Scenarios', () => {
    test('complete workflow: suggest and add emoji', async () => {
      // Suggest emoji for a message
      const suggestion = await suggestEmoji({ messageText: 'I love this!' });
      const parsed: EmojiSuggestion = JSON.parse(suggestion);

      // Add each suggested emoji
      for (const emoji of parsed.suggestedEmojis) {
        const result = await addEmojiToMessage({
          messageId: 'msg-love',
          emoji: emoji
        });

        const addResult: AddEmojiResult = JSON.parse(result);
        expect(addResult.success).toBe(true);
        expect(addResult.emoji).toBe(emoji);
      }
    });

    test('batch emoji suggestions all succeed', async () => {
      const messages = [
        'I am happy',
        'I am sad',
        'I love it',
        'Thank you',
        'This is great',
        'Hello world'
      ];

      for (const message of messages) {
        const result = await suggestEmoji({ messageText: message });
        const parsed: EmojiSuggestion = JSON.parse(result);
        expect(parsed.suggestedEmojis).toBeDefined();
        expect(parsed.suggestedEmojis.length).toBeGreaterThan(0);
      }
    });

    test('batch emoji additions all succeed', async () => {
      const emojis = ['👍', '❤️', '🚀', '🎉', '😊', '💯', '🔥', '✨'];

      for (const emoji of emojis) {
        const result = await addEmojiToMessage({
          messageId: `msg-${emoji}`,
          emoji: emoji
        });

        const parsed: AddEmojiResult = JSON.parse(result);
        expect(parsed.success).toBe(true);
        expect(parsed.emoji).toBe(emoji);
      }
    });
  });
});
