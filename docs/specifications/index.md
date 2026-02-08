# Behavioral Specifications

This section documents **how** the Agent Runtime API behaves - state machines, validation rules, error semantics, and consistency guarantees.

## Specification Documents

| Document | Description |
|----------|-------------|
| [run-lifecycle.md](./run-lifecycle.md) | Run state machine, transitions, cancellation behavior |
| [message-lifecycle.md](./message-lifecycle.md) | Message creation, ID assignment, storage, retrieval |
| [streaming.md](./streaming.md) | Streaming behavior for content, tools, and runs |
| [tool-execution.md](./tool-execution.md) | Tool call flow, execution, results, retries |
| [content-encryption.md](./content-encryption.md) | Encryption requirements, key management, client-side crypto |
| [authentication.md](./authentication.md) | Auth flows, connections, scope enforcement |
| [validation.md](./validation.md) | Input validation, business rules, constraints |
| [error-handling.md](./error-handling.md) | Error codes, recovery strategies, retries |

## Specification vs. Implementation

These documents define **requirements** that implementations must satisfy:

**Specifications define:**
- Required state transitions
- Validation rules that must be enforced
- Error conditions that must be detected
- Ordering guarantees that must be preserved

**Implementations decide:**
- Which database to use
- How to optimize queries
- Caching strategies
- Deployment topology

## Specification Format

Each specification follows this structure:

1. **Overview**: What behavior is being specified
2. **State Machines**: Valid states and transitions (where applicable)
3. **Requirements**: MUST/SHOULD/MAY requirements
4. **Validation Rules**: What inputs are valid
5. **Error Conditions**: What errors can occur
6. **Examples**: Concrete scenarios

## Requirement Keywords

Following [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119):

- **MUST** / **REQUIRED**: Absolute requirement
- **MUST NOT**: Absolute prohibition
- **SHOULD** / **RECOMMENDED**: Strong recommendation (may ignore for valid reasons)
- **SHOULD NOT**: Strong discouragement
- **MAY** / **OPTIONAL**: Truly optional

## Target Audience

These specifications are for:
- **Server implementers** - know what behavior to implement
- **Client implementers** - know what behavior to expect
- **Testers** - know what to test
- **Integrators** - understand edge cases and constraints

## Related Documentation

- **API Reference**: [api-reference/](../api-reference/) - API structure
- **TypeSpec**: [typespec/](../../typespec/) - API contracts
- **Guides**: [guides/](../guides/) - integration patterns
