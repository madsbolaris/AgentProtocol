# Quick Start - Run the Demo Now

## Automated Issues

The automated setup encountered workspace protocol issues with npm. Here's how to run it manually:

## Step 1: Start the Echo Bot

**Open a new terminal** and run:

```bash
cd /Users/mabolan/AgentProtocol/dotnet/samples/agents/EchoBot
dotnet run
```

You should see:
```
info: Microsoft.Hosting.Lifetime[14]
      Now listening on: http://localhost:3978
```

Keep this terminal open!

## Step 2: Test the Bot

**In another terminal:**

```bash
curl http://localhost:3978/
```

Should return: `Agent Framework Protocol SDK Sample`

## Step 3: Option A - Use a Simple HTML Demo

I've created a standalone HTML file that works without build steps:

```bash
cd /Users/mabolan/AgentProtocol/javascript/samples/chat-demo
open simple-demo.html
```

This opens directly in your browser - no build needed!

## Step 3: Option B - Build and Run Full Demo

If you want the full demo with all features:

### Fix Workspace Issues

```bash
cd /Users/mabolan/AgentProtocol/javascript/samples/chat-demo

# Remove workspace references temporarily
npm init -y
npm install react react-dom vite @vitejs/plugin-react typescript @types/react @types/react-dom

# Then manually build the dependent packages first
cd ../../packages/agents-protocol-types
npm install
npm run build

cd ../agents-protocol-client
npm install
npm run build

cd ../agents-react-ui
npm install
npm run build

# Go back to demo
cd ../../samples/chat-demo
npm install
npm run dev
```

## Alternative: Use Python Echo Bot

If .NET doesn't work, use Python:

```bash
cd /Users/mabolan/AgentProtocol/python/samples/agents/echo-bot
python -m src.main
```

## What You Should See

1. **Console Output**: Bot logs showing it's receiving and responding to messages
2. **Chat Interface**: A beautiful gradient header, bot selector, theme toggle, and chat window
3. **Echo Responses**: Whatever you type, the bot echoes back with "You said: [your message]"

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 3978
lsof -i :3978

# Kill it if needed
kill -9 <PID>
```

### Bot Won't Start

Make sure you have .NET SDK installed:
```bash
dotnet --version
```

Should be 8.0 or higher.

### CORS Errors

Make sure you're accessing through the dev server, not file:// protocol (unless using simple-demo.html).

## Next Steps

Once you have it running:
1. Try switching between light and dark themes
2. Type various messages and see them echoed
3. Look at the browser console to see API calls
4. Explore the source code in `src/App.tsx`

Enjoy! 🎉
