# Basic Test Files

This directory contains basic test files for fundamental message types and simple content validation.

## Subdirectories

### messages/
Tests for individual message types representing each role in the Agent Protocol:
- `01-system-message.xml` - System configuration message
- `02-developer-message.xml` - Developer instruction message
- `03-user-text-only.xml` - User message with text only
- `04-user-simple-text.xml` - User message with simple text content
- `05-user-multimodal.xml` - User message with multiple content types
- `06-agent-thinking-and-call.xml` - Agent message with reasoning and function call
- `07-tool-result-success.xml` - Tool message with successful result
- `08-tool-result-simple.xml` - Tool message with simple result
- `09-tool-result-error.xml` - Tool message with error result
- `10-agent-with-text-response.xml` - Agent message with text response
- `11-channel-message.xml` - Channel message type

**Total**: 11 files

### simple-content/
Tests for simple content types that can appear in messages:
- `19-text-content.xml` - Plain text content
- `19-refusal-content.xml` - Refusal content (model declined to respond)
- `20-function-call-content.xml` - Function call content
- `21-function-result-content.xml` - Function result content
- `21-typing-indicator-content.xml` - Typing indicator content
- `22-error-content.xml` - Error content
- `22-message-reaction-content.xml` - Message reaction content
- `23-message-delete-content.xml` - Message deletion content
- `23-text-reasoning-content.xml` - Text with reasoning (thinking) content
- `24-data-content.xml` - Structured data content
- `24-message-update-content.xml` - Message update content
- `25-uri-content.xml` - URI/link content
- `25-hosted-file-content.xml` - Hosted file reference content
- `26-image-content.xml` - Image content
- `26-hosted-vector-store-content.xml` - Hosted vector store reference content

**Total**: 15 files

## Purpose

These files validate:
- Message serialization/deserialization for each role type
- Content type parsing and validation
- Attribute handling (user-id, agent-id, call-id, etc.)
- Basic XML structure compliance

## Testing Focus

- **Structural validation** - Ensures XML matches the schema
- **Role validation** - Verifies correct role assignment
- **Content parsing** - Tests content extraction and typing
- **Attribute validation** - Confirms required attributes are present

## Usage Example

```python
# Python
from pathlib import Path
xml_content = Path("basic/messages/01-system-message.xml").read_text()
message = parse_xml_message(xml_content)
assert message.role == "system"
```

```typescript
// TypeScript
const xml = fs.readFileSync("basic/messages/01-system-message.xml", "utf-8");
const message = parseXmlMessage(xml);
expect(message.role).toBe("system");
```

```csharp
// C#
var xml = File.ReadAllText("basic/messages/01-system-message.xml");
var message = ParseXmlMessage(xml);
Assert.Equal("system", message.Role);
```

## Related Directories

- See `../content-types/` for more complex content types
- See `../conversations/` for multi-message scenarios
