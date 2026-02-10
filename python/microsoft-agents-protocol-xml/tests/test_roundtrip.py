"""
Round-trip serialization tests for agent-xml Python implementation.

Port of AgentXml.CodeGen.Tests/RoundTripTests.cs to Python.

Tests that XML files can be deserialized and serialized back with no data loss.
"""

from pathlib import Path

import pytest

# Get path to shared test data at repository root
TEST_DATA_PATH = Path(__file__).parent.parent.parent.parent / "test-data" / "input"


def get_test_files():
    """Get all XML test files from the shared test-data directory."""
    if not TEST_DATA_PATH.exists():
        return []
    return sorted(TEST_DATA_PATH.glob("*.xml"))


@pytest.mark.parametrize(
    "xml_file",
    get_test_files(),
    ids=lambda f: f.name
)
def test_roundtrip_test_file_preserves_all_data(xml_file: Path):
    """
    Test that XML files can be deserialized and serialized back with no data loss.

    Equivalent to C#: RoundTrip_TestFile_PreservesAllData

    This test loads an XML file, deserializes it, serializes it back,
    and verifies perfect round-trip (no data loss).
    """
    pytest.skip("Waiting for generated models and working serialization")

    # from microsoft.agents.xml.serialization import XmlSerializer, XmlDeserializer
    # from microsoft.agents.xml.models.messages import ChatMessage

    # # Arrange
    # original_xml = xml_file.read_text(encoding="utf-8")

    # # Act - Deserialize
    # deserializer = XmlDeserializer()
    # message = deserializer.deserialize(original_xml, ChatMessage)
    # assert message is not None, f"Failed to deserialize {xml_file.name}"

    # # Act - Serialize back
    # serializer = XmlSerializer(pretty_print=True)
    # serialized_xml = serializer.serialize(message)
    # assert serialized_xml, f"Failed to serialize {xml_file.name}"

    # # Assert - Compare XMLs (semantically, not byte-by-byte)
    # # TODO: Implement XML comparison logic
    # assert_xml_equivalent(original_xml, serialized_xml, xml_file.name)

    # print(f"✅ {xml_file.name} - Round-trip successful")
    # print(f"   Message Type: {type(message).__name__}")
    # print(f"   Message ID: {message.message_id}")


def test_roundtrip_system_message_preserves_all_properties():
    """
    Test that a SystemMessage round-trip preserves all properties.

    Equivalent to C#: RoundTrip_SystemMessage_PreservesAllProperties
    """
    pytest.skip("Waiting for generated models")

    # from microsoft.agents.xml.serialization import XmlSerializer, XmlDeserializer
    # from microsoft.agents.xml.models.messages import SystemMessage, ChatRole

    # # Arrange
    # file_path = TEST_DATA_PATH / "01-system-message.xml"
    # original_xml = file_path.read_text(encoding="utf-8")

    # # Act - Deserialize
    # deserializer = XmlDeserializer()
    # message = deserializer.deserialize(original_xml, SystemMessage)

    # # Assert properties
    # assert message.message_id
    # assert not message.thread_id  # ThreadId should NOT be deserialized (marked xmlIgnore)
    # assert message.created_at
    # assert "helpful AI assistant" in message.content
    # assert message.role == ChatRole.SYSTEM

    # # Serialize and compare
    # serializer = XmlSerializer(pretty_print=True)
    # serialized = serializer.serialize(message)
    # assert_xml_equivalent(original_xml, serialized, "01-system-message.xml")


def test_roundtrip_user_message_preserves_all_properties():
    """
    Test that a UserMessage round-trip preserves all properties.

    Equivalent to C#: RoundTrip_UserMessage_PreservesAllProperties
    """
    pytest.skip("Waiting for generated models")

    # from microsoft.agents.xml.serialization import XmlSerializer, XmlDeserializer
    # from microsoft.agents.xml.models.messages import UserMessage, ChatRole

    # # Arrange
    # file_path = TEST_DATA_PATH / "03-user-text-only.xml"
    # original_xml = file_path.read_text(encoding="utf-8")

    # # Act - Deserialize
    # deserializer = XmlDeserializer()
    # message = deserializer.deserialize(original_xml, UserMessage)

    # # Assert properties
    # assert message.message_id
    # assert message.user_id
    # assert message.contents
    # assert len(message.contents) > 0
    # assert message.role == ChatRole.USER

    # # Serialize and compare
    # serializer = XmlSerializer(pretty_print=True)
    # serialized = serializer.serialize(message)
    # assert_xml_equivalent(original_xml, serialized, "03-user-text-only.xml")


def test_roundtrip_agent_message_with_function_call():
    """
    Test that an AgentMessage with function call round-trips correctly.

    Equivalent to C#: RoundTrip_AgentMessage_WithFunctionCall
    """
    pytest.skip("Waiting for generated models")

    # from microsoft.agents.xml.serialization import XmlSerializer, XmlDeserializer
    # from microsoft.agents.xml.models.messages import AgentMessage, FunctionCallContent

    # # Arrange
    # file_path = TEST_DATA_PATH / "06-agent-thinking-and-call.xml"
    # original_xml = file_path.read_text(encoding="utf-8")

    # # Act - Deserialize
    # deserializer = XmlDeserializer()
    # message = deserializer.deserialize(original_xml, AgentMessage)

    # # Assert properties
    # assert message.message_id
    # assert message.agent_id
    # assert message.completion_id
    # assert message.contents

    # # Find function call content
    # function_calls = [c for c in message.contents if isinstance(c, FunctionCallContent)]
    # assert len(function_calls) > 0, "Should have at least one function call"

    # # Serialize and compare
    # serializer = XmlSerializer(pretty_print=True)
    # serialized = serializer.serialize(message)
    # assert_xml_equivalent(original_xml, serialized, "06-agent-thinking-and-call.xml")


def test_roundtrip_tool_message_with_result():
    """
    Test that a ToolMessage with result round-trips correctly.

    Equivalent to C#: RoundTrip_ToolMessage_WithResult
    """
    pytest.skip("Waiting for generated models")

    # from microsoft.agents.xml.serialization import XmlSerializer, XmlDeserializer
    # from microsoft.agents.xml.models.messages import ToolMessage, FunctionResultContent

    # # Arrange
    # file_path = TEST_DATA_PATH / "07-tool-result-success.xml"
    # original_xml = file_path.read_text(encoding="utf-8")

    # # Act - Deserialize
    # deserializer = XmlDeserializer()
    # message = deserializer.deserialize(original_xml, ToolMessage)

    # # Assert properties
    # assert message.message_id
    # assert message.contents

    # # Find function result content
    # function_results = [c for c in message.contents if isinstance(c, FunctionResultContent)]
    # assert len(function_results) > 0, "Should have at least one function result"

    # # Serialize and compare
    # serializer = XmlSerializer(pretty_print=True)
    # serialized = serializer.serialize(message)
    # assert_xml_equivalent(original_xml, serialized, "07-tool-result-success.xml")


def assert_xml_equivalent(xml1: str, xml2: str, filename: str):
    """
    Assert that two XML strings are semantically equivalent.

    This compares the XML structure and values, ignoring formatting differences.
    """
    # TODO: Implement proper XML comparison
    # For now, just check they're both non-empty
    assert xml1.strip(), f"{filename}: Original XML is empty"
    assert xml2.strip(), f"{filename}: Serialized XML is empty"

    # Future: Use lxml or xmldiff to compare XML semantically
    # from lxml import etree
    # tree1 = etree.fromstring(xml1.encode('utf-8'))
    # tree2 = etree.fromstring(xml2.encode('utf-8'))
    # assert etree.tostring(tree1, method='c14n') == etree.tostring(tree2, method='c14n')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
