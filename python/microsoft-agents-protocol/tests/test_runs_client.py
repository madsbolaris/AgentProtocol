# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tests for RunsClient covering all low-level API operations.

These tests verify the RunsClient directly, matching the .NET RunsClientTests.cs.
Tests cover:
- create() - Creating runs with various options
- create_and_wait() - Blocking run creation
- retrieve() - Getting run by ID
- list() - Listing runs with pagination and filters
- cancel() - Cancelling runs with different actions
- submit_tool_outputs() - Handling tool calls (HITL)
- submit_input() - Handling user input requests
- submit_auth() - Handling auth requirements
- wait() - Waiting for existing runs to complete
- Error handling for each method
- Request validation
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime, timezone
from aiohttp import ClientSession, ClientResponse
from microsoft.agents.protocol.client import AgentProtocolClient
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions


@pytest.fixture
def mock_session():
    """Creates a mock aiohttp ClientSession"""
    session = Mock(spec=ClientSession)
    return session


@pytest.fixture
def client_options():
    """Creates client options for testing"""
    return AgentProtocolClientOptions(base_url="https://api.example.com")


@pytest.fixture
def client(mock_session, client_options):
    """Creates an AgentProtocolClient with mocked session"""
    with patch("aiohttp.ClientSession", return_value=mock_session):
        client = AgentProtocolClient(client_options)
        client.runs._session = mock_session
        return client


def create_mock_response(json_data, status=200):
    """Helper to create a mock aiohttp response"""
    response = AsyncMock(spec=ClientResponse)
    response.status = status
    response.json = AsyncMock(return_value=json_data)
    response.raise_for_status = Mock()
    response.__aenter__ = AsyncMock(return_value=response)
    response.__aexit__ = AsyncMock(return_value=None)
    return response


@pytest.mark.asyncio
async def test_create_with_basic_run_returns_created_run(client, mock_session):
    """Test creating a basic run - matches CreateAsync_WithBasicRun_ReturnsCreatedRun"""
    # Arrange
    expected_run = {
        "run_id": "run_001",
        "agent_id": "agent_001",
        "thread_id": "thread_123",
        "status": "in_progress",
        "input": [
            {
                "role": "user",
                "contents": [{"kind": "text", "text": "What's 2+2?"}],
            }
        ],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "thread_id": "thread_123",
        "input": [
            {
                "role": "user",
                "contents": [{"kind": "text", "text": "What's 2+2?"}],
            }
        ],
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert result["run_id"] == "run_001"
    assert result["agent_id"] == "agent_001"
    assert result["status"] == "in_progress"
    mock_session.post.assert_called_once_with("/runs", json=run_request)


@pytest.mark.asyncio
async def test_create_and_wait_with_ephemeral_run_returns_completed_run(
    client, mock_session
):
    """Test create_and_wait for ephemeral run - matches CreateAndWaitAsync_WithEphemeralRun_ReturnsCompletedRun"""
    # Arrange - Example from "Create and Wait for Completion" section
    expected_response = {
        "run_id": "run_002",
        "status": "completed",
        "output": [
            {
                "role": "assistant",
                "contents": [{"kind": "text", "text": "Hola"}],
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_response, status=200)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [
            {
                "role": "user",
                "contents": [{"kind": "text", "text": "Translate 'hello' to Spanish"}],
            }
        ],
        "thread_cleanup": "delete",
    }

    # Act
    result = await client.runs.create_and_wait(run_request)

    # Assert
    assert result is not None
    assert result["status"] == "completed"
    assert len(result["output"]) == 1
    assert result["output"][0]["contents"][0]["text"] == "Hola"
    mock_session.post.assert_called_once_with("/runs/wait", json=run_request)


@pytest.mark.asyncio
async def test_get_with_valid_run_id_returns_run(client, mock_session):
    """Test retrieving a run by ID - matches GetAsync_WithValidRunId_ReturnsRun"""
    # Arrange
    expected_run = {
        "run_id": "run_123",
        "agent_id": "agent_001",
        "status": "completed",
        "input": [],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.get("run_123")

    # Assert
    assert result is not None
    assert result["run_id"] == "run_123"
    assert result["status"] == "completed"
    mock_session.get.assert_called_once_with("/runs/run_123")


@pytest.mark.asyncio
async def test_list_with_filters_returns_filtered_runs(client, mock_session):
    """Test listing runs with filters - matches ListAsync_WithFilters_ReturnsFilteredRuns"""
    # Arrange - Example from "List Runs with Filtering" section
    now = datetime.now(timezone.utc)
    expected_runs = [
        {
            "run_id": "run_001",
            "agent_id": "agent_001",
            "thread_id": "thread_123",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": now.isoformat(),
        },
        {
            "run_id": "run_002",
            "agent_id": "agent_001",
            "thread_id": "thread_123",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": now.isoformat(),
        },
    ]

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list(thread_id="thread_123", limit=50)

    # Assert
    assert result is not None
    assert len(result) == 2
    for run in result:
        assert run["thread_id"] == "thread_123"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_with_status_filter_returns_completed_runs(client, mock_session):
    """Test listing runs with status filter - matches ListAsync_WithStatusFilter_ReturnsCompletedRuns"""
    # Arrange - Example from "Filter by status" section
    expected_runs = [
        {
            "run_id": "run_003",
            "agent_id": "agent_001",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list(status="completed", limit=100)

    # Assert
    assert result is not None
    for run in result:
        assert run["status"] == "completed"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_with_interrupt_action_stops_run_and_preserves_state(
    client, mock_session
):
    """Test cancelling with interrupt - matches CancelAsync_WithInterruptAction_StopsRunAndPreservesState"""
    # Arrange - Example from "Cancel a Running Execution - Interrupt" section
    expected_run = {
        "run_id": "run_456",
        "agent_id": "agent_001",
        "status": "cancelled",
        "input": [],
        "output": [
            {
                "role": "assistant",
                "contents": [{"kind": "text", "text": "Partial response..."}],
            }
        ],
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
        "cancellation_reason": "User stopped generation",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.cancel(
        "run_456", action="interrupt", reason="User stopped generation"
    )

    # Assert
    assert result is not None
    assert result["status"] == "cancelled"
    assert result["cancellation_reason"] == "User stopped generation"
    assert result["output"] is not None
    assert len(result["output"]) > 0
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "/runs/run_456/cancel"


@pytest.mark.asyncio
async def test_cancel_with_rollback_action_stops_run_and_cleans_up(
    client, mock_session
):
    """Test cancelling with rollback - matches CancelAsync_WithRollbackAction_StopsRunAndCleansUp"""
    # Arrange - Example from "Cancel a Running Execution - Rollback" section
    expected_run = {
        "run_id": "run_456",
        "agent_id": "agent_001",
        "status": "cancelled",
        "input": [],
        "output": [],  # Rollback cleans up output
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
        "cancellation_reason": "Failed run cleanup",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.cancel(
        "run_456", action="rollback", reason="Failed run cleanup"
    )

    # Assert
    assert result is not None
    assert result["status"] == "cancelled"
    assert result["cancellation_reason"] == "Failed run cleanup"
    assert len(result["output"]) == 0  # Rollback cleans up output
    mock_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_submit_tool_outputs_with_requires_action_status_continues_run(
    client, mock_session
):
    """Test submitting tool outputs - matches SubmitToolOutputsAsync_WithRequiresActionStatus_ContinuesRun"""
    # Arrange - Example from "Handle Tool Calls (HITL)" section
    expected_run = {
        "run_id": "run_789",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [
            {
                "role": "tool",
                "contents": [
                    {
                        "kind": "function_result",
                        "call_id": "call_abc123",
                        "name": "delete_file",
                        "result": "File deleted successfully",
                    }
                ],
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    tool_outputs = [
        {"tool_call_id": "call_abc123", "output": "File deleted successfully"}
    ]

    # Act
    result = await client.runs.submit_tool_outputs("run_789", tool_outputs)

    # Assert
    assert result is not None
    assert result["status"] == "in_progress"
    assert len(result["output"]) > 0
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "/runs/run_789/submit_tool_outputs"


@pytest.mark.asyncio
async def test_submit_input_with_input_required_status_continues_run(
    client, mock_session
):
    """Test submitting user input - matches SubmitInputAsync_WithInputRequiredStatus_ContinuesRun"""
    # Arrange - Example from "Handle User Input Requests" section
    expected_run = {
        "run_id": "run_789",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [
            {
                "role": "user",
                "contents": [{"kind": "text", "text": "Option 1"}],
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.submit_input("run_789", "Option 1")

    # Assert
    assert result is not None
    assert result["status"] == "in_progress"
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "/runs/run_789/submit_input"


@pytest.mark.asyncio
async def test_submit_auth_with_auth_required_status_continues_run(client, mock_session):
    """Test submitting auth credentials - matches SubmitAuthAsync_WithAuthRequiredStatus_ContinuesRun"""
    # Arrange
    expected_run = {
        "run_id": "run_890",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.submit_auth("run_890", "eyJhbGc...", "Bearer")

    # Assert
    assert result is not None
    assert result["status"] == "in_progress"
    mock_session.post.assert_called_once()
    call_args = mock_session.post.call_args
    assert call_args[0][0] == "/runs/run_890/submit_auth"


@pytest.mark.asyncio
async def test_wait_with_existing_run_waits_for_completion(client, mock_session):
    """Test waiting for existing run - matches WaitAsync_WithExistingRun_WaitsForCompletion"""
    # Arrange
    now = datetime.now(timezone.utc)
    expected_response = {
        "run_id": "run_999",
        "thread_id": "thread_123",
        "status": "completed",
        "output": [
            {
                "role": "assistant",
                "contents": [{"kind": "text", "text": "Task completed!"}],
            }
        ],
        "created_at": now.isoformat(),
        "completed_at": now.isoformat(),
    }

    mock_response = create_mock_response(expected_response, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.wait("run_999")

    # Assert
    assert result is not None
    assert result["run_id"] == "run_999"
    assert result["status"] == "completed"
    assert result["completed_at"] is not None
    mock_session.get.assert_called_once_with("/runs/run_999/wait")


@pytest.mark.asyncio
async def test_create_with_metadata_includes_metadata(client, mock_session):
    """Test creating run with metadata"""
    # Arrange
    expected_run = {
        "run_id": "run_100",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [],
        "metadata": {"session_id": "sess_123", "user_id": "user_456"},
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Hello"}]}],
        "metadata": {"session_id": "sess_123", "user_id": "user_456"},
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert result["metadata"]["session_id"] == "sess_123"
    assert result["metadata"]["user_id"] == "user_456"


@pytest.mark.asyncio
async def test_create_with_max_tokens_includes_max_tokens(client, mock_session):
    """Test creating run with max_tokens"""
    # Arrange
    expected_run = {
        "run_id": "run_101",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [],
        "max_tokens": 1000,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Hello"}]}],
        "max_tokens": 1000,
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert result["max_tokens"] == 1000


@pytest.mark.asyncio
async def test_create_with_temperature_includes_temperature(client, mock_session):
    """Test creating run with temperature setting"""
    # Arrange
    expected_run = {
        "run_id": "run_102",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [],
        "temperature": 0.7,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Hello"}]}],
        "temperature": 0.7,
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert result["temperature"] == 0.7


@pytest.mark.asyncio
async def test_list_with_pagination_parameters(client, mock_session):
    """Test listing runs with pagination (limit and offset)"""
    # Arrange
    expected_runs = [
        {
            "run_id": f"run_{i}",
            "agent_id": "agent_001",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        for i in range(10)
    ]

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list(limit=10, offset=20)

    # Assert
    assert result is not None
    assert len(result) == 10
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_list_with_agent_id_filter(client, mock_session):
    """Test listing runs filtered by agent_id"""
    # Arrange
    expected_runs = [
        {
            "run_id": "run_200",
            "agent_id": "agent_specific",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list(agent_id="agent_specific")

    # Assert
    assert result is not None
    for run in result:
        assert run["agent_id"] == "agent_specific"
    mock_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_create_with_http_error_raises_exception(client, mock_session):
    """Test that HTTP errors are properly raised"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 400
    mock_response.raise_for_status = Mock(
        side_effect=Exception("400 Bad Request")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Hello"}]}],
    }

    # Act & Assert
    with pytest.raises(Exception, match="400 Bad Request"):
        await client.runs.create(run_request)


@pytest.mark.asyncio
async def test_get_with_not_found_raises_exception(client, mock_session):
    """Test that 404 errors are properly raised"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 404
    mock_response.raise_for_status = Mock(
        side_effect=Exception("404 Not Found")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.get = Mock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(Exception, match="404 Not Found"):
        await client.runs.get("nonexistent_run")


@pytest.mark.asyncio
async def test_create_with_invalid_json_raises_exception(client, mock_session):
    """Test that invalid JSON responses are handled"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 200
    mock_response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
    mock_response.raise_for_status = Mock()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Hello"}]}],
    }

    # Act & Assert
    with pytest.raises(ValueError, match="Invalid JSON"):
        await client.runs.create(run_request)


@pytest.mark.asyncio
async def test_cancel_without_reason_uses_default(client, mock_session):
    """Test cancelling without providing a reason"""
    # Arrange
    expected_run = {
        "run_id": "run_500",
        "agent_id": "agent_001",
        "status": "cancelled",
        "input": [],
        "output": [],
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.cancel("run_500")

    # Assert
    assert result is not None
    assert result["status"] == "cancelled"
    mock_session.post.assert_called_once()


@pytest.mark.asyncio
async def test_list_returns_empty_array_when_no_runs(client, mock_session):
    """Test listing runs returns empty array when no runs exist"""
    # Arrange
    expected_runs = []

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list()

    # Assert
    assert result is not None
    assert len(result) == 0
    assert isinstance(result, list)


@pytest.mark.asyncio
async def test_create_with_thread_cleanup_delete(client, mock_session):
    """Test creating ephemeral run with thread_cleanup=delete"""
    # Arrange
    expected_run = {
        "run_id": "run_600",
        "agent_id": "agent_001",
        "status": "completed",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
        "output": [
            {"role": "assistant", "contents": [{"kind": "text", "text": "Response"}]}
        ],
        "thread_cleanup": "delete",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
        "thread_cleanup": "delete",
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert result["thread_cleanup"] == "delete"


@pytest.mark.asyncio
async def test_create_with_multiple_input_messages(client, mock_session):
    """Test creating run with multiple input messages"""
    # Arrange
    expected_run = {
        "run_id": "run_700",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [
            {"role": "user", "contents": [{"kind": "text", "text": "First message"}]},
            {"role": "user", "contents": [{"kind": "text", "text": "Second message"}]},
        ],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [
            {"role": "user", "contents": [{"kind": "text", "text": "First message"}]},
            {"role": "user", "contents": [{"kind": "text", "text": "Second message"}]},
        ],
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert len(result["input"]) == 2


@pytest.mark.asyncio
async def test_submit_tool_outputs_with_multiple_outputs(client, mock_session):
    """Test submitting multiple tool outputs"""
    # Arrange
    expected_run = {
        "run_id": "run_800",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [
            {
                "role": "tool",
                "contents": [
                    {
                        "kind": "function_result",
                        "call_id": "call_1",
                        "name": "tool_1",
                        "result": "Result 1",
                    },
                    {
                        "kind": "function_result",
                        "call_id": "call_2",
                        "name": "tool_2",
                        "result": "Result 2",
                    },
                ],
            }
        ],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    tool_outputs = [
        {"tool_call_id": "call_1", "output": "Result 1"},
        {"tool_call_id": "call_2", "output": "Result 2"},
    ]

    # Act
    result = await client.runs.submit_tool_outputs("run_800", tool_outputs)

    # Assert
    assert result is not None
    assert result["status"] == "in_progress"


@pytest.mark.asyncio
async def test_create_with_failed_status(client, mock_session):
    """Test creating run that fails immediately"""
    # Arrange
    expected_run = {
        "run_id": "run_900",
        "agent_id": "agent_001",
        "status": "failed",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
        "output": [],
        "error": {"code": "internal_error", "message": "An error occurred"},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "failed_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=201)
    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
    }

    # Act
    result = await client.runs.create(run_request)

    # Assert
    assert result is not None
    assert result["status"] == "failed"
    assert result["error"]["code"] == "internal_error"


@pytest.mark.asyncio
async def test_list_with_multiple_filters(client, mock_session):
    """Test listing runs with multiple filters combined"""
    # Arrange
    expected_runs = [
        {
            "run_id": "run_1000",
            "agent_id": "agent_001",
            "thread_id": "thread_123",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list(
        agent_id="agent_001", thread_id="thread_123", status="completed", limit=50
    )

    # Assert
    assert result is not None
    assert len(result) == 1
    assert result[0]["agent_id"] == "agent_001"
    assert result[0]["thread_id"] == "thread_123"
    assert result[0]["status"] == "completed"


@pytest.mark.asyncio
async def test_create_and_stream_yields_sse_lines(client, mock_session):
    """Test create_and_stream yields SSE lines"""
    # Arrange
    async def mock_stream_content():
        # Simulate SSE stream
        lines = [
            b'event: message.start\n',
            b'data: {"message_id": "msg_1"}\n',
            b'\n',
            b'event: message.delta\n',
            b'data: {"text": "Hello"}\n',
            b'\n',
            b'event: message.completed\n',
            b'data: {"status": "done"}\n',
        ]
        for line in lines:
            yield line

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.raise_for_status = Mock()
    mock_response.content = mock_stream_content()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
    }

    # Act
    lines = []
    async for line in client.runs.create_and_stream(run_request):
        lines.append(line)

    # Assert
    assert len(lines) > 0
    assert 'event: message.start' in lines
    mock_session.post.assert_called_once_with("/runs/stream", json=run_request)


@pytest.mark.asyncio
async def test_list_with_offset_parameter(client, mock_session):
    """Test listing runs with offset for pagination"""
    # Arrange
    expected_runs = [
        {
            "run_id": "run_1100",
            "agent_id": "agent_001",
            "status": "completed",
            "input": [],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    ]

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list(offset=10, limit=5)

    # Assert
    assert result is not None
    mock_session.get.assert_called_once()
    # Verify URL has offset parameter
    call_args = mock_session.get.call_args[0][0]
    assert "offset=10" in call_args


@pytest.mark.asyncio
async def test_cancel_with_empty_payload(client, mock_session):
    """Test cancelling without action or reason sends None payload"""
    # Arrange
    expected_run = {
        "run_id": "run_1200",
        "agent_id": "agent_001",
        "status": "cancelled",
        "input": [],
        "output": [],
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.cancel("run_1200")

    # Assert
    assert result is not None
    assert result["status"] == "cancelled"
    call_args = mock_session.post.call_args
    # Payload should be None when no action or reason provided
    assert call_args[1]["json"] is None


@pytest.mark.asyncio
async def test_cancel_with_only_action(client, mock_session):
    """Test cancelling with only action parameter"""
    # Arrange
    expected_run = {
        "run_id": "run_1300",
        "status": "cancelled",
        "input": [],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.cancel("run_1300", action="interrupt")

    # Assert
    assert result is not None
    call_args = mock_session.post.call_args
    payload = call_args[1]["json"]
    assert payload["action"] == "interrupt"
    assert "reason" not in payload


@pytest.mark.asyncio
async def test_cancel_with_only_reason(client, mock_session):
    """Test cancelling with only reason parameter"""
    # Arrange
    expected_run = {
        "run_id": "run_1400",
        "status": "cancelled",
        "input": [],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.cancel("run_1400", reason="User requested")

    # Assert
    assert result is not None
    call_args = mock_session.post.call_args
    payload = call_args[1]["json"]
    assert payload["reason"] == "User requested"
    assert "action" not in payload


@pytest.mark.asyncio
async def test_list_with_no_parameters(client, mock_session):
    """Test listing runs with no filter parameters"""
    # Arrange
    expected_runs = []

    mock_response = create_mock_response(expected_runs, status=200)
    mock_session.get = Mock(return_value=mock_response)

    # Act
    result = await client.runs.list()

    # Assert
    assert result is not None
    assert isinstance(result, list)
    # URL should have no query parameters
    call_args = mock_session.get.call_args[0][0]
    assert call_args == "/runs"


@pytest.mark.asyncio
async def test_wait_with_http_error_raises_exception(client, mock_session):
    """Test that wait raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 500
    mock_response.raise_for_status = Mock(
        side_effect=Exception("500 Internal Server Error")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.get = Mock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(Exception, match="500 Internal Server Error"):
        await client.runs.wait("run_error")


@pytest.mark.asyncio
async def test_submit_input_with_http_error_raises_exception(client, mock_session):
    """Test that submit_input raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 400
    mock_response.raise_for_status = Mock(
        side_effect=Exception("400 Bad Request")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(Exception, match="400 Bad Request"):
        await client.runs.submit_input("run_123", "Input text")


@pytest.mark.asyncio
async def test_submit_auth_with_http_error_raises_exception(client, mock_session):
    """Test that submit_auth raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 401
    mock_response.raise_for_status = Mock(
        side_effect=Exception("401 Unauthorized")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(Exception, match="401 Unauthorized"):
        await client.runs.submit_auth("run_123", "token")


@pytest.mark.asyncio
async def test_submit_tool_outputs_with_http_error_raises_exception(client, mock_session):
    """Test that submit_tool_outputs raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 404
    mock_response.raise_for_status = Mock(
        side_effect=Exception("404 Not Found")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    tool_outputs = [{"tool_call_id": "call_1", "output": "Result"}]

    # Act & Assert
    with pytest.raises(Exception, match="404 Not Found"):
        await client.runs.submit_tool_outputs("run_123", tool_outputs)


@pytest.mark.asyncio
async def test_cancel_with_http_error_raises_exception(client, mock_session):
    """Test that cancel raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 403
    mock_response.raise_for_status = Mock(
        side_effect=Exception("403 Forbidden")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(Exception, match="403 Forbidden"):
        await client.runs.cancel("run_123")


@pytest.mark.asyncio
async def test_create_and_wait_with_http_error_raises_exception(client, mock_session):
    """Test that create_and_wait raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 503
    mock_response.raise_for_status = Mock(
        side_effect=Exception("503 Service Unavailable")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
    }

    # Act & Assert
    with pytest.raises(Exception, match="503 Service Unavailable"):
        await client.runs.create_and_wait(run_request)


@pytest.mark.asyncio
async def test_list_with_http_error_raises_exception(client, mock_session):
    """Test that list raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock(spec=ClientResponse)
    mock_response.status = 500
    mock_response.raise_for_status = Mock(
        side_effect=Exception("500 Internal Server Error")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.get = Mock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(Exception, match="500 Internal Server Error"):
        await client.runs.list()


@pytest.mark.asyncio
async def test_submit_auth_with_custom_token_type(client, mock_session):
    """Test submitting auth with custom token type"""
    # Arrange
    expected_run = {
        "run_id": "run_1500",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act
    result = await client.runs.submit_auth("run_1500", "custom_token", "Custom")

    # Assert
    assert result is not None
    assert result["status"] == "in_progress"
    call_args = mock_session.post.call_args
    payload = call_args[1]["json"]
    assert payload["token"] == "custom_token"
    assert payload["token_type"] == "Custom"


@pytest.mark.asyncio
async def test_submit_auth_with_default_token_type(client, mock_session):
    """Test submitting auth with default Bearer token type"""
    # Arrange
    expected_run = {
        "run_id": "run_1600",
        "agent_id": "agent_001",
        "status": "in_progress",
        "input": [],
        "output": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    mock_response = create_mock_response(expected_run, status=200)
    mock_session.post = Mock(return_value=mock_response)

    # Act - Not specifying token_type should default to "Bearer"
    result = await client.runs.submit_auth("run_1600", "bearer_token")

    # Assert
    assert result is not None
    call_args = mock_session.post.call_args
    payload = call_args[1]["json"]
    assert payload["token"] == "bearer_token"
    assert payload["token_type"] == "Bearer"


@pytest.mark.asyncio
async def test_create_and_stream_with_http_error_raises_exception(client, mock_session):
    """Test that create_and_stream raises exception on HTTP error"""
    # Arrange
    mock_response = AsyncMock()
    mock_response.status = 400
    mock_response.raise_for_status = Mock(
        side_effect=Exception("400 Bad Request")
    )
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
    }

    # Act & Assert
    with pytest.raises(Exception, match="400 Bad Request"):
        async for _ in client.runs.create_and_stream(run_request):
            pass


@pytest.mark.asyncio
async def test_create_and_stream_with_empty_lines_filters_them(client, mock_session):
    """Test that create_and_stream filters out empty lines"""
    # Arrange
    async def mock_stream_content():
        lines = [
            b'event: message.start\n',
            b'\n',  # Empty line
            b'data: {"message_id": "msg_1"}\n',
            b'   \n',  # Whitespace only
            b'event: message.completed\n',
        ]
        for line in lines:
            yield line

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.raise_for_status = Mock()
    mock_response.content = mock_stream_content()
    mock_response.__aenter__ = AsyncMock(return_value=mock_response)
    mock_response.__aexit__ = AsyncMock(return_value=None)

    mock_session.post = Mock(return_value=mock_response)

    run_request = {
        "agent_id": "agent_001",
        "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}],
    }

    # Act
    lines = []
    async for line in client.runs.create_and_stream(run_request):
        lines.append(line)

    # Assert - Empty lines should be filtered out
    for line in lines:
        assert len(line.strip()) > 0
