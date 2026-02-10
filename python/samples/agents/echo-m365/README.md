# Echo M365 Agent (Python)

Simple echo agent that responds to messages by echoing them back. Perfect for testing the Agent Protocol without requiring LLM configuration.

## ⚠️ How to Start This Agent

**DO NOT** run directly from this directory. Use the startup script from the repository root:

```bash
# From repository root
python scripts/ci/start_samples.py echo-m365 --lang python

# Or start with chat UI
python scripts/ci/start_samples.py echo-m365 --lang python --ui
```

**Why?** The startup script:
- ✅ Sets correct environment variables (PORT from agent-config.json)
- ✅ Configures logging to `.logs/` directory
- ✅ Handles graceful shutdown
- ✅ Optionally starts the chat UI

## Manual Start (Not Recommended)

If you must run manually for debugging:

```bash
cd python/samples/agents/echo-m365
python -m src.main
```

Port will be 3978 (or from `PORT` environment variable).

## Testing

```bash
# Test the health endpoint
curl http://localhost:3978/health

# Test streaming (should work without CORS errors)
curl -N -X POST http://localhost:3978/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "Hello!"}]
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

## No LLM Required

This echo agent does NOT require:
- ❌ FOUNDRY_ENDPOINT
- ❌ FOUNDRY_API_KEY
- ❌ USE_LLM_RECORDINGS

It simply echoes back whatever you send.

## Port Configuration

The agent uses port **3978** by default, configured in:
- [`agent-config.json`](../../../../agent-config.json) → `bots.python.port`
- Or environment variable `PORT`

## Troubleshooting

### CORS Errors
- ✅ **Fixed** - CORS middleware allows all origins and headers
- The fix is in [start_server.py:31-49](src/start_server.py#L31-L49)

### Connection Refused
- Make sure the agent is running: `curl http://localhost:3978/health`
- Check logs: `cat .logs/echo-m365-python.log` (if started with script)

### Wrong Port
- Agent uses port from `agent-config.json` or `PORT` env var
- Chat UI typically runs on port 5173 (Vite default)
- Make sure your client is connecting to the correct port

## Related Documentation

- [Agent Protocol Documentation](../../../../docs/)
- [Startup Scripts](../../../../scripts/ci/)
- [Agent Configuration](../../../../agent-config.json)
