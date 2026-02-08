# Quick Setup Guide

Follow these steps to run the Agent Protocol Chat Demo.

## Step 1: Install Dependencies

From the repository root:

```bash
cd /Users/mabolan/AgentProtocol
npm install
```

This will install all dependencies for the monorepo including the demo app.

## Step 2: Build the Packages

Build the protocol types, client, and React UI packages:

```bash
npm run build
```

This compiles:
- `@microsoft/agents-protocol-types` - Generated TypeScript types
- `@microsoft/agents-protocol-client` - API client
- `@microsoft/agents-react-ui` - React UI components

## Step 3: Start an Echo Bot

You need at least one echo bot running. Choose one:

### Option A: .NET Echo Bot (Recommended)

```bash
cd dotnet/samples/agents/EchoBot
dotnet run
```

The bot will start on **port 3978**.

### Option B: Python Echo Bot

```bash
cd python/samples/agents/echo-bot
PORT=3979 python -m src.main
```

The bot will start on **port 3979** (to avoid conflict with .NET).

### Option C: TypeScript Echo Bot

_Coming soon - This needs to be implemented._

## Step 4: Run the Demo

In a new terminal, from the repository root:

```bash
npm run demo
```

Or navigate to the demo directory:

```bash
cd javascript/samples/chat-demo
npm run dev
```

The demo will be available at: **http://localhost:3000**

## Step 5: Use the Demo

1. **Select a Bot**: Click on one of the bot options (make sure it's running!)
2. **Check Connection**: Look for the "Connected" badge
3. **Start Chatting**: Type a message and the bot will echo it back
4. **Try Dark Mode**: Toggle the theme switcher

## Troubleshooting

### "Cannot connect to EchoBot"

- Make sure the bot is running on the expected port
- Check that you selected the correct bot implementation
- Verify no firewall is blocking the connection

### Build Errors

```bash
# Clean and rebuild
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Port Already in Use

If port 3978 is already in use for the .NET bot, you can change it:

In `dotnet/samples/agents/EchoBot/Program.cs`, change:
```csharp
app.Urls.Add($"http://localhost:3978");
```

Then update the port in `javascript/samples/chat-demo/src/App.tsx`.

## Running Multiple Bots

To see all implementations working simultaneously:

**Terminal 1 - .NET Bot:**
```bash
cd dotnet/samples/agents/EchoBot
dotnet run
```

**Terminal 2 - Python Bot:**
```bash
cd python/samples/agents/echo-bot
PORT=3979 python -m src.main
```

**Terminal 3 - Demo App:**
```bash
npm run demo
```

Now you can switch between bots in the UI!

## Next Steps

- Explore the [examples](../../packages/agents-react-ui/examples) for more UI patterns
- Read the [React UI documentation](../../packages/agents-react-ui/README.md)
- Check out the [Protocol Client docs](../../packages/agents-protocol-client/README.md)
- Implement your own bot using the protocol!
