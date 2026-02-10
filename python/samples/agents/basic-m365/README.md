# Basic M365 Agent (Python)

AI-powered agent with weather and time functions. Requires LLM connection (Foundry/OpenAI) or recordings.

## ⚠️ How to Start This Agent

**DO NOT** run directly from this directory. Use the startup script from the repository root:

```bash
# From repository root
python scripts/ci/start_samples.py basic-m365 --lang python

# Or start with chat UI
python scripts/ci/start_samples.py basic-m365 --lang python --ui
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
python scripts/ci/start_samples.py basic-m365 --lang python
```

### Option 2: Real LLM (Production)

Create `.env` file in **repository root** (not in this directory):

```bash
# /Users/mabolan/AgentProtocol/.env
FOUNDRY_ENDPOINT=https://your-foundry-endpoint.com
FOUNDRY_API_KEY=your-api-key-here
FOUNDRY_MODEL_DEPLOYMENT=gpt-4
```

Then start:

```bash
python scripts/ci/start_samples.py basic-m365 --lang python
```

## Manual Start (Not Recommended)

If you must run manually for debugging:

```bash
# Make sure .env exists in repository root first!
cd python/samples/agents/basic-m365
python -m src.main
```

## Testing

```bash
# Test the health endpoint
curl http://localhost:3979/health

# Test with a weather query
curl -X POST http://localhost:3979/runs/wait \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What is the weather in Seattle?"}]
    }]
  }'

# Test streaming
curl -N -X POST http://localhost:3979/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What time is it?"}]
    }]
  }'
```

## CORS Configuration

The server has **fully permissive CORS** for development:
- Allows all origins (`*`)
- Allows all methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
- Allows all headers (`*`)
- Exposes all headers (`*`)

This is configured in [src/start_server.py](src/start_server.py) lines 31-49.

**⚠️ Production:** Replace with restrictive CORS policy before deploying.

## Available Functions

The agent can call these functions:
- **GetWeatherAsync** - Get weather for a location
- **GetCurrentTime** - Get current UTC time

## Port Configuration

The agent uses port **3979** by default, configured in:
- [`agent-config.json`](../../../../agent-config.json) → `bots.python-basic-m365.port`
- Or environment variable `PORT`

## Troubleshooting

### "(no response)" from Streaming

This usually means the LLM is not configured:
- ✅ **Solution 1:** Set `USE_LLM_RECORDINGS=true` for testing
- ✅ **Solution 2:** Create `.env` file in repo root with FOUNDRY_* variables
- ❌ **Don't:** Try to run without LLM configuration

### CORS Errors
- ✅ **Fixed** - CORS middleware allows all origins and headers
- The fix is in [start_server.py:31-49](src/start_server.py#L31-L49)

### Connection Refused
- Make sure the agent is running: `curl http://localhost:3979/health`
- Check logs: `cat .logs/basic-m365-python.log` (if started with script)

### Environment Variables Not Loading
- `.env` file must be in **repository root**, not in this directory
- The agent loads it from [src/start_server.py](src/start_server.py)

## Comparison: Basic M365 vs Echo M365

| Feature | Echo M365 | Basic M365 |
|---------|-----------|------------|
| LLM Required | ❌ No | ✅ Yes |
| Function Calling | ❌ No | ✅ Yes (weather, time) |
| Streaming | ✅ Yes | ✅ Yes |
| Best For | Testing protocol | Testing LLM integration |
| Configuration | None needed | Requires .env or recordings |

**For testing streaming:** Use **echo-m365** (simpler, no LLM needed)

## Related Documentation

- [Agent Protocol Documentation](../../../../docs/)
- [Startup Scripts](../../../../scripts/ci/)
- [Agent Configuration](../../../../agent-config.json)
- [LLM Recording System](../../../../docs/testing/llm-recordings.md)
