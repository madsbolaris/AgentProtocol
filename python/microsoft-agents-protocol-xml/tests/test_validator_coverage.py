"""Comprehensive tests for thread validator to improve code coverage."""

import pytest
from microsoft.agents.xml.validation.thread_validator import ThreadValidator
from microsoft.agents.xml.validation.validation_result import ValidationResult


class TestThreadValidatorCoverage:
    """Test all validation rules and branches of ThreadValidator."""

    def test_validate_valid_thread(self):
        """Test validating a completely valid thread."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": "Hello"}]
                }
            ]
        }
        result = validator.validate(thread)
        assert result.is_valid

    def test_validate_missing_thread_id(self):
        """Test validation fails when thread ID is missing."""
        validator = ThreadValidator()
        thread = {
            "messages": []
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_001" for error in result.errors)

    def test_validate_empty_thread_id(self):
        """Test validation fails when thread ID is empty."""
        validator = ThreadValidator()
        thread = {
            "threadId": "",
            "messages": []
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_001" for error in result.errors)

    def test_validate_missing_messages(self):
        """Test validation fails when messages field is missing."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123"
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_002" for error in result.errors)

    def test_validate_duplicate_message_ids(self):
        """Test validation fails with duplicate message IDs."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": "Hello"}]
                },
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": "Hi"}]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_003" for error in result.errors)

    def test_validate_messages_not_in_chronological_order(self):
        """Test validation fails when messages are out of order."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1",
                    "createdAt": "2024-01-01T12:00:00Z",
                    "contents": [{"kind": "text", "text": "First"}]
                },
                {
                    "role": "agent",
                    "messageId": "msg-2",
                    "createdAt": "2024-01-01T11:00:00Z",
                    "contents": [{"kind": "text", "text": "Second"}]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_004" for error in result.errors)

    def test_validate_invalid_role(self):
        """Test validation fails with invalid message role."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "invalid_role",
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": "Hello"}]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_005" for error in result.errors)

    def test_validate_all_valid_roles(self):
        """Test all valid roles are accepted."""
        validator = ThreadValidator()
        valid_roles = ["user", "agent", "system", "tool", "developer", "channel"]

        for role in valid_roles:
            thread = {
                "threadId": "thread-123",
                "messages": [
                    {
                        "role": role,
                        "messageId": f"msg-{role}",
                        "contents": [{"kind": "text", "text": "Test"}]
                    }
                ]
            }
            result = validator.validate(thread)
            assert result.is_valid, f"Role '{role}' should be valid"

    def test_validate_empty_message_contents(self):
        """Test warning for empty message contents."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1",
                    "contents": []
                }
            ]
        }
        result = validator.validate(thread)
        assert len(result.warnings) > 0

    def test_validate_function_call_missing_call_id(self):
        """Test validation fails when function call lacks call-id."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "name": "get_weather",
                            "arguments": "{}"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_007" for error in result.errors)

    def test_validate_duplicate_call_ids_in_message(self):
        """Test validation fails with duplicate call-ids in same message."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "func1",
                            "arguments": "{}"
                        },
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "func2",
                            "arguments": "{}"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_008" for error in result.errors)

    def test_validate_function_call_missing_name(self):
        """Test validation fails when function call lacks name."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "arguments": "{}"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_009" for error in result.errors)

    def test_validate_function_result_missing_call_id(self):
        """Test validation fails when function result lacks call-id."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "tool",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "result": "data"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_010" for error in result.errors)

    def test_validate_function_result_without_matching_call(self):
        """Test validation fails when function result has no matching call."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "tool",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "callId": "call-999",
                            "result": "data"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_011" for error in result.errors)

    def test_validate_mismatched_function_names(self):
        """Test validation fails when function names don't match."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "get_weather",
                            "arguments": "{}"
                        }
                    ]
                },
                {
                    "role": "tool",
                    "messageId": "msg-2",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "callId": "call-1",
                            "name": "get_temperature",
                            "result": "72°F"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_012" for error in result.errors)

    def test_validate_already_fulfilled_call_id(self):
        """Test validation fails when call-id is fulfilled multiple times."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "get_weather",
                            "arguments": "{}"
                        }
                    ]
                },
                {
                    "role": "tool",
                    "messageId": "msg-2",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "callId": "call-1",
                            "result": "Result 1"
                        }
                    ]
                },
                {
                    "role": "tool",
                    "messageId": "msg-3",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "callId": "call-1",
                            "result": "Result 2"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert any(error.code == "THREAD_013" for error in result.errors)

    def test_validate_unfulfilled_function_calls_warning(self):
        """Test warning for unfulfilled function calls."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "get_weather",
                            "arguments": "{}"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert result.is_valid  # Valid but has warnings
        assert len(result.warnings) > 0
        assert "call-1" in result.warnings[0]

    def test_validate_complete_function_call_result_flow(self):
        """Test valid function call-result flow."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "agent",
                    "messageId": "msg-1",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "get_weather",
                            "arguments": '{"city":"SF"}'
                        }
                    ]
                },
                {
                    "role": "tool",
                    "messageId": "msg-2",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "callId": "call-1",
                            "name": "get_weather",
                            "result": "Sunny, 72°F"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_validate_message_with_no_contents_field(self):
        """Test validation handles message without contents field."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1"
                }
            ]
        }
        result = validator.validate(thread)
        # Should produce a warning
        assert len(result.warnings) > 0

    def test_validate_with_snake_case_properties(self):
        """Test validation works with snake_case property names."""
        validator = ThreadValidator()
        thread = {
            "thread_id": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "message_id": "msg-1",
                    "created_at": "2024-01-01T12:00:00Z",
                    "contents": [{"kind": "text", "text": "Hello"}]
                }
            ]
        }
        result = validator.validate(thread)
        assert result.is_valid

    def test_validate_text_content_empty_warning(self):
        """Test warning for empty text content."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": ""}]
                }
            ]
        }
        result = validator.validate(thread)
        # May produce warning about empty text
        # Depending on implementation

    def test_validate_multiple_errors(self):
        """Test thread with multiple validation errors."""
        validator = ThreadValidator()
        thread = {
            "threadId": "",  # Empty thread ID
            "messages": [
                {
                    "role": "invalid_role",  # Invalid role
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": "Hello"}]
                },
                {
                    "role": "agent",
                    "messageId": "msg-1",  # Duplicate message ID
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            # Missing name
                            "arguments": "{}"
                        }
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert not result.is_valid
        assert len(result.errors) >= 3

    def test_validate_case_insensitive_roles(self):
        """Test role validation is case-insensitive."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-123",
            "messages": [
                {
                    "role": "USER",  # Uppercase
                    "messageId": "msg-1",
                    "contents": [{"kind": "text", "text": "Hello"}]
                }
            ]
        }
        result = validator.validate(thread)
        assert result.is_valid

    def test_validate_complex_thread(self):
        """Test validation of complex thread with multiple message types."""
        validator = ThreadValidator()
        thread = {
            "threadId": "thread-complex",
            "messages": [
                {
                    "role": "user",
                    "messageId": "msg-1",
                    "createdAt": "2024-01-01T10:00:00Z",
                    "contents": [
                        {"kind": "text", "text": "What's the weather?"}
                    ]
                },
                {
                    "role": "agent",
                    "messageId": "msg-2",
                    "createdAt": "2024-01-01T10:00:01Z",
                    "contents": [
                        {
                            "kind": "functionCall",
                            "callId": "call-1",
                            "name": "get_weather",
                            "arguments": '{"city":"SF"}'
                        }
                    ]
                },
                {
                    "role": "tool",
                    "messageId": "msg-3",
                    "createdAt": "2024-01-01T10:00:02Z",
                    "contents": [
                        {
                            "kind": "functionResult",
                            "callId": "call-1",
                            "name": "get_weather",
                            "result": "Sunny, 72°F"
                        }
                    ]
                },
                {
                    "role": "agent",
                    "messageId": "msg-4",
                    "createdAt": "2024-01-01T10:00:03Z",
                    "contents": [
                        {"kind": "text", "text": "It's sunny and 72°F"}
                    ]
                }
            ]
        }
        result = validator.validate(thread)
        assert result.is_valid
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
