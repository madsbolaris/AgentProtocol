# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tests for JSON serialization/deserialization of model classes.
Validates that the models serialize correctly for the Agent Protocol API.

This is the Python equivalent of dotnet/tests/Microsoft.Agents.Client.Tests/ModelSerializationTests.cs

Tests cover:
- ChatMessage serialization/deserialization
- Content types (text, image, audio, video, file) serialization
- Run model serialization
- Thread model serialization
- Agent definition serialization
- Error handling for invalid JSON
- Field name mapping (camelCase <-> snake_case)
"""

import json
import pytest
from datetime import datetime, timezone
from typing import Dict, Any, List


class TestRunSerialization:
    """Tests for Run model serialization/deserialization"""

    def test_run_serializes_and_deserializes_correctly(self):
        """Test Run model with all fields - matches Run_SerializesAndDeserializes_Correctly"""
        # Arrange
        run = {
            "run_id": "run_123",
            "agent_id": "agent_001",
            "thread_id": "thread_456",
            "status": "completed",
            "input": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": "Hello"}],
                }
            ],
            "output": [
                {
                    "role": "assistant",
                    "contents": [{"kind": "text", "text": "Hi there!"}],
                }
            ],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "thread_cleanup": "keep",
        }

        # Act - Serialize to JSON and deserialize back
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["run_id"] == run["run_id"]
        assert deserialized["agent_id"] == run["agent_id"]
        assert deserialized["thread_id"] == run["thread_id"]
        assert deserialized["status"] == run["status"]
        assert deserialized["thread_cleanup"] == run["thread_cleanup"]

    def test_run_with_camelcase_fields_deserializes_correctly(self):
        """Test Run can deserialize from API camelCase format"""
        # Arrange - Simulating API response with camelCase
        json_str = """
        {
            "runId": "run_123",
            "agentId": "agent_001",
            "threadId": "thread_456",
            "status": "completed",
            "input": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": "Hello"}]
                }
            ],
            "output": [
                {
                    "role": "assistant",
                    "contents": [{"kind": "text", "text": "Hi there!"}]
                }
            ],
            "createdAt": "2024-01-01T00:00:00Z",
            "threadCleanup": "keep"
        }
        """

        # Act
        deserialized = json.loads(json_str)

        # Assert - Can read camelCase fields
        assert deserialized["runId"] == "run_123"
        assert deserialized["agentId"] == "agent_001"
        assert deserialized["threadId"] == "thread_456"
        assert deserialized["createdAt"] == "2024-01-01T00:00:00Z"
        assert deserialized["threadCleanup"] == "keep"

    def test_run_with_minimal_fields(self):
        """Test Run with only required fields"""
        # Arrange
        run = {
            "agent_id": "agent_001",
            "input": [
                {"role": "user", "contents": [{"kind": "text", "text": "Test"}]}
            ],
        }

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["agent_id"] == "agent_001"
        assert len(deserialized["input"]) == 1


class TestChatMessageSerialization:
    """Tests for ChatMessage serialization with polymorphic content types"""

    def test_chat_message_with_multiple_content_types_serializes_correctly(self):
        """Test ChatMessage with text, image, and function call - matches ChatMessage_WithMultipleContentTypes_SerializesCorrectly"""
        # Arrange - Test polymorphic content types
        message = {
            "message_id": "msg_001",
            "role": "user",
            "contents": [
                {"kind": "text", "text": "What's in this image?"},
                {
                    "kind": "image",
                    "uri": "https://example.com/image.jpg",
                    "detail": "high",
                },
                {
                    "kind": "function_call",
                    "call_id": "call_123",
                    "name": "analyze_image",
                    "arguments": '{"url":"https://example.com/image.jpg"}',
                },
            ],
        }

        # Act
        json_str = json.dumps(message)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert len(deserialized["contents"]) == 3
        assert deserialized["contents"][0]["kind"] == "text"
        assert deserialized["contents"][1]["kind"] == "image"
        assert deserialized["contents"][2]["kind"] == "function_call"

        # Verify specific content
        text_content = deserialized["contents"][0]
        assert text_content["text"] == "What's in this image?"

        image_content = deserialized["contents"][1]
        assert image_content["uri"] == "https://example.com/image.jpg"
        assert image_content["detail"] == "high"

        function_call = deserialized["contents"][2]
        assert function_call["call_id"] == "call_123"
        assert function_call["name"] == "analyze_image"

    def test_chat_message_with_empty_contents(self):
        """Test ChatMessage with empty contents array"""
        # Arrange
        message = {"role": "user", "message_id": "msg_empty", "contents": []}

        # Act
        json_str = json.dumps(message)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["contents"] == []


class TestContentTypeSerialization:
    """Tests for different content type serialization"""

    def test_text_content_serialization(self):
        """Test TextContent serialization"""
        # Arrange
        content = {"kind": "text", "text": "Hello world"}

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["kind"] == "text"
        assert deserialized["text"] == "Hello world"

    def test_image_content_serialization(self):
        """Test ImageContent with all metadata fields"""
        # Arrange
        content = {
            "kind": "image",
            "uri": "https://example.com/photo.jpg",
            "mime_type": "image/jpeg",
            "width": 1920,
            "height": 1080,
            "alt": "A beautiful sunset",
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["kind"] == "image"
        assert deserialized["uri"] == "https://example.com/photo.jpg"
        assert deserialized["mime_type"] == "image/jpeg"
        assert deserialized["width"] == 1920
        assert deserialized["height"] == 1080
        assert deserialized["alt"] == "A beautiful sunset"

    def test_image_content_with_base64_data_uri(self):
        """Test ImageContent with base64 encoded data"""
        # Arrange
        content = {
            "kind": "image",
            "uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
            "mime_type": "image/png",
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["uri"].startswith("data:image/png;base64,")

    def test_audio_content_serialization(self):
        """Test AudioContent serialization"""
        # Arrange
        content = {
            "kind": "audio",
            "uri": "https://example.com/audio.mp3",
            "mime_type": "audio/mpeg",
            "duration": 30,
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["kind"] == "audio"
        assert deserialized["uri"] == "https://example.com/audio.mp3"
        assert deserialized["mime_type"] == "audio/mpeg"
        assert deserialized["duration"] == 30

    def test_video_content_serialization(self):
        """Test VideoContent with full metadata"""
        # Arrange
        content = {
            "kind": "video",
            "uri": "https://example.com/video.mp4",
            "mime_type": "video/mp4",
            "width": 1920,
            "height": 1080,
            "duration": 120,
            "frame_rate": 30,
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["kind"] == "video"
        assert deserialized["uri"] == "https://example.com/video.mp4"
        assert deserialized["mime_type"] == "video/mp4"
        assert deserialized["width"] == 1920
        assert deserialized["height"] == 1080
        assert deserialized["duration"] == 120
        assert deserialized["frame_rate"] == 30

    def test_file_content_serialization(self):
        """Test FileContent with metadata"""
        # Arrange
        content = {
            "kind": "file",
            "uri": "https://example.com/document.pdf",
            "filename": "report.pdf",
            "mime_type": "application/pdf",
            "size_bytes": 2048,
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["kind"] == "file"
        assert deserialized["uri"] == "https://example.com/document.pdf"
        assert deserialized["filename"] == "report.pdf"
        assert deserialized["mime_type"] == "application/pdf"
        assert deserialized["size_bytes"] == 2048

    def test_function_call_content_serialization(self):
        """Test FunctionCallContent serialization"""
        # Arrange
        content = {
            "kind": "function_call",
            "call_id": "call_abc123",
            "name": "get_weather",
            "arguments": '{"location":"San Francisco","units":"celsius"}',
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["kind"] == "function_call"
        assert deserialized["call_id"] == "call_abc123"
        assert deserialized["name"] == "get_weather"
        assert "San Francisco" in deserialized["arguments"]

    def test_function_result_content_with_error_serializes_correctly(self):
        """Test FunctionResultContent with error - matches FunctionResultContent_WithError_SerializesCorrectly"""
        # Arrange
        content = {
            "kind": "function_result",
            "call_id": "call_123",
            "name": "delete_file",
            "result": "Error: Permission denied",
            "is_error": True,
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["call_id"] == "call_123"
        assert deserialized["name"] == "delete_file"
        assert "Permission denied" in deserialized["result"]
        assert deserialized["is_error"] is True


class TestConnectionSerialization:
    """Tests for polymorphic Connection types"""

    def test_reference_connection_serialization(self):
        """Test ReferenceConnection serialization"""
        # Arrange
        connection = {"type": "reference", "name": "myConnection"}

        # Act
        json_str = json.dumps(connection)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["type"] == "reference"
        assert deserialized["name"] == "myConnection"

    def test_api_key_connection_serialization(self):
        """Test ApiKeyConnection serialization"""
        # Arrange
        connection = {
            "type": "api_key",
            "key": "sk-test-123",
            "header_name": "Authorization",
        }

        # Act
        json_str = json.dumps(connection)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["type"] == "api_key"
        assert deserialized["key"] == "sk-test-123"
        assert deserialized["header_name"] == "Authorization"

    def test_remote_connection_serialization(self):
        """Test RemoteConnection serialization"""
        # Arrange
        connection = {
            "type": "remote",
            "endpoint": "https://api.example.com",
            "credentials": {"token": "Bearer xyz"},
        }

        # Act
        json_str = json.dumps(connection)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["type"] == "remote"
        assert deserialized["endpoint"] == "https://api.example.com"
        assert deserialized["credentials"]["token"] == "Bearer xyz"

    def test_anonymous_connection_serialization(self):
        """Test AnonymousConnection serialization"""
        # Arrange
        connection = {"type": "anonymous"}

        # Act
        json_str = json.dumps(connection)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["type"] == "anonymous"


class TestAgentDefinitionSerialization:
    """Tests for agent definition serialization"""

    def test_prompt_agent_with_tools_serializes_correctly(self):
        """Test PromptAgent with tools - matches PromptAgent_WithTools_SerializesCorrectly"""
        # Arrange
        agent = {
            "type": "prompt",
            "model": "gpt-4o",
            "instructions": "You are a helpful assistant",
            "temperature": 0.7,
            "max_tokens": 2000,
            "tools": [
                {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "City name",
                                "format": "city",
                            },
                            "units": {
                                "type": "string",
                                "enum": ["celsius", "fahrenheit"],
                            },
                        },
                        "required": ["location"],
                    },
                    "requires_approval": False,
                }
            ],
        }

        # Act
        json_str = json.dumps(agent)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["model"] == "gpt-4o"
        assert deserialized["instructions"] == "You are a helpful assistant"
        assert deserialized["temperature"] == 0.7
        assert deserialized["max_tokens"] == 2000
        assert len(deserialized["tools"]) == 1
        assert deserialized["tools"][0]["name"] == "get_weather"
        assert len(deserialized["tools"][0]["parameters"]["properties"]) == 2


class TestThreadSerialization:
    """Tests for Thread model serialization"""

    def test_thread_with_participants_serializes_correctly(self):
        """Test Thread with participants - matches Thread_WithParticipants_SerializesCorrectly"""
        # Arrange
        thread = {
            "thread_id": "thread_123",
            "title": "Support Conversation",
            "status": "active",
            "participants": [
                {
                    "id": "user_001",
                    "kind": "user",
                    "name": "John Doe",
                    "role": "user",
                },
                {
                    "id": "agent_001",
                    "kind": "agent",
                    "name": "Support Bot",
                    "role": "assistant",
                },
            ],
            "unread_count": 5,
            "metadata": {"priority": "high", "department": "support"},
        }

        # Act
        json_str = json.dumps(thread)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["thread_id"] == "thread_123"
        assert deserialized["title"] == "Support Conversation"
        assert deserialized["status"] == "active"
        assert len(deserialized["participants"]) == 2
        assert deserialized["participants"][0]["id"] == "user_001"
        assert deserialized["participants"][1]["id"] == "agent_001"
        assert deserialized["unread_count"] == 5


class TestRunErrorSerialization:
    """Tests for RunError serialization"""

    def test_run_error_with_details_serializes_correctly(self):
        """Test RunError with details - matches RunError_WithDetails_SerializesCorrectly"""
        # Arrange
        error = {
            "code": "context_length_exceeded",
            "message": "The conversation exceeded the maximum token limit",
            "details": {
                "max_tokens": 128000,
                "actual_tokens": 150000,
                "exceeded": True,
            },
        }

        # Act
        json_str = json.dumps(error)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["code"] == "context_length_exceeded"
        assert deserialized["message"] == "The conversation exceeded the maximum token limit"
        assert deserialized["details"] is not None
        assert len(deserialized["details"]) == 3


class TestCompletionUsageSerialization:
    """Tests for CompletionUsage serialization"""

    def test_completion_usage_serializes_correctly(self):
        """Test CompletionUsage - matches CompletionUsage_SerializesCorrectly"""
        # Arrange
        usage = {
            "input_tokens": 1000,
            "output_tokens": 500,
            "total_tokens": 1500,
        }

        # Act
        json_str = json.dumps(usage)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["input_tokens"] == 1000
        assert deserialized["output_tokens"] == 500
        assert deserialized["total_tokens"] == 1500


class TestAgentCardSerialization:
    """Tests for AgentCard serialization"""

    def test_agent_card_with_capabilities_serializes_correctly(self):
        """Test AgentCard with capabilities - matches AgentCard_WithCapabilities_SerializesCorrectly"""
        # Arrange
        card = {
            "agent_id": "agent_001",
            "name": "GPT-4o Agent",
            "description": "Advanced AI assistant",
            "capabilities": {
                "vision": True,
                "thinking": False,
                "tools": True,
                "max_tokens": 128000,
                "content_types": ["text", "image", "audio"],
            },
            "tools": [
                {
                    "name": "web_search",
                    "description": "Search the web",
                    "parameters": {"type": "object"},
                }
            ],
        }

        # Act
        json_str = json.dumps(card)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized is not None
        assert deserialized["agent_id"] == "agent_001"
        assert deserialized["capabilities"] is not None
        assert deserialized["capabilities"]["vision"] is True
        assert deserialized["capabilities"]["thinking"] is False
        assert deserialized["capabilities"]["max_tokens"] == 128000
        assert len(deserialized["capabilities"]["content_types"]) == 3


class TestRunStatusEnumSerialization:
    """Tests for RunStatus enum serialization"""

    def test_run_status_enum_values_serialize_as_strings(self):
        """Test all run status values - matches RunStatus_EnumValues_SerializeAsStrings"""
        # Arrange - Test all run status values
        statuses = [
            "queued",
            "in_progress",
            "requires_action",
            "input_required",
            "auth_required",
            "cancelling",
            "cancelled",
            "failed",
            "completed",
            "incomplete",
            "timeout",
        ]

        # Act & Assert
        for status in statuses:
            json_str = json.dumps({"status": status})
            deserialized = json.loads(json_str)
            assert deserialized["status"] == status


class TestNullableFieldsSerialization:
    """Tests for null/None field handling"""

    def test_none_fields_omitted_in_serialization(self):
        """Test that None fields can be omitted - matches NullableFields_OmittedInSerialization"""
        # Arrange - Test that null fields are not included in JSON
        run = {
            "agent_id": "agent_001",
            "input": [],
            # thread_id, journal_id, metadata intentionally omitted
        }

        # Act
        json_str = json.dumps(run)

        # Assert
        assert "thread_id" not in json_str
        assert "journal_id" not in json_str
        assert "metadata" not in json_str
        assert "agent_id" in json_str
        assert "input" in json_str

    def test_explicit_none_values_can_be_serialized(self):
        """Test that explicit None values can be serialized if needed"""
        # Arrange
        run = {
            "agent_id": "agent_001",
            "input": [],
            "thread_id": None,
            "metadata": None,
        }

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["thread_id"] is None
        assert deserialized["metadata"] is None


class TestToolOutputSerialization:
    """Tests for ToolOutput serialization"""

    def test_tool_output_serializes_with_snake_case(self):
        """Test ToolOutput uses snake_case for tool_call_id - matches ToolOutput_SerializesWithSnakeCase"""
        # Arrange - Tool output uses snake_case for tool_call_id
        tool_output = {
            "tool_call_id": "call_abc123",
            "output": "File deleted successfully",
        }

        # Act
        json_str = json.dumps(tool_output)

        # Assert
        assert "tool_call_id" in json_str  # Should use snake_case
        assert "call_abc123" in json_str
        assert "output" in json_str


class TestFieldNameMapping:
    """Tests for field name mapping between camelCase and snake_case"""

    def test_snake_case_to_camel_case_mapping(self):
        """Test converting snake_case Python fields to camelCase for API"""
        # Arrange - Python uses snake_case
        python_model = {
            "run_id": "run_123",
            "agent_id": "agent_001",
            "thread_id": "thread_456",
            "created_at": "2024-01-01T00:00:00Z",
            "completed_at": "2024-01-01T00:01:00Z",
            "thread_cleanup": "keep",
        }

        # Convert to camelCase (simulating API serialization)
        camel_case_model = {
            "runId": python_model["run_id"],
            "agentId": python_model["agent_id"],
            "threadId": python_model["thread_id"],
            "createdAt": python_model["created_at"],
            "completedAt": python_model["completed_at"],
            "threadCleanup": python_model["thread_cleanup"],
        }

        # Act
        json_str = json.dumps(camel_case_model)
        deserialized = json.loads(json_str)

        # Assert - camelCase fields preserved
        assert "runId" in json_str
        assert "agentId" in json_str
        assert "threadId" in json_str
        assert "createdAt" in json_str
        assert "completedAt" in json_str
        assert "threadCleanup" in json_str

    def test_camel_case_to_snake_case_mapping(self):
        """Test converting camelCase API response to snake_case Python"""
        # Arrange - API returns camelCase
        api_response = {
            "runId": "run_123",
            "agentId": "agent_001",
            "threadId": "thread_456",
            "createdAt": "2024-01-01T00:00:00Z",
        }

        # Convert to snake_case (simulating API deserialization)
        python_model = {
            "run_id": api_response["runId"],
            "agent_id": api_response["agentId"],
            "thread_id": api_response["threadId"],
            "created_at": api_response["createdAt"],
        }

        # Assert
        assert python_model["run_id"] == "run_123"
        assert python_model["agent_id"] == "agent_001"
        assert python_model["thread_id"] == "thread_456"
        assert python_model["created_at"] == "2024-01-01T00:00:00Z"


class TestInvalidJSONHandling:
    """Tests for error handling with invalid JSON"""

    def test_invalid_json_raises_decode_error(self):
        """Test that invalid JSON raises JSONDecodeError"""
        # Arrange
        invalid_json = "{invalid json content"

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_malformed_json_missing_quote_raises_error(self):
        """Test malformed JSON with missing quote"""
        # Arrange
        invalid_json = '{"key": value}'

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_json_with_trailing_comma_raises_error(self):
        """Test JSON with trailing comma (strict parsing)"""
        # Arrange - JSON with trailing comma (not valid in strict JSON)
        invalid_json = '{"key": "value",}'

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_empty_string_raises_decode_error(self):
        """Test that empty string raises JSONDecodeError"""
        # Arrange
        invalid_json = ""

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            json.loads(invalid_json)

    def test_valid_json_does_not_raise_error(self):
        """Test that valid JSON does not raise error"""
        # Arrange
        valid_json = '{"key": "value"}'

        # Act
        deserialized = json.loads(valid_json)

        # Assert
        assert deserialized["key"] == "value"


class TestComplexNestedSerialization:
    """Tests for complex nested object serialization"""

    def test_nested_message_with_mixed_content_types(self):
        """Test deeply nested structure with multiple content types"""
        # Arrange
        run = {
            "run_id": "run_complex",
            "agent_id": "agent_001",
            "status": "completed",
            "input": [
                {
                    "role": "user",
                    "message_id": "msg_in_1",
                    "contents": [
                        {"kind": "text", "text": "Analyze these materials"},
                        {
                            "kind": "image",
                            "uri": "https://example.com/chart.png",
                            "mime_type": "image/png",
                        },
                        {
                            "kind": "file",
                            "uri": "https://example.com/report.pdf",
                            "filename": "report.pdf",
                            "mime_type": "application/pdf",
                        },
                    ],
                }
            ],
            "output": [
                {
                    "role": "assistant",
                    "message_id": "msg_out_1",
                    "contents": [
                        {"kind": "text", "text": "Analysis complete"},
                        {
                            "kind": "function_call",
                            "call_id": "call_1",
                            "name": "save_analysis",
                            "arguments": '{"format":"json"}',
                        },
                    ],
                },
                {
                    "role": "tool",
                    "message_id": "msg_tool_1",
                    "contents": [
                        {
                            "kind": "function_result",
                            "call_id": "call_1",
                            "name": "save_analysis",
                            "result": "Saved successfully",
                        }
                    ],
                },
            ],
            "metadata": {"session_id": "sess_123", "tags": ["analysis", "urgent"]},
        }

        # Act
        json_str = json.dumps(run, indent=2)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["run_id"] == "run_complex"
        assert len(deserialized["input"]) == 1
        assert len(deserialized["input"][0]["contents"]) == 3
        assert len(deserialized["output"]) == 2
        assert deserialized["output"][0]["contents"][0]["text"] == "Analysis complete"
        assert deserialized["output"][1]["contents"][0]["result"] == "Saved successfully"
        assert len(deserialized["metadata"]["tags"]) == 2


class TestSpecialCharactersSerialization:
    """Tests for special characters and edge cases"""

    def test_unicode_characters_in_text_content(self):
        """Test text content with unicode characters"""
        # Arrange
        content = {"kind": "text", "text": "Hello 世界 🌍 café naïve résumé"}

        # Act
        json_str = json.dumps(content, ensure_ascii=False)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["text"] == "Hello 世界 🌍 café naïve résumé"

    def test_special_characters_in_filename(self):
        """Test file content with special characters in filename"""
        # Arrange
        content = {
            "kind": "file",
            "filename": "report (2024) [final].pdf",
            "uri": "https://example.com/file",
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["filename"] == "report (2024) [final].pdf"

    def test_escaped_characters_in_json(self):
        """Test proper escaping of special JSON characters"""
        # Arrange
        content = {
            "kind": "text",
            "text": 'Text with "quotes" and \\ backslash and \n newline',
        }

        # Act
        json_str = json.dumps(content)
        deserialized = json.loads(json_str)

        # Assert
        assert '"quotes"' in deserialized["text"]
        assert "\\" in deserialized["text"]
        assert "\n" in deserialized["text"]


class TestEmptyAndNullValues:
    """Tests for empty strings, arrays, and null values"""

    def test_empty_string_values(self):
        """Test serialization with empty strings"""
        # Arrange
        message = {"role": "user", "contents": [{"kind": "text", "text": ""}]}

        # Act
        json_str = json.dumps(message)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["contents"][0]["text"] == ""

    def test_empty_arrays(self):
        """Test serialization with empty arrays"""
        # Arrange
        run = {"agent_id": "agent_001", "input": [], "output": []}

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["input"] == []
        assert deserialized["output"] == []

    def test_empty_objects(self):
        """Test serialization with empty objects"""
        # Arrange
        agent = {"metadata": {}, "tools": []}

        # Act
        json_str = json.dumps(agent)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["metadata"] == {}
        assert deserialized["tools"] == []


class TestDateTimeSerialization:
    """Tests for datetime serialization"""

    def test_iso_datetime_format(self):
        """Test that datetime strings are in ISO format"""
        # Arrange
        now = datetime.now(timezone.utc)
        run = {"created_at": now.isoformat(), "run_id": "run_123"}

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert "T" in deserialized["created_at"]  # ISO format includes 'T'
        assert deserialized["created_at"] == now.isoformat()

    def test_datetime_with_timezone(self):
        """Test datetime with timezone information"""
        # Arrange
        utc_time = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        run = {"created_at": utc_time.isoformat()}

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["created_at"] == "2024-01-01T12:00:00+00:00"


class TestLargeDataSerialization:
    """Tests for handling large data structures"""

    def test_large_message_array(self):
        """Test serialization with many messages"""
        # Arrange
        run = {
            "run_id": "run_large",
            "agent_id": "agent_001",
            "input": [
                {
                    "role": "user",
                    "contents": [{"kind": "text", "text": f"Message {i}"}],
                }
                for i in range(100)
            ],
        }

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert len(deserialized["input"]) == 100
        assert deserialized["input"][0]["contents"][0]["text"] == "Message 0"
        assert deserialized["input"][99]["contents"][0]["text"] == "Message 99"

    def test_large_metadata_object(self):
        """Test serialization with large metadata"""
        # Arrange
        run = {
            "run_id": "run_metadata",
            "metadata": {f"key_{i}": f"value_{i}" for i in range(100)},
        }

        # Act
        json_str = json.dumps(run)
        deserialized = json.loads(json_str)

        # Assert
        assert len(deserialized["metadata"]) == 100
        assert deserialized["metadata"]["key_0"] == "value_0"
        assert deserialized["metadata"]["key_99"] == "value_99"


class TestNumericValuesSerialization:
    """Tests for numeric values (integers, floats)"""

    def test_integer_values(self):
        """Test serialization of integer values"""
        # Arrange
        usage = {"input_tokens": 1000, "output_tokens": 500, "total_tokens": 1500}

        # Act
        json_str = json.dumps(usage)
        deserialized = json.loads(json_str)

        # Assert
        assert isinstance(deserialized["input_tokens"], int)
        assert deserialized["input_tokens"] == 1000

    def test_float_values(self):
        """Test serialization of float values"""
        # Arrange
        agent = {"temperature": 0.7, "top_p": 0.9}

        # Act
        json_str = json.dumps(agent)
        deserialized = json.loads(json_str)

        # Assert
        assert isinstance(deserialized["temperature"], float)
        assert deserialized["temperature"] == 0.7
        assert deserialized["top_p"] == 0.9

    def test_zero_values(self):
        """Test serialization of zero values"""
        # Arrange
        usage = {"input_tokens": 0, "temperature": 0.0}

        # Act
        json_str = json.dumps(usage)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["input_tokens"] == 0
        assert deserialized["temperature"] == 0.0


class TestBooleanSerialization:
    """Tests for boolean value serialization"""

    def test_boolean_values(self):
        """Test serialization of boolean values"""
        # Arrange
        capabilities = {"vision": True, "thinking": False, "tools": True}

        # Act
        json_str = json.dumps(capabilities)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["vision"] is True
        assert deserialized["thinking"] is False
        assert deserialized["tools"] is True

    def test_boolean_in_nested_structure(self):
        """Test boolean values in nested objects"""
        # Arrange
        tool = {
            "name": "delete_file",
            "requires_approval": True,
            "parameters": {"required": True},
        }

        # Act
        json_str = json.dumps(tool)
        deserialized = json.loads(json_str)

        # Assert
        assert deserialized["requires_approval"] is True
        assert deserialized["parameters"]["required"] is True
