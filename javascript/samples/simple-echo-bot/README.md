# Simple Echo Bot

A minimal Bot Framework-compatible echo bot for testing the Agent Protocol React UI demo.

## Features

- ✅ **Zero configuration** - Just install and run
- ✅ **Bot Framework compatible** - Works with the protocol
- ✅ **Simple echo** - Repeats back everything you say
- ✅ **CORS enabled** - Works with the web demo
- ✅ **Clear logging** - See every message in the console

## Quick Start

```bash
# Install dependencies
npm install

# Start the bot
npm start
```

The bot will be available at **http://localhost:3978**

## Usage with Demo

1. **Start this bot** (in one terminal):
   ```bash
   cd /Users/mabolan/AgentProtocol/javascript/samples/simple-echo-bot
   npm install
   npm start
   ```

2. **Refresh your browser** with the demo already open

3. **Watch the connection status** turn green

4. **Start chatting!** Type any message and see it echoed back

## How It Works

The bot implements a minimal Bot Framework Activity protocol:

- **GET /** - Health check endpoint
- **POST /api/messages** - Receives Bot Framework Activities

When it receives a message activity, it:
1. Logs the incoming message
2. Creates a response activity with "You said: [your message]"
3. Returns the response

That's it! Simple and effective for testing.

## Troubleshooting

### Port Already in Use

If port 3978 is already taken:
```bash
lsof -i :3978
kill -9 <PID>
```

### Demo Not Connecting

1. Make sure the bot is running (you should see "Ready to receive messages!")
2. Refresh your browser with the demo
3. Check the browser console for errors
4. Verify the bot logs show no errors

## Next Steps

Once you have this working, you can:
- Try the .NET or Python echo bots for comparison
- Modify this bot to add custom responses
- Add more complex conversational logic
- Integrate with AI services

Enjoy! 🎉
