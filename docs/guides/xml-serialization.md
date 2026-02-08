# XML Message Serialization

This guide demonstrates how to serialize and deserialize messages using the XML format in the Agent Protocol.

## Overview

The Agent Protocol supports XML serialization for all message types, providing a human-readable and easily parsable format for agent communication.

## Basic Message Serialization

Here's how to create and serialize a simple message:

=== "Python"

    {% include-test "basic-xml-serialization" language="python" %}

=== "C#"

    {% include-test "basic-xml-serialization" language="csharp" %}

### Output

The serialized XML looks like this:

{% include-result "basic-xml-serialization" language="python" %}

## Working with Test Data

You can load and work with XML test data files:

{% include-test "read-xml-file" language="python" %}

### Result

{% include-result "read-xml-file" language="python" %}

## Multimodal Messages

Messages can contain multiple types of content (text, images, files):

=== "Python"

    {% include-test "multimodal-message" language="python" %}

=== "C#"

    {% include-test "multimodal-message" language="csharp" %}

### Output

The multimodal message serializes to:

{% include-result "multimodal-message" language="python" %}

## Key Features

- **Type Safety**: Strong typing ensures message integrity
- **Validation**: Automatic schema validation
- **Round-Trip**: Perfect serialization/deserialization fidelity
- **Human-Readable**: XML format is easy to inspect and debug

## Next Steps

- Learn about [message types](../api-reference/models/chatmessage.md)
- Explore [content types](../specifications/index.md)
- See [streaming](../specifications/streaming.md) for real-time communication

---

!!! tip "Test-Driven Documentation"
    All code examples on this page are extracted from actual test files and are guaranteed to work.
    The outputs shown are captured from running tests.

    - Python examples: `python/microsoft-agents-xml/tests/test_doc_examples.py`
    - C# examples: `dotnet/tests/Microsoft.Agents.Xml.Tests/AgentXml.CodeGen.Tests/RoundTripTests.cs`
