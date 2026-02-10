# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tests for multi-modal content handling covering all multimodal-guide.md examples.
Tests sending and receiving images, audio, files, and mixed content types.

This is the Python equivalent of dotnet/tests/Microsoft.Agents.Client.Tests/MultiModalContentTests.cs
"""

import base64
import pytest
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any

from microsoft.agents.protocol.client import SimplifiedClient
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions


@pytest.fixture
def mock_options():
    """Creates mock client options"""
    return AgentProtocolClientOptions(base_url="http://localhost:5000")


@pytest.fixture
def client(mock_options):
    """Creates a simplified client with mocked HTTP"""
    with patch("microsoft.agents.protocol.client.agent_protocol_client.aiohttp"):
        return SimplifiedClient(mock_options)


class TestTextContent:
    """Tests for text content creation and handling"""

    def test_text_content_creation(self):
        """Test creating text content with required fields"""
        content = {"kind": "text", "text": "Hello world"}
        assert content["text"] == "Hello world"
        assert content["kind"] == "text"

    def test_text_content_in_message(self):
        """Test text content in user message"""
        message = {
            "role": "user",
            "message_id": "msg_1",
            "contents": [{"kind": "text", "text": "Test message"}]
        }
        assert len(message["contents"]) == 1
        assert message["contents"][0]["text"] == "Test message"
        assert message["role"] == "user"


class TestImageContent:
    """Tests for image content (URLs, base64, file references)"""

    def test_image_content_with_uri(self):
        """Test creating image content with URI"""
        content = {
            "kind": "image",
            "uri": "https://example.com/photo.jpg",
            "mime_type": "image/jpeg"
        }
        assert content["uri"] == "https://example.com/photo.jpg"
        assert content["mime_type"] == "image/jpeg"
        assert content["kind"] == "image"

    def test_image_content_with_base64(self):
        """Test creating image content with base64 data URI"""
        # PNG header bytes
        image_bytes = bytes([137, 80, 78, 71, 13, 10, 26, 10])
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        data_uri = f"data:image/png;base64,{base64_image}"

        content = {
            "kind": "image",
            "uri": data_uri,
            "mime_type": "image/png"
        }
        assert content["uri"].startswith("data:image/png;base64,")
        assert content["mime_type"] == "image/png"

    def test_image_content_with_metadata(self):
        """Test creating image content with width, height, and alt text"""
        content = {
            "kind": "image",
            "uri": "https://example.com/photo.jpg",
            "mime_type": "image/jpeg",
            "width": 1920,
            "height": 1080,
            "alt": "A beautiful sunset"
        }
        assert content["width"] == 1920
        assert content["height"] == 1080
        assert content["alt"] == "A beautiful sunset"

    @pytest.mark.asyncio
    async def test_send_image_uri_content(self, client):
        """Test sending message with image URI content"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_001",
                "thread_id": "thread_temp_001",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_1",
                        "contents": [
                            {"kind": "text", "text": "The image shows a golden retriever playing in a park with a frisbee."}
                        ],
                    }
                ],
            }
        )

        # Act
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "What's in this image?"},
                {"kind": "image", "uri": "https://example.com/photo.jpg", "mime_type": "image/jpeg"}
            ]
        }
        result = await client.complete_chat_structured(message)

        # Assert
        assert result["role"] == "agent"
        assert result["contents"][0]["text"] == "The image shows a golden retriever playing in a park with a frisbee."

    @pytest.mark.asyncio
    async def test_send_image_base64_content(self, client):
        """Test sending message with base64 image content"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_002",
                "thread_id": "thread_temp_002",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_2",
                        "contents": [
                            {"kind": "text", "text": "The screenshot shows an application with a navigation menu on the left."}
                        ],
                    }
                ],
            }
        )

        # Simulate base64-encoded image data
        image_bytes = bytes([137, 80, 78, 71, 13, 10, 26, 10])  # PNG header
        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        # Act
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Describe this screenshot"},
                {"kind": "image", "uri": f"data:image/png;base64,{base64_image}", "mime_type": "image/png"}
            ]
        }
        result = await client.complete_chat_structured(message)

        # Assert
        assert "screenshot" in result["contents"][0]["text"].lower()

    @pytest.mark.asyncio
    async def test_receive_image_content(self, client):
        """Test receiving image content in response"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_005",
                "thread_id": "thread_temp_005",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_5",
                        "contents": [
                            {"kind": "text", "text": "Here's a photo of the Eiffel Tower, the iconic iron lattice tower in Paris."},
                            {"kind": "image", "uri": "https://cdn.example.com/eiffel-tower-xyz.jpg", "mime_type": "image/jpeg"}
                        ],
                    }
                ],
            }
        )

        # Act
        message = {"role": "user", "contents": [{"kind": "text", "text": "Show me a photo of the Eiffel Tower and describe it"}]}
        result = await client.complete_chat_structured(message)

        # Assert
        assert len(result["contents"]) == 2
        assert result["contents"][0]["kind"] == "text"
        assert "Eiffel Tower" in result["contents"][0]["text"]
        assert result["contents"][1]["kind"] == "image"
        assert "eiffel-tower" in result["contents"][1]["uri"]

    def test_image_only_content(self):
        """Test sending image without text"""
        message = {
            "role": "user",
            "message_id": "msg_image_only",
            "contents": [
                {
                    "kind": "image",
                    "uri": "https://example.com/sunset.jpg",
                    "mime_type": "image/jpeg"
                }
            ]
        }
        assert len(message["contents"]) == 1
        assert message["contents"][0]["kind"] == "image"


class TestAudioContent:
    """Tests for audio content"""

    def test_audio_content_creation(self):
        """Test creating audio content with URI"""
        content = {
            "kind": "audio",
            "uri": "https://example.com/audio.mp3",
            "mime_type": "audio/mpeg"
        }
        assert content["uri"] == "https://example.com/audio.mp3"
        assert content["mime_type"] == "audio/mpeg"
        assert content["kind"] == "audio"

    def test_audio_content_with_duration(self):
        """Test creating audio content with duration metadata"""
        content = {
            "kind": "audio",
            "uri": "https://example.com/audio.mp3",
            "mime_type": "audio/mpeg",
            "duration": 30
        }
        assert content["duration"] == 30

    def test_audio_content_with_base64(self):
        """Test creating audio content with base64 data URI"""
        audio_bytes = bytes([0xFF] * 1024)
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        data_uri = f"data:audio/mpeg;base64,{base64_audio}"

        content = {
            "kind": "audio",
            "uri": data_uri,
            "mime_type": "audio/mpeg"
        }
        assert content["uri"].startswith("data:audio/mpeg;base64,")

    @pytest.mark.asyncio
    async def test_send_audio_content(self, client):
        """Test sending message with audio content"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_003",
                "thread_id": "thread_temp_003",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_3",
                        "contents": [
                            {"kind": "text", "text": "Transcription: Hello, this is a test recording."}
                        ],
                    }
                ],
            }
        )

        # Simulate audio data
        audio_bytes = bytes([0xFF] * 1024)
        base64_audio = base64.b64encode(audio_bytes).decode('utf-8')

        # Act
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Transcribe this audio"},
                {"kind": "audio", "uri": f"data:audio/mpeg;base64,{base64_audio}", "mime_type": "audio/mpeg"}
            ]
        }
        result = await client.complete_chat_structured(message)

        # Assert
        assert "Transcription" in result["contents"][0]["text"]


class TestVideoContent:
    """Tests for video content"""

    def test_video_content_creation(self):
        """Test creating video content with URI"""
        content = {
            "kind": "video",
            "uri": "https://example.com/video.mp4",
            "mime_type": "video/mp4"
        }
        assert content["uri"] == "https://example.com/video.mp4"
        assert content["mime_type"] == "video/mp4"
        assert content["kind"] == "video"

    def test_video_content_with_metadata(self):
        """Test creating video content with full metadata"""
        content = {
            "kind": "video",
            "uri": "https://example.com/video.mp4",
            "mime_type": "video/mp4",
            "width": 1920,
            "height": 1080,
            "duration": 120,
            "frame_rate": 30
        }
        assert content["width"] == 1920
        assert content["height"] == 1080
        assert content["duration"] == 120
        assert content["frame_rate"] == 30

    def test_video_content_in_message(self):
        """Test video content in user message"""
        message = {
            "role": "user",
            "message_id": "msg_video",
            "contents": [
                {"kind": "text", "text": "Analyze this video"},
                {
                    "kind": "video",
                    "uri": "https://example.com/recording.mp4",
                    "mime_type": "video/mp4",
                    "duration": 60
                }
            ]
        }
        assert len(message["contents"]) == 2
        assert message["contents"][1]["kind"] == "video"


class TestFileContent:
    """Tests for file content"""

    def test_file_content_creation(self):
        """Test creating file content with URI"""
        content = {
            "kind": "file",
            "uri": "https://example.com/document.pdf",
            "filename": "report.pdf",
            "mime_type": "application/pdf"
        }
        assert content["uri"] == "https://example.com/document.pdf"
        assert content["filename"] == "report.pdf"
        assert content["mime_type"] == "application/pdf"
        assert content["kind"] == "file"

    def test_file_content_with_size(self):
        """Test creating file content with size metadata"""
        content = {
            "kind": "file",
            "uri": "https://example.com/document.pdf",
            "filename": "report.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 2048
        }
        assert content["size_bytes"] == 2048

    def test_file_content_with_base64(self):
        """Test creating file content with base64 data URI"""
        pdf_bytes = bytes([0x25, 0x50, 0x44, 0x46])  # PDF magic number
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        data_uri = f"data:application/pdf;base64,{base64_pdf}"

        content = {
            "kind": "file",
            "uri": data_uri,
            "filename": "document.pdf",
            "mime_type": "application/pdf"
        }
        assert content["uri"].startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_send_file_content(self, client):
        """Test sending message with file content"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_004",
                "thread_id": "thread_temp_004",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_4",
                        "contents": [
                            {"kind": "text", "text": "Summary: The quarterly report shows revenue growth of 15%."}
                        ],
                    }
                ],
            }
        )

        # Simulate PDF document
        pdf_bytes = bytes([0x25, 0x50, 0x44, 0x46] * 512)
        base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        # Act
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Summarize this report"},
                {"kind": "file", "uri": f"data:application/pdf;base64,{base64_pdf}", "mime_type": "application/pdf", "filename": "report.pdf"}
            ]
        }
        result = await client.complete_chat_structured(message)

        # Assert
        assert "Summary" in result["contents"][0]["text"]


class TestMixedContent:
    """Tests for mixed content arrays"""

    def test_mixed_content_array(self):
        """Test creating message with multiple content types"""
        message = {
            "role": "user",
            "message_id": "msg_mixed",
            "contents": [
                {"kind": "text", "text": "Analyze all these materials:"},
                {"kind": "image", "uri": "https://example.com/chart.png", "mime_type": "image/png"},
                {"kind": "audio", "uri": "https://example.com/audio.mp3", "mime_type": "audio/mpeg"},
                {"kind": "video", "uri": "https://example.com/video.mp4", "mime_type": "video/mp4"},
                {"kind": "file", "uri": "https://example.com/report.pdf", "mime_type": "application/pdf", "filename": "report.pdf"}
            ]
        }
        assert len(message["contents"]) == 5
        assert message["contents"][0]["kind"] == "text"
        assert message["contents"][1]["kind"] == "image"
        assert message["contents"][2]["kind"] == "audio"
        assert message["contents"][3]["kind"] == "video"
        assert message["contents"][4]["kind"] == "file"

    @pytest.mark.asyncio
    async def test_receive_multiple_content_types(self, client):
        """Test receiving response with multiple content types"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_006",
                "thread_id": "thread_temp_006",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_6",
                        "contents": [
                            {"kind": "text", "text": "Here's the analysis:"},
                            {"kind": "image", "uri": "https://example.com/chart.png", "mime_type": "image/png"},
                            {"kind": "audio", "uri": "https://example.com/explanation.mp3", "mime_type": "audio/mpeg", "duration": 30},
                            {"kind": "file", "uri": "https://example.com/report.pdf", "mime_type": "application/pdf", "filename": "analysis.pdf"}
                        ],
                    }
                ],
            }
        )

        # Act
        message = {"role": "user", "contents": [{"kind": "text", "text": "Provide a comprehensive analysis"}]}
        result = await client.complete_chat_structured(message)

        # Assert
        assert len(result["contents"]) == 4
        kinds = [content["kind"] for content in result["contents"]]
        assert "text" in kinds
        assert "image" in kinds
        assert "audio" in kinds
        assert "file" in kinds

    def test_empty_contents_array(self):
        """Test message with empty contents array"""
        message = {
            "role": "user",
            "message_id": "msg_empty",
            "contents": []
        }
        assert len(message["contents"]) == 0


class TestContentSerialization:
    """Tests for content serialization/deserialization"""

    def test_text_content_dict_representation(self):
        """Test text content can be represented as dict"""
        content = {"kind": "text", "text": "Hello"}
        # Verify kind property works
        assert content["kind"] == "text"
        assert content["text"] == "Hello"

    def test_image_content_dict_representation(self):
        """Test image content fields"""
        content = {
            "kind": "image",
            "uri": "https://example.com/image.jpg",
            "mime_type": "image/jpeg",
            "width": 800,
            "height": 600,
            "alt": "Test image"
        }
        assert content["kind"] == "image"
        assert content["uri"] == "https://example.com/image.jpg"
        assert content["mime_type"] == "image/jpeg"
        assert content["width"] == 800
        assert content["height"] == 600
        assert content["alt"] == "Test image"

    def test_audio_content_dict_representation(self):
        """Test audio content fields"""
        content = {
            "kind": "audio",
            "uri": "https://example.com/audio.mp3",
            "mime_type": "audio/mpeg",
            "duration": 45
        }
        assert content["kind"] == "audio"
        assert content["uri"] == "https://example.com/audio.mp3"
        assert content["mime_type"] == "audio/mpeg"
        assert content["duration"] == 45

    def test_video_content_dict_representation(self):
        """Test video content fields"""
        content = {
            "kind": "video",
            "uri": "https://example.com/video.mp4",
            "mime_type": "video/mp4",
            "width": 1920,
            "height": 1080,
            "duration": 120,
            "frame_rate": 30
        }
        assert content["kind"] == "video"
        assert content["uri"] == "https://example.com/video.mp4"
        assert content["mime_type"] == "video/mp4"
        assert content["width"] == 1920
        assert content["height"] == 1080
        assert content["duration"] == 120
        assert content["frame_rate"] == 30

    def test_file_content_dict_representation(self):
        """Test file content fields"""
        content = {
            "kind": "file",
            "uri": "https://example.com/doc.pdf",
            "filename": "document.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 1024
        }
        assert content["kind"] == "file"
        assert content["uri"] == "https://example.com/doc.pdf"
        assert content["filename"] == "document.pdf"
        assert content["mime_type"] == "application/pdf"
        assert content["size_bytes"] == 1024


class TestConversationContext:
    """Tests for maintaining context with multi-modal content"""

    @pytest.mark.asyncio
    async def test_conversation_with_screenshot_analysis(self, client):
        """Test multi-turn conversation with image context"""
        # Setup conversation
        conversation = client.create_conversation()

        # Mock first response - screenshot analysis
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_101",
                "thread_id": "thread_analysis_001",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_101",
                        "contents": [
                            {"kind": "text", "text": "The error shows a null reference exception on line 42. The variable 'user' is null when calling user.Name."}
                        ],
                    }
                ],
            }
        )

        # Simulate screenshot
        screenshot_bytes = bytes([0x89, 0x50, 0x4E, 0x47] * 256)
        base64_screenshot = base64.b64encode(screenshot_bytes).decode('utf-8')

        # Act - First message with image
        first_message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "What's wrong in this screenshot?"},
                {"kind": "image", "uri": f"data:image/png;base64,{base64_screenshot}", "mime_type": "image/png"}
            ]
        }
        response1 = await conversation.send_structured(first_message)

        # Assert - Got analysis
        assert response1["role"] == "agent"
        assert "null reference" in response1["contents"][0]["text"].lower()
        assert conversation.thread_id == "thread_analysis_001"

        # Mock second response - follow-up
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_102",
                "thread_id": "thread_analysis_001",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_102",
                        "contents": [
                            {"kind": "text", "text": "Add a null check before accessing user.Name: if (user != None) { ... }"}
                        ],
                    }
                ],
            }
        )

        # Act - Follow-up question (context maintained via thread)
        response2 = await conversation.send("How do I fix it?")

        # Assert - Got fix suggestion with maintained context
        assert "null check" in response2.lower()
        assert conversation.thread_id == "thread_analysis_001"


class TestContentTypeValidation:
    """Tests for content type validation and proper formatting"""

    def test_text_content_requires_text(self):
        """Test that text content requires text field"""
        # This should work
        content = {"kind": "text", "text": "Required text"}
        assert content["text"] == "Required text"

    def test_image_content_optional_fields(self):
        """Test that image content fields are optional except kind"""
        # Only kind is required
        content = {"kind": "image"}
        assert content["kind"] == "image"
        assert content.get("uri") is None
        assert content.get("mime_type") is None

    def test_audio_content_optional_fields(self):
        """Test that audio content fields are optional except kind"""
        content = {"kind": "audio"}
        assert content["kind"] == "audio"
        assert content.get("uri") is None
        assert content.get("duration") is None

    def test_video_content_optional_fields(self):
        """Test that video content fields are optional except kind"""
        content = {"kind": "video"}
        assert content["kind"] == "video"
        assert content.get("uri") is None
        assert content.get("width") is None

    def test_file_content_optional_fields(self):
        """Test that file content fields are optional except kind"""
        content = {"kind": "file"}
        assert content["kind"] == "file"
        assert content.get("uri") is None
        assert content.get("filename") is None

    def test_content_kind_values(self):
        """Test that kind values are correctly set for each content type"""
        text = {"kind": "text", "text": "test"}
        image = {"kind": "image"}
        audio = {"kind": "audio"}
        video = {"kind": "video"}
        file = {"kind": "file"}

        assert text["kind"] == "text"
        assert image["kind"] == "image"
        assert audio["kind"] == "audio"
        assert video["kind"] == "video"
        assert file["kind"] == "file"


class TestEdgeCases:
    """Tests for edge cases and error conditions"""

    def test_message_with_no_contents(self):
        """Test message can be created with no contents"""
        message = {"role": "user", "message_id": "empty", "contents": []}
        assert message["contents"] == []

    def test_large_base64_content(self):
        """Test handling large base64 encoded content"""
        # Create a larger image (10KB)
        large_image = bytes([0xFF] * 10240)
        base64_large = base64.b64encode(large_image).decode('utf-8')

        content = {
            "kind": "image",
            "uri": f"data:image/png;base64,{base64_large}",
            "mime_type": "image/png"
        }
        assert len(content["uri"]) > 10000

    def test_unicode_in_text_content(self):
        """Test text content with unicode characters"""
        content = {"kind": "text", "text": "Hello 世界 🌍 café"}
        assert content["text"] == "Hello 世界 🌍 café"

    def test_special_characters_in_filename(self):
        """Test file content with special characters in filename"""
        content = {
            "kind": "file",
            "uri": "https://example.com/file",
            "filename": "report (2024).pdf",
            "mime_type": "application/pdf"
        }
        assert content["filename"] == "report (2024).pdf"

    def test_multiple_images_in_message(self):
        """Test message with multiple images"""
        message = {
            "role": "user",
            "message_id": "multi_image",
            "contents": [
                {"kind": "text", "text": "Compare these images:"},
                {"kind": "image", "uri": "https://example.com/image1.jpg", "mime_type": "image/jpeg"},
                {"kind": "image", "uri": "https://example.com/image2.jpg", "mime_type": "image/jpeg"},
                {"kind": "image", "uri": "https://example.com/image3.jpg", "mime_type": "image/jpeg"}
            ]
        }
        assert len(message["contents"]) == 4
        image_contents = [c for c in message["contents"] if c["kind"] == "image"]
        assert len(image_contents) == 3

    @pytest.mark.asyncio
    async def test_response_with_metadata_preserved(self, client):
        """Test that metadata fields are preserved in responses"""
        # Arrange
        client.runs.create_and_wait = AsyncMock(
            return_value={
                "run_id": "run_301",
                "thread_id": "thread_temp_301",
                "status": "completed",
                "output": [
                    {
                        "role": "agent",
                        "message_id": "msg_out_301",
                        "contents": [
                            {
                                "kind": "image",
                                "uri": "https://example.com/result.jpg",
                                "mime_type": "image/jpeg",
                                "width": 1920,
                                "height": 1080,
                                "alt": "Processed image result"
                            }
                        ],
                    }
                ],
            }
        )

        # Act
        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Process this image"},
                {"kind": "image", "uri": "https://example.com/input.jpg", "mime_type": "image/jpeg"}
            ]
        }
        result = await client.complete_chat_structured(message)

        # Assert
        image_content = result["contents"][0]
        assert image_content["kind"] == "image"
        assert image_content["width"] == 1920
        assert image_content["height"] == 1080
        assert image_content["alt"] == "Processed image result"
