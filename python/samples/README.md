# Agent Protocol Samples (Python)

This directory contains sample implementations for the Agent Protocol in Python.

## Structure

```
samples/
├── agents/          # Agent implementations
│   └── echo-bot/    # Simple echo bot agent
└── hooks/           # Hook service implementations
    ├── block-hook/          # Content blocking
    ├── modify-hook/         # PII redaction
    ├── telemetry-hook/      # Audit logging
    ├── sendmessage-hook/    # Quality control
    └── remote-hook/         # Full-featured hook
```

## Agent Samples

### [echo-bot](agents/echo-bot/) - Full Agent 365 SDK
A comprehensive agent sample using Agent Framework with the Microsoft Agent 365 SDK.

**Features:**
- **Agent Protocol routes** - Added in one line of code
- **AgentFramework integration** - Using Azure OpenAI
- **MCP tooling** - Model Context Protocol for dynamic tools
- **Observability** - End-to-end tracing and monitoring
- **Notifications** - Email and Word document notifications
- **Centralized config** - Port configuration from `/agent-config.json`

**Requires:** Full Agent 365 SDK stack (agent-framework, microsoft_agents_a365, etc.)

### [simple-echo-bot](agents/simple-echo-bot/) - Protocol Test
A minimal echo bot for testing the Agent Protocol package without the full SDK stack.

**Features:**
- Minimal dependencies (aiohttp + microsoft-agents-protocol)
- Agent Protocol routes integration
- Quick verification and testing

**Use for:** Protocol testing, understanding basic integration pattern

**Port:** 3979 (from agent-config.json)

## Hook Samples

Hook services intercept and process agent events to enable content moderation, PII redaction, audit logging, and quality control.

### [block-hook](hooks/block-hook/)
Blocks content based on prohibited keywords.

**Port:** 5001
**Use Case:** Content moderation, policy enforcement

### [modify-hook](hooks/modify-hook/)
Redacts PII (emails, phone numbers, SSN, credit cards) from content.

**Port:** 5002
**Use Case:** GDPR/CCPA compliance, data protection

### [telemetry-hook](hooks/telemetry-hook/)
Collects telemetry and audit logs for all agent events.

**Port:** 5003
**Use Case:** Compliance auditing, monitoring, analytics

### [sendmessage-hook](hooks/sendmessage-hook/)
Injects messages to improve response quality through LLM regeneration.

**Port:** 5004
**Use Case:** Quality control, tone enforcement, iterative refinement

### [remote-hook](hooks/remote-hook/)
Full-featured hook service combining all capabilities with runtime configuration.

**Port:** 5005
**Use Case:** Production-ready content moderation and compliance

## Getting Started

### Prerequisites
- Python 3.8 or later
- pip

### Running Agent Samples

```bash
cd agents/echo-bot
pip install -r requirements.txt
python -m src.main
```

### Running Hook Samples

Each hook sample can be run independently:

```bash
cd hooks/block-hook
pip install -r requirements.txt
python main.py
```

The service will start on the configured port (see individual README files).

### Interactive API Documentation

All hook samples provide interactive API documentation via FastAPI:

Visit `http://localhost:{PORT}/docs` (e.g., `http://localhost:5001/docs`)

## Hook Configuration

To use a hook with your agent, configure it in your agent's lifecycle hooks:

```json
{
  "beforeRun": [
    {
      "kind": "remote",
      "name": "content-filter",
      "endpoint": "http://localhost:5001/api/hooks/block",
      "condition": {
        "kind": "content",
        "contentTypes": ["text"]
      }
    }
  ]
}
```

## Documentation

- [Agent Protocol Specification](../../specs/)
- [Hooks Specification](../../docs/specifications/hooks.md)
- [Hook SDK Documentation](../../python/microsoft-agents-hooks/)

## Contributing

When adding new samples:
1. Place agent samples in `agents/`
2. Place hook samples in `hooks/`
3. Include a README.md with usage instructions
4. Include a requirements.txt file
5. Follow existing naming and structure patterns
