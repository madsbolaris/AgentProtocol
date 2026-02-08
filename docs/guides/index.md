# Integration Guides

This section provides **integration patterns** and **implementation guides** for common scenarios.

## Available Guides

| Guide | Level | Time | Description |
|-------|-------|------|-------------|
| 🟢 [getting-started.md](./getting-started.md) | **Beginner** | 15 min | Quickstart for first integration |
| 🟢 [webhooks.md](./webhooks.md) | **Beginner** | 10 min | Webhook subscriptions and notifications |
| 🟡 [error-handling.md](./error-handling.md) | **Intermediate** | 20 min | Retry strategies, resilience patterns, error recovery |
| 🟡 [testing-agents.md](./testing-agents.md) | **Intermediate** | 30 min | Unit testing, integration testing, mocking, CI/CD |
| 🟡 [proactive-messaging.md](./proactive-messaging.md) | **Intermediate** | 25 min | Event-driven agent initiation patterns |
| 🟡 [voice-integration.md](./voice-integration.md) | **Intermediate** | 30 min | Voice pipeline setup with bidirectional streaming |
| 🟡 [multi-agent.md](./multi-agent.md) | **Intermediate** | 35 min | Multi-agent orchestration patterns |
| 🟡 [human-in-loop.md](./human-in-loop.md) | **Intermediate** | 25 min | Human approval and interruption patterns |
| 🔴 [security-compliance.md](./security-compliance.md) | **Advanced** | 45 min | OAuth2, content encryption, PII handling, HIPAA/PHI compliance |
| 🔴 [content-guardrails.md](./content-guardrails.md) | **Advanced** | 40 min | Content filtering, PII redaction, hooks, and compliance controls |
| 🔴 [production-deployment.md](./production-deployment.md) | **Advanced** | 50 min | Monitoring, scaling, performance optimization, Kubernetes |

!!! tip "New to Agent Protocol?"

    Start with 🟢 **Beginner** guides, then move to 🟡 **Intermediate** patterns, and finally explore 🔴 **Advanced** topics like security and deployment.

## Guide vs. Specification

**Guides** (this section) show **how to use** the API:
- Concrete examples
- Best practices
- Design patterns
- Integration scenarios

**[Specifications](../specifications/)** define **required behavior**:
- State machines
- Validation rules
- Error semantics
- Consistency guarantees

**[API Reference](../api-reference/)** describes **API structure**:
- Models and fields
- Endpoints and parameters
- Content types

## Guide Format

Each guide follows this structure:

1. **Overview**: What scenario is covered
2. **Use Cases**: When to use this pattern
3. **Architecture**: High-level design
4. **Implementation**: Step-by-step instructions
5. **Examples**: Working code samples
6. **Troubleshooting**: Common issues

## Target Audience

These guides are for:
- **Application developers** integrating the Agent Runtime API
- **Solution architects** designing agent systems
- **Client implementers** building SDKs or frameworks
- **DevOps engineers** deploying agent applications

## Common Patterns

### Basic Patterns
- Request/response (synchronous)
- Streaming responses (Server-Sent Events)
- Long polling
- Webhooks

### Advanced Patterns
- Security and compliance (OAuth2, encryption, PII)
- Content guardrails (filtering, redaction, compliance)
- Error handling and resilience (retries, circuit breakers)
- Testing and validation (unit tests, integration tests)
- Production deployment (monitoring, scaling, optimization)
- Proactive messaging (event-driven agent initiation)
- Multi-agent orchestration (handoffs, delegation)
- Human-in-the-loop (approval workflows)
- Voice pipelines (bidirectional audio streaming)

## Related Documentation

- **API Reference**: [api-reference/](../api-reference/) - API structure
- **Specifications**: [specifications/](../specifications/) - behavioral requirements
- **TypeSpec**: [typespec/](../../typespec/) - API contracts
- **Strategy**: [specs/TYPESPEC_STRATEGY.md](../specs/TYPESPEC_STRATEGY.md) - design philosophy
