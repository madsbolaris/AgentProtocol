# ⚠️ How to Start This Agent

**DO NOT** run `npm start` directly from this directory!

## Use the Startup Script

```bash
# From repository root
python scripts/ci/start_samples.py echo-m365 --lang typescript

# Or start with chat UI
python scripts/ci/start_samples.py echo-m365 --lang typescript --ui
```

## Why?

The startup script:
- ✅ Sets correct PORT from agent-config.json
- ✅ Logs to `.logs/` directory
- ✅ Handles graceful shutdown
- ✅ Optionally starts chat UI

See [HOW_TO_START_AGENTS.md](../../../../HOW_TO_START_AGENTS.md) for details.
