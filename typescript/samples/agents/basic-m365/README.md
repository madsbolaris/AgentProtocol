# Basic M365 Agent (TypeScript)

AI-powered agent with weather and time functions. Requires LLM connection (Foundry/OpenAI) or recordings.

## ⚠️ How to Start This Agent

**DO NOT** run `npm start` directly from this directory. Use the startup script from the repository root:

```bash
# From repository root
python scripts/ci/start_samples.py basic-m365 --lang typescript

# Or start with chat UI
python scripts/ci/start_samples.py basic-m365 --lang typescript --ui
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
python scripts/ci/start_samples.py basic-m365 --lang typescript
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
python scripts/ci/start_samples.py basic-m365 --lang typescript
```

## Port Configuration

This agent uses port **3983** by default, configured in:
- [`agent-config.json`](../../../../agent-config.json) → `bots.typescript-basic-m365.port`
- Or environment variable `PORT`

## Testing

```bash
# Test the health endpoint
curl http://localhost:3983/health

# Test with a weather query
curl -X POST http://localhost:3983/runs/wait \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What is the weather in Seattle?"}]
    }]
  }'

# Test streaming
curl -N -X POST http://localhost:3983/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "What time is it?"}]
    }]
  }'
```

## Available Functions

The agent can call these functions:
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

## CORS Configuration

The server has **fully permissive CORS** for development (configured in [src/index.ts](src/index.ts) lines 12-21):
```typescript
server.use((_req, res, next) => {
  res.header('Access-Control-Allow-Origin', '*')
  res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
  res.header('Access-Control-Allow-Headers', '*')
  res.header('Access-Control-Expose-Headers', '*')
  // ...
})
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
