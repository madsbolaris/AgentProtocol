# Basic M365 Agent (.NET)

AI-powered agent with weather and time functions. Requires LLM connection (Foundry/OpenAI) or recordings.

## ⚠️ How to Start This Agent

**DO NOT** run `dotnet run` directly from this directory. Use the startup script from the repository root:

```bash
# From repository root
python scripts/ci/start_samples.py basic-m365 --lang dotnet

# Or start with chat UI
python scripts/ci/start_samples.py basic-m365 --lang dotnet --ui
```

**Why?** The startup script:
- ✅ Sets correct environment variables (PORT from agent-config.json)
- ✅ Configures logging to `.logs/` directory
- ✅ Handles graceful shutdown
- ✅ Optionally starts the chat UI

## Prerequisites

This agent requires **LLM configuration**. Choose one:

### Option 1: LLM Recordings (Testing)

```bash
# Set environment variable
export USE_LLM_RECORDINGS=true

# Then start normally
python scripts/ci/start_samples.py basic-m365 --lang dotnet
```

### Option 2: Real LLM (Production)

Create `.env` file in **repository root** (not in this directory):

```bash
# /Users/mabolan/AgentProtocol/.env
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.com
FOUNDRY_API_KEY=your-api-key-here
FOUNDRY_MODEL_DEPLOYMENT=gpt-4
```

The agent loads this from [Program.cs](Program.cs) lines 20-37.

Then start:

```bash
python scripts/ci/start_samples.py basic-m365 --lang dotnet
```

## Port Configuration

This agent uses port **3981** by default, configured in:
- [`agent-config.json`](../../../../agent-config.json) → `bots.dotnet-basic-m365.port`
- Or environment variable `PORT`

## Testing

```bash
# Test the health endpoint
curl http://localhost:3981/health

# Test with a weather query
curl -X POST http://localhost:3981/runs/wait \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What is the weather in Seattle?"}]
    }]
  }'

# Test streaming
curl -N -X POST http://localhost:3981/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What time is it?"}]
    }]
  }'
```

## Available Functions

The agent can call these functions (see [BasicM365Agent.cs](BasicM365Agent.cs)):
- **GetWeatherAsync** - Get weather for a location
- **GetCurrentTime** - Get current UTC time

## Troubleshooting

### "(no response)" from Streaming

This means the LLM is not configured:
- ✅ **Solution 1:** Set `USE_LLM_RECORDINGS=true` for testing
- ✅ **Solution 2:** Create `.env` file in repo root with FOUNDRY_* variables
- ✅ **Solution 3:** Use echo-m365 instead (no LLM needed)

### Environment Variables Not Loading
- `.env` file must be in **repository root**, not in this directory
- The agent loads it from [Program.cs](Program.cs) lines 20-37

## CORS Configuration

The server has **fully permissive CORS** for development (configured in [Program.cs](Program.cs)):
```csharp
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});
```

**⚠️ Production:** Replace with restrictive CORS policy before deploying.

## Comparison: Basic M365 vs Echo M365

| Feature | Echo M365 | Basic M365 |
|---------|-----------|------------|
| LLM Required | ❌ No | ✅ Yes |
| Function Calling | ❌ No | ✅ Yes (weather, time) |
| Best For | Testing protocol | Testing LLM integration |

**For testing streaming:** Use **echo-m365** (simpler, no LLM needed)

## Related Documentation

- [How to Start Agents](../../../../HOW_TO_START_AGENTS.md)
- [Startup Scripts](../../../../scripts/ci/)
- [Agent Configuration](../../../../agent-config.json)
- [LLM Recording System](../../../../docs/testing/llm-recordings.md)
