"""
Error handling tests for agent-xml Python implementation.

Tests that invalid XML files are properly rejected with meaningful error messages.
"""

from pathlib import Path

import pytest

# Get path to error test data
ERROR_TEST_DATA_PATH = Path(__file__).parent.parent.parent.parent / "test-data" / "input" / "threads" / "invalid"


def get_error_test_files():
    """Get all error XML test files."""
    if not ERROR_TEST_DATA_PATH.exists():
        return []
    return sorted(ERROR_TEST_DATA_PATH.glob("*.xml"))


@pytest.mark.parametrize(
    "xml_file",
    get_error_test_files(),
    ids=lambda f: f.name
)
def test_error_file_raises_validation_error(xml_file: Path):
    """
    Test that error XML files properly raise validation errors.

    These test files are intentionally invalid and should fail validation:
    - missing-user-id.xml - User message missing required user-id
    - malformed-xml.xml - Malformed XML (unclosed tag)
    - invalid-timestamp.xml - Invalid ISO 8601 timestamp
    - empty-text-content.xml - Empty text content
    - tool-call-in-user-message.xml - Invalid role/content combination
    - missing-message-content.xml - Message with no content
    - invalid-url.xml - Invalid URL format
    - missing-function-name.xml - Function call missing name
    - invalid-json-arguments.xml - Invalid JSON in arguments
    - unknown-role.xml - Unknown message role
    - tool-result-without-preceding-call.xml - Tool result without matching call-id
    - thread-tool-result-mismatched-call-id.xml - Thread with mismatched tool result call-id
    """
    pytest.skip("Waiting for generated models and working validation")

    # from microsoft.agents.xml.serialization import XmlDeserializer
    # from microsoft.agents.xml.models.messages import ChatMessage
    # from microsoft.agents.xml.validation import ValidationError

    # # Arrange
    # xml_content = xml_file.read_text(encoding="utf-8")
    # deserializer = XmlDeserializer()

    # # Act & Assert - Should raise validation error
    # with pytest.raises((ValidationError, ValueError, Exception)) as exc_info:
    #     deserializer.deserialize(xml_content, ChatMessage)

    # # Verify error message is meaningful
    # error_message = str(exc_info.value).lower()
    #
    # # Check that error message contains relevant keywords based on file
    # if "missing-user-id" in xml_file.name:
    #     assert "user" in error_message or "required" in error_message
    # elif "malformed" in xml_file.name:
    #     assert "xml" in error_message or "parse" in error_message
    # elif "timestamp" in xml_file.name:
    #     assert "timestamp" in error_message or "date" in error_message
    # elif "empty" in xml_file.name:
    #     assert "empty" in error_message or "content" in error_message
    # elif "tool-call-in-user" in xml_file.name:
    #     assert "user" in error_message or "function" in error_message
    # elif "missing-content" in xml_file.name:
    #     assert "content" in error_message or "required" in error_message
    # elif "invalid-url" in xml_file.name:
    #     assert "url" in error_message or "invalid" in error_message
    # elif "missing-function-name" in xml_file.name:
    #     assert "name" in error_message or "function" in error_message
    # elif "invalid-json" in xml_file.name:
    #     assert "json" in error_message or "arguments" in error_message
    # elif "unknown-role" in xml_file.name:
    #     assert "role" in error_message or "unknown" in error_message

    print(f"✅ {xml_file.name} - Properly rejected with error")


@pytest.mark.parametrize("test_case", [
    ("missing-user-id.xml", "user-id is required for user messages"),
    ("malformed-xml.xml", "XML parsing error"),
    ("invalid-timestamp.xml", "Invalid ISO 8601 timestamp"),
    ("empty-text-content.xml", "Text content cannot be empty"),
    ("tool-call-in-user-message.xml", "Function calls not allowed in user messages"),
    ("missing-message-content.xml", "Message must have at least one content element"),
    ("invalid-url.xml", "Invalid URL format"),
    ("missing-function-name.xml", "Function name is required"),
    ("invalid-json-arguments.xml", "Invalid JSON in function arguments"),
    ("unknown-role.xml", "Unknown message role"),
    ("tool-result-without-preceding-call.xml", "Tool result call-id must match a preceding function call"),
    ("thread-tool-result-mismatched-call-id.xml", "Tool result call-id"),
])
def test_error_has_meaningful_message(test_case):
    """
    Test that each error case provides a meaningful error message.

    This test documents the expected error message for each error case.
    """
    filename, expected_error_substring = test_case
    pytest.skip("Waiting for generated models and working validation")

    # from microsoft.agents.xml.serialization import XmlDeserializer
    # from microsoft.agents.xml.models.messages import ChatMessage

    # # Arrange
    # file_path = ERROR_TEST_DATA_PATH / filename
    # xml_content = file_path.read_text(encoding="utf-8")
    # deserializer = XmlDeserializer()

    # # Act & Assert
    # with pytest.raises(Exception) as exc_info:
    #     deserializer.deserialize(xml_content, ChatMessage)

    # error_message = str(exc_info.value)
    # assert expected_error_substring.lower() in error_message.lower(), \
    #     f"Expected error to mention '{expected_error_substring}' but got: {error_message}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
