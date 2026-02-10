# Emoji Chat Bot Sample

A TypeScript agent sample demonstrating the Agent Hosting SDK capabilities with emoji-focused functionality.

> **Note**: This sample demonstrates the complete API design for the TypeScript Hosting SDK. While the code is fully implemented and follows best practices, the underlying SDK is still under active development. See [STATUS.md](./STATUS.md) for details on what's working and what's pending.

## Features

This sample demonstrates:

1. **Tool/Function Calling** - Two functions for emoji operations:
   - `addEmojiToMessage@v1` - Add emoji reactions to messages
   - `suggestEmoji@v1` - Suggest emojis based on message sentiment

2. **User Message Handling** - Processes user messages and tracks conversation state

3. **Emoji Reaction Handling** - Responds to emoji reactions from users

4. **State Management** - Tracks:
   - Message count per conversation
   - Last emoji used

## Architecture

The sample uses the **AgentHostBuilder** fluent API from `@microsoft/agents-hosting`:

```typescript
const agentHost = new AgentHostBuilder()
  .addDefaultAgent(agent => agent
    .useLLM('gpt-4', 'You are an emoji bot assistant...')
    .addFunctions(f => f
      .add('addEmojiToMessage@v1', ...)
      .add('suggestEmoji@v1', ...)
    )
    .onUserMessage(onUserMessage)
    .onReaction(onReaction)
  )
  .build();
```

## Prerequisites

- Node.js 18.0.0 or higher
- TypeScript 5.0 or higher

## Installation

```bash
# Install dependencies
npm install

# Build the project
npm run build
```

## Running the Sample

```bash
# Run the agent
npm start

# Or run in development mode with rebuild
npm run dev
```

The agent will start on port 3984 by default. You can customize the port by:

1. Setting the `PORT` environment variable
2. Adding a configuration to `agent-config.json` at the repository root:

```json
{
  "bots": {
    "typescript-emoji-chat": {
      "port": 3984
    }
  }
}
```

## Usage

### Chat Commands

- `/help` - Show available commands and features
- `/stats` - Show conversation statistics

### Example Interactions

1. **Add emoji to a message**:

   ```text
   User: Add a thumbs up emoji to message msg_123
   Bot: [Calls addEmojiToMessage function] Added 👍 reaction to message msg_123
   ```

2. **Suggest emojis**:

   ```text
   User: What emojis should I use for "I'm so happy today!"
   Bot: [Calls suggestEmoji function] I suggest: 😊, 🎉, 👍
   ```

3. **React with emoji**:

   ```text
   User: [Reacts with ❤️]
   Bot: I see you reacted with ❤️! That's a great choice! 😊
   ```

## Project Structure

```text
emoji-chat-bot/
├── src/
│   ├── index.ts       # Main entry point with AgentHostBuilder
│   └── types.ts       # Type definitions for results and context
├── package.json       # Dependencies and scripts
├── tsconfig.json      # TypeScript configuration
└── README.md          # This file
```

## Key Concepts

### AgentHostBuilder

The builder provides a fluent API for configuring agents:

- `.useLLM(model, instructions, options?)` - Configure the LLM
- `.addFunctions(configure)` - Add callable functions/tools
- `.onUserMessage(handler)` - Handle user messages
- `.onReaction(handler)` - Handle emoji reactions

### TurnResult

Handlers return a `TurnResult` enum to control processing:

- `TurnResult.Continue` - Pass to next handler or LLM
- `TurnResult.Consumed` - Stop processing, no response needed
- `TurnResult.Replied` - Stop processing, response already sent

### State Management

Use `IAgentContext` methods to manage conversation state:

```typescript
// Get state
const context = await ctx.getStateAsync<ChatContext>('context');

// Update state
await ctx.setStateAsync('context', { messageCount: 5, lastEmojiUsed: '👍' });
```

## Development

```bash
# Build
npm run build

# Clean build artifacts
npm run clean

# Run tests
npm test

# Run tests in watch mode
npm test:watch
```

## Comparison with .NET Implementation

This TypeScript implementation mirrors the .NET EmojiChatBot at `dotnet/samples/agents/EmojiChatBot/EmojiBotAgent.cs`:

| Feature          | .NET                                    | TypeScript                                           |
| ---------------- | --------------------------------------- | ---------------------------------------------------- |
| Base class       | `AgentProtocolApplication<ChatContext>` | `AgentHostBuilder`                                   |
| Tool definition  | `[Tool]` attribute                      | `.addFunctions()`                                    |
| Event handlers   | `OnEvent<T>()`                          | `.onUserMessage()`, `.onReaction()`                  |
| State management | `context.Context`                       | `context.getStateAsync()`, `context.setStateAsync()` |
| Async functions  | `async Task<T>`                         | `async (): Promise<string>`                          |

## License

MIT

## Related Samples

- .NET version: `dotnet/samples/agents/EmojiChatBot/`
- Basic TypeScript agent: `typescript/packages/agents-hosting/examples/basic-agent.ts`
