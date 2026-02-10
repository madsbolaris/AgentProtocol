# Getting Started

Get started with XML message serialization and validation.

## Overview

The XML libraries provide schema-based serialization, validation, and testing tools for Agent Protocol messages.

---

## Why XML Format?

- **Schema Validation** - Validate messages against XSD schema
- **Testing Support** - EvalXML format for test cases
- **Interoperability** - Standard XML format
- **Tooling** - Rich XML ecosystem

---

## Choose Your Language

=== "Python"
    **Best for:** Data science, scripting, backend services
    
    ```bash
    pip install microsoft-agents-xml
    ```
    
    [View Python Guide →](api-reference/python.md)

=== "TypeScript"
    **Best for:** Frontend, Node.js backends, full-stack apps
    
    ```bash
    npm install @microsoft/agents-xml
    ```
    
    [View TypeScript Guide →](api-reference/typescript.md)

=== ".NET"
    **Best for:** Enterprise apps, Windows services, Azure
    
    ```bash
    dotnet add package Microsoft.Agents.Xml
    ```
    
    [View .NET Guide →](api-reference/csharp.md)

---

## Quick Example

Serialize a message to XML:

=== "Python"
    ```python
    from microsoft.agents.xml import MessageSerializer
    
    xml = serializer.serialize(message)
    ```

=== "TypeScript"
    ```typescript
    import { MessageSerializer } from '@microsoft/agents-xml';
    
    const xml = serializer.serialize(message);
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Xml;
    
    var xml = serializer.Serialize(message);
    ```

---

## Next Steps

1. [Complete the Quickstart](quickstart.md) - 15-minute introduction
2. [Learn Core Concepts](core-concepts/index.md) - XML format fundamentals
3. [Explore Cookbooks](cookbooks/index.md) - Practical examples
4. [Read API Reference](api-reference/index.md) - Detailed documentation

---

## Need Help?

- [Troubleshooting](troubleshooting/README.md)
- [GitHub Discussions](https://github.com/microsoft/AgentProtocol/discussions)
- [GitHub Issues](https://github.com/microsoft/AgentProtocol/issues)
