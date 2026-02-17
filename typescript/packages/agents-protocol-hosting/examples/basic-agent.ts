/**
 * Basic Agent Example
 *
 * This example shows how to create a simple agent with functions
 * and message handlers.
 */

import {
  AgentHostBuilder,
  TurnResult,
  UserMessageHandler,
  IAgentContext,
  ChatMessage
} from '../src/index.js';

// Create a message handler
const onUserMessage: UserMessageHandler = async (
  message: ChatMessage,
  context: IAgentContext,
  cancellationToken?: AbortSignal
): Promise<TurnResult> => {
  // Log the message
  await context.logAsync(`User said: ${message.text}`);

  // Handle special commands
  if (message.text.toLowerCase() === '/help') {
    await context.respondAsync(
      'Available commands:\n' +
      '/help - Show this message\n' +
      '/time - Get current time\n' +
      '/count <text> - Count words'
    );
    return TurnResult.Replied;
  }

  // Let the LLM handle other messages
  return TurnResult.Continue;
};

// Create the agent host
const agentHost = new AgentHostBuilder()
  .addDefaultAgent(agent => agent
    .useLLM('gpt-4', 'You are a helpful assistant with a sense of humor.')
    .addFunctions(f => f
      .add('getTime@v1', 'Gets current UTC time',
        {},  // No parameters
        (): string => new Date().toISOString(),
        { trustLevel: 'trusted' }
      )
      .add('addNumbers@v1', 'Adds two numbers safely',
        {
          type: 'object',
          properties: {
            a: { type: 'number', description: 'First number' },
            b: { type: 'number', description: 'Second number' }
          },
          required: ['a', 'b']
        },
        ({ a, b }: { a: number; b: number }): string => {
          if (!Number.isFinite(a) || !Number.isFinite(b)) {
            return 'Error: Invalid numbers';
          }
          return (a + b).toString();
        },
        { trustLevel: 'trusted' }
      )
      .add('wordCount@v1', 'Counts words in text',
        {
          type: 'object',
          properties: {
            text: { type: 'string', minLength: 1, maxLength: 10000 }
          },
          required: ['text']
        },
        ({ text }: { text: string }): string => {
          if (!text || text.trim().length === 0) {
            return '0';
          }
          return text.trim().split(/\s+/).length.toString();
        },
        { trustLevel: 'trusted' }
      )
    )
    .onUserMessage(onUserMessage)
  )
  .build();

// Start the agent
const port = parseInt(process.env.PORT || '3000', 10);

agentHost.start(port)
  .then(() => {
    console.log(`✓ Agent running on http://localhost:${port}`);
    console.log('✓ Ready to accept requests');
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
