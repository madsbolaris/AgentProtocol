# Error Test Cases

This directory contains intentionally invalid XML message files used for error handling and validation testing.

## Purpose

These test files verify that:
1. **XML parsers** properly reject invalid messages with meaningful error messages
2. **Serialization/deserialization** validates input and fails gracefully
3. **Echo bot** returns appropriate HTTP 400 Bad Request responses
4. **Error messages** are clear and actionable

## Test Cases

### Required Attribute Errors

| File | Error | Expected Behavior |
|------|-------|-------------------|
| `20-error-missing-user-id.xml` | User message missing required `user-id` attribute | Validation error: "user-id is required for user messages" |
| `27-error-missing-function-name.xml` | Function call missing required `name` attribute | Validation error: "Function name is required" |

### XML Structure Errors

| File | Error | Expected Behavior |
|------|-------|-------------------|
| `21-error-malformed-xml.xml` | Unclosed `<text>` tag | XML parsing error |
| `29-error-unknown-role.xml` | Unknown message role (`<unknown-role>`) | Validation error: "Unknown message role" |

### Data Validation Errors

| File | Error | Expected Behavior |
|------|-------|-------------------|
| `22-error-invalid-timestamp.xml` | Non-ISO 8601 timestamp format | Validation error: "Invalid ISO 8601 timestamp" |
| `23-error-empty-text-content.xml` | Empty/whitespace-only text content | Validation error: "Text content cannot be empty" |
| `26-error-invalid-url.xml` | Invalid URL format in image | Validation error: "Invalid URL format" |
| `28-error-invalid-json-arguments.xml` | Malformed JSON in function arguments | Validation error: "Invalid JSON in function arguments" |

### Semantic Validation Errors

| File | Error | Expected Behavior |
|------|-------|-------------------|
| `24-error-tool-call-in-user-message.xml` | Function call in user message (should only be in agent messages) | Validation error: "Function calls not allowed in user messages" |
| `25-error-missing-message-content.xml` | Message with no content elements | Validation error: "Message must have at least one content element" |
| `30-error-tool-result-without-preceding-call.xml` | Tool result without a preceding tool call with matching call-id (standalone message) | Validation error: "Tool result call-id must match a preceding function call" |
| `31-error-thread-tool-result-mismatched-call-id.xml` | Thread with tool result call-id that doesn't match any preceding function call | Validation error: "Tool result call-id 'call_999' does not match any preceding function call" |
| `32-error-duplicate-call-ids-in-message.xml` | Multiple function calls with the same call-id within one message | Validation error: "Duplicate call-id 'call_123' within message" |
| `33-error-function-name-mismatch.xml` | Function result name doesn't match function call name | Validation error: "Function result name 'get_time' does not match call name 'get_weather'" |
| `34-error-duplicate-tool-result-submission.xml` | Same call-id submitted in multiple function results | Validation error: "Call-id 'call_123' already submitted" |
| `35-error-message-empty-contents.xml` | Message with empty contents array | Validation error: "Message must have non-empty contents" |
| `36-error-invalid-role.xml` | Message with invalid role (not user/agent/system/tool/developer) | Validation error: "Invalid message role 'hacker'" |

## Usage in Tests

### Python - Roundtrip/Validation Tests

```python
from pathlib import Path
import pytest

ERROR_TEST_DATA = Path("test-data/input/errors")

@pytest.mark.parametrize("xml_file", ERROR_TEST_DATA.glob("*.xml"))
def test_error_file_raises_validation_error(xml_file):
    """Test that error files properly raise validation errors."""
    from microsoft.agents.xml.serialization import XmlDeserializer

    xml_content = xml_file.read_text()
    deserializer = XmlDeserializer()

    with pytest.raises((ValidationError, ValueError)):
        deserializer.deserialize(xml_content, ChatMessage)
```

### Python - Echo Bot Integration Tests

```python
@pytest.mark.asyncio
async def test_echobot_rejects_invalid_message(client, xml_file):
    """Test that EchoBot returns 400 for invalid messages."""
    xml_content = xml_file.read_text()

    response = await client.post(
        "/runs",
        content=xml_content,
        headers={"Content-Type": "application/xml"}
    )

    assert response.status_code == 400
```

### .NET - Validation Tests

```csharp
[Theory]
[MemberData(nameof(GetErrorTestFiles))]
public void ErrorFile_ShouldRaiseValidationException(string xmlFile)
{
    // Arrange
    var xml = File.ReadAllText(xmlFile);
    var deserializer = new XmlDeserializer();

    // Act & Assert
    Assert.Throws<ValidationException>(() =>
        deserializer.Deserialize<ChatMessage>(xml));
}
```

### TypeScript - Validation Tests

```typescript
describe('Error Handling', () => {
  const errorFiles = fs.readdirSync('test-data/input/errors');

  errorFiles.forEach(file => {
    it(`should reject ${file}`, () => {
      const xml = fs.readFileSync(`test-data/input/errors/${file}`, 'utf8');
      const deserializer = new XmlDeserializer();

      expect(() => deserializer.deserialize(xml))
        .toThrow(ValidationError);
    });
  });
});
```

## Adding New Error Cases

When adding new error test cases:

1. **File naming**: Use format `##-error-<description>.xml` where `##` is the next sequential number
2. **Comment**: Include a comment at the top describing the error
3. **Realistic**: Make the error realistic - something a developer might actually encounter
4. **Single error**: Each file should test exactly one type of error
5. **Update tests**: Add corresponding test cases to validation and integration tests
6. **Document**: Update this README with the new error case

## Example Error File

```xml
<!-- ERROR: User message missing required user-id attribute -->
<user
  author-name="Alice"
  created-at="2026-02-07T10:02:00Z">
  <text>This message is missing the required user-id attribute.</text>
</user>
```

## Expected Error Response Format

When echo bot encounters an error, it should return:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "User message missing required user-id attribute",
    "details": {
      "field": "user-id",
      "messageType": "user"
    }
  }
}
```

Or in XML:

```xml
<error code="VALIDATION_ERROR">
  <message>User message missing required user-id attribute</message>
  <details>
    <field>user-id</field>
    <message-type>user</message-type>
  </details>
</error>
```

## Related Documentation

- [Error Handling Guide](../../../docs/guides/error-handling.md)
- [Validation Documentation](../../../docs/specifications/validation.md)
- [Echo Bot Compliance Tests](../../../python/microsoft-agents-protocol/tests/compliance/)
- [XML Serialization Guide](../../../docs/guides/xml-serialization.md)
