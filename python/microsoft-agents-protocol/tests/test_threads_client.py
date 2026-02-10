# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Comprehensive tests for ThreadsClient covering all low-level API operations.
Mirrors the .NET ThreadsClientTests.cs implementation.

Test Coverage:
- create() - Creating threads with various configurations (participants, metadata, status)
- get() - Retrieving threads by ID with all field types
- add_message() - Adding messages with different roles, content types, and metadata
- get_messages() - Listing messages with pagination support
- Error handling - HTTP errors (404, 401, 403, 400, 500)
- Request validation - Parameter handling and edge cases
- Data types - Text, images, function calls/results, attachments, unicode
- Special cases - Empty data, null values, zero limits, nested structures

All tests use mocked HTTP client to ensure deterministic, fast unit tests.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List
import json

from microsoft.agents.protocol.client import AgentProtocolClient
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions
from microsoft.agents.protocol.client.threads_client import ThreadsClient


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
    """Creates a ThreadsClient with mocked session"""
    return ThreadsClient(mock_session, client_options)


@pytest.mark.asyncio
async def test_create_with_participants_returns_created_thread(threads_client, mock_session):
    """Test creating a thread with participants"""
    # Arrange - Example from "Create a Thread" section
    expected_thread = {
        "thread_id": "thread_001",
        "title": "Customer Support Conversation",
        "participants": [
            {
                "id": "user_001",
                "kind": "user",
                "name": "John Doe"
            }
        ],
        "status": "Active",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "title": "Customer Support Conversation",
        "participants": [
            {
                "id": "user_001",
                "kind": "user",
                "name": "John Doe"
            }
        ]
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result is not None
    assert result["thread_id"] == "thread_001"
    assert result["title"] == "Customer Support Conversation"
    assert len(result["participants"]) == 1
    assert result["participants"][0]["id"] == "user_001"
    mock_session.post.assert_called_once_with("/threads", json=thread)


@pytest.mark.asyncio
async def test_create_with_no_data_returns_default_thread(threads_client, mock_session):
    """Test creating a thread with no initial data"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_002",
        "status": "Active",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    # Act
    result = await threads_client.create()

    # Assert
    assert result is not None
    assert result["thread_id"] == "thread_002"
    mock_session.post.assert_called_once_with("/threads", json={})


@pytest.mark.asyncio
async def test_get_with_valid_thread_id_returns_thread(threads_client, mock_session):
    """Test retrieving a thread by ID"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_123",
        "title": "Test Thread",
        "status": "Active",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.get, expected_thread)

    # Act
    result = await threads_client.get("thread_123")

    # Assert
    assert result is not None
    assert result["thread_id"] == "thread_123"
    assert result["status"] == "Active"
    mock_session.get.assert_called_once_with("/threads/thread_123")


@pytest.mark.asyncio
async def test_get_with_invalid_thread_id_raises_error(threads_client, mock_session):
    """Test retrieving a non-existent thread raises error"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Not found"}, 404)

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.get("invalid_thread")


@pytest.mark.asyncio
async def test_add_message_with_user_message_returns_created_message(threads_client, mock_session):
    """Test adding a message to a thread"""
    # Arrange - Example from "Add Messages to a Thread" section
    expected_message = {
        "message_id": "msg_001",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "I need help with my order"}
        ],
        "user_id": "user_001",
        "thread_id": "thread_123",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [
            {"kind": "text", "text": "I need help with my order"}
        ],
        "user_id": "user_001"
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result is not None
    assert result["message_id"] == "msg_001"
    assert result["role"] == "user"
    assert result["user_id"] == "user_001"
    assert len(result["contents"]) == 1
    mock_session.post.assert_called_once_with(
        "/threads/thread_123/messages",
        json=message
    )


@pytest.mark.asyncio
async def test_get_messages_with_thread_id_returns_messages(threads_client, mock_session):
    """Test getting messages from a thread"""
    # Arrange - Example from "Get Thread Messages" section
    now = datetime.now(UTC)
    expected_messages = [
        {
            "message_id": "msg_001",
            "role": "user",
            "contents": [
                {"kind": "text", "text": "Hello"}
            ],
            "created_at": (now - timedelta(minutes=5)).isoformat()
        },
        {
            "message_id": "msg_002",
            "role": "assistant",
            "contents": [
                {"kind": "text", "text": "Hi! How can I help?"}
            ],
            "created_at": now.isoformat()
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123", limit=100)

    # Assert
    assert result is not None
    assert len(result) == 2
    assert result[0]["message_id"] == "msg_001"
    assert result[1]["message_id"] == "msg_002"
    mock_session.get.assert_called_once_with(
        "/threads/thread_123/messages",
        params={"limit": 100}
    )


@pytest.mark.asyncio
async def test_get_messages_without_limit_returns_all_messages(threads_client, mock_session):
    """Test getting messages without limit parameter"""
    # Arrange
    expected_messages = [
        {
            "message_id": "msg_001",
            "role": "user",
            "contents": [{"kind": "text", "text": "Message 1"}]
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123")

    # Assert
    assert result is not None
    assert len(result) == 1
    mock_session.get.assert_called_once_with(
        "/threads/thread_123/messages",
        params={}
    )


@pytest.mark.asyncio
async def test_create_with_metadata_includes_metadata(threads_client, mock_session):
    """Test creating a thread with metadata"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_003",
        "title": "Project Discussion",
        "metadata": {
            "project_id": "proj_123",
            "department": "engineering",
            "priority": "high"
        },
        "status": "Active",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "title": "Project Discussion",
        "metadata": {
            "project_id": "proj_123",
            "department": "engineering",
            "priority": "high"
        }
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result is not None
    assert result["thread_id"] == "thread_003"
    assert "metadata" in result
    assert result["metadata"]["project_id"] == "proj_123"
    assert result["metadata"]["priority"] == "high"


@pytest.mark.asyncio
async def test_get_with_detailed_thread_returns_all_fields(threads_client, mock_session):
    """Test retrieving a thread with all fields populated"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_456",
        "title": "Detailed Thread",
        "status": "Active",
        "participants": [
            {"id": "user_001", "kind": "user", "name": "Alice"},
            {"id": "agent_001", "kind": "agent", "name": "Support Bot"}
        ],
        "metadata": {"category": "support"},
        "unread_count": 3,
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.get, expected_thread)

    # Act
    result = await threads_client.get("thread_456")

    # Assert
    assert result is not None
    assert result["thread_id"] == "thread_456"
    assert result["title"] == "Detailed Thread"
    assert len(result["participants"]) == 2
    assert result["unread_count"] == 3
    assert "metadata" in result


@pytest.mark.asyncio
async def test_add_message_with_multiple_contents_succeeds(threads_client, mock_session):
    """Test adding a message with multiple content items"""
    # Arrange
    expected_message = {
        "message_id": "msg_003",
        "role": "assistant",
        "contents": [
            {"kind": "text", "text": "Here is the information:"},
            {"kind": "image", "image_url": "https://example.com/image.png"}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "assistant",
        "contents": [
            {"kind": "text", "text": "Here is the information:"},
            {"kind": "image", "image_url": "https://example.com/image.png"}
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result is not None
    assert len(result["contents"]) == 2
    assert result["contents"][0]["kind"] == "text"
    assert result["contents"][1]["kind"] == "image"


@pytest.mark.asyncio
async def test_add_message_to_invalid_thread_raises_error(threads_client, mock_session):
    """Test adding a message to a non-existent thread raises error"""
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
async def test_get_messages_with_empty_thread_returns_empty_list(threads_client, mock_session):
    """Test getting messages from an empty thread"""
    # Arrange
    mock_http_method(mock_session.get, [])

    # Act
    result = await threads_client.get_messages("thread_empty")

    # Assert
    assert result is not None
    assert len(result) == 0
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_multiple_threads_succeeds(threads_client, mock_session):
    """Test creating multiple threads in sequence"""
    # Arrange
    threads_data = [
        {"thread_id": "thread_100", "title": "Thread 1"},
        {"thread_id": "thread_101", "title": "Thread 2"},
        {"thread_id": "thread_102", "title": "Thread 3"}
    ]

    # Create context managers for each response
    cms = []
    for data in threads_data:
        response = MockResponse(data, 201)
        cm = MagicMock()
        cm.__aenter__.return_value = response
        cm.__aexit__.return_value = None
        cms.append(cm)

    mock_session.post.side_effect = cms

    # Act
    results = []
    for i in range(3):
        result = await threads_client.create({"title": f"Thread {i+1}"})
        results.append(result)

    # Assert
    assert len(results) == 3
    assert results[0]["thread_id"] == "thread_100"
    assert results[1]["thread_id"] == "thread_101"
    assert results[2]["thread_id"] == "thread_102"


@pytest.mark.asyncio
async def test_create_with_complex_participant_structure(threads_client, mock_session):
    """Test creating a thread with complex participant data"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_200",
        "participants": [
            {
                "id": "user_001",
                "kind": "user",
                "name": "John Doe",
                "email": "john@example.com",
                "metadata": {"department": "sales"}
            },
            {
                "id": "agent_001",
                "kind": "agent",
                "name": "AI Assistant",
                "capabilities": ["chat", "search"]
            }
        ],
        "status": "Active"
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "participants": [
            {
                "id": "user_001",
                "kind": "user",
                "name": "John Doe",
                "email": "john@example.com",
                "metadata": {"department": "sales"}
            },
            {
                "id": "agent_001",
                "kind": "agent",
                "name": "AI Assistant",
                "capabilities": ["chat", "search"]
            }
        ]
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert len(result["participants"]) == 2
    assert result["participants"][0]["email"] == "john@example.com"
    assert result["participants"][1]["capabilities"] == ["chat", "search"]


@pytest.mark.asyncio
async def test_get_messages_pagination_with_limit(threads_client, mock_session):
    """Test getting messages with pagination limit"""
    # Arrange
    expected_messages = [
        {"message_id": f"msg_{i:03d}", "role": "user", "contents": []}
        for i in range(1, 11)
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123", limit=10)

    # Assert
    assert len(result) == 10
    assert result[0]["message_id"] == "msg_001"
    assert result[9]["message_id"] == "msg_010"
    mock_session.get.assert_called_once()
    call_params = mock_session.get.call_args[1]["params"]
    assert call_params["limit"] == 10


@pytest.mark.asyncio
async def test_add_message_with_agent_role(threads_client, mock_session):
    """Test adding an agent message to a thread"""
    # Arrange
    expected_message = {
        "message_id": "msg_agent_001",
        "role": "agent",
        "contents": [
            {"kind": "text", "text": "I've processed your request"}
        ],
        "agent_id": "agent_support",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "agent",
        "contents": [
            {"kind": "text", "text": "I've processed your request"}
        ],
        "agent_id": "agent_support"
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["role"] == "agent"
    assert result["agent_id"] == "agent_support"


@pytest.mark.asyncio
async def test_create_with_empty_participants_list(threads_client, mock_session):
    """Test creating a thread with empty participants list"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_empty_participants",
        "participants": [],
        "status": "Active"
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "participants": []
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result["thread_id"] == "thread_empty_participants"
    assert len(result["participants"]) == 0


@pytest.mark.asyncio
async def test_get_thread_with_archived_status(threads_client, mock_session):
    """Test retrieving an archived thread"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_archived",
        "title": "Old Conversation",
        "status": "Archived",
        "archived_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.get, expected_thread)

    # Act
    result = await threads_client.get("thread_archived")

    # Assert
    assert result["status"] == "Archived"
    assert "archived_at" in result


@pytest.mark.asyncio
async def test_add_message_with_function_call_content(threads_client, mock_session):
    """Test adding a message with function call content"""
    # Arrange
    expected_message = {
        "message_id": "msg_func_001",
        "role": "assistant",
        "contents": [
            {
                "kind": "function_call",
                "function_call": {
                    "name": "search_database",
                    "arguments": '{"query": "customer order"}'
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
                    "name": "search_database",
                    "arguments": '{"query": "customer order"}'
                }
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["contents"][0]["kind"] == "function_call"
    assert result["contents"][0]["function_call"]["name"] == "search_database"


@pytest.mark.asyncio
async def test_add_message_with_function_result_content(threads_client, mock_session):
    """Test adding a message with function result content"""
    # Arrange
    expected_message = {
        "message_id": "msg_func_result_001",
        "role": "function",
        "contents": [
            {
                "kind": "function_result",
                "function_result": {
                    "name": "search_database",
                    "result": '{"status": "found", "count": 5}'
                }
            }
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "function",
        "contents": [
            {
                "kind": "function_result",
                "function_result": {
                    "name": "search_database",
                    "result": '{"status": "found", "count": 5}'
                }
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["role"] == "function"
    assert result["contents"][0]["kind"] == "function_result"


@pytest.mark.asyncio
async def test_get_thread_with_unread_count(threads_client, mock_session):
    """Test retrieving a thread with unread count"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_unread",
        "title": "Active Chat",
        "unread_count": 5,
        "status": "Active"
    }

    mock_http_method(mock_session.get, expected_thread)

    # Act
    result = await threads_client.get("thread_unread")

    # Assert
    assert result["unread_count"] == 5


@pytest.mark.asyncio
async def test_get_messages_returns_messages_in_order(threads_client, mock_session):
    """Test that messages are returned in the correct order"""
    # Arrange
    base_time = datetime.now(UTC)
    expected_messages = [
        {
            "message_id": "msg_1",
            "created_at": (base_time - timedelta(minutes=10)).isoformat()
        },
        {
            "message_id": "msg_2",
            "created_at": (base_time - timedelta(minutes=5)).isoformat()
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
async def test_create_with_null_metadata_succeeds(threads_client, mock_session):
    """Test creating a thread with null metadata field"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_null_meta",
        "title": "Test Thread",
        "metadata": None,
        "status": "Active"
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "title": "Test Thread",
        "metadata": None
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result["thread_id"] == "thread_null_meta"
    assert result["metadata"] is None


@pytest.mark.asyncio
async def test_add_message_with_attachments(threads_client, mock_session):
    """Test adding a message with file attachments"""
    # Arrange
    expected_message = {
        "message_id": "msg_attach_001",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Please review this document"}
        ],
        "attachments": [
            {
                "file_id": "file_001",
                "filename": "report.pdf",
                "mime_type": "application/pdf"
            }
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Please review this document"}
        ],
        "attachments": [
            {
                "file_id": "file_001",
                "filename": "report.pdf",
                "mime_type": "application/pdf"
            }
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert len(result["attachments"]) == 1
    assert result["attachments"][0]["filename"] == "report.pdf"


@pytest.mark.asyncio
async def test_get_with_minimal_thread_data(threads_client, mock_session):
    """Test retrieving a thread with only required fields"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_minimal",
        "status": "Active"
    }

    mock_http_method(mock_session.get, expected_thread)

    # Act
    result = await threads_client.get("thread_minimal")

    # Assert
    assert result["thread_id"] == "thread_minimal"
    assert result["status"] == "Active"
    assert "title" not in result or result.get("title") is None


@pytest.mark.asyncio
async def test_add_message_validation_error(threads_client, mock_session):
    """Test adding an invalid message returns validation error"""
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
async def test_get_messages_with_various_content_types(threads_client, mock_session):
    """Test getting messages with different content types"""
    # Arrange
    expected_messages = [
        {
            "message_id": "msg_text",
            "contents": [{"kind": "text", "text": "Text content"}]
        },
        {
            "message_id": "msg_image",
            "contents": [{"kind": "image", "image_url": "https://example.com/img.png"}]
        },
        {
            "message_id": "msg_error",
            "contents": [{"kind": "error", "error": {"message": "Error occurred"}}]
        }
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123")

    # Assert
    assert len(result) == 3
    assert result[0]["contents"][0]["kind"] == "text"
    assert result[1]["contents"][0]["kind"] == "image"
    assert result[2]["contents"][0]["kind"] == "error"


@pytest.mark.asyncio
async def test_create_thread_with_custom_status(threads_client, mock_session):
    """Test creating a thread with custom initial status"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_custom",
        "status": "Pending",
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "status": "Pending"
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result["status"] == "Pending"


@pytest.mark.asyncio
async def test_add_message_with_metadata(threads_client, mock_session):
    """Test adding a message with metadata"""
    # Arrange
    expected_message = {
        "message_id": "msg_meta_001",
        "role": "user",
        "contents": [{"kind": "text", "text": "Message with metadata"}],
        "metadata": {
            "intent": "question",
            "confidence": 0.95,
            "language": "en"
        },
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [{"kind": "text", "text": "Message with metadata"}],
        "metadata": {
            "intent": "question",
            "confidence": 0.95,
            "language": "en"
        }
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert "metadata" in result
    assert result["metadata"]["intent"] == "question"
    assert result["metadata"]["confidence"] == 0.95


@pytest.mark.asyncio
async def test_get_thread_with_all_timestamps(threads_client, mock_session):
    """Test retrieving a thread with all timestamp fields"""
    # Arrange
    now = datetime.now(UTC)
    expected_thread = {
        "thread_id": "thread_timestamps",
        "created_at": (now - timedelta(days=7)).isoformat(),
        "updated_at": (now - timedelta(hours=1)).isoformat(),
        "last_message_at": now.isoformat(),
        "status": "Active"
    }

    mock_http_method(mock_session.get, expected_thread)

    # Act
    result = await threads_client.get("thread_timestamps")

    # Assert
    assert "created_at" in result
    assert "updated_at" in result
    assert "last_message_at" in result


@pytest.mark.asyncio
async def test_create_thread_server_error(threads_client, mock_session):
    """Test handling server error during thread creation"""
    # Arrange
    mock_http_method(mock_session.post, {"error": "Internal server error"}, 500)

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.create({"title": "Test"})


@pytest.mark.asyncio
async def test_get_messages_empty_params_dict(threads_client, mock_session):
    """Test that get_messages with no limit passes empty params dict"""
    # Arrange
    mock_http_method(mock_session.get, [])

    # Act
    await threads_client.get_messages("thread_123")

    # Assert
    mock_session.get.assert_called_once_with(
        "/threads/thread_123/messages",
        params={}
    )


@pytest.mark.asyncio
async def test_add_message_with_system_role(threads_client, mock_session):
    """Test adding a system message to a thread"""
    # Arrange
    expected_message = {
        "message_id": "msg_system_001",
        "role": "system",
        "contents": [
            {"kind": "text", "text": "System notification: Thread archived"}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "system",
        "contents": [
            {"kind": "text", "text": "System notification: Thread archived"}
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["role"] == "system"


@pytest.mark.asyncio
async def test_create_thread_with_title_only(threads_client, mock_session):
    """Test creating a thread with only a title"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_title_only",
        "title": "Simple Thread Title",
        "status": "Active"
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "title": "Simple Thread Title"
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result["title"] == "Simple Thread Title"
    assert result["thread_id"] == "thread_title_only"


@pytest.mark.asyncio
async def test_get_messages_with_zero_limit(threads_client, mock_session):
    """Test getting messages with limit of 0 (treated as no limit due to falsy value)"""
    # Arrange
    mock_http_method(mock_session.get, [])

    # Act
    result = await threads_client.get_messages("thread_123", limit=0)

    # Assert
    assert len(result) == 0
    mock_session.get.assert_called_once()
    # Note: limit=0 is treated as falsy, so params will be empty dict
    call_params = mock_session.get.call_args[1]["params"]
    assert call_params == {}


@pytest.mark.asyncio
async def test_add_message_with_unicode_content(threads_client, mock_session):
    """Test adding a message with unicode characters"""
    # Arrange
    expected_message = {
        "message_id": "msg_unicode_001",
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello 世界! 🌍 Привет"}
        ],
        "created_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.post, expected_message, 201)

    message = {
        "role": "user",
        "contents": [
            {"kind": "text", "text": "Hello 世界! 🌍 Привет"}
        ]
    }

    # Act
    result = await threads_client.add_message("thread_123", message)

    # Assert
    assert result["contents"][0]["text"] == "Hello 世界! 🌍 Привет"


@pytest.mark.asyncio
async def test_get_thread_unauthorized_error(threads_client, mock_session):
    """Test handling unauthorized error when getting thread"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Unauthorized"}, 401)

    # Act & Assert
    with pytest.raises(Exception):
        await threads_client.get("thread_123")


@pytest.mark.asyncio
async def test_add_message_forbidden_error(threads_client, mock_session):
    """Test handling forbidden error when adding message"""
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
async def test_create_thread_with_nested_metadata(threads_client, mock_session):
    """Test creating a thread with nested metadata structure"""
    # Arrange
    expected_thread = {
        "thread_id": "thread_nested_meta",
        "metadata": {
            "project": {
                "id": "proj_123",
                "name": "Alpha Project",
                "tags": ["important", "urgent"]
            },
            "owner": {
                "user_id": "user_001",
                "department": "engineering"
            }
        },
        "status": "Active"
    }

    mock_http_method(mock_session.post, expected_thread, 201)

    thread = {
        "metadata": {
            "project": {
                "id": "proj_123",
                "name": "Alpha Project",
                "tags": ["important", "urgent"]
            },
            "owner": {
                "user_id": "user_001",
                "department": "engineering"
            }
        }
    }

    # Act
    result = await threads_client.create(thread)

    # Assert
    assert result["metadata"]["project"]["id"] == "proj_123"
    assert "urgent" in result["metadata"]["project"]["tags"]
    assert result["metadata"]["owner"]["department"] == "engineering"


@pytest.mark.asyncio
async def test_get_messages_with_large_limit(threads_client, mock_session):
    """Test getting messages with large limit value"""
    # Arrange
    expected_messages = [
        {"message_id": f"msg_{i:04d}", "role": "user"}
        for i in range(1000)
    ]

    mock_http_method(mock_session.get, expected_messages)

    # Act
    result = await threads_client.get_messages("thread_123", limit=1000)

    # Assert
    assert len(result) == 1000
    mock_session.get.assert_called_once()
    call_params = mock_session.get.call_args[1]["params"]
    assert call_params["limit"] == 1000


@pytest.mark.asyncio
async def test_add_message_with_empty_contents_list(threads_client, mock_session):
    """Test adding a message with empty contents list"""
    # Arrange
    expected_message = {
        "message_id": "msg_empty_contents",
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


@pytest.mark.asyncio
async def test_session_context_manager_integration(client_options):
    """Test ThreadsClient integration with session lifecycle"""
    # This test verifies the client can be used with session management
    # Arrange
    mock_session = Mock()
    mock_http_method(mock_session.get, {"thread_id": "test"})

    threads_client = ThreadsClient(mock_session, client_options)

    # Act
    result = await threads_client.get("test")

    # Assert
    assert result["thread_id"] == "test"
    mock_session.get.assert_called_once()
