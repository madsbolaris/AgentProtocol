"""
Integration test for thread validation.

This test verifies that the ThreadValidator works correctly
with real Thread objects.
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
    def __init__(self, message_id, created_at, contents=None):
        self.message_id = message_id
        self.created_at = created_at
        self.contents = contents or []


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
    def __init__(self, call_id, name, result):
        self.call_id = call_id
        self.name = name
        self.result = result


def test_thread_validator_accepts_valid_thread():
    """Test that ThreadValidator accepts a valid thread."""
    # Arrange
    now = datetime.utcnow()

    # Create a valid thread with matching call IDs
    function_call = FunctionCallContent(
        call_id="call_123",
        name="get_weather",
        arguments='{"location": "Seattle"}'
    )

    function_result = FunctionResultContent(
        call_id="call_123",  # Matches function call
        name="get_weather",  # Matches function call name
        result='{"temperature": 52}'
    )

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                contents=[function_call]
            ),
            MockMessage(
                message_id="msg_002",
                created_at=now,
                contents=[function_result]
            ),
        ]
    )

    # Act
    validator = ThreadValidator()
    result = validator.validate(thread)

    # Assert
    assert result.is_valid, f"Expected valid thread but got errors: {result.errors}"
    assert len(result.errors) == 0


def test_thread_validator_rejects_mismatched_call_id():
    """Test that ThreadValidator rejects thread with mismatched call-id."""
    # Arrange
    now = datetime.utcnow()

    # Create thread with mismatched call IDs
    function_call = FunctionCallContent(
        call_id="call_123",
        name="get_weather",
        arguments='{"location": "Seattle"}'
    )

    function_result = FunctionResultContent(
        call_id="call_999",  # DOES NOT MATCH - should fail validation
        name="get_weather",
        result='{"temperature": 52}'
    )

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                contents=[function_call]
            ),
            MockMessage(
                message_id="msg_002",
                created_at=now,
                contents=[function_result]
            ),
        ]
    )

    # Act
    validator = ThreadValidator()
    result = validator.validate(thread)

    # Assert
    assert not result.is_valid, "Expected validation to fail for mismatched call-id"
    assert len(result.errors) > 0
    assert any("call_999" in str(e) for e in result.errors), \
        f"Expected error about call_999 but got: {result.errors}"
    assert any("TOOL_001" in str(e.code) for e in result.errors if e.code), \
        f"Expected TOOL_001 error code but got: {[e.code for e in result.errors]}"


def test_thread_validator_rejects_duplicate_message_ids():
    """Test that ThreadValidator rejects threads with duplicate message IDs."""
    # Arrange
    now = datetime.utcnow()

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=now,
                contents=[]
            ),
            MockMessage(
                message_id="msg_001",  # Duplicate!
                created_at=now,
                contents=[]
            ),
        ]
    )

    # Act
    validator = ThreadValidator()
    result = validator.validate(thread)

    # Assert
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("duplicate" in str(e).lower() for e in result.errors)


def test_thread_validator_rejects_out_of_order_messages():
    """Test that ThreadValidator rejects messages not in chronological order."""
    # Arrange
    now = datetime.utcnow()
    earlier = datetime(2026, 1, 1, 10, 0, 0)
    later = datetime(2026, 1, 1, 11, 0, 0)

    thread = MockThread(
        thread_id="thread_001",
        created_at=now,
        messages=[
            MockMessage(
                message_id="msg_001",
                created_at=later,  # Later timestamp first
                contents=[]
            ),
            MockMessage(
                message_id="msg_002",
                created_at=earlier,  # Earlier timestamp second - out of order!
                contents=[]
            ),
        ]
    )

    # Act
    validator = ThreadValidator()
    result = validator.validate(thread)

    # Assert
    assert not result.is_valid
    assert len(result.errors) > 0
    assert any("chronological" in str(e).lower() for e in result.errors)


if __name__ == "__main__":
    pytest.main([__file__, "-xvs"])
