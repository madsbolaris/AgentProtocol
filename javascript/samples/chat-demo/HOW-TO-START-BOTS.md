# How to Start the Echo Bots

Both echo bot implementations need dependencies installed. Here are the solutions:

## ✅ Solution 1: Fix .NET Echo Bot (Recommended)

The .NET echo bot needs access to private NuGet feeds. **I've already created a local NuGet.Config** to work around this.

### Steps:

1. **Open a terminal** in the EchoBot directory:
```bash
cd /Users/mabolan/AgentProtocol/dotnet/samples/agents/EchoBot
```

2. **Temporarily update your credentials** in `~/.nuget/NuGet/NuGet.Config`:
   - The PAT (Personal Access Token) may have expired
   - OR remove the private feeds from the global config temporarily

3. **Restore and run**:
```bash
dotnet restore
dotnet run
```

### Alternative: Use Public NuGet Only

If you don't need the latest packages, you can remove the private feed dependencies entirely by commenting out the PackageReferences in `QuickStart.csproj` that aren't available on nuget.org.

---

## ✅ Solution 2: Use Python Echo Bot

The Python echo bot needs Python packages installed.

### Steps:

1. **Install Python dependencies**:
```bash
cd /Users/mabolan/AgentProtocol/python/samples/agents/echo-bot
pip install -r requirements.txt

# Or if there's no requirements.txt:
cd ../../..  # Go to python root
pip install -e ./microsoft-agents-hosting
pip install -e ./microsoft-agents-authentication
pip install -e ./microsoft-agents-activity
```

2. **Run the bot**:
```bash
cd samples/agents/echo-bot
python -m src.main
```

---

## ✅ Solution 3: Mock Echo Bot (Quick Test)

For immediate testing, I can create a simple standalone mock echo bot that doesn't require any dependencies.

### Mock Bot Features:
- Runs on port 3978
- Implements basic Bot Framework protocol
- Echoes messages back
- Works immediately without any setup

**Would you like me to create this mock bot?**

---

## Current Status

| Bot | Status | Issue |
|-----|--------|-------|
| .NET EchoBot | ❌ Not running | Private NuGet feed authentication required |
| Python EchoBot | ❌ Not running | Python packages not installed |
| Demo Website | ✅ Open in browser | Waiting for bot connection |

---

## What I Recommend

**Option A (Fastest):** Let me create a simple mock echo bot in Node.js/Python that runs immediately.

**Option B (Production):** Fix the .NET bot's NuGet authentication:
- Update the PAT in ~/.nuget/NuGet/NuGet.Config
- OR temporarily disable private feeds
- Then run `dotnet restore && dotnet run`

**Option C (Python):** Install Python packages and run the Python bot.

---

## Testing the Demo

Once any bot is running on port 3978:

1. **Refresh the browser** with the demo
2. **Watch the status indicator** turn green
3. **Type a message** and press Enter
4. **See the bot echo** your message back!

---

Which solution would you like to try?
