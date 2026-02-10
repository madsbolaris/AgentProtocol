"""
Comprehensive validation tests for edge cases and spec requirements.

This file contains tests for validation rules from the spec that weren't
initially implemented. All tests now pass after implementing the full
validation logic.

Based on validation spec requirements at:
docs/specifications/validation.md
"""

import pytest
from datetime import datetime
from microsoft.agents.xml.validation import ThreadValidator, ValidationResult


class MockContent:
    """Mock content for testing."""
    def __init__(self, content_type, **kwargs):
        self.content_type = content_type
        for key, value in kwargs.items():
            setattr(self, key, value)


class MockMessage:
    """Mock message for testing."""
    def __init__(self, message_id, created_at, contents=None, role="user"):
        self.message_id = message_id
        self.created_at = created_at
        self.contents = contents or []
        self.role = role


class MockThread:
    """Mock thread for testing."""
    def __init__(self, thread_id, created_at, messages=None):
        self.thread_id = thread_id
        self.created_at = created_at
        self.messages = messages or []


class FunctionCallContent:
    """Mock function call content."""
    def __init__(self, call_id, name, arguments):
        self.call_id = call_id
        self.name = name
        self.arguments = arguments


class FunctionResultContent:
    """Mock function result content."""
    def __init__(self, call_id, name=None, result=None):
        self.call_id = call_id
        self.name = name
        self.result = result


def test_duplicate_call_ids_in_same_message():
    """
    Test validation rule: callId MUST be unique within message.

    Spec: docs/specifications/validation.md line 304
    - callId MUST be unique within message

    Expected behavior: Should reject message with duplicate call-ids
    Current behavior: Does not validate, allowing duplicate call-ids
    """
    now = datetime.utcnow()

    # Create message with TWO function calls using the SAME call-id
    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="agent",
                contents=[
                    FunctionCallContent(
                        call_id="call_123",  # First use
                        name="get_weather",
                        arguments='{"location": "Seattle"}'
                    ),
                    FunctionCallContent(
                        call_id="call_123",  # DUPLICATE - should fail!
                        name="get_time",
                        arguments='{"timezone": "PST"}'
                    ),
                ]
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject duplicate call-ids within message"
    assert any("duplicate" in str(e).lower() and "call_123" in str(e) for e in result.errors), \
        f"Expected error about duplicate call_123 but got: {result.errors}"


def test_function_result_name_must_match_call_name():
    """
    Test validation rule: name MUST match tool call name.

    Spec: docs/specifications/validation.md line 329
    - name MUST match tool call name

    Expected behavior: Should reject result with mismatched function name
    Current behavior: Only checks call-id, not function name
    """
    now = datetime.utcnow()

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="agent",
                contents=[
                    FunctionCallContent(
                        call_id="call_123",
                        name="get_weather",  # Called get_weather
                        arguments='{"location": "Seattle"}'
                    )
                ]
            ),
            MockMessage(
                message_id="msg_002",
                created_at=now,
                role="tool",
                contents=[
                    FunctionResultContent(
                        call_id="call_123",  # Correct call-id
                        name="get_time",     # WRONG NAME - should fail!
                        result='{"temperature": 52}'
                    )
                ]
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject function result with mismatched name"
    assert any("name" in str(e).lower() and ("get_weather" in str(e) or "get_time" in str(e))
               for e in result.errors), \
        f"Expected error about name mismatch but got: {result.errors}"


def test_call_id_already_submitted():
    """
    Test validation rule: REJECT if callId already submitted.

    Spec: docs/specifications/validation.md line 167
    - REJECT if callId already submitted

    Expected behavior: Should reject second result for same call-id
    Current behavior: Allows multiple results for same call-id
    """
    now = datetime.utcnow()

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="agent",
                contents=[
                    FunctionCallContent(
                        call_id="call_123",
                        name="get_weather",
                        arguments='{"location": "Seattle"}'
                    )
                ]
            ),
            MockMessage(
                message_id="msg_002",
                created_at=now,
                role="tool",
                contents=[
                    FunctionResultContent(
                        call_id="call_123",
                        name="get_weather",
                        result='{"temperature": 52}'
                    )
                ]
            ),
            MockMessage(
                message_id="msg_003",
                created_at=now,
                role="tool",
                contents=[
                    FunctionResultContent(
                        call_id="call_123",  # DUPLICATE SUBMISSION - should fail!
                        name="get_weather",
                        result='{"temperature": 55}'  # Different result
                    )
                ]
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject duplicate submission of same call-id"
    assert any("already" in str(e).lower() or "duplicate" in str(e).lower()
               for e in result.errors), \
        f"Expected error about duplicate submission but got: {result.errors}"


def test_message_must_have_non_empty_contents():
    """
    Test validation rule: Each message MUST have non-empty contents.

    Spec: docs/specifications/validation.md line 88
    - Each message MUST have non-empty contents

    Expected behavior: Should reject message with empty contents array
    Current behavior: Allows messages with empty contents
    """
    now = datetime.utcnow()

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="user",
                contents=[]  # EMPTY - should fail!
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject message with empty contents"
    assert any("content" in str(e).lower() and "empty" in str(e).lower()
               for e in result.errors), \
        f"Expected error about empty contents but got: {result.errors}"


def test_message_must_have_valid_role():
    """
    Test validation rule: Each message MUST have valid role.

    Spec: docs/specifications/validation.md line 87
    - Each message MUST have valid role

    Expected behavior: Should reject message with invalid role
    Current behavior: Does not validate role field
    """
    now = datetime.utcnow()

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="hacker",  # INVALID ROLE - should fail!
                contents=[MockContent("text", text="Hello")]
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject message with invalid role"
    assert any("role" in str(e).lower() and "hacker" in str(e).lower()
               for e in result.errors), \
        f"Expected error about invalid role but got: {result.errors}"


def test_function_call_must_have_call_id():
    """
    Test validation rule: FunctionCallContent requires callId.

    Spec: docs/specifications/validation.md line 300
    - **Required**: `callId`, `name`

    Expected behavior: Should reject function call without call_id
    Current behavior: May allow missing call_id
    """
    now = datetime.utcnow()

    # Create function call without call_id
    call_without_id = FunctionCallContent(
        call_id=None,  # MISSING - should fail!
        name="get_weather",
        arguments='{"location": "Seattle"}'
    )
    # Remove call_id attribute entirely
    delattr(call_without_id, 'call_id')

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="agent",
                contents=[call_without_id]
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject function call without call_id"
    assert any("call" in str(e).lower() and ("id" in str(e).lower() or "required" in str(e).lower())
               for e in result.errors), \
        f"Expected error about missing call_id but got: {result.errors}"


def test_function_result_must_have_name():
    """
    Test validation rule: FunctionResultContent requires name.

    Spec: docs/specifications/validation.md line 324
    - **Required**: `callId`, `name`

    Expected behavior: Should reject function result without name
    Current behavior: May allow missing name
    """
    now = datetime.utcnow()

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                role="agent",
                contents=[
                    FunctionCallContent(
                        call_id="call_123",
                        name="get_weather",
                        arguments='{"location": "Seattle"}'
                    )
                ]
            ),
            MockMessage(
                message_id="msg_002",
                created_at=now,
                role="tool",
                contents=[
                    FunctionResultContent(
                        call_id="call_123",
                        name=None,  # MISSING - should fail!
                        result='{"temperature": 52}'
                    )
                ]
            ),
        ]
    )

    validator = ThreadValidator()
    result = validator.validate(thread)

    assert not result.is_valid, "Should reject function result without name"
    assert any("name" in str(e).lower() and ("required" in str(e).lower() or "must have" in str(e).lower())
               for e in result.errors), \
        f"Expected error about missing name but got: {result.errors}"


if __name__ == "__main__":
    # Run tests and show which ones are failing (expected to fail)
    pytest.main([__file__, "-v", "--tb=short"])
