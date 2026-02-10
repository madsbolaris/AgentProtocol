"""
Auto-generated property validation tests.
Tests that every property serializes and deserializes correctly.
"""

import pytest
from microsoft.agents.xml.serialization import MessageSerializer
from microsoft.agents.xml.models.messages import (
    TextContent,
    FunctionCallContent,
    FunctionResultContent,
    ErrorContent,
    TextReasoningContent,
    DataContent,
    UriContent,
    ImageContent,
    AudioContent,
    TranscriptContent,
    VideoContent,
    FileContent,
    SearchResultContent,
    DocumentContent,
    AdaptiveCardContent,
    RefusalContent,
    ContentFilterResultContent,
    UserInputRequestContent,
    SuggestedActionsContent,
    EventContent,
    TraceContent,
    ActionContent,
    TypingIndicatorContent,
    MessageReactionContent,
    MessageDeleteContent,
    MessageUpdateContent,
    HostedFileContent,
    HostedVectorStoreContent,
)


# TextContent Property Tests

def test_text_content_text_property():
    """Test TextContent.text property serialization."""
    # Arrange: XML with text property set
    xml = """<agent message-id="test_text_content_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_1">
  <text>test_value</text>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TextContent)
    assert content.text is not None
    assert content.text == test_value


# FunctionCallContent Property Tests

def test_function_call_content_call_id_property():
    """Test FunctionCallContent.callId property serialization."""
    # Arrange: XML with callId property set
    xml = """<agent message-id="test_function_call_content_call_id_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_2">
  <function-call call-id="test_id_123" name="test">test</function-call>
</agent>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionCallContent)
    assert content.call_id is not None
    assert content.call_id == test_value


def test_function_call_content_name_property():
    """Test FunctionCallContent.name property serialization."""
    # Arrange: XML with name property set
    xml = """<agent message-id="test_function_call_content_name_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_3">
  <function-call call-id="test" name="Test Name">test</function-call>
</agent>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionCallContent)
    assert content.name is not None
    assert content.name == test_value


def test_function_call_content_arguments_property():
    """Test FunctionCallContent.arguments property serialization."""
    # Arrange: XML with arguments property set
    xml = """<agent message-id="test_function_call_content_arguments_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_4">
  <function-call call-id="test" name="test">test_value</function-call>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionCallContent)
    assert content.arguments is not None
    assert content.arguments == test_value


# FunctionResultContent Property Tests

def test_function_result_content_call_id_property():
    """Test FunctionResultContent.callId property serialization."""
    # Arrange: XML with callId property set
    xml = """<tool message-id="test_function_result_content_call_id_property_msg" created-at="2026-02-07T10:00:00Z">
  <function-result call-id="test_id_123">test</function-result>
</tool>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionResultContent)
    assert content.call_id is not None
    assert content.call_id == test_value


def test_function_result_content_name_property():
    """Test FunctionResultContent.name property serialization."""
    # Arrange: XML with name property set
    xml = """<tool message-id="test_function_result_content_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <function-result name="Test Name">test</function-result>
</tool>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionResultContent)
    assert content.name is not None
    assert content.name == test_value


def test_function_result_content_result_property():
    """Test FunctionResultContent.result property serialization."""
    # Arrange: XML with result property set
    xml = """<tool message-id="test_function_result_content_result_property_msg" created-at="2026-02-07T10:00:00Z">
  <function-result>test_value</function-result>
</tool>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionResultContent)
    assert content.result is not None
    assert content.result == test_value


# ErrorContent Property Tests

def test_error_content_code_property():
    """Test ErrorContent.code property serialization."""
    # Arrange: XML with code property set
    xml = """<agent message-id="test_error_content_code_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_8">
  <error code="test_value">
    <message>test</message>
  </error>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ErrorContent)
    assert content.code is not None
    assert content.code == test_value


def test_error_content_message_property():
    """Test ErrorContent.message property serialization."""
    # Arrange: XML with message property set
    xml = """<agent message-id="test_error_content_message_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_9">
  <error>
    <message>test_value</message>
  </error>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ErrorContent)
    assert content.message is not None
    assert content.message == test_value


def test_error_content_stack_trace_property():
    """Test ErrorContent.stackTrace property serialization."""
    # Arrange: XML with stackTrace property set
    xml = """<agent message-id="test_error_content_stack_trace_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_10">
  <error>
    <message>test</message>
    <stack-trace>test_value</stack-trace>
  </error>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ErrorContent)
    assert content.stack_trace is not None
    assert content.stack_trace == test_value


# TextReasoningContent Property Tests

def test_text_reasoning_content_text_property():
    """Test TextReasoningContent.text property serialization."""
    # Arrange: XML with text property set
    xml = """<agent message-id="test_text_reasoning_content_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_11">
  <thinking>test_value</thinking>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TextReasoningContent)
    assert content.text is not None
    assert content.text == test_value


def test_text_reasoning_content_exposed_property():
    """Test TextReasoningContent.exposed property serialization."""
    # Arrange: XML with exposed property set
    xml = """<agent message-id="test_text_reasoning_content_exposed_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_12">
  <thinking exposed="true">test</thinking>
</agent>
"""
    test_value = "true"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TextReasoningContent)
    assert content.exposed is not None
    assert content.exposed == (test_value.lower() == 'true')


# DataContent Property Tests

def test_data_content_uri_property():
    """Test DataContent.uri property serialization."""
    # Arrange: XML with uri property set
    xml = """<agent message-id="test_data_content_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_13">
  <data uri="https://example.com"/>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DataContent)
    assert content.uri is not None
    assert content.uri == test_value


def test_data_content_mime_type_property():
    """Test DataContent.mimeType property serialization."""
    # Arrange: XML with mimeType property set
    xml = """<agent message-id="test_data_content_mime_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_14">
  <data mime-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DataContent)
    assert content.mime_type is not None
    assert content.mime_type == test_value


def test_data_content_value_property():
    """Test DataContent.value property serialization."""
    # Arrange: XML with value property set
    xml = """<agent message-id="test_data_content_value_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_15">
  <data>test_value</data>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DataContent)
    assert content.value is not None
    assert content.value == test_value


# UriContent Property Tests

def test_uri_content_uri_property():
    """Test UriContent.uri property serialization."""
    # Arrange: XML with uri property set
    xml = """<agent message-id="test_uri_content_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_16">
  <uri>https://example.com</uri>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UriContent)
    assert content.uri is not None
    assert content.uri == test_value


# ImageContent Property Tests

def test_image_content_uri_property():
    """Test ImageContent.uri property serialization."""
    # Arrange: XML with uri property set
    xml = """<agent message-id="test_image_content_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_17">
  <image uri="https://example.com"/>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)
    assert content.uri is not None
    assert content.uri == test_value


def test_image_content_alt_property():
    """Test ImageContent.alt property serialization."""
    # Arrange: XML with alt property set
    xml = """<agent message-id="test_image_content_alt_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_18">
  <image alt="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)
    assert content.alt is not None
    assert content.alt == test_value


def test_image_content_mime_type_property():
    """Test ImageContent.mimeType property serialization."""
    # Arrange: XML with mimeType property set
    xml = """<agent message-id="test_image_content_mime_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_19">
  <image mime-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)
    assert content.mime_type is not None
    assert content.mime_type == test_value


def test_image_content_width_property():
    """Test ImageContent.width property serialization."""
    # Arrange: XML with width property set
    xml = """<agent message-id="test_image_content_width_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_20">
  <image width="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)
    assert content.width is not None
    assert content.width == int(test_value)


def test_image_content_height_property():
    """Test ImageContent.height property serialization."""
    # Arrange: XML with height property set
    xml = """<agent message-id="test_image_content_height_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_21">
  <image height="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)
    assert content.height is not None
    assert content.height == int(test_value)


# AudioContent Property Tests

def test_audio_content_uri_property():
    """Test AudioContent.uri property serialization."""
    # Arrange: XML with uri property set
    xml = """<agent message-id="test_audio_content_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_22">
  <audio uri="https://example.com"/>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AudioContent)
    assert content.uri is not None
    assert content.uri == test_value


def test_audio_content_mime_type_property():
    """Test AudioContent.mimeType property serialization."""
    # Arrange: XML with mimeType property set
    xml = """<agent message-id="test_audio_content_mime_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_23">
  <audio mime-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AudioContent)
    assert content.mime_type is not None
    assert content.mime_type == test_value


def test_audio_content_duration_property():
    """Test AudioContent.duration property serialization."""
    # Arrange: XML with duration property set
    xml = """<agent message-id="test_audio_content_duration_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_24">
  <audio duration="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AudioContent)
    assert content.duration is not None
    assert content.duration == int(test_value)


# TranscriptContent Property Tests

def test_transcript_content_text_property():
    """Test TranscriptContent.text property serialization."""
    # Arrange: XML with text property set
    xml = """<agent message-id="test_transcript_content_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_25">
  <transcript text="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TranscriptContent)
    assert content.text is not None
    assert content.text == test_value


def test_transcript_content_language_property():
    """Test TranscriptContent.language property serialization."""
    # Arrange: XML with language property set
    xml = """<agent message-id="test_transcript_content_language_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_26">
  <transcript text="test" language="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TranscriptContent)
    assert content.language is not None
    assert content.language == test_value


def test_transcript_content_confidence_property():
    """Test TranscriptContent.confidence property serialization."""
    # Arrange: XML with confidence property set
    xml = """<agent message-id="test_transcript_content_confidence_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_27">
  <transcript text="test" confidence="3.14"/>
</agent>
"""
    test_value = "3.14"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TranscriptContent)
    assert content.confidence is not None
    assert abs(content.confidence - float(test_value)) < 0.01


def test_transcript_content_speaker_property():
    """Test TranscriptContent.speaker property serialization."""
    # Arrange: XML with speaker property set
    xml = """<agent message-id="test_transcript_content_speaker_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_28">
  <transcript text="test" speaker="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TranscriptContent)
    assert content.speaker is not None
    assert content.speaker == test_value


# VideoContent Property Tests

def test_video_content_uri_property():
    """Test VideoContent.uri property serialization."""
    # Arrange: XML with uri property set
    xml = """<agent message-id="test_video_content_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_29">
  <video uri="https://example.com"/>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.uri is not None
    assert content.uri == test_value


def test_video_content_mime_type_property():
    """Test VideoContent.mimeType property serialization."""
    # Arrange: XML with mimeType property set
    xml = """<agent message-id="test_video_content_mime_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_30">
  <video mime-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.mime_type is not None
    assert content.mime_type == test_value


def test_video_content_width_property():
    """Test VideoContent.width property serialization."""
    # Arrange: XML with width property set
    xml = """<agent message-id="test_video_content_width_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_31">
  <video width="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.width is not None
    assert content.width == int(test_value)


def test_video_content_height_property():
    """Test VideoContent.height property serialization."""
    # Arrange: XML with height property set
    xml = """<agent message-id="test_video_content_height_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_32">
  <video height="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.height is not None
    assert content.height == int(test_value)


def test_video_content_duration_property():
    """Test VideoContent.duration property serialization."""
    # Arrange: XML with duration property set
    xml = """<agent message-id="test_video_content_duration_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_33">
  <video duration="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.duration is not None
    assert content.duration == int(test_value)


def test_video_content_frame_rate_property():
    """Test VideoContent.frameRate property serialization."""
    # Arrange: XML with frameRate property set
    xml = """<agent message-id="test_video_content_frame_rate_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_34">
  <video frame-rate="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.frame_rate is not None
    assert content.frame_rate == int(test_value)


# FileContent Property Tests

def test_file_content_uri_property():
    """Test FileContent.uri property serialization."""
    # Arrange: XML with uri property set
    xml = """<agent message-id="test_file_content_uri_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_35">
  <file uri="https://example.com"/>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FileContent)
    assert content.uri is not None
    assert content.uri == test_value


def test_file_content_filename_property():
    """Test FileContent.filename property serialization."""
    # Arrange: XML with filename property set
    xml = """<agent message-id="test_file_content_filename_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_36">
  <file filename="Test Name"/>
</agent>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FileContent)
    assert content.filename is not None
    assert content.filename == test_value


def test_file_content_mime_type_property():
    """Test FileContent.mimeType property serialization."""
    # Arrange: XML with mimeType property set
    xml = """<agent message-id="test_file_content_mime_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_37">
  <file mime-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FileContent)
    assert content.mime_type is not None
    assert content.mime_type == test_value


def test_file_content_size_bytes_property():
    """Test FileContent.sizeBytes property serialization."""
    # Arrange: XML with sizeBytes property set
    xml = """<agent message-id="test_file_content_size_bytes_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_38">
  <file size-bytes="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FileContent)
    assert content.size_bytes is not None
    assert content.size_bytes == int(test_value)


# SearchResultContent Property Tests

def test_search_result_content_title_property():
    """Test SearchResultContent.title property serialization."""
    # Arrange: XML with title property set
    xml = """<agent message-id="test_search_result_content_title_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_39">
  <search-result title="test_value" url="test">
    <snippet>test</snippet>
  </search-result>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SearchResultContent)
    assert content.title is not None
    assert content.title == test_value


def test_search_result_content_url_property():
    """Test SearchResultContent.url property serialization."""
    # Arrange: XML with url property set
    xml = """<agent message-id="test_search_result_content_url_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_40">
  <search-result title="test" url="https://example.com">
    <snippet>test</snippet>
  </search-result>
</agent>
"""
    test_value = "https://example.com"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SearchResultContent)
    assert content.url is not None
    assert content.url == test_value


def test_search_result_content_score_property():
    """Test SearchResultContent.score property serialization."""
    # Arrange: XML with score property set
    xml = """<agent message-id="test_search_result_content_score_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_41">
  <search-result title="test" url="test" score="3.14">
    <snippet>test</snippet>
  </search-result>
</agent>
"""
    test_value = "3.14"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SearchResultContent)
    assert content.score is not None
    assert abs(content.score - float(test_value)) < 0.01


def test_search_result_content_snippet_property():
    """Test SearchResultContent.snippet property serialization."""
    # Arrange: XML with snippet property set
    xml = """<agent message-id="test_search_result_content_snippet_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_42">
  <search-result title="test" url="test">
    <snippet>test_value</snippet>
  </search-result>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SearchResultContent)
    assert content.snippet is not None
    assert content.snippet == test_value


# DocumentContent Property Tests

def test_document_content_title_property():
    """Test DocumentContent.title property serialization."""
    # Arrange: XML with title property set
    xml = """<agent message-id="test_document_content_title_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_43">
  <document title="test_value" document-id="test" source="test"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)
    assert content.title is not None
    assert content.title == test_value


def test_document_content_document_id_property():
    """Test DocumentContent.documentId property serialization."""
    # Arrange: XML with documentId property set
    xml = """<agent message-id="test_document_content_document_id_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_44">
  <document title="test" document-id="test_id_123" source="test"/>
</agent>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)
    assert content.document_id is not None
    assert content.document_id == test_value


def test_document_content_source_property():
    """Test DocumentContent.source property serialization."""
    # Arrange: XML with source property set
    xml = """<agent message-id="test_document_content_source_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_45">
  <document title="test" document-id="test" source="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)
    assert content.source is not None
    assert content.source == test_value


def test_document_content_mime_type_property():
    """Test DocumentContent.mimeType property serialization."""
    # Arrange: XML with mimeType property set
    xml = """<agent message-id="test_document_content_mime_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_46">
  <document title="test" document-id="test" source="test" mime-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)
    assert content.mime_type is not None
    assert content.mime_type == test_value


def test_document_content_content_property():
    """Test DocumentContent.content property serialization."""
    # Arrange: XML with content property set
    xml = """<agent message-id="test_document_content_content_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_47">
  <document title="test" document-id="test" source="test">
    <content>test_value</content>
  </document>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)
    assert content.content is not None
    assert content.content == test_value


# AdaptiveCardContent Property Tests

def test_adaptive_card_content_version_property():
    """Test AdaptiveCardContent.version property serialization."""
    # Arrange: XML with version property set
    xml = """<agent message-id="test_adaptive_card_content_version_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_48">
  <adaptive-card version="test_value">test</adaptive-card>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AdaptiveCardContent)
    assert content.version is not None
    assert content.version == test_value


def test_adaptive_card_content_fallback_text_property():
    """Test AdaptiveCardContent.fallbackText property serialization."""
    # Arrange: XML with fallbackText property set
    xml = """<agent message-id="test_adaptive_card_content_fallback_text_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_49">
  <adaptive-card fallback-text="test_value">test</adaptive-card>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AdaptiveCardContent)
    assert content.fallback_text is not None
    assert content.fallback_text == test_value


def test_adaptive_card_content_card_property():
    """Test AdaptiveCardContent.card property serialization."""
    # Arrange: XML with card property set
    xml = """<agent message-id="test_adaptive_card_content_card_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_50">
  <adaptive-card>test_value</adaptive-card>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AdaptiveCardContent)
    assert content.card is not None
    assert content.card == test_value


# RefusalContent Property Tests

def test_refusal_content_reason_property():
    """Test RefusalContent.reason property serialization."""
    # Arrange: XML with reason property set
    xml = """<agent message-id="test_refusal_content_reason_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_51">
  <refusal reason="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, RefusalContent)
    assert content.reason is not None
    assert content.reason == test_value


# ContentFilterResultContent Property Tests

def test_content_filter_result_content_filtered_property():
    """Test ContentFilterResultContent.filtered property serialization."""
    # Arrange: XML with filtered property set
    xml = """<agent message-id="test_content_filter_result_content_filtered_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_52">
  <content-filter-result filtered="true" category="test" severity="test"/>
</agent>
"""
    test_value = "true"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ContentFilterResultContent)
    assert content.filtered is not None
    assert content.filtered == (test_value.lower() == 'true')


def test_content_filter_result_content_category_property():
    """Test ContentFilterResultContent.category property serialization."""
    # Arrange: XML with category property set
    xml = """<agent message-id="test_content_filter_result_content_category_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_53">
  <content-filter-result filtered="true" category="test_value" severity="test"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ContentFilterResultContent)
    assert content.category is not None
    assert content.category == test_value


def test_content_filter_result_content_severity_property():
    """Test ContentFilterResultContent.severity property serialization."""
    # Arrange: XML with severity property set
    xml = """<agent message-id="test_content_filter_result_content_severity_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_54">
  <content-filter-result filtered="true" category="test" severity="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ContentFilterResultContent)
    assert content.severity is not None
    assert content.severity == test_value


# UserInputRequestContent Property Tests

def test_user_input_request_content_request_id_property():
    """Test UserInputRequestContent.requestId property serialization."""
    # Arrange: XML with requestId property set
    xml = """<agent message-id="test_user_input_request_content_request_id_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_55">
  <user-input-request request-id="test_id_123" prompt="test"/>
</agent>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UserInputRequestContent)
    assert content.request_id is not None
    assert content.request_id == test_value


def test_user_input_request_content_prompt_property():
    """Test UserInputRequestContent.prompt property serialization."""
    # Arrange: XML with prompt property set
    xml = """<agent message-id="test_user_input_request_content_prompt_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_56">
  <user-input-request request-id="test" prompt="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UserInputRequestContent)
    assert content.prompt is not None
    assert content.prompt == test_value


def test_user_input_request_content_input_type_property():
    """Test UserInputRequestContent.inputType property serialization."""
    # Arrange: XML with inputType property set
    xml = """<agent message-id="test_user_input_request_content_input_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_57">
  <user-input-request request-id="test" prompt="test" input-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UserInputRequestContent)
    assert content.input_type is not None
    assert content.input_type == test_value


def test_user_input_request_content_required_property():
    """Test UserInputRequestContent.required property serialization."""
    # Arrange: XML with required property set
    xml = """<agent message-id="test_user_input_request_content_required_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_58">
  <user-input-request request-id="test" prompt="test" required="true"/>
</agent>
"""
    test_value = "true"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UserInputRequestContent)
    assert content.required is not None
    assert content.required == (test_value.lower() == 'true')


# SuggestedActionsContent Property Tests

def test_suggested_actions_content_actions_property():
    """Test SuggestedActionsContent.actions property serialization."""
    # Arrange: XML with actions property set
    xml = """<agent message-id="test_suggested_actions_content_actions_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_59">
  <suggested-actions>
    <action>test_value</action>
  </suggested-actions>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SuggestedActionsContent)
    assert content.actions is not None
    assert content.actions == test_value


# EventContent Property Tests

def test_event_content_name_property():
    """Test EventContent.name property serialization."""
    # Arrange: XML with name property set
    xml = """<channel message-id="test_event_content_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <event name="Test Name"/>
</channel>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, EventContent)
    assert content.name is not None
    assert content.name == test_value


def test_event_content_timestamp_property():
    """Test EventContent.timestamp property serialization."""
    # Arrange: XML with timestamp property set
    xml = """<channel message-id="test_event_content_timestamp_property_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test" timestamp="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, EventContent)
    assert content.timestamp is not None
    assert content.timestamp == test_value


def test_event_content_value_property():
    """Test EventContent.value property serialization."""
    # Arrange: XML with value property set
    xml = """<channel message-id="test_event_content_value_property_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test">test_value</event>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, EventContent)
    assert content.value is not None
    assert content.value == test_value


# TraceContent Property Tests

def test_trace_content_name_property():
    """Test TraceContent.name property serialization."""
    # Arrange: XML with name property set
    xml = """<channel message-id="test_trace_content_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="Test Name"/>
</channel>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)
    assert content.name is not None
    assert content.name == test_value


def test_trace_content_label_property():
    """Test TraceContent.label property serialization."""
    # Arrange: XML with label property set
    xml = """<channel message-id="test_trace_content_label_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test" label="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)
    assert content.label is not None
    assert content.label == test_value


def test_trace_content_severity_property():
    """Test TraceContent.severity property serialization."""
    # Arrange: XML with severity property set
    xml = """<channel message-id="test_trace_content_severity_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test" severity="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)
    assert content.severity is not None
    assert content.severity == test_value


def test_trace_content_timestamp_property():
    """Test TraceContent.timestamp property serialization."""
    # Arrange: XML with timestamp property set
    xml = """<channel message-id="test_trace_content_timestamp_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test" timestamp="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)
    assert content.timestamp is not None
    assert content.timestamp == test_value


def test_trace_content_value_property():
    """Test TraceContent.value property serialization."""
    # Arrange: XML with value property set
    xml = """<channel message-id="test_trace_content_value_property_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test">test_value</trace>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)
    assert content.value is not None
    assert content.value == test_value


# ActionContent Property Tests

def test_action_content_name_property():
    """Test ActionContent.name property serialization."""
    # Arrange: XML with name property set
    xml = """<channel message-id="test_action_content_name_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="Test Name"/>
</channel>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ActionContent)
    assert content.name is not None
    assert content.name == test_value


def test_action_content_text_property():
    """Test ActionContent.text property serialization."""
    # Arrange: XML with text property set
    xml = """<channel message-id="test_action_content_text_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test" text="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ActionContent)
    assert content.text is not None
    assert content.text == test_value


def test_action_content_timestamp_property():
    """Test ActionContent.timestamp property serialization."""
    # Arrange: XML with timestamp property set
    xml = """<channel message-id="test_action_content_timestamp_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test" timestamp="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ActionContent)
    assert content.timestamp is not None
    assert content.timestamp == test_value


def test_action_content_value_property():
    """Test ActionContent.value property serialization."""
    # Arrange: XML with value property set
    xml = """<channel message-id="test_action_content_value_property_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test">test_value</action>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ActionContent)
    assert content.value is not None
    assert content.value == test_value


# TypingIndicatorContent Property Tests

def test_typing_indicator_content_from_property():
    """Test TypingIndicatorContent.from property serialization."""
    # Arrange: XML with from property set
    xml = """<channel message-id="test_typing_indicator_content_from_property_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test_value" status="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TypingIndicatorContent)
    assert content.from_ is not None
    assert content.from_ == test_value


def test_typing_indicator_content_status_property():
    """Test TypingIndicatorContent.status property serialization."""
    # Arrange: XML with status property set
    xml = """<channel message-id="test_typing_indicator_content_status_property_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test" status="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TypingIndicatorContent)
    assert content.status is not None
    assert content.status == test_value


def test_typing_indicator_content_timestamp_property():
    """Test TypingIndicatorContent.timestamp property serialization."""
    # Arrange: XML with timestamp property set
    xml = """<channel message-id="test_typing_indicator_content_timestamp_property_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test" status="test_value" timestamp="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TypingIndicatorContent)
    assert content.timestamp is not None
    assert content.timestamp == test_value


# MessageReactionContent Property Tests

def test_message_reaction_content_referenced_message_id_property():
    """Test MessageReactionContent.referencedMessageId property serialization."""
    # Arrange: XML with referencedMessageId property set
    xml = """<channel message-id="test_message_reaction_content_referenced_message_id_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test_id_123"/>
</channel>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageReactionContent)
    assert content.referenced_message_id is not None
    assert content.referenced_message_id == test_value


def test_message_reaction_content_reactions_added_property():
    """Test MessageReactionContent.reactionsAdded property serialization."""
    # Arrange: XML with reactionsAdded property set
    xml = """<channel message-id="test_message_reaction_content_reactions_added_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test">
    <added>test_value</added>
  </message-reaction>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageReactionContent)
    assert content.reactions_added is not None
    assert content.reactions_added == test_value


def test_message_reaction_content_reactions_removed_property():
    """Test MessageReactionContent.reactionsRemoved property serialization."""
    # Arrange: XML with reactionsRemoved property set
    xml = """<channel message-id="test_message_reaction_content_reactions_removed_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test">
    <removed>test_value</removed>
  </message-reaction>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageReactionContent)
    assert content.reactions_removed is not None
    assert content.reactions_removed == test_value


# MessageDeleteContent Property Tests

def test_message_delete_content_message_id_property():
    """Test MessageDeleteContent.messageId property serialization."""
    # Arrange: XML with messageId property set
    xml = """<channel message-id="test_message_delete_content_message_id_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test_id_123"/>
</channel>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageDeleteContent)
    assert content.message_id is not None
    assert content.message_id == test_value


def test_message_delete_content_reason_property():
    """Test MessageDeleteContent.reason property serialization."""
    # Arrange: XML with reason property set
    xml = """<channel message-id="test_message_delete_content_reason_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test" reason="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageDeleteContent)
    assert content.reason is not None
    assert content.reason == test_value


# MessageUpdateContent Property Tests

def test_message_update_content_message_id_property():
    """Test MessageUpdateContent.messageId property serialization."""
    # Arrange: XML with messageId property set
    xml = """<channel message-id="test_message_update_content_message_id_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test_id_123"/>
</channel>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageUpdateContent)
    assert content.message_id is not None
    assert content.message_id == test_value


def test_message_update_content_reason_property():
    """Test MessageUpdateContent.reason property serialization."""
    # Arrange: XML with reason property set
    xml = """<channel message-id="test_message_update_content_reason_property_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test" reason="test_value"/>
</channel>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageUpdateContent)
    assert content.reason is not None
    assert content.reason == test_value


# HostedFileContent Property Tests

def test_hosted_file_content_file_id_property():
    """Test HostedFileContent.fileId property serialization."""
    # Arrange: XML with fileId property set
    xml = """<agent message-id="test_hosted_file_content_file_id_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_82">
  <hosted-file file-id="test_id_123"/>
</agent>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedFileContent)
    assert content.file_id is not None
    assert content.file_id == test_value


def test_hosted_file_content_filename_property():
    """Test HostedFileContent.filename property serialization."""
    # Arrange: XML with filename property set
    xml = """<agent message-id="test_hosted_file_content_filename_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_83">
  <hosted-file file-id="test" filename="Test Name"/>
</agent>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedFileContent)
    assert content.filename is not None
    assert content.filename == test_value


def test_hosted_file_content_media_type_property():
    """Test HostedFileContent.mediaType property serialization."""
    # Arrange: XML with mediaType property set
    xml = """<agent message-id="test_hosted_file_content_media_type_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_84">
  <hosted-file file-id="test" media-type="test_value"/>
</agent>
"""
    test_value = "test_value"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedFileContent)
    assert content.media_type is not None
    assert content.media_type == test_value


def test_hosted_file_content_size_bytes_property():
    """Test HostedFileContent.sizeBytes property serialization."""
    # Arrange: XML with sizeBytes property set
    xml = """<agent message-id="test_hosted_file_content_size_bytes_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_85">
  <hosted-file file-id="test" size-bytes="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedFileContent)
    assert content.size_bytes is not None
    assert content.size_bytes == int(test_value)


# HostedVectorStoreContent Property Tests

def test_hosted_vector_store_content_vector_store_id_property():
    """Test HostedVectorStoreContent.vectorStoreId property serialization."""
    # Arrange: XML with vectorStoreId property set
    xml = """<agent message-id="test_hosted_vector_store_content_vector_store_id_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_86">
  <hosted-vector-store vector-store-id="test_id_123"/>
</agent>
"""
    test_value = "test_id_123"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedVectorStoreContent)
    assert content.vector_store_id is not None
    assert content.vector_store_id == test_value


def test_hosted_vector_store_content_name_property():
    """Test HostedVectorStoreContent.name property serialization."""
    # Arrange: XML with name property set
    xml = """<agent message-id="test_hosted_vector_store_content_name_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_87">
  <hosted-vector-store vector-store-id="test" name="Test Name"/>
</agent>
"""
    test_value = "Test Name"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedVectorStoreContent)
    assert content.name is not None
    assert content.name == test_value


def test_hosted_vector_store_content_document_count_property():
    """Test HostedVectorStoreContent.documentCount property serialization."""
    # Arrange: XML with documentCount property set
    xml = """<agent message-id="test_hosted_vector_store_content_document_count_property_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_88">
  <hosted-vector-store vector-store-id="test" document-count="42"/>
</agent>
"""
    test_value = "42"

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify property value
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedVectorStoreContent)
    assert content.document_count is not None
    assert content.document_count == int(test_value)


# Discriminator Tests

def test_text_content_discriminator():
    """Test TextContent discriminator field."""
    # Arrange: XML with text discriminator
    xml = """<agent message-id="test_text_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_89">
  <text>test</text>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TextContent)
    assert content.kind == "text"


def test_function_call_content_discriminator():
    """Test FunctionCallContent discriminator field."""
    # Arrange: XML with functionCall discriminator
    xml = """<agent message-id="test_function_call_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_90">
  <function-call call-id="test" name="test">test</function-call>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionCallContent)
    assert content.kind == "functionCall"


def test_function_result_content_discriminator():
    """Test FunctionResultContent discriminator field."""
    # Arrange: XML with functionResult discriminator
    xml = """<tool message-id="test_function_result_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <function-result>test</function-result>
</tool>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionResultContent)
    assert content.kind == "functionResult"


def test_error_content_discriminator():
    """Test ErrorContent discriminator field."""
    # Arrange: XML with error discriminator
    xml = """<agent message-id="test_error_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_92">
  <error>
    <message>test</message>
  </error>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ErrorContent)
    assert content.kind == "error"


def test_text_reasoning_content_discriminator():
    """Test TextReasoningContent discriminator field."""
    # Arrange: XML with reasoning discriminator
    xml = """<agent message-id="test_text_reasoning_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_93">
  <thinking>test</thinking>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TextReasoningContent)
    assert content.kind == "reasoning"


def test_data_content_discriminator():
    """Test DataContent discriminator field."""
    # Arrange: XML with data discriminator
    xml = """<agent message-id="test_data_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_94">
  <data/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DataContent)
    assert content.kind == "data"


def test_uri_content_discriminator():
    """Test UriContent discriminator field."""
    # Arrange: XML with uri discriminator
    xml = """<agent message-id="test_uri_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_95">
  <uri>test</uri>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UriContent)
    assert content.kind == "uri"


def test_image_content_discriminator():
    """Test ImageContent discriminator field."""
    # Arrange: XML with image discriminator
    xml = """<agent message-id="test_image_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_96">
  <image/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)
    assert content.kind == "image"


def test_audio_content_discriminator():
    """Test AudioContent discriminator field."""
    # Arrange: XML with audio discriminator
    xml = """<agent message-id="test_audio_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_97">
  <audio/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AudioContent)
    assert content.kind == "audio"


def test_transcript_content_discriminator():
    """Test TranscriptContent discriminator field."""
    # Arrange: XML with transcript discriminator
    xml = """<agent message-id="test_transcript_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_98">
  <transcript text="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TranscriptContent)
    assert content.kind == "transcript"


def test_video_content_discriminator():
    """Test VideoContent discriminator field."""
    # Arrange: XML with video discriminator
    xml = """<agent message-id="test_video_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_99">
  <video/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)
    assert content.kind == "video"


def test_file_content_discriminator():
    """Test FileContent discriminator field."""
    # Arrange: XML with file discriminator
    xml = """<agent message-id="test_file_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_100">
  <file/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FileContent)
    assert content.kind == "file"


def test_search_result_content_discriminator():
    """Test SearchResultContent discriminator field."""
    # Arrange: XML with searchResult discriminator
    xml = """<agent message-id="test_search_result_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_101">
  <search-result title="test" url="test">
    <snippet>test</snippet>
  </search-result>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SearchResultContent)
    assert content.kind == "searchResult"


def test_document_content_discriminator():
    """Test DocumentContent discriminator field."""
    # Arrange: XML with document discriminator
    xml = """<agent message-id="test_document_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_102">
  <document title="test" document-id="test" source="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)
    assert content.kind == "document"


def test_adaptive_card_content_discriminator():
    """Test AdaptiveCardContent discriminator field."""
    # Arrange: XML with adaptiveCard discriminator
    xml = """<agent message-id="test_adaptive_card_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_103">
  <adaptive-card>test</adaptive-card>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AdaptiveCardContent)
    assert content.kind == "adaptiveCard"


def test_refusal_content_discriminator():
    """Test RefusalContent discriminator field."""
    # Arrange: XML with refusal discriminator
    xml = """<agent message-id="test_refusal_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_104">
  <refusal reason="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, RefusalContent)
    assert content.kind == "refusal"


def test_content_filter_result_content_discriminator():
    """Test ContentFilterResultContent discriminator field."""
    # Arrange: XML with contentFilterResult discriminator
    xml = """<agent message-id="test_content_filter_result_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_105">
  <content-filter-result filtered="true" category="test" severity="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ContentFilterResultContent)
    assert content.kind == "contentFilterResult"


def test_user_input_request_content_discriminator():
    """Test UserInputRequestContent discriminator field."""
    # Arrange: XML with userInputRequest discriminator
    xml = """<agent message-id="test_user_input_request_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_106">
  <user-input-request request-id="test" prompt="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UserInputRequestContent)
    assert content.kind == "userInputRequest"


def test_suggested_actions_content_discriminator():
    """Test SuggestedActionsContent discriminator field."""
    # Arrange: XML with suggestedActions discriminator
    xml = """<agent message-id="test_suggested_actions_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_107">
  <suggested-actions>
    <action>test_value</action>
  </suggested-actions>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SuggestedActionsContent)
    assert content.kind == "suggestedActions"


def test_event_content_discriminator():
    """Test EventContent discriminator field."""
    # Arrange: XML with event discriminator
    xml = """<channel message-id="test_event_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, EventContent)
    assert content.kind == "event"


def test_trace_content_discriminator():
    """Test TraceContent discriminator field."""
    # Arrange: XML with trace discriminator
    xml = """<channel message-id="test_trace_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)
    assert content.kind == "trace"


def test_action_content_discriminator():
    """Test ActionContent discriminator field."""
    # Arrange: XML with action discriminator
    xml = """<channel message-id="test_action_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ActionContent)
    assert content.kind == "action"


def test_typing_indicator_content_discriminator():
    """Test TypingIndicatorContent discriminator field."""
    # Arrange: XML with typingIndicator discriminator
    xml = """<channel message-id="test_typing_indicator_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test" status="test_value"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TypingIndicatorContent)
    assert content.kind == "typingIndicator"


def test_message_reaction_content_discriminator():
    """Test MessageReactionContent discriminator field."""
    # Arrange: XML with messageReaction discriminator
    xml = """<channel message-id="test_message_reaction_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageReactionContent)
    assert content.kind == "messageReaction"


def test_message_delete_content_discriminator():
    """Test MessageDeleteContent discriminator field."""
    # Arrange: XML with messageDelete discriminator
    xml = """<channel message-id="test_message_delete_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageDeleteContent)
    assert content.kind == "messageDelete"


def test_message_update_content_discriminator():
    """Test MessageUpdateContent discriminator field."""
    # Arrange: XML with messageUpdate discriminator
    xml = """<channel message-id="test_message_update_content_discriminator_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test"/>
</channel>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageUpdateContent)
    assert content.kind == "messageUpdate"


def test_hosted_file_content_discriminator():
    """Test HostedFileContent discriminator field."""
    # Arrange: XML with hostedFile discriminator
    xml = """<agent message-id="test_hosted_file_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_115">
  <hosted-file file-id="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedFileContent)
    assert content.kind == "hostedFile"


def test_hosted_vector_store_content_discriminator():
    """Test HostedVectorStoreContent discriminator field."""
    # Arrange: XML with hostedVectorStore discriminator
    xml = """<agent message-id="test_hosted_vector_store_content_discriminator_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_116">
  <hosted-vector-store vector-store-id="test"/>
</agent>
"""

    # Act: Deserialize
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Verify correct type is instantiated
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedVectorStoreContent)
    assert content.kind == "hostedVectorStore"


# Required vs Optional Tests

def test_function_result_content_optional_fields_can_be_omitted():
    """Test FunctionResultContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: callId, name
    xml = """<tool message-id="test_function_result_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <function-result>test</function-result>
</tool>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FunctionResultContent)


def test_error_content_optional_fields_can_be_omitted():
    """Test ErrorContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: code, stackTrace
    xml = """<agent message-id="test_error_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_118">
  <error>
    <message>test</message>
  </error>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ErrorContent)


def test_text_reasoning_content_optional_fields_can_be_omitted():
    """Test TextReasoningContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: exposed
    xml = """<agent message-id="test_text_reasoning_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_119">
  <thinking>test</thinking>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TextReasoningContent)


def test_data_content_optional_fields_can_be_omitted():
    """Test DataContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: uri, mimeType, value
    xml = """<agent message-id="test_data_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_120">
  <data/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DataContent)


def test_image_content_optional_fields_can_be_omitted():
    """Test ImageContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: uri, alt, mimeType
    xml = """<agent message-id="test_image_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_121">
  <image/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ImageContent)


def test_audio_content_optional_fields_can_be_omitted():
    """Test AudioContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: uri, mimeType, duration
    xml = """<agent message-id="test_audio_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_122">
  <audio/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AudioContent)


def test_transcript_content_optional_fields_can_be_omitted():
    """Test TranscriptContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: language, confidence, speaker
    xml = """<agent message-id="test_transcript_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_123">
  <transcript text="test"/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TranscriptContent)


def test_video_content_optional_fields_can_be_omitted():
    """Test VideoContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: uri, mimeType, width
    xml = """<agent message-id="test_video_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_124">
  <video/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, VideoContent)


def test_file_content_optional_fields_can_be_omitted():
    """Test FileContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: uri, filename, mimeType
    xml = """<agent message-id="test_file_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_125">
  <file/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, FileContent)


def test_search_result_content_optional_fields_can_be_omitted():
    """Test SearchResultContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: score
    xml = """<agent message-id="test_search_result_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_126">
  <search-result title="test" url="test">
    <snippet>test</snippet>
  </search-result>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, SearchResultContent)


def test_document_content_optional_fields_can_be_omitted():
    """Test DocumentContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: mimeType, content
    xml = """<agent message-id="test_document_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_127">
  <document title="test" document-id="test" source="test"/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, DocumentContent)


def test_adaptive_card_content_optional_fields_can_be_omitted():
    """Test AdaptiveCardContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: version, fallbackText
    xml = """<agent message-id="test_adaptive_card_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_128">
  <adaptive-card>test</adaptive-card>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, AdaptiveCardContent)


def test_user_input_request_content_optional_fields_can_be_omitted():
    """Test UserInputRequestContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: inputType, required
    xml = """<agent message-id="test_user_input_request_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_129">
  <user-input-request request-id="test" prompt="test"/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, UserInputRequestContent)


def test_event_content_optional_fields_can_be_omitted():
    """Test EventContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: timestamp, value
    xml = """<channel message-id="test_event_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <event name="test"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, EventContent)


def test_trace_content_optional_fields_can_be_omitted():
    """Test TraceContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: label, severity, timestamp
    xml = """<channel message-id="test_trace_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <trace name="test"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TraceContent)


def test_action_content_optional_fields_can_be_omitted():
    """Test ActionContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: text, timestamp, value
    xml = """<channel message-id="test_action_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <action name="test"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, ActionContent)


def test_typing_indicator_content_optional_fields_can_be_omitted():
    """Test TypingIndicatorContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: timestamp
    xml = """<channel message-id="test_typing_indicator_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <typing-indicator from="test" status="test_value"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, TypingIndicatorContent)


def test_message_reaction_content_optional_fields_can_be_omitted():
    """Test MessageReactionContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: reactionsAdded, reactionsRemoved
    xml = """<channel message-id="test_message_reaction_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <message-reaction referenced-message-id="test"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageReactionContent)


def test_message_delete_content_optional_fields_can_be_omitted():
    """Test MessageDeleteContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: reason
    xml = """<channel message-id="test_message_delete_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <message-delete message-id="test"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageDeleteContent)


def test_message_update_content_optional_fields_can_be_omitted():
    """Test MessageUpdateContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: reason
    xml = """<channel message-id="test_message_update_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z">
  <message-update message-id="test"/>
</channel>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, MessageUpdateContent)


def test_hosted_file_content_optional_fields_can_be_omitted():
    """Test HostedFileContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: filename, mediaType, sizeBytes
    xml = """<agent message-id="test_hosted_file_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_137">
  <hosted-file file-id="test"/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedFileContent)


def test_hosted_vector_store_content_optional_fields_can_be_omitted():
    """Test HostedVectorStoreContent optional fields can be omitted."""
    # Arrange: XML omitting optional fields: name, documentCount
    xml = """<agent message-id="test_hosted_vector_store_content_optional_fields_can_be_omitted_msg" created-at="2026-02-07T10:00:00Z" agent-id="agent_test_138">
  <hosted-vector-store vector-store-id="test"/>
</agent>
"""

    # Act: Deserialize (should succeed)
    serializer = MessageSerializer()
    message = serializer.deserialize(xml)

    # Assert: Message deserializes successfully
    assert message is not None
    assert len(message.contents) > 0
    content = message.contents[0]
    assert isinstance(content, HostedVectorStoreContent)

