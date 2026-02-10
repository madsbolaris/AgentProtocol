# Emoji Chat Bot - Quick Start Guide

Get the Emoji Chat Bot running in 3 steps!

## Prerequisites

- Node.js 18.0.0 or higher
- npm 9.0.0 or higher

## Quick Start

### Option 1: Run from Workspace Root (Recommended)

This is the easiest way to get started as it builds all dependencies automatically:

```bash
# From the repository root
cd typescript

# Install all dependencies and link workspace packages
npm install

# Build all packages (including the hosting SDK)
npm run build

# Run the emoji chat bot
cd samples/agents/emoji-chat-bot
npm start
```

### Option 2: Build Hosting SDK First

If you prefer to build components separately:

```bash
# Build the hosting SDK
cd typescript/packages/agents-hosting
npm install
npm run build

# Install and run the sample
cd ../../samples/agents/emoji-chat-bot
npm install
npm start
```

## Verify It's Running

You should see:

```
🤖 Emoji Chat Bot Sample
========================
✓ Agent running on http://localhost:3986
✓ Ready to accept requests

Features:
- Add emoji reactions to messages
- Suggest emojis based on sentiment
- Track message count and last emoji used

Commands:
- /help - Show help message
- /stats - Show conversation statistics

Press Ctrl+C to stop
```

## Test the Agent

### Using curl

```bash
# Health check
curl http://localhost:3986/health

# Send a message
curl -X POST http://localhost:3986/runs/wait \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "emoji-bot",
    "threadId": "thread_123",
    "input": [
      {
        "role": "user",
        "contents": [
          {
            "kind": "text",
            "text": "I am so happy today!"
          }
        ]
      }
    ]
  }'
```

### Example Requests

1. **Get Help**:
```json
{
  "input": [
    {
      "role": "user",
      "contents": [{"kind": "text", "text": "/help"}]
    }
  ]
}
```

2. **Suggest Emojis**:
```json
{
  "input": [
    {
      "role": "user",
      "contents": [{"kind": "text", "text": "What emojis should I use for 'thank you so much'?"}]
    }
  ]
}
```

3. **Add Emoji to Message**:
```json
{
  "input": [
    {
      "role": "user",
      "contents": [{"kind": "text", "text": "Add a heart emoji to message msg_123"}]
    }
  ]
}
```

## Troubleshooting

### "Cannot find module '@microsoft/agents-hosting'"

Make sure you've built the hosting SDK first:

```bash
cd typescript/packages/agents-hosting
npm install
npm run build
```

### "Port 3986 is already in use"

Change the port using the PORT environment variable:

```bash
PORT=4000 npm start
```

### TypeScript compilation errors

Clean and rebuild:

```bash
npm run clean
npm run build
```

## Next Steps

- Read the full [README.md](./README.md) for detailed documentation
- Check out the [.NET version](../../../../dotnet/samples/agents/EmojiChatBot/) for comparison
- Explore the [Agent Hosting SDK](../../../packages/agents-hosting/)

## Development Tips

### Watch Mode

For active development, use watch mode to rebuild automatically:

```bash
# In one terminal - watch the hosting SDK
cd typescript/packages/agents-hosting
npm run dev

# In another terminal - watch the sample
cd typescript/samples/agents/emoji-chat-bot
tsc --build --watch
```

### Hot Reload

Use nodemon for automatic restarts on file changes:

```bash
npm install -g nodemon
npm run build
nodemon --watch dist --exec node dist/src/index.js
```
