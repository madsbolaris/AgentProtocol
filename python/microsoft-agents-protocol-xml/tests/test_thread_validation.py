"""
Thread-level validation tests for agent-xml Python implementation.

Tests that thread-level validation works correctly, including:
- Tool result call-ids match preceding function call call-ids
- Messages are in chronological order
- Message IDs are unique within a thread
"""

from pathlib import Path

import pytest

# Get path to shared test data at repository root
TEST_DATA_PATH = Path(__file__).parent.parent.parent.parent / "test-data" / "input"
ERROR_TEST_DATA_PATH = TEST_DATA_PATH.parent / "input" / "errors"


def test_valid_thread_with_tool_use_passes_validation():
    """
    Test that a valid thread with tool use passes validation.

    This test uses 29-thread-with-tool-use.xml which has:
    - User message
    - Agent message with function-call (call-id="call_123")
    - Tool message with function-result (call-id="call_123") - MATCHES
    - Agent message with response
    """
    pytest.skip("Waiting for thread validation implementation")

    # from microsoft.agents.xml.serialization import MessageSerializer
    # from microsoft.agents.xml.validation import ThreadValidator

    # # Arrange
    # file_path = TEST_DATA_PATH / "29-thread-with-tool-use.xml"
    # xml_content = file_path.read_text(encoding="utf-8")
    # serializer = MessageSerializer()

    # # Act - Deserialize thread
    # thread = serializer.deserialize(xml_content)

    # # Act - Validate thread
    # validator = ThreadValidator()
    # result = validator.validate(thread)

    # # Assert - Should pass validation
    # assert result.is_valid, f"Expected valid thread but got errors: {result.errors}"
    # print(f"✅ Valid thread passed validation")


def test_thread_with_mismatched_call_id_fails_validation():
    """
    Test that a thread with mismatched tool result call-id fails validation.

    This test uses 31-error-thread-tool-result-mismatched-call-id.xml which has:
    - User message
    - Agent message with function-call (call-id="call_123")
    - Tool message with function-result (call-id="call_999") - MISMATCH!

    This should fail validation because call_999 doesn't match any preceding function call.
    """
    pytest.skip("Waiting for thread validation implementation")

    # from microsoft.agents.xml.serialization import MessageSerializer
    # from microsoft.agents.xml.validation import ThreadValidator, ValidationError

    # # Arrange
    # file_path = ERROR_TEST_DATA_PATH / "31-error-thread-tool-result-mismatched-call-id.xml"
    # xml_content = file_path.read_text(encoding="utf-8")
    # serializer = MessageSerializer()

    # # Act - Deserialize thread
    # thread = serializer.deserialize(xml_content)

    # # Act - Validate thread
    # validator = ThreadValidator()
    # result = validator.validate(thread)

    # # Assert - Should fail validation
    # assert not result.is_valid, "Expected validation to fail for mismatched call-id"
    # assert any("call-id" in str(e).lower() or "call_999" in str(e).lower()
    #           for e in result.errors), \
    #     f"Expected error about mismatched call-id but got: {result.errors}"
    # print(f"✅ Mismatched call-id correctly rejected")


def test_standalone_tool_message_without_context():
    """
    Test that a standalone tool message (tested in isolation) can still deserialize.

    File 08-tool-result-simple.xml contains a tool message with call-id="call_002"
    but no preceding function call. When tested as a standalone message (not in a thread),
    this might be valid for scenarios like:
    - Testing individual message serialization
    - Storing individual messages in a database
    - Messages received out of order

    However, when validated in a thread context, it should fail if there's no matching call.
    """
    pytest.skip("Waiting for message deserialization implementation")

    # from microsoft.agents.xml.serialization import MessageSerializer

    # # Arrange
    # file_path = TEST_DATA_PATH / "08-tool-result-simple.xml"
    # xml_content = file_path.read_text(encoding="utf-8")
    # serializer = MessageSerializer()

    # # Act - Deserialize as standalone message
    # message = serializer.deserialize(xml_content)

    # # Assert - Should deserialize successfully (no thread context validation)
    # assert message is not None
    # assert message.message_id
    # assert message.call_id == "call_002"
    # print(f"✅ Standalone tool message deserialized successfully")


def test_thread_validator_tracks_function_calls():
    """
    Test that the thread validator correctly tracks function call IDs.

    A valid thread should:
    1. Track function call IDs when encountering function-call elements
    2. Validate that function-result elements have matching call IDs
    3. Clear or track call IDs appropriately across messages
    """
    pytest.skip("Waiting for thread validation implementation")

    # from microsoft.agents.xml.validation import ThreadValidator
    # from microsoft.agents.xml.models import (
    #     Thread, UserMessage, AgentMessage, ToolMessage,
    #     TextContent, FunctionCallContent, FunctionResultContent
    # )
    # from datetime import datetime

    # # Arrange - Build thread programmatically
    # now = datetime.utcnow()
    # thread = Thread(
    #     thread_id="thread_test_001",
    #     created_at=now,
    #     messages=[
    #         UserMessage(
    #             message_id="msg_001",
    #             user_id="user_123",
    #             created_at=now,
    #             contents=[TextContent(text="Call the weather API")]
    #         ),
    #         AgentMessage(
    #             message_id="msg_002",
    #             agent_id="agent_001",
    #             created_at=now,
    #             contents=[
    #                 FunctionCallContent(
    #                     call_id="call_abc",
    #                     name="get_weather",
    #                     arguments='{"location": "Seattle"}'
    #                 )
    #             ]
    #         ),
    #         ToolMessage(
    #             message_id="msg_003",
    #             call_id="call_abc",  # Matches above
    #             created_at=now,
    #             contents=[
    #                 FunctionResultContent(
    #                     call_id="call_abc",
    #                     result='{"temp": 52}'
    #                 )
    #             ]
    #         ),
    #     ]
    # )

    # # Act
    # validator = ThreadValidator()
    # result = validator.validate(thread)

    # # Assert
    # assert result.is_valid, f"Expected valid thread but got errors: {result.errors}"
    # print(f"✅ Thread validator correctly tracked function call IDs")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
