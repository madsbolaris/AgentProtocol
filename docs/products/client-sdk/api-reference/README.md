# API Reference

Comprehensive API documentation for all Client SDK languages.

## Quick Links

- [Common Types & Models](common/index.md) - Shared data structures and types
- [C# API Reference](csharp.md) - Complete C#/.NET documentation
- [Python API Reference](python.md) - Complete Python documentation
- [TypeScript API Reference](typescript.md) - Complete TypeScript/JavaScript documentation
- [XML Schema Reference](xml-schema/index.md) - XML message format specification

---

## Language-Specific APIs

### C# / .NET

The C# SDK provides idiomatic .NET patterns including dependency injection, IOptions, and async/await support.

[View C# API Reference](csharp.md){ .md-button .md-button--primary }

**Key Packages:**
- `Microsoft.Agents.Protocol.Client` - Core client library
- `Microsoft.Agents.Abstractions` - Interfaces and abstractions
- `Microsoft.Agents.Validation` - Message validation utilities
- `Microsoft.Agents.Xml` - XML serialization support

### Python

The Python SDK provides pythonic APIs with type hints, async/await, and context managers.

[View Python API Reference](python.md){ .md-button .md-button--primary }

**Key Modules:**
- `microsoft.agents.client` - Core client implementation
- `microsoft.agents.models` - Data model classes
- `microsoft.agents.conversation` - Conversation abstractions
- `microsoft.agents.exceptions` - Error types

### TypeScript

The TypeScript SDK provides full type safety with discriminated unions and generics.

[View TypeScript API Reference](typescript.md){ .md-button .md-button--primary }

**Key Exports:**
- `AgentProtocolClient` - Main client class
- Type definitions for all protocol messages
- Tool collection and management utilities
- WebSocket streaming support

---

## Common Concepts

These concepts apply across all language SDKs:

- **[Data Models](common/data-models.md)** - Core protocol entities (Runs, Threads, Messages)
- **[Error Codes](common/error-codes.md)** - Standard error codes and handling
- **[REST API Mapping](common/rest-api-mapping.md)** - How SDK methods map to HTTP endpoints

---

## Design Philosophy

All Client SDKs share these principles:

1. **Type Safety** - Leverage language type systems to catch errors at compile time
2. **Async First** - All I/O operations are asynchronous by default
3. **Streaming Support** - Built-in support for real-time event streaming
4. **Composable** - Tools and features work together seamlessly
5. **Extensible** - Easy to add custom tools, middleware, and handlers

---

## Version Compatibility

| SDK Version | Protocol Version | Status |
|------------|------------------|---------|
| 1.0.x | 1.0 | ✅ Current |
| 0.9.x | 1.0-beta | 🔶 Deprecated |

!!! tip "Stay Updated"
    Subscribe to the [GitHub releases](https://github.com/microsoft/AgentProtocol) to get notified of new versions.

---

## Next Steps

- Review language-specific API documentation
- Explore [code examples](../examples/index.md)
- Check out [design patterns](../patterns/README.md) for your language
