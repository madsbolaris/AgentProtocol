# Agent Framework

A unified protocol for building AI agents that work across multiple platforms and frameworks.

## Overview

The Agent Framework provides a standardized way to build, deploy, and integrate AI agents. It defines:

- **API Structure** - REST endpoints for agent execution, message handling, and tool calling
- **Data Models** - TypeSpec-based schemas for messages, content types, and agent configurations
- **Behavioral Specifications** - State machines, validation rules, and error semantics
- **Integration Patterns** - Common patterns for security, webhooks, streaming, and multi-agent systems

This protocol aligns with and extends patterns from:
- Microsoft Agent Framework (MAF)
- OpenAI Agents SDK
- Azure Agent API
- Google A2A Protocol
- LangGraph

## Documentation

**📚 [View Full Documentation](https://madsbolaris.github.io/AgentFramework/)**

Quick links:
- [Getting Started](https://madsbolaris.github.io/AgentFramework/getting-started/) - Start here
- [API Reference](https://madsbolaris.github.io/AgentFramework/api-reference/) - Complete API documentation
- [Specifications](https://madsbolaris.github.io/AgentFramework/specifications/) - Behavioral requirements
- [Guides](https://madsbolaris.github.io/AgentFramework/guides/) - Integration patterns

## Quick Start

### 1. Basic Agent Execution

```http
POST /runs/wait HTTP/1.1
Content-Type: application/json

{
  "agentId": "my-agent",
  "thread": {
    "messages": [
      {
        "role": "user",
        "contents": [
          {
            "kind": "text",
            "text": "Hello, what can you help me with?"
          }
        ]
      }
    ]
  }
}
```

### 2. Streaming Responses

```http
GET /runs/{runId}/stream HTTP/1.1
Accept: text/event-stream
```

### 3. Tool Calling

```json
{
  "agentId": "weather-agent",
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {"type": "string"}
          }
        }
      }
    }
  ]
}
```

See the [Getting Started Guide](docs/getting-started/index.md) for complete examples.

## Repository Structure

```
AgentFramework/
├── docs/                  # Documentation source (Markdown)
│   ├── getting-started/   # Getting started guides
│   ├── guides/            # Integration patterns
│   ├── specifications/    # Behavioral specifications
│   ├── api-reference/     # API documentation
│   └── typespec/          # TypeSpec documentation
├── typespec/              # TypeSpec schema definitions (source of truth)
├── scripts/               # Documentation generation and validation
├── agent-xml/             # C# implementation example
└── mkdocs.yml            # Documentation site configuration
```

## Key Features

### 🔄 Multi-Modal Content
Support for text, images, audio, video, files, and structured data in messages.

### 🛠️ Tool Execution
Standardized function calling with streaming support for large inputs/outputs.

### 🔐 Security & Compliance
OAuth2 authentication, content encryption, PII handling, and HIPAA compliance patterns.

### 📡 Real-Time Communication
Server-Sent Events (SSE) streaming, webhooks, and bidirectional audio/video.

### 🤝 Multi-Agent Orchestration
Agent handoffs, delegation patterns, and human-in-the-loop workflows.

### 🎯 State Management
Run lifecycle management, thread persistence, and conversation history.

## TypeSpec Definitions

The protocol is defined using [TypeSpec](https://typespec.io/), providing:

- **Type-safe contracts** - Validated schemas for all API operations
- **OpenAPI generation** - Automatic OpenAPI 3.0 spec generation
- **SDK generation** - Client library generation for multiple languages
- **Documentation sync** - Single source of truth for API structure

See [typespec/](typespec/) for schema definitions.

## Implementation

### Reference Implementation

The [agent-xml/](agent-xml/) directory contains a C# reference implementation including:

- XML serialization/deserialization
- TypeSpec-to-C# code generation
- Runtime validation
- Unit tests

### Building Your Own

To implement this protocol:

1. **Review Specifications** - Understand required behaviors in [docs/specifications/](docs/specifications/)
2. **Implement API Endpoints** - Follow REST patterns in [docs/api-reference/](docs/api-reference/)
3. **Use TypeSpec Schemas** - Generate models from [typespec/](typespec/)
4. **Follow Integration Patterns** - Use patterns from [docs/guides/](docs/guides/)
5. **Validate Implementation** - Use validation scripts in [scripts/validation/](scripts/validation/)

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Documentation guidelines
- TypeSpec as source of truth
- Validation workflow
- Submitting pull requests

### Development Workflow

```bash
# 1. Install dependencies
cd scripts
pip install -r requirements.txt

# 2. Make changes to TypeSpec or documentation
vim typespec/messages.tsp
vim docs/specifications/message-lifecycle.md

# 3. Validate changes
make validate

# 4. Build documentation site
cd ..
mkdocs serve  # Preview at http://localhost:8000

# 5. Submit PR
git add .
git commit -m "Update message lifecycle documentation"
git push origin feature-branch
```

## Documentation System

Documentation is automatically generated from TypeSpec definitions and merged with human-written guides:

```
TypeSpec (typespec/*.tsp)
    ↓
generate-api-reference.py
    ↓
.generated/api-reference/
    ↓
merge-api-docs.py (+ manual content)
    ↓
docs/api-reference/
    ↓
MkDocs + Material theme
    ↓
Static website (GitHub Pages)
```

See [scripts/README.md](scripts/README.md) for details on the documentation pipeline.

## Validation

Run validation checks before committing:

```bash
cd scripts
make validate
```

This validates:
- ✅ Enum synchronization (TypeSpec ↔ docs)
- ✅ Internal links
- ✅ Cross-references
- ✅ Model name consistency
- ✅ Route definitions

## License

[Your License Here]

## Support

- **Documentation**: https://madsbolaris.github.io/AgentFramework/
- **Issues**: [GitHub Issues](https://github.com/madsbolaris/AgentFramework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/madsbolaris/AgentFramework/discussions)

## Related Projects

- **TypeSpec**: https://typespec.io/
- **MkDocs Material**: https://squidfunk.github.io/mkdocs-material/
- **OpenAI Agents SDK**: https://github.com/openai/swarm
- **Microsoft Agent Framework**: [Documentation](https://learn.microsoft.com/en-us/azure/ai-services/)
- **LangGraph**: https://github.com/langchain-ai/langgraph

---

Built with [TypeSpec](https://typespec.io/) • Documented with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
