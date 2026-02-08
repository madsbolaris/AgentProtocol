# Agent Protocol Chat Demo

An interactive demo application showcasing the **Microsoft Agent Protocol React UI** library with the EchoBot sample implementations.

## Features

- 🎯 **Multi-Bot Support** - Switch between .NET, Python, and TypeScript bot implementations
- 😊 **Emoji Reactions** - Add emoji reactions to messages and see bot responses
- 🎨 **Theme Switching** - Light and dark mode support
- 🔌 **Real-time Connection Status** - Visual feedback for bot connectivity
- 💬 **Full Protocol Support** - Complete implementation of the Agent Protocol
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🤖 **Multiple Bot Types** - Echo bots, function tools agents, and emoji chat bots

## Prerequisites

Before running this demo, you need to have at least one echo bot running:

### .NET Echo Bot (Port 3978)

```bash
cd ../../dotnet/samples/agents/EchoBot
dotnet run
```

### Python Echo Bot (Port 3979)

```bash
cd ../../python/samples/agents/echo-bot
# Set PORT environment variable to avoid conflict with .NET bot
PORT=3979 python -m src.main
```

### TypeScript Echo Bot (Port 3980)

```bash
cd ../../typescript/samples/EchoBot
npm start
```

### FunctionTools Agent (.NET) (Port 3981)

```bash
cd ../../dotnet/samples/agents/FunctionToolsAgent
dotnet run
```

### EmojiChatBot (.NET) (Port 3984)

```bash
cd ../../dotnet/samples/agents/EmojiChatBot
dotnet run
```

## Installation

```bash
# From the root of the repository
npm install

# Or from this directory
cd javascript/samples/chat-demo
npm install
```

## Running the Demo

```bash
npm run dev
```

The demo will be available at [http://localhost:3000](http://localhost:3000)

## How It Works

### Bot Selection

The demo allows you to switch between different bot implementations:

1. **EchoBot (.NET)** - C# implementation using ASP.NET Core (Port 3978)
2. **EchoBot (Python)** - Python implementation using aiohttp (Port 3979)
3. **EchoBot (TypeScript)** - TypeScript implementation (Port 3980)
4. **FunctionToolsAgent (.NET)** - Agent with function calling capabilities (Port 3981)
5. **EmojiChatBot (.NET)** - Chatbot with emoji reactions and event handling (Port 3984)

Each bot demonstrates different capabilities of the Agent Protocol.

### Connection Status

The demo automatically tests connectivity to the selected bot and displays:
- ✅ **Connected** - Bot is running and reachable
- ❌ **Disconnected** - Bot is not running or unreachable

### Theme Selection

Toggle between light and dark themes to see how the UI adapts. The theme system uses CSS variables for easy customization.

### Emoji Reactions

The chat UI supports adding emoji reactions to messages:

1. **Hover over any message** to see the "➕" button
2. **Click the ➕ button** to open the emoji picker
3. **Select an emoji** to add it as a reaction
4. **Click a reaction again** to add another one (count increases)

When connected to the **EmojiChatBot**, the bot will:

- Respond to your emoji reactions with friendly messages
- Track the emojis you use
- Handle system events like user joining/leaving

The reaction events are sent to the bot using the Agent Protocol's `MessageReactionContent` type.

## Architecture

This demo uses:

- **[@microsoft/agents-react-ui](../../packages/agents-react-ui)** - Pre-built React components and hooks
- **[@microsoft/agents-protocol-client](../../packages/agents-protocol-client)** - Protocol client for API communication
- **[@microsoft/agents-protocol-types](../../packages/agents-protocol-types)** - TypeScript types generated from TypeSpec
- **[Vite](https://vitejs.dev/)** - Fast development server and build tool
- **[React 18](https://react.dev/)** - UI framework

## Configuration

The bot configurations are automatically loaded from the centralized `agent-config.json` file in the repository root. This ensures all samples and UIs use consistent port configurations.

The demo falls back to default configurations defined in `src/App.tsx`:

```typescript
const DEFAULT_BOT_CONFIGS: Record<BotImplementation, BotConfig> = {
  dotnet: {
    name: 'EchoBot (.NET)',
    port: 3978,
  },
  python: {
    name: 'EchoBot (Python)',
    port: 3979,
  },
  typescript: {
    name: 'EchoBot (TypeScript)',
    port: 3980,
  },
  'dotnet-function-tools': {
    name: 'FunctionToolsAgent (.NET)',
    port: 3981,
  },
  'dotnet-emoji-chat': {
    name: 'EmojiChatBot (.NET)',
    port: 3984,
  },
};
```

To change port configurations, edit the `agent-config.json` file at the repository root.

## Troubleshooting

### Bot Not Connecting

1. Make sure the bot is running on the expected port
2. Check that no firewall is blocking the connection
3. Verify the bot is listening on `localhost` (not `127.0.0.1` only)
4. Check the browser console for detailed error messages

### CORS Errors

The Vite dev server is configured to proxy API requests to avoid CORS issues. If you're still seeing CORS errors:

1. Make sure you're accessing the demo through Vite's dev server (port 3000)
2. Check that the bot has CORS configured correctly
3. Review the `vite.config.ts` proxy settings

### Build Errors

If you encounter build errors:

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Rebuild packages
cd ../../
npm run build
```

## Customization

### Changing Ports

Edit `src/App.tsx` and update the `BOT_CONFIGS` object with your desired ports.

### Adding More Bots

1. Add a new entry to `BotImplementation` type
2. Add configuration to `BOT_CONFIGS`
3. Update the UI to include your new bot option

### Custom Styling

The demo uses custom CSS in `src/App.css`. You can modify this file to change the demo's appearance. The chat component itself is styled using the default theme from `@microsoft/agents-react-ui`.

## Learn More

- [Agent Protocol Documentation](../../../docs/)
- [React UI Package](../../packages/agents-react-ui)
- [Protocol Client Package](../../packages/agents-protocol-client)
- [TypeSpec Specifications](../../../specs/typespec)

## License

MIT
