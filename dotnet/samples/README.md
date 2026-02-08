# Agent Protocol Samples (C#)

This directory contains sample implementations for the Agent Protocol in C#/.NET.

## Structure

```
samples/
├── agents/          # Agent implementations
│   └── EchoBot/     # Simple echo bot agent
└── hooks/           # Hook service implementations
    ├── BlockHook/          # Content blocking
    ├── ModifyHook/         # PII redaction
    ├── TelemetryHook/      # Audit logging
    ├── SendMessageHook/    # Quality control
    └── RemoteHook/         # Full-featured hook
```

## Agent Samples

### [EchoBot](agents/EchoBot/)
A simple agent that echoes back user messages. Great starting point for building agents.

**Features:**
- Basic message handling
- Agent Protocol compliance
- Simple conversation flow

## Hook Samples

Hook services intercept and process agent events to enable content moderation, PII redaction, audit logging, and quality control.

### [BlockHook](hooks/BlockHook/)
Blocks content based on prohibited keywords.

**Port:** 5001
**Use Case:** Content moderation, policy enforcement

### [ModifyHook](hooks/ModifyHook/)
Redacts PII (emails, phone numbers, SSN, credit cards) from content.

**Port:** 5002
**Use Case:** GDPR/CCPA compliance, data protection

### [TelemetryHook](hooks/TelemetryHook/)
Collects telemetry and audit logs for all agent events.

**Port:** 5003
**Use Case:** Compliance auditing, monitoring, analytics

### [SendMessageHook](hooks/SendMessageHook/)
Injects messages to improve response quality through LLM regeneration.

**Port:** 5004
**Use Case:** Quality control, tone enforcement, iterative refinement

### [RemoteHook](hooks/RemoteHook/)
Full-featured hook service combining all capabilities with runtime configuration.

**Port:** 5005
**Use Case:** Production-ready content moderation and compliance

## Getting Started

### Prerequisites
- .NET 8.0 SDK or later

### Running Agent Samples

```bash
cd agents/EchoBot
dotnet run
```

### Running Hook Samples

Each hook sample can be run independently:

```bash
cd hooks/BlockHook
dotnet run
```

The service will start on the configured port (see individual README files).

## Hook Configuration

To use a hook with your agent, configure it in your agent's lifecycle hooks:

```json
{
  "beforeRun": [
    {
      "kind": "remote",
      "name": "content-filter",
      "endpoint": "https://localhost:5001/api/hooks/block",
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
- [Hook SDK](../../src/Microsoft.Agents.Hooks.Abstractions/)

## Contributing

When adding new samples:
1. Place agent samples in `agents/`
2. Place hook samples in `hooks/`
3. Include a README.md with usage instructions
4. Follow existing naming and structure patterns
