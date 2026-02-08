# Echo Bot Scripts

This directory contains scripts for managing echo bot samples across all language SDKs.

## Port Configuration

Echo bots for each language are configured to run on different ports to enable simultaneous execution during development and testing. Ports are configured in [`echo-bot-ports.json`](../echo-bot-ports.json) at the project root:

```json
{
  "python": 3978,
  "dotnet": 3979,
  "typescript": 3980
}
```

All echo bots read the `PORT` environment variable, allowing easy override without code changes.

## Starting Echo Bots

### Start All Echo Bots Simultaneously

**Linux/macOS:**
```bash
./scripts/start-all-echo-bots.sh
```

**Windows:**
```powershell
.\scripts\start-all-echo-bots.ps1
```

This will:
- Read port configuration from `echo-bot-ports.json`
- Start all three echo bots (Python, .NET, TypeScript) on their configured ports
- Log output to `.logs/` directory
- Wait for Ctrl+C to stop all bots

### Start Individual Echo Bots

**Python:**
```bash
cd python/samples/agents/echo-bot
PORT=3978 python src/start_server.py
```

**.NET:**
```bash
cd dotnet/samples/agents/EchoBot
PORT=3979 dotnet run
```

**TypeScript:**
```bash
cd typescript/samples/echo-bot
PORT=3980 npm start
```

## Testing Echo Bots

Once running, test the health endpoint for each:

```bash
curl http://localhost:3978/health  # Python
curl http://localhost:3979/health  # .NET
curl http://localhost:3980/health  # TypeScript
```

Test the Agent Protocol endpoints:

```bash
# Create and wait for a run
curl -X POST http://localhost:3978/runs/wait \
  -H "Content-Type: application/json" \
  -d '{
    "agentId": "echo-bot",
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "Hello!"}]
    }]
  }'
```

## Echo Bot Validation

The `validate-echo-bots.py` script ensures echo bot samples remain minimal and don't drift from their baseline implementations.

### Validate Echo Bots

```bash
python3 scripts/validate-echo-bots.py
```

This computes SHA256 hashes of all tracked echo bot files and compares them against `echo-bot-snapshots.json`.

### Update Snapshots

When you intentionally modify echo bot samples (like adding port configuration support), update the snapshots:

```bash
python3 scripts/validate-echo-bots.py --update
```

⚠️ **Warning:** Only update snapshots when you've made intentional, approved changes to echo bots. Always commit the updated `echo-bot-snapshots.json` file.

### CI/CD Validation

Echo bot validation runs automatically in GitHub Actions on every push and pull request. See `.github/workflows/test-and-docs.yml` for the pipeline configuration.

## Copying Echo Bots from M365 Agents SDK

To refresh echo bot samples from the upstream M365 Agents SDK:

```bash
./scripts/copy-echo-bots.sh
```

This will:
- Delete existing echo bot samples
- Copy fresh samples from `~/repos/Agents/samples/`
- You'll need to re-apply Agent Protocol integrations after copying

## File Structure

```
scripts/
├── README-echo-bots.md           # This file
├── start-all-echo-bots.sh        # Start all bots (Linux/macOS)
├── start-all-echo-bots.ps1       # Start all bots (Windows)
├── validate-echo-bots.py         # Validate bot samples
├── echo-bot-snapshots.json       # SHA256 hash snapshots
└── copy-echo-bots.sh             # Copy from M365 SDK

echo-bot-ports.json                # Port configuration (project root)

.logs/                             # Log output from running bots
├── python-echo-bot.log
├── dotnet-echo-bot.log
└── typescript-echo-bot.log
```

## Architecture

Echo bots demonstrate minimal integration with the Agent Protocol:

- **Python**: Uses `add_agent_protocol_routes(app, agent_application)` from `microsoft.agents.protocol.server`
- **.NET**: Uses `app.MapAgentProtocol()` from `Microsoft.Agents.Protocol.Server`
- **TypeScript**: Uses `createAgentProtocolRouter(agentApp)` from `@microsoft/agents-protocol`

All Agent Protocol complexity (message translation, run management, SSE streaming) is handled by the respective SDKs, keeping echo bot samples minimal (typically 1-2 lines of code for Agent Protocol support).
