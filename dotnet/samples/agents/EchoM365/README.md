# Echo M365 Agent (.NET)

Simple echo agent that responds to messages by echoing them back. Perfect for testing the Agent Protocol without requiring LLM configuration.

## ⚠️ How to Start This Agent

**DO NOT** run `dotnet run` directly from this directory. Use the startup script from the repository root:

```bash
# From repository root
python scripts/ci/start_samples.py echo-m365 --lang dotnet

# Or start with chat UI
python scripts/ci/start_samples.py echo-m365 --lang dotnet --ui
```

**Why?** The startup script:
- ✅ Sets correct environment variables (PORT from agent-config.json)
- ✅ Configures logging to `.logs/` directory
- ✅ Handles graceful shutdown
- ✅ Optionally starts the chat UI

## Port Configuration

This agent uses port **3980** by default, configured in:
- [`agent-config.json`](../../../../agent-config.json) → `bots.dotnet.port`
- Or environment variable `PORT`

## Testing

```bash
# Test the health endpoint
curl http://localhost:3980/health

# Test streaming
curl -N -X POST http://localhost:3980/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "input": [{
      "role": "user",
      "contents": [{"kind": "text", "text": "Hello!"}]
    }]
  }'
```

## No LLM Required

This echo agent does NOT require any configuration. It simply echoes back whatever you send.

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

## Related Documentation

- [How to Start Agents](../../../../HOW_TO_START_AGENTS.md)
- [Startup Scripts](../../../../scripts/ci/)
- [Agent Configuration](../../../../agent-config.json)
