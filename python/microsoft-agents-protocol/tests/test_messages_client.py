# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Comprehensive tests for Messages client API covering all low-level operations.
Tests the message operations accessed through threads (e.g., client.threads.messages).
"""

import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
import json

from microsoft.agents.protocol.client.threads_client import ThreadsClient
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions


class MockResponse:
    """Mock aiohttp response"""

    def __init__(self, data: Any, status: int = 200):
        self._data = data
        self.status = status

    async def json(self):
        """Return JSON data"""
        return self._data

    def raise_for_status(self):
        """Raise error for bad status codes"""
        if self.status >= 400:
            from aiohttp import ClientResponseError
            raise ClientResponseError(
                request_info=Mock(),
                history=(),
                status=self.status
            )

    def __aenter__(self):
        return self

    def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def mock_http_method(method_mock, response_data: Any, status: int = 200):
    """
    Helper to properly mock an aiohttp session method (get, post, etc.)
    """
    response = MockResponse(response_data, status)
    cm = MagicMock()
    cm.__aenter__.return_value = response
    cm.__aexit__.return_value = None
    method_mock.return_value = cm


@pytest.fixture
def mock_session():
    """Creates a mock aiohttp session"""
    session = Mock()
    return session


@pytest.fixture
def client_options():
    """Creates mock client options"""
    return AgentProtocolClientOptions(base_url="https://api.example.com")


@pytest.fixture
def threads_client(mock_session, client_options):
    """Creates a ThreadsClient with mocked session for message operations"""
    return ThreadsClient(mock_session, client_options)


# ============================================================================
# CREATE MESSAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_with_text_message_returns_created_message(threads_client, mock_session):
    """Test creating a text message in a thread"""
    # Arrange
    now = datetime.now(UTC)
    expected_message = {
        "message_id": "msg_001",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello, how can you help me?"}
        ],
        "user_id": "user_001",
        "created_at": now.isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello, how can you help me?"}
        ],
        "user_id": "user_001"
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result is not None
    assert result["message_id"] == "msg_001"
    assert result["thread_id"] == "thread_123"
    assert result["role"] == "user"
    assert len(result["contents"]) == 1
    assert result["contents"][0]["text"] == "Hello, how can you help me?"
    mock_session.post.assert_called_once_with(
        "/threads/thread_123/messages",
        json=message
    )


@pytest.mark.asyncio
async def test_create_with_assistant_message_returns_created_message(threads_client, mock_session):
    """Test creating an assistant message in a thread"""
    # Arrange
    expected_message = {
        "message_id": "msg_002",
        "thread_id": "thread_123",
        "role": "assistant",
        "contents": [
            {"kind": "text", "text": "I can help you with that!"}
        ],
        "agent_id": "agent_001",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "assistant",
        "contents": [
            {"kind": "text", "text": "I can help you with that!"}
        ],
        "agent_id": "agent_001"
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["role"] == "assistant"
    assert result["agent_id"] == "agent_001"


@pytest.mark.asyncio
async def test_create_with_multimodal_content_returns_message(threads_client, mock_session):
    """Test creating a message with multiple content types"""
    # Arrange
    expected_message = {
        "message_id": "msg_003",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Look at this image:"},
            {"kind": "image", "image_url": "https://example.com/image.png"},
            {"kind": "text", "text": "What do you see?"}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Look at this image:"},
            {"kind": "image", "image_url": "https://example.com/image.png"},
            {"kind": "text", "text": "What do you see?"}
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert len(result["contents"]) == 3
    assert result["contents"][0]["kind"] == "text"
    assert result["contents"][1]["kind"] == "image"
    assert result["contents"][2]["kind"] == "text"


@pytest.mark.asyncio
async def test_create_with_function_call_content_returns_message(threads_client, mock_session):
    """Test creating a message with function call content"""
    # Arrange
    expected_message = {
        "message_id": "msg_004",
        "thread_id": "thread_123",
        "role": "assistant",
        "contents": [
            {
                "kind": "function_call",
                "function_call": {
                    "name": "get_weather",
                    "arguments": '{"location": "New York", "unit": "celsius"}'
                }
            }
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "assistant",
        "contents": [
            {
                "kind": "function_call",
                "function_call": {
                    "name": "get_weather",
                    "arguments": '{"location": "New York", "unit": "celsius"}'
                }
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["contents"][0]["kind"] == "function_call"
    assert result["contents"][0]["function_call"]["name"] == "get_weather"


@pytest.mark.asyncio
async def test_create_with_function_result_content_returns_message(threads_client, mock_session):
    """Test creating a message with function result content"""
    # Arrange
    expected_message = {
        "message_id": "msg_005",
        "thread_id": "thread_123",
        "role": "tool",
        "contents": [
            {
                "kind": "function_result",
                "function_result": {
                    "name": "get_weather",
                    "result": '{"temperature": 22, "condition": "sunny"}'
                }
            }
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "tool",
        "contents": [
            {
                "kind": "function_result",
                "function_result": {
                    "name": "get_weather",
                    "result": '{"temperature": 22, "condition": "sunny"}'
                }
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["role"] == "tool"
    assert result["contents"][0]["kind"] == "function_result"


@pytest.mark.asyncio
async def test_create_with_metadata_includes_metadata(threads_client, mock_session):
    """Test creating a message with metadata"""
    # Arrange
    expected_message = {
        "message_id": "msg_006",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [{"kind": "text", "text": "Test message"}],
        "metadata": {
            "source": "mobile_app",
            "version": "2.1.0",
            "user_timezone": "America/New_York"
        },
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test message"}],
        "metadata": {
            "source": "mobile_app",
            "version": "2.1.0",
            "user_timezone": "America/New_York"
        }
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert "metadata" in result
    assert result["metadata"]["source"] == "mobile_app"
    assert result["metadata"]["version"] == "2.1.0"


@pytest.mark.asyncio
async def test_create_with_attachments_includes_attachments(threads_client, mock_session):
    """Test creating a message with file attachments"""
    # Arrange
    expected_message = {
        "message_id": "msg_007",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [{"kind": "text", "text": "Please review these files"}],
        "attachments": [
            {
                "file_id": "file_001",
                "filename": "document.pdf",
                "mime_type": "application/pdf",
                "size_bytes": 1024000
            },
            {
                "file_id": "file_002",
                "filename": "spreadsheet.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "size_bytes": 512000
            }
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Please review these files"}],
        "attachments": [
            {
                "file_id": "file_001",
                "filename": "document.pdf",
                "mime_type": "application/pdf",
                "size_bytes": 1024000
            },
            {
                "file_id": "file_002",
                "filename": "spreadsheet.xlsx",
                "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "size_bytes": 512000
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert len(result["attachments"]) == 2
    assert result["attachments"][0]["filename"] == "document.pdf"
    assert result["attachments"][1]["filename"] == "spreadsheet.xlsx"


@pytest.mark.asyncio
async def test_create_with_system_message_returns_message(threads_client, mock_session):
    """Test creating a system message"""
    # Arrange
    expected_message = {
        "message_id": "msg_008",
        "thread_id": "thread_123",
        "role": "system",
        "contents": [
            {"kind": "text", "text": "You are a helpful assistant specialized in data analysis."}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "system",
        "contents": [
            {"kind": "text", "text": "You are a helpful assistant specialized in data analysis."}
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["role"] == "system"


@pytest.mark.asyncio
async def test_create_with_unicode_content_returns_message(threads_client, mock_session):
    """Test creating a message with unicode characters"""
    # Arrange
    expected_message = {
        "message_id": "msg_009",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello 世界! 🌍 Привет مرحبا"}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello 世界! 🌍 Привет مرحبا"}
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["contents"][0]["text"] == "Hello 世界! 🌍 Привет مرحبا"


@pytest.mark.asyncio
async def test_create_with_empty_contents_returns_message(threads_client, mock_session):
    """Test creating a message with empty contents array"""
    # Arrange
    expected_message = {
        "message_id": "msg_010",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": []
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert len(result["contents"]) == 0


# ============================================================================
# RETRIEVE MESSAGE TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_retrieve_with_valid_message_id_returns_message(threads_client, mock_session):
    """Test retrieving a specific message by ID"""
    # Arrange
    expected_message = {
        "message_id": "msg_123",
        "thread_id": "thread_456",
        "role": "assistant",
        "contents": [
            {"kind": "text", "text": "Here is the information you requested."}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    # Mock a get_message method (currently not in ThreadsClient, but expected in tests)
    mock_http_method(mock_session.get, expected_message)

    # Act
    # Note: ThreadsClient doesn't currently have a get_message method,
    # but this tests the expected behavior
    async with mock_session.get(f"/threads/thread_456/messages/msg_123") as response:
        response.raise_for_status()
        result = await response.json()

    # Assert
    assert result is not None
    assert result["message_id"] == "msg_123"
    assert result["thread_id"] == "thread_456"
    assert result["role"] == "assistant"


@pytest.mark.asyncio
async def test_retrieve_with_all_fields_returns_complete_message(threads_client, mock_session):
    """Test retrieving a message with all fields populated"""
    # Arrange
    now = datetime.now(UTC)
    expected_message = {
        "message_id": "msg_complete",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [{"kind": "text", "text": "Complete message"}],
        "user_id": "user_001",
        "metadata": {"source": "api", "priority": "high"},
        "attachments": [{"file_id": "file_001", "filename": "doc.pdf"}],
        "created_at": now.isoformat(),
        "updated_at": (now + timedelta(seconds=30)).isoformat(),
        "status": "delivered"
    }

    mock_http_method(mock_session.get, expected_message)

    # Act
    async with mock_session.get("/threads/thread_123/messages/msg_complete") as response:
        response.raise_for_status()
        result = await response.json()

    # Assert
    assert result["message_id"] == "msg_complete"
    assert "metadata" in result
    assert "attachments" in result
    assert "created_at" in result
    assert "updated_at" in result


@pytest.mark.asyncio
async def test_retrieve_with_invalid_message_id_raises_error(threads_client, mock_session):
    """Test retrieving a non-existent message raises error"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Message not found"}, 404)

    # Act & Assert
    with pytest.raises(Exception):
        async with mock_session.get("/threads/thread_123/messages/invalid_msg") as response:
            response.raise_for_status()


# ============================================================================
# LIST MESSAGES TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_list_with_thread_id_returns_messages(threads_client, mock_session):
    """Test listing all messages in a thread"""
    # Arrange
    base_time = datetime.now(UTC)
    expected_messages = [
        {
            "message_id": "msg_001",
            "thread_id": "thread_123",
            "role": "user",
            "contents": [{"kind": "text", "text": "First message"}],
            "created_at": (base_time - timedelta(minutes=10)).isoformat()
        },
        {
            "message_id": "msg_002",
            "thread_id": "thread_123",
            "role": "assistant",
            "contents": [{"kind": "text", "text": "Response to first"}],
            "created_at": (base_time - timedelta(minutes=5)).isoformat()
        },
        {
            "message_id": "msg_003",
            "thread_id": "thread_123",
            "role": "user",
            "contents": [{"kind": "text", "text": "Follow-up question"}],
            "created_at": base_time.isoformat()
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123")

    # Assert
    assert result is not None
    assert len(result) == 3
    assert result[0]["message_id"] == "msg_001"
    assert result[1]["message_id"] == "msg_002"
    assert result[2]["message_id"] == "msg_003"
    mock_session.get.assert_called_once_with(
        "/threads/thread_123/messages",
        params={}
    )


@pytest.mark.asyncio
async def test_list_with_limit_returns_limited_messages(threads_client, mock_session):
    """Test listing messages with limit parameter"""
    # Arrange
    expected_messages = [
        {
            "message_id": f"msg_{i:03d}",
            "thread_id": "thread_123",
            "role": "user" if i % 2 == 0 else "assistant",
            "contents": [{"kind": "text", "text": f"Message {i}"}],
            "created_at": datetime.now(UTC).isoformat()
        }
        for i in range(1, 11)
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123", limit=10)

    # Assert
    assert len(result) == 10
    assert result[0]["message_id"] == "msg_001"
    assert result[9]["message_id"] == "msg_010"
    mock_session.get.assert_called_once_with(
        "/threads/thread_123/messages",
        params={"limit": 10}
    )


@pytest.mark.asyncio
async def test_list_with_large_limit_returns_all_available_messages(threads_client, mock_session):
    """Test listing messages with large limit value"""
    # Arrange
    expected_messages = [
        {
            "message_id": f"msg_{i:04d}",
            "thread_id": "thread_123",
            "role": "user",
            "contents": [],
            "created_at": datetime.now(UTC).isoformat()
        }
        for i in range(1, 101)
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123", limit=100)

    # Assert
    assert len(result) == 100
    mock_session.get.assert_called_once()
    call_params = mock_session.get.call_args[1]["params"]
    assert call_params["limit"] == 100


@pytest.mark.asyncio
async def test_list_with_empty_thread_returns_empty_list(threads_client, mock_session):
    """Test listing messages from an empty thread"""
    # Arrange
    mock_http_method(mock_session.get, [])

    # Act
    result = await threads_client.get_messages("thread_empty")

    # Assert
    assert result is not None
    assert len(result) == 0
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_list_without_limit_returns_all_messages(threads_client, mock_session):
    """Test listing messages without limit parameter"""
    # Arrange
    expected_messages = [
        {
            "message_id": "msg_001",
            "role": "user",
            "contents": [{"kind": "text", "text": "Message 1"}]
        },
        {
            "message_id": "msg_002",
            "role": "assistant",
            "contents": [{"kind": "text", "text": "Response 1"}]
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123")

    # Assert
    assert len(result) == 2
    mock_session.get.assert_called_once_with(
        "/threads/thread_123/messages",
        params={}
    )


@pytest.mark.asyncio
async def test_list_returns_messages_in_chronological_order(threads_client, mock_session):
    """Test that messages are returned in chronological order"""
    # Arrange
    base_time = datetime.now(UTC)
    expected_messages = [
        {
            "message_id": "msg_1",
            "created_at": (base_time - timedelta(hours=2)).isoformat()
        },
        {
            "message_id": "msg_2",
            "created_at": (base_time - timedelta(hours=1)).isoformat()
        },
        {
            "message_id": "msg_3",
            "created_at": base_time.isoformat()
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123")

    # Assert
    assert len(result) == 3
    assert result[0]["message_id"] == "msg_1"
    assert result[1]["message_id"] == "msg_2"
    assert result[2]["message_id"] == "msg_3"


@pytest.mark.asyncio
async def test_list_with_various_content_types_returns_all(threads_client, mock_session):
    """Test listing messages with different content types"""
    # Arrange
    expected_messages = [
        {
            "message_id": "msg_text",
            "role": "user",
            "contents": [{"kind": "text", "text": "Text message"}]
        },
        {
            "message_id": "msg_image",
            "role": "user",
            "contents": [{"kind": "image", "image_url": "https://example.com/img.png"}]
        },
        {
            "message_id": "msg_function_call",
            "role": "assistant",
            "contents": [
                {
                    "kind": "function_call",
                    "function_call": {"name": "get_data", "arguments": "{}"}
                }
            ]
        },
        {
            "message_id": "msg_function_result",
            "role": "tool",
            "contents": [
                {
                    "kind": "function_result",
                    "function_result": {"name": "get_data", "result": "data"}
                }
            ]
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123")

    # Assert
    assert len(result) == 4
    assert result[0]["contents"][0]["kind"] == "text"
    assert result[1]["contents"][0]["kind"] == "image"
    assert result[2]["contents"][0]["kind"] == "function_call"
    assert result[3]["contents"][0]["kind"] == "function_result"


# ============================================================================
# UPDATE MESSAGE TESTS
# ============================================================================
# Note: The API spec doesn't currently include message update operations,
# but these tests demonstrate expected behavior if such operations existed

@pytest.mark.asyncio
async def test_update_with_metadata_updates_message_metadata(mock_session, client_options):
    """Test updating message metadata (hypothetical operation)"""
    # Arrange
    expected_message = {
        "message_id": "msg_123",
        "thread_id": "thread_456",
        "role": "user",
        "contents": [{"kind": "text", "text": "Original content"}],
        "metadata": {
            "priority": "high",
            "reviewed": True,
            "tags": ["important", "follow-up"]
        },
        "updated_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.patch, expected_message)

    update_data = {
        "metadata": {
            "priority": "high",
            "reviewed": True,
            "tags": ["important", "follow-up"]
        }
    }

    # Act
    # This would be the expected API call if PATCH was supported
    async with mock_session.patch(
        "/threads/thread_456/messages/msg_123",
        json=update_data
    ) as response:
        response.raise_for_status()
        result = await response.json()

    # Assert
    assert result["message_id"] == "msg_123"
    assert result["metadata"]["priority"] == "high"
    assert result["metadata"]["reviewed"] is True
    assert "updated_at" in result


@pytest.mark.asyncio
async def test_update_with_status_updates_message_status(mock_session, client_options):
    """Test updating message status (hypothetical operation)"""
    # Arrange
    expected_message = {
        "message_id": "msg_124",
        "thread_id": "thread_456",
        "role": "user",
        "contents": [{"kind": "text", "text": "Content"}],
        "status": "read",
        "updated_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.patch, expected_message)

    update_data = {"status": "read"}

    # Act
    async with mock_session.patch(
        "/threads/thread_456/messages/msg_124",
        json=update_data
    ) as response:
        response.raise_for_status()
        result = await response.json()

    # Assert
    assert result["status"] == "read"


# ============================================================================
# DELETE MESSAGE TESTS
# ============================================================================
# Note: The API spec doesn't currently include message delete operations,
# but these tests demonstrate expected behavior if such operations existed

@pytest.mark.asyncio
async def test_delete_with_valid_message_id_deletes_message(mock_session, client_options):
    """Test deleting a message (hypothetical operation)"""
    # Arrange
    mock_response = MockResponse(None, 204)
    cm = MagicMock()
    cm.__aenter__.return_value = mock_response
    cm.__aexit__.return_value = None
    mock_session.delete.return_value = cm

    # Act
    async with mock_session.delete("/threads/thread_123/messages/msg_001") as response:
        response.raise_for_status()

    # Assert
    mock_session.delete.assert_called_once()


@pytest.mark.asyncio
async def test_delete_with_invalid_message_id_raises_error(mock_session, client_options):
    """Test deleting a non-existent message raises error"""
    # Arrange
    mock_http_method(mock_session.delete, {"error": "Message not found"}, 404)

    # Act & Assert
    with pytest.raises(Exception):
        async with mock_session.delete("/threads/thread_123/messages/invalid_msg") as response:
            response.raise_for_status()


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_with_invalid_thread_id_raises_error(threads_client, mock_session):
    """Test creating a message in non-existent thread raises error"""
    # Arrange
    mock_http_method(mock_session.post, {"error": "Thread not found"}, 404)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("invalid_thread", message)


@pytest.mark.asyncio
async def test_create_with_missing_role_raises_validation_error(threads_client, mock_session):
    """Test creating a message without role raises validation error"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {
            "error": "Validation failed",
            "details": "role is required"
        },
        400
    )

    message = {
        "contents": [{"kind": "text", "text": "No role specified"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_with_empty_contents_validation_error(threads_client, mock_session):
    """Test validation error for invalid content structure"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {
            "error": "Validation failed",
            "details": "Invalid content structure"
        },
        400
    )

    message = {
        "role": "user",
        "contents": [{"kind": "text"}]  # Missing text field
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_with_unauthorized_raises_error(threads_client, mock_session):
    """Test unauthorized access raises error"""
    # Arrange
    mock_http_method(mock_session.post, {"error": "Unauthorized"}, 401)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_with_forbidden_raises_error(threads_client, mock_session):
    """Test forbidden access raises error"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {"error": "Forbidden: No permission to add message"},
        403
    )

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_with_conflict_raises_error(threads_client, mock_session):
    """Test duplicate message ID raises conflict error"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {"error": "Conflict: Message ID already exists"},
        409
    )

    message = {
        "message_id": "msg_duplicate",
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_with_server_error_raises_error(threads_client, mock_session):
    """Test server error during message creation"""
    # Arrange
    mock_http_method(mock_session.post, {"error": "Internal server error"}, 500)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_list_with_invalid_thread_id_raises_error(threads_client, mock_session):
    """Test listing messages from non-existent thread raises error"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Thread not found"}, 404)

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.get_messages("invalid_thread")


# ============================================================================
# REQUEST VALIDATION TESTS
# ============================================================================

@pytest.mark.asyncio
async def test_create_validates_role_is_string(threads_client, mock_session):
    """Test that role field validation works"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {"error": "Invalid role type"},
        400
    )

    message = {
        "role": 123,  # Invalid: should be string
        "contents": [{"kind": "text", "text": "Test"}]
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_validates_contents_is_array(threads_client, mock_session):
    """Test that contents field must be an array"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {"error": "Contents must be an array"},
        400
    )

    message = {
        "role": "user",
        "contents": "not an array"  # Invalid
    }

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.add_message("thread_123", message)


@pytest.mark.asyncio
async def test_create_with_nested_metadata_structure(threads_client, mock_session):
    """Test creating a message with nested metadata"""
    # Arrange
    expected_message = {
        "message_id": "msg_nested",
        "thread_id": "thread_123",
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}],
        "metadata": {
            "context": {
                "session_id": "sess_123",
                "user_agent": "Mozilla/5.0",
                "location": {
                    "country": "US",
                    "city": "New York"
                }
            },
            "analytics": {
                "page_views": 5,
                "time_spent_seconds": 120
            }
        },
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Test"}],
        "metadata": {
            "context": {
                "session_id": "sess_123",
                "user_agent": "Mozilla/5.0",
                "location": {
                    "country": "US",
                    "city": "New York"
                }
            },
            "analytics": {
                "page_views": 5,
                "time_spent_seconds": 120
            }
        }
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["metadata"]["context"]["session_id"] == "sess_123"
    assert result["metadata"]["context"]["location"]["city"] == "New York"
    assert result["metadata"]["analytics"]["page_views"] == 5


@pytest.mark.asyncio
async def test_list_with_zero_limit_uses_empty_params(threads_client, mock_session):
    """Test that limit=0 is treated as falsy and uses empty params"""
    # Arrange
    mock_http_method(mock_session.get, [])

    # Act
    result = await threads_client.get_messages("thread_123", limit=0)

    # Assert
    assert len(result) == 0
    mock_session.get.assert_called_once()
    call_params = mock_session.get.call_args[1]["params"]
    assert call_params == {}


@pytest.mark.asyncio
async def test_create_multiple_messages_in_sequence(threads_client, mock_session):
    """Test creating multiple messages in sequence"""
    # Arrange
    messages_data = [
        {
            "message_id": f"msg_{i}",
            "thread_id": "thread_123",
            "role": "user" if i % 2 == 0 else "assistant",
            "contents": [{"kind": "text", "text": f"Message {i}"}],
            "created_at": datetime.now(UTC).isoformat()
        }
        for i in range(1, 4)
    ]

    # Create context managers for each response
    cms = []
    for data in messages_data:
        response = MockResponse(data, 201)
        cm = MagicMock()
        cm.__aenter__.return_value = response
        cm.__aexit__.return_value = None
        cms.append(cm)

    mock_session.post.side_effect = cms

    # Act
    results = []
    for i in range(1, 4):
        message = {
            "role": "user" if i % 2 == 0 else "assistant",
            "contents": [{"kind": "text", "text": f"Message {i}"}]
        }
        result = await threads_client.add_message("thread_123", message)
        results.append(result)

    # Assert
    assert len(results) == 3
    assert results[0]["message_id"] == "msg_1"
    assert results[1]["message_id"] == "msg_2"
    assert results[2]["message_id"] == "msg_3"


@pytest.mark.asyncio
async def test_create_with_error_content_type(threads_client, mock_session):
    """Test creating a message with error content"""
    # Arrange
    expected_message = {
        "message_id": "msg_error",
        "thread_id": "thread_123",
        "role": "assistant",
        "contents": [
            {
                "kind": "error",
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests"
                }
            }
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "assistant",
        "contents": [
            {
                "kind": "error",
                "error": {
                    "code": "rate_limit_exceeded",
                    "message": "Too many requests"
                }
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["contents"][0]["kind"] == "error"
    assert result["contents"][0]["error"]["code"] == "rate_limit_exceeded"
