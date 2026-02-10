"""Tests for model instantiation to improve coverage of generated code."""

import pytest
from datetime import datetime
from microsoft.agents.xml.models.messages import (
    ChatMessage, ChatRole,
    TextContent, ImageContent, AudioContent, VideoContent, FileContent,
    FunctionCallContent, FunctionResultContent, ErrorContent,
    DataContent, TextReasoningContent, TranscriptContent,
    SearchResultContent, DocumentContent, AdaptiveCardContent,
    RefusalContent, ContentFilterResultContent, UriContent,
    UserInputRequestContent, SuggestedActionsContent,
    MessageReactionContent, MessageDeleteContent, MessageUpdateContent
)


class TestContentModels:
    """Test instantiation of content models."""

    def test_text_content(self):
        """Test TextContent instantiation."""
        content = TextContent(text="Hello, world!")
        assert content.text == "Hello, world!"

        content_with_audience = TextContent(text="Test", audience="developer")
        assert content_with_audience.audience == "developer"

    def test_image_content(self):
        """Test ImageContent instantiation."""
        content = ImageContent(uri="https://example.com/image.jpg")
        assert content.uri == "https://example.com/image.jpg"

        content_full = ImageContent(
            uri="https://example.com/image.jpg",
            alt="Test image",
            mime_type="image/jpeg"
        )
        assert content_full.alt == "Test image"
        assert content_full.mime_type == "image/jpeg"

    def test_audio_content(self):
        """Test AudioContent instantiation."""
        content = AudioContent(uri="https://example.com/audio.mp3")
        assert content.uri == "https://example.com/audio.mp3"

        content_with_mime = AudioContent(
            uri="https://example.com/audio.mp3",
            mime_type="audio/mpeg"
        )
        assert content_with_mime.mime_type == "audio/mpeg"

    def test_video_content(self):
        """Test VideoContent instantiation."""
        content = VideoContent(uri="https://example.com/video.mp4")
        assert content.uri == "https://example.com/video.mp4"

        content_with_mime = VideoContent(
            uri="https://example.com/video.mp4",
            mime_type="video/mp4"
        )
        assert content_with_mime.mime_type == "video/mp4"

    def test_file_content(self):
        """Test FileContent instantiation."""
        content = FileContent(uri="https://example.com/doc.pdf")
        assert content.uri == "https://example.com/doc.pdf"

        content_full = FileContent(
            uri="https://example.com/doc.pdf",
            filename="document.pdf",
            mime_type="application/pdf"
        )
        assert content_full.filename == "document.pdf"
        assert content_full.mime_type == "application/pdf"

    def test_function_call_content(self):
        """Test FunctionCallContent instantiation."""
        content = FunctionCallContent(
            call_id="call-1",
            name="get_weather",
            arguments='{"city": "SF"}'
        )
        assert content.call_id == "call-1"
        assert content.name == "get_weather"
        assert content.arguments == '{"city": "SF"}'

    def test_function_result_content(self):
        """Test FunctionResultContent instantiation."""
        content = FunctionResultContent(
            call_id="call-1",
            name="get_weather",
            result="Sunny, 72°F"
        )
        assert content.call_id == "call-1"
        assert content.name == "get_weather"
        assert content.result == "Sunny, 72°F"

    def test_error_content(self):
        """Test ErrorContent instantiation."""
        content = ErrorContent(
            message="An error occurred",
            code="ERROR_001"
        )
        assert content.message == "An error occurred"
        assert content.code == "ERROR_001"

    def test_data_content(self):
        """Test DataContent instantiation."""
        content = DataContent(
            data="Some data",
            mime_type="application/json"
        )
        assert content.data == "Some data"
        assert content.mime_type == "application/json"


class TestMessageModels:
    """Test instantiation of message models."""

    def test_user_message(self):
        """Test user message instantiation."""
        message = ChatMessage(
            message_id="msg-1",
            role=ChatRole.USER,
            contents=[TextContent(text="Hello")]
        )
        assert message.message_id == "msg-1"
        assert message.role == ChatRole.USER
        assert len(message.contents) == 1
        assert message.contents[0].text == "Hello"

    def test_agent_message(self):
        """Test agent message instantiation."""
        message = ChatMessage(
            message_id="msg-2",
            role=ChatRole.AGENT,
            contents=[TextContent(text="Hi there")]
        )
        assert message.message_id == "msg-2"
        assert message.role == ChatRole.AGENT

    def test_system_message(self):
        """Test system message instantiation."""
        message = ChatMessage(
            message_id="msg-3",
            role=ChatRole.SYSTEM,
            contents=[TextContent(text="System message")]
        )
        assert message.message_id == "msg-3"
        assert message.role == ChatRole.SYSTEM

    def test_developer_message(self):
        """Test developer message instantiation."""
        message = ChatMessage(
            message_id="msg-4",
            role=ChatRole.DEVELOPER,
            contents=[TextContent(text="Developer message")]
        )
        assert message.message_id == "msg-4"
        assert message.role == ChatRole.DEVELOPER

    def test_tool_message(self):
        """Test tool message instantiation."""
        message = ChatMessage(
            message_id="msg-5",
            role=ChatRole.TOOL,
            contents=[
                FunctionResultContent(
                    call_id="call-1",
                    name="get_weather",
                    result="Sunny"
                )
            ]
        )
        assert message.message_id == "msg-5"
        assert message.role == ChatRole.TOOL

    def test_channel_message(self):
        """Test channel message instantiation."""
        message = ChatMessage(
            message_id="msg-6",
            role=ChatRole.CHANNEL,
            contents=[TextContent(text="Channel message")]
        )
        assert message.message_id == "msg-6"
        assert message.role == ChatRole.CHANNEL

    def test_message_with_multiple_contents(self):
        """Test message with multiple content items."""
        message = ChatMessage(
            message_id="msg-multi",
            role=ChatRole.USER,
            contents=[
                TextContent(text="Check this out:"),
                ImageContent(uri="https://example.com/img.jpg"),
                TextContent(text="What do you think?")
            ]
        )
        assert message.message_id == "msg-multi"
        assert len(message.contents) == 3
        assert isinstance(message.contents[0], TextContent)
        assert isinstance(message.contents[1], ImageContent)
        assert isinstance(message.contents[2], TextContent)

    def test_message_with_parent(self):
        """Test message with parent_message_id."""
        message = ChatMessage(
            message_id="msg-child",
            role=ChatRole.USER,
            parent_message_id="msg-parent",
            contents=[TextContent(text="Reply")]
        )
        assert message.parent_message_id == "msg-parent"

    def test_message_with_thread_id(self):
        """Test message with thread_id."""
        message = ChatMessage(
            message_id="msg-thread",
            role=ChatRole.USER,
            thread_id="thread-123",
            contents=[TextContent(text="Hello")]
        )
        assert message.thread_id == "thread-123"

    def test_all_chat_roles(self):
        """Test all ChatRole enum values."""
        assert ChatRole.SYSTEM == "system"
        assert ChatRole.DEVELOPER == "developer"
        assert ChatRole.USER == "user"
        assert ChatRole.AGENT == "agent"
        assert ChatRole.TOOL == "tool"
        assert ChatRole.CHANNEL == "channel"

    def test_text_reasoning_content(self):
        """Test TextReasoningContent instantiation."""
        content = TextReasoningContent(text="Let me think...")
        assert content.text == "Let me think..."

    def test_uri_content(self):
        """Test UriContent instantiation."""
        content = UriContent(uri="https://example.com")
        assert content.uri == "https://example.com"

    def test_transcript_content(self):
        """Test TranscriptContent instantiation."""
        content = TranscriptContent(text="Transcribed text")
        assert content.text == "Transcribed text"

    def test_search_result_content(self):
        """Test SearchResultContent instantiation."""
        content = SearchResultContent(
            title="Result",
            uri="https://example.com"
        )
        assert content.title == "Result"

    def test_document_content(self):
        """Test DocumentContent instantiation."""
        content = DocumentContent(
            title="Doc",
            uri="https://example.com/doc"
        )
        assert content.title == "Doc"

    def test_adaptive_card_content(self):
        """Test AdaptiveCardContent instantiation."""
        content = AdaptiveCardContent(card='{"type":"AdaptiveCard"}')
        assert content.card == '{"type":"AdaptiveCard"}'

    def test_refusal_content(self):
        """Test RefusalContent instantiation."""
        content = RefusalContent(message="I cannot help with that")
        assert content.message == "I cannot help with that"

    def test_content_filter_result_content(self):
        """Test ContentFilterResultContent instantiation."""
        content = ContentFilterResultContent(result="filtered")
        assert content.result == "filtered"

    def test_user_input_request_content(self):
        """Test UserInputRequestContent instantiation."""
        content = UserInputRequestContent(prompt="Please enter your name")
        assert content.prompt == "Please enter your name"

    def test_suggested_actions_content(self):
        """Test SuggestedActionsContent instantiation."""
        content = SuggestedActionsContent(actions=["Yes", "No"])
        assert content.actions == ["Yes", "No"]

    def test_message_reaction_content(self):
        """Test MessageReactionContent instantiation."""
        content = MessageReactionContent(
            message_id="msg-1",
            reaction="thumbs_up"
        )
        assert content.message_id == "msg-1"
        assert content.reaction == "thumbs_up"

    def test_message_delete_content(self):
        """Test MessageDeleteContent instantiation."""
        content = MessageDeleteContent(message_id="msg-to-delete")
        assert content.message_id == "msg-to-delete"

    def test_message_update_content(self):
        """Test MessageUpdateContent instantiation."""
        content = MessageUpdateContent(
            message_id="msg-to-update",
            updated_text="New text"
        )
        assert content.message_id == "msg-to-update"
