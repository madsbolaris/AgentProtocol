# Agent Protocol Demo - Quick Start

This is a unified demo that lets you select and chat with different Agent Protocol bots.

## 🚀 Quick Start

### 1. Start the Demo Server

```bash
cd demos
node start-demo.js
```

This starts the web UI on **http://localhost:3000**

### 2. Start a Bot

The quick emoji bot is already included. Start it with:

```bash
cd demos/echo-m365-js
npm start
```

This starts the emoji bot on **http://localhost:3984**

### 3. Open the Demo

Open **http://localhost:3000** in your browser.

- Select "EmojiChatBot (.NET)" from the dropdown
- Start chatting!

## 📁 File Structure

```
AgentProtocol/
├── agent-config.json        # Bot configuration (dropdown reads from here)
└── demos/
    ├── agent-demo.html      # Main demo UI (standalone, no build required)
    ├── start-demo.js        # Demo server
    ├── DEMO-QUICKSTART.md   # This file
    └── echo-m365-js/        # Simple JS echo bot for testing
        ├── server.js        # Bot implementation
        └── package.json
```

## 🤖 Available Bots

The demo reads from `agent-config.json` and displays all configured bots in a dropdown:

- **EchoM365 (.NET)** - Port 3978
- **EchoM365 (Python)** - Port 3979
- **EchoM365 (TypeScript)** - Port 3980
- **EmojiChatBot (.NET)** - Port 3984
- **Quick Emoji Bot (Node.js)** - Port 3984 ✅ (Currently running)

## 🎨 Features

- **Bot Selector Dropdown** - Choose any bot from agent-config.json
- **Live Connection Status** - See if the bot is reachable
- **Chat Interface** - Clean, modern UI
- **No Build Required** - Pure HTML/JS, works immediately
- **Agent Protocol Compliant** - Standard POST to `/api/messages`

## 🔧 Adding New Bots

1. Add your bot to `agent-config.json`:

```json
{
  "bots": {
    "my-bot": {
      "name": "My Cool Bot",
      "port": 4000,
      "baseUrl": "http://localhost"
    }
  }
}
```

2. Implement the Agent Protocol endpoints:
   - `GET /health` - Health check
   - `POST /api/messages` - Handle messages

3. Start your bot on the specified port

4. Refresh the demo - your bot appears in the dropdown!

## 📝 Testing with the Quick Emoji Bot

Try these messages:
- "I'm feeling happy!" → 😊 🎉 👍 ✨
- "I'm sad" → 😢 💔 🤗 🫂
- "I love this!" → ❤️ 💕 😍 💖
- "Thank you so much" → 🙏 😊 👍 💝

## 🗑️ Removed/Deprecated

The following have been consolidated into this single demo:

- `javascript/samples/echo-m365-demo/` (incomplete implementation)
- `javascript/samples/chat-demo/` (had build issues)
- `quick-emoji-bot/test-ui.html` (merged into main demo)

Everything is now in one place: **agent-demo.html** served by **start-demo.js**

## 🐛 Troubleshooting

**Bot not connecting?**
1. Make sure the bot is running: `curl http://localhost:PORT/health`
2. Check the browser console for errors
3. Verify the port in `agent-config.json` matches your bot

**Demo won't start?**
1. Check if port 3000 is available: `lsof -i :3000`
2. Install dependencies: `npm install express cors`
3. Make sure you're in the right directory

**Can't see any bots in dropdown?**
1. Check `agent-config.json` exists and is valid JSON
2. Look in browser console for fetch errors
3. Refresh the page

## ✅ What's Working

- ✅ Single unified demo with bot selector dropdown
- ✅ Reads bot configuration from agent-config.json
- ✅ Quick emoji bot (Node.js) working on port 3984
- ✅ Clean, modern UI with status indicators
- ✅ No build system required
- ✅ Ready to test with any Agent Protocol bot
