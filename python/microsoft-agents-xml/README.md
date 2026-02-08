# Agent XML - Python Implementation

XML serialization for Agent Protocol messages in Python.

## Installation

```bash
pip install agent-xml
```

Or install from source:

```bash
cd python
pip install -e .
```

## Quick Start

### Serialization

```python
from agent_xml.models.messages import ChatMessage, TextContent
from agent_xml.serialization import XmlSerializer

# Create a message
message = ChatMessage(
    message_id="msg_123",
    role="user",
    contents=[
        TextContent(text="What's the weather today?")
    ],
    author_name="Alice",
    created_at="2026-02-07T10:00:00Z"
)

# Serialize to XML
serializer = XmlSerializer(pretty_print=True)
xml = serializer.serialize(message)
print(xml)
```

Output:
```xml
<?xml version="1.0" encoding="utf-8"?>
<user message-id="msg_123" author-name="Alice" created-at="2026-02-07T10:00:00Z">
  <text>What's the weather today?</text>
</user>
```

### Deserialization

```python
from agent_xml.serialization import XmlDeserializer
from agent_xml.models.messages import ChatMessage

xml_string = """
<user message-id="msg_123">
  <text>Hello world</text>
</user>
"""

# Deserialize from XML
deserializer = XmlDeserializer()
message = deserializer.deserialize(xml_string, ChatMessage)

print(message.message_id)  # "msg_123"
print(message.contents[0].text)  # "Hello world"
```

## Project Structure

```
python/
├── agent_xml/                    # Runtime package
│   ├── models/                   # Generated models
│   │   ├── __init__.py
│   │   └── messages.py           # Auto-generated from TypeSpec
│   ├── serialization/            # Serialization runtime
│   │   ├── __init__.py
│   │   ├── xml_serializer.py
│   │   └── xml_deserializer.py
│   └── __init__.py
├── tests/                        # Tests
│   └── test_basic_serialization.py
├── examples/                     # Usage examples
├── pyproject.toml
└── README.md
```

## Code Generation

The models in `agent_xml/models/` are auto-generated from TypeSpec definitions:

```bash
# From project root
./tools/generate-python.sh
```

This runs:
```bash
agent-xml-codegen \
    --typespec schemas/messages.tsp \
    --output python/agent_xml/models/messages.py
```

## Features

- ✅ **Type-safe**: Python dataclasses with full type hints
- ✅ **XML Serialization**: Using xsdata for robust XML support
- ✅ **Multi-modal**: Supports text, images, audio, video, files
- ✅ **Polymorphic Content**: Discriminated unions for content types
- ✅ **TypeSpec-driven**: Single source of truth for schema

## Dependencies

- **xsdata**: XML dataclass serialization
- **lxml**: XML parsing

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run tests:

```bash
pytest tests/
```

Format code:

```bash
black agent_xml/ tests/
ruff check agent_xml/ tests/
```

## Comparison with C# Implementation

| Feature | C# | Python |
|---------|-----|--------|
| Runtime | .NET 8.0 | Python 3.10+ |
| Serialization | System.Xml.Serialization | xsdata |
| Code Generation | Roslyn | Custom AST |
| Package Manager | NuGet | PyPI |

Both implementations:
- Share the same TypeSpec source files
- Share the same test XML files
- Support identical XML formats
- Provide round-trip serialization

## License

MIT
