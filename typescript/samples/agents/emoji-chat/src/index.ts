/**
 * Emoji Chat Bot Sample
 *
 * Demonstrates:
 * 1. Tool/function calling with the Hosting SDK
 * 2. User message event handling
 * 3. Emoji reaction handling
 * 4. State management (message count, last emoji used)
 *
 * This sample mirrors the .NET EmojiChatBot implementation using the TypeScript Hosting SDK.
 */

import {
  AgentHostBuilder,
  TurnResult,
  ChatMessage,
  ReactionContent,
  IAgentContext
} from '@microsoft/agents-protocol-hosting';
import { AddEmojiResult, EmojiSuggestion, ChatContext } from './types.js';
import * as fs from 'fs';
import * as path from 'path';

// __dirname is available in CommonJS
// const __dirname is available globally in CommonJS modules

/**
 * Tool: Add an emoji reaction to a specific message.
 * The LLM can call this tool when users ask to add reactions or emojis.
 */
async function addEmojiToMessage(params: {
  messageId: string;
  emoji: string;
}): Promise<string> {
  // In a real implementation, this would call an API to add the reaction
  // For this demo, we'll just return a success message

  const result: AddEmojiResult = {
    success: true,
    messageId: params.messageId,
    emoji: params.emoji,
    message: `Added ${params.emoji} reaction to message ${params.messageId}`
  };

  return JSON.stringify(result);
}

/**
 * Tool: Suggest appropriate emojis based on message sentiment.
 */
async function suggestEmoji(params: { messageText: string }): Promise<string> {
  // Simple sentiment-based emoji suggestion
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

/**
 * Handler for user messages.
 * Increments message count and logs the message.
 */
async function onUserMessage(
  message: ChatMessage,
  context: IAgentContext,
  cancellationToken?: AbortSignal
): Promise<TurnResult> {
  // Get current state
  const chatContext = await context.getStateAsync<ChatContext>('context');
  const messageCount = (chatContext?.messageCount || 0) + 1;

  // Update state
  await context.setStateAsync<ChatContext>('context', {
    messageCount,
    lastEmojiUsed: chatContext?.lastEmojiUsed || null
  });

  // Log the message
  await context.logAsync(`User message #${messageCount}: ${message.text}`, 'info');

  // Handle special commands
  if (message.text.toLowerCase() === '/help') {
    await context.respondAsync(
      '👋 Welcome to Emoji Chat Bot!\n\n' +
      'I can help you with emojis! Try asking me to:\n' +
      '- Add an emoji reaction to a message\n' +
      '- Suggest emojis for a message\n' +
      '- React to messages with emojis\n\n' +
      `You've sent ${messageCount} message(s) in this conversation.`
    );
    return TurnResult.Replied;
  }

  if (message.text.toLowerCase() === '/stats') {
    const ctx = await context.getStateAsync<ChatContext>('context');
    const lastEmoji = ctx?.lastEmojiUsed || 'none';
    await context.respondAsync(
      `📊 Conversation Stats:\n` +
      `- Messages: ${messageCount}\n` +
      `- Last emoji used: ${lastEmoji}`
    );
    return TurnResult.Replied;
  }

  // Let the LLM handle other messages
  return TurnResult.Continue;
}

/**
 * Handler for emoji reactions.
 * Responds to user reactions and tracks the last emoji used.
 */
async function onReaction(
  reaction: ReactionContent,
  context: IAgentContext,
  cancellationToken?: AbortSignal
): Promise<TurnResult> {
  // Get emoji
  const emoji = reaction.emoji || '?';

  // Update context to remember the last emoji
  const chatContext = await context.getStateAsync<ChatContext>('context');
  await context.setStateAsync<ChatContext>('context', {
    messageCount: chatContext?.messageCount || 0,
    lastEmojiUsed: emoji
  });

  // Log the reaction
  await context.logAsync(`User reacted with ${emoji}`, 'info');

  // Respond to the reaction
  await context.respondAsync(
    `I see you reacted with ${emoji}! That's a great choice! 😊`
  );

  return TurnResult.Replied;
}

/**
 * Helper function to read port from centralized agent-config.json
 * Falls back to environment variable PORT, then default 3984
 */
function getPortFromConfig(): number {
  try {
    // Navigate up to repository root (4 levels up from src directory)
    const configPath = path.join(__dirname, '..', '..', '..', '..', 'agent-config.json');

    if (fs.existsSync(configPath)) {
      const configContent = fs.readFileSync(configPath, 'utf-8');
      const config = JSON.parse(configContent);

      if (config?.bots?.['typescript-emoji-chat']?.port) {
        return config.bots['typescript-emoji-chat'].port;
      }
    }
  } catch (error) {
    console.log('Note: Could not read agent-config.json, using default port');
  }

  return parseInt(process.env.PORT || '3986', 10);
}

// Get model from environment (matches basic-m365 pattern)
const model = process.env.FOUNDRY_MODEL_DEPLOYMENT || 'gpt-4';

// Create the agent host using the fluent builder API
const agentHost = new AgentHostBuilder()
  .addDefaultAgent(agent => agent
    .useLLM(
      model,
      'You are an emoji bot assistant. You help users add emojis to messages and react with emojis. ' +
      'You have access to two tools: addEmojiToMessage and suggestEmoji. ' +
      'Be friendly and enthusiastic about emojis!'
    )
    .addFunctions(f => f
      .add(
        'addEmojiToMessage@v1',
        'Add an emoji reaction to a specific message. Use this when the user wants to react to a message with an emoji.',
        {
          type: 'object',
          properties: {
            messageId: {
              type: 'string',
              description: 'The ID of the message to add emoji to'
            },
            emoji: {
              type: 'string',
              description: "The emoji to add (e.g., '👍', '❤️', '😊')"
            }
          },
          required: ['messageId', 'emoji']
        },
        addEmojiToMessage,
        { trustLevel: 'trusted' }
      )
      .add(
        'suggestEmoji@v1',
        'Suggest appropriate emojis based on the sentiment or content of a message.',
        {
          type: 'object',
          properties: {
            messageText: {
              type: 'string',
              description: 'The message text to analyze'
            }
          },
          required: ['messageText']
        },
        suggestEmoji,
        { trustLevel: 'trusted' }
      )
    )
    .onUserMessage(onUserMessage)
    .onReaction(onReaction)
  )
  .build();

// Start the agent
const port = getPortFromConfig();

agentHost.start(port)
  .then(() => {
    console.log('🤖 Emoji Chat Bot Sample');
    console.log('========================');
    console.log(`✓ Agent running on http://localhost:${port}`);
    console.log('✓ Ready to accept requests');
    console.log('\nFeatures:');
    console.log('- Add emoji reactions to messages');
    console.log('- Suggest emojis based on sentiment');
    console.log('- Track message count and last emoji used');
    console.log('\nCommands:');
    console.log('- /help - Show help message');
    console.log('- /stats - Show conversation statistics');
    console.log('\nPress Ctrl+C to stop');
  })
  .catch((error: Error) => {
    console.error('✗ Failed to start agent:', error.message);
    console.error('Stack trace:', error.stack);
    process.exit(1);
  });

// Graceful shutdown
process.on('SIGTERM', async () => {
  console.log('\nReceived SIGTERM, shutting down gracefully...');
  try {
    await agentHost.stop();
    console.log('Agent stopped successfully');
    process.exit(0);
  } catch (error) {
    console.error('Error during shutdown:', error);
    process.exit(1);
  }
});

process.on('SIGINT', async () => {
  console.log('\nReceived SIGINT, shutting down gracefully...');
  try {
    await agentHost.stop();
    console.log('Agent stopped successfully');
    process.exit(0);
  } catch (error) {
    console.error('Error during shutdown:', error);
    process.exit(1);
  }
});
