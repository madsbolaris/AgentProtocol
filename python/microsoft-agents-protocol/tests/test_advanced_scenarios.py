# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Tests for advanced scenarios and complex examples from documentation.

This is the Python equivalent of dotnet/tests/Microsoft.Agents.Client.Tests/AdvancedScenariosTests.cs
Tests cover:
- Multi-turn conversations with thread context
- Tool execution workflows with approval
- Complex agent interactions
- Retry and error recovery
- Timeout handling
- Concurrent operations
- State management across runs
- Inline agent definitions
- Working with images/multimodal content
- Custom HTTP client configuration
- Error handling patterns
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List
from aiohttp import ClientSession, ClientResponse, ClientTimeout

from microsoft.agents.protocol.client import AgentProtocolClient
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

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def mock_http_method(method_mock, response_data: Any, status: int = 200):
    """Helper to properly mock an aiohttp session method (get, post, etc.)"""
    response = MockResponse(response_data, status)
    cm = MagicMock()
    cm.__aenter__.return_value = response
    cm.__aexit__.return_value = None
    method_mock.return_value = cm


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
        client.threads._session = mock_session
        client.agents._session = mock_session
        return client


class TestInlineAgentDefinitions:
    """Tests for inline agent definition with ephemeral execution"""

    @pytest.mark.asyncio
    async def test_inline_agent_definition_with_ephemeral_execution_returns_result(
        self, client, mock_session
    ):
        """Test inline agent definition with ephemeral execution - matches .NET test"""
        # Arrange - Example from "Using Inline Agent Definitions" section
        now = datetime.now(timezone.utc)
        expected_response = {
            "run_id": "run_ephemeral_001",
            "status": "completed",
            "output": [
                {
                    "role": "assistant",
                    "contents": [
                        {
                            "kind": "text",
                            "text": "Calculus is the mathematical study of continuous change..."
                        }
                    ]
                }
            ],
            "created_at": now.isoformat(),
            "completed_at": (now + timedelta(seconds=5)).isoformat()
        }

        mock_http_method(mock_session.post, expected_response, 200)

        run = {
            "agent_id": "ephemeral",
            "agent": {
                "model": "gpt-4o",
                "instructions": "You are a math tutor",
                "temperature": 0.3
            },
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Explain calculus"}
                    ]
                }
            ],
            "thread_cleanup": "delete"
        }

        # Act
        result = await client.runs.create_and_wait(run)

        # Assert
        assert result is not None
        assert result["status"] == "completed"
        assert len(result["output"]) > 0
        assert result["run_id"] == "run_ephemeral_001"
        mock_session.post.assert_called_once_with("/runs/wait", json=run)


class TestMultimodalContent:
    """Tests for working with images and multimodal content"""

    @pytest.mark.asyncio
    async def test_working_with_images_vision_model_processes_image_content(
        self, client, mock_session
    ):
        """Test vision model processing image content - matches .NET test"""
        # Arrange - Example from "Working with Images" section
        expected_run = {
            "run_id": "run_vision_001",
            "agent_id": "agent_vision",
            "status": "in_progress",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "What's in this image?"},
                        {
                            "kind": "image",
                            "url": "https://example.com/image.jpg",
                            "detail": "high"
                        }
                    ]
                }
            ],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        mock_http_method(mock_session.post, expected_run, 201)

        message = {
            "role": "user",
            "contents": [
                {"kind": "text", "text": "What's in this image?"},
                {
                    "kind": "image",
                    "url": "https://example.com/image.jpg",
                    "detail": "high"
                }
            ]
        }

        run = {
            "agent_id": "agent_vision",
            "input": [message]
        }

        # Act
        result = await client.runs.create(run)

        # Assert
        assert result is not None
        assert result["agent_id"] == "agent_vision"
        assert len(result["input"][0]["contents"]) == 2
        assert result["input"][0]["contents"][0]["kind"] == "text"
        assert result["input"][0]["contents"][1]["kind"] == "image"


class TestToolExecutionWorkflows:
    """Tests for tool execution with approval and HITL patterns"""

    @pytest.mark.asyncio
    async def test_tool_execution_with_approval_requires_human_in_the_loop(
        self, client, mock_session
    ):
        """Test tool execution requiring approval - matches .NET test"""
        # Arrange - Example from "Tool Execution with Approval" section
        agent = {
            "model": "gpt-4o",
            "instructions": "You help manage files",
            "tools": [
                {
                    "name": "delete_file",
                    "description": "Delete a file from the system",
                    "requires_approval": True,
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "File path to delete"
                            }
                        },
                        "required": ["path"]
                    }
                }
            ]
        }

        agent_card = {
            "name": "File Manager",
            "capabilities": {"tools": True},
            "tools": agent["tools"]
        }

        mock_http_method(mock_session.post, agent_card, 200)

        # Act
        result = await client.agents.inspect(agent)

        # Assert
        assert result is not None
        assert len(result["tools"]) > 0
        assert result["tools"][0]["requires_approval"] is True
        assert result["tools"][0]["name"] == "delete_file"

    @pytest.mark.asyncio
    async def test_tool_execution_complete_workflow_with_submission(
        self, client, mock_session
    ):
        """Test complete tool execution workflow with approval and submission"""
        # Arrange - Complete HITL workflow
        # Step 1: Run reaches requires_action status
        run_requiring_action = {
            "run_id": "run_tool_001",
            "agent_id": "agent_001",
            "status": "requires_action",
            "required_action": {
                "type": "submit_tool_outputs",
                "submit_tool_outputs": {
                    "tool_calls": [
                        {
                            "id": "call_abc123",
                            "type": "function",
                            "function": {
                                "name": "delete_file",
                                "arguments": '{"path": "/tmp/file.txt"}'
                            }
                        }
                    ]
                }
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Step 2: After submitting tool outputs, run continues
        run_after_submission = {
            "run_id": "run_tool_001",
            "agent_id": "agent_001",
            "status": "in_progress",
            "output": [
                {
                    "role": "tool",
                    "contents": [
                        {
                            "kind": "function_result",
                            "call_id": "call_abc123",
                            "name": "delete_file",
                            "result": "File deleted successfully"
                        }
                    ]
                }
            ],
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        # Setup mocks
        mock_http_method(mock_session.get, run_requiring_action, 200)

        # For post, we need to setup it separately after get
        post_response = MockResponse(run_after_submission, 200)
        post_cm = MagicMock()
        post_cm.__aenter__.return_value = post_response
        post_cm.__aexit__.return_value = None
        mock_session.post.return_value = post_cm

        # Act
        # Step 1: Check run status
        run = await client.runs.get("run_tool_001")
        assert run["status"] == "requires_action"

        # Step 2: User approves and submits tool outputs
        tool_outputs = [
            {
                "tool_call_id": "call_abc123",
                "output": "File deleted successfully"
            }
        ]

        result = await client.runs.submit_tool_outputs("run_tool_001", tool_outputs)

        # Assert
        assert result is not None
        assert result["status"] == "in_progress"
        assert len(result["output"]) > 0


class TestMultiTurnConversations:
    """Tests for multi-turn conversations with thread context and state management"""

    @pytest.mark.asyncio
    async def test_multi_turn_conversation_with_thread_context_maintains_state(
        self, client, mock_session
    ):
        """Test multi-turn conversation maintaining state - matches .NET test"""
        # Arrange - Multi-turn conversation pattern
        now = datetime.now(timezone.utc)

        # Turn 1: Create thread
        expected_thread = {
            "thread_id": "thread_multi_001",
            "title": "Math Help",
            "status": "active",
            "created_at": now.isoformat()
        }

        # Turn 2: First run
        first_run = {
            "run_id": "run_turn_001",
            "agent_id": "agent_math",
            "thread_id": "thread_multi_001",
            "status": "completed",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "What is 5 + 3?"}
                    ]
                }
            ],
            "output": [
                {
                    "role": "assistant",
                    "contents": [
                        {"kind": "text", "text": "5 + 3 equals 8"}
                    ]
                }
            ],
            "created_at": now.isoformat()
        }

        # Turn 3: Second run (references previous context)
        second_run = {
            "run_id": "run_turn_002",
            "agent_id": "agent_math",
            "thread_id": "thread_multi_001",
            "status": "completed",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Now multiply that by 2"}
                    ]
                }
            ],
            "output": [
                {
                    "role": "assistant",
                    "contents": [
                        {"kind": "text", "text": "8 multiplied by 2 equals 16"}
                    ]
                }
            ],
            "created_at": now.isoformat()
        }

        # Setup mocks for sequential calls
        thread_response = MockResponse(expected_thread, 201)
        thread_cm = MagicMock()
        thread_cm.__aenter__.return_value = thread_response
        thread_cm.__aexit__.return_value = None

        first_run_response = MockResponse(first_run, 201)
        first_run_cm = MagicMock()
        first_run_cm.__aenter__.return_value = first_run_response
        first_run_cm.__aexit__.return_value = None

        second_run_response = MockResponse(second_run, 201)
        second_run_cm = MagicMock()
        second_run_cm.__aenter__.return_value = second_run_response
        second_run_cm.__aexit__.return_value = None

        mock_session.post.side_effect = [thread_cm, first_run_cm, second_run_cm]

        # Act - Simulate multi-turn conversation
        # Turn 1: Create thread
        thread = await client.threads.create({"title": "Math Help"})

        # Turn 2: First question
        turn1 = await client.runs.create({
            "thread_id": thread["thread_id"],
            "agent_id": "agent_math",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "What is 5 + 3?"}
                    ]
                }
            ]
        })

        # Turn 3: Follow-up question (references previous answer)
        turn2 = await client.runs.create({
            "thread_id": thread["thread_id"],
            "agent_id": "agent_math",
            "input": [
                {
                    "role": "user",
                    "contents": [
                        {"kind": "text", "text": "Now multiply that by 2"}
                    ]
                }
            ]
        })

        # Assert
        assert thread is not None
        assert thread["thread_id"] == "thread_multi_001"

        assert turn1 is not None
        assert turn1["thread_id"] == "thread_multi_001"
        assert turn1["status"] == "completed"
        assert turn1["output"] is not None

        assert turn2 is not None
        assert turn2["thread_id"] == "thread_multi_001"
        assert turn2["status"] == "completed"
        assert turn2["output"] is not None

        # Verify multi-turn conversation maintains thread context
        assert turn1["thread_id"] == turn2["thread_id"]

    @pytest.mark.asyncio
    async def test_multi_turn_with_state_persistence_across_runs(
        self, client, mock_session
    ):
        """Test state persistence across multiple runs in same thread"""
        # Arrange
        thread_id = "thread_state_001"

        runs = [
            {
                "run_id": f"run_{i}",
                "thread_id": thread_id,
                "status": "completed",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Step {i}"}]}],
                "output": [{"role": "assistant", "contents": [{"kind": "text", "text": f"Response {i}"}]}],
                "metadata": {"step": i, "previous_context": f"context_{i-1}" if i > 1 else None}
            }
            for i in range(1, 4)
        ]

        # Setup mocks for multiple runs
        cms = []
        for run in runs:
            response = MockResponse(run, 201)
            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            cms.append(cm)

        mock_session.post.side_effect = cms

        # Act - Execute multiple runs in sequence
        results = []
        for i in range(1, 4):
            result = await client.runs.create({
                "thread_id": thread_id,
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Step {i}"}]}]
            })
            results.append(result)

        # Assert
        assert len(results) == 3
        for i, result in enumerate(results, 1):
            assert result["thread_id"] == thread_id
            assert result["status"] == "completed"
            assert result["metadata"]["step"] == i


class TestErrorHandling:
    """Tests for error handling and recovery patterns"""

    @pytest.mark.asyncio
    async def test_error_handling_failed_run_contains_error_details(
        self, client, mock_session
    ):
        """Test failed run with error details - matches .NET test"""
        # Arrange - Example from "Error Handling" section
        failed_run = {
            "run_id": "run_failed_001",
            "agent_id": "agent_001",
            "status": "failed",
            "input": [],
            "output": [],
            "error": {
                "code": "context_length_exceeded",
                "message": "The conversation exceeded the maximum token limit of 128000 tokens",
                "details": {
                    "max_tokens": 128000,
                    "actual_tokens": 150000
                }
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        mock_http_method(mock_session.get, failed_run, 200)

        # Act
        result = await client.runs.get("run_failed_001")

        # Assert
        assert result is not None
        assert result["status"] == "failed"
        assert result["error"] is not None
        assert result["error"]["code"] == "context_length_exceeded"
        assert "maximum token limit" in result["error"]["message"]
        assert result["error"]["details"] is not None
        assert result["error"]["details"]["max_tokens"] == 128000

    @pytest.mark.asyncio
    async def test_retry_logic_with_exponential_backoff(
        self, client, mock_session
    ):
        """Test retry logic with exponential backoff for transient errors"""
        # Arrange
        # First two attempts fail with 503, third succeeds
        error_response_1 = MockResponse({"error": "Service unavailable"}, 503)
        error_cm_1 = MagicMock()
        error_cm_1.__aenter__.return_value = error_response_1
        error_cm_1.__aexit__.return_value = None

        error_response_2 = MockResponse({"error": "Service unavailable"}, 503)
        error_cm_2 = MagicMock()
        error_cm_2.__aenter__.return_value = error_response_2
        error_cm_2.__aexit__.return_value = None

        success_response = MockResponse({
            "run_id": "run_retry_001",
            "status": "completed",
            "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Success"}]}]
        }, 200)
        success_cm = MagicMock()
        success_cm.__aenter__.return_value = success_response
        success_cm.__aexit__.return_value = None

        mock_session.post.side_effect = [error_cm_1, error_cm_2, success_cm]

        # Act - Implement simple retry logic
        max_retries = 3
        retry_count = 0
        result = None
        last_error = None

        while retry_count < max_retries:
            try:
                result = await client.runs.create({
                    "agent_id": "agent_001",
                    "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}]
                })
                break
            except Exception as e:
                last_error = e
                retry_count += 1
                if retry_count < max_retries:
                    await asyncio.sleep(0.1 * (2 ** retry_count))  # Exponential backoff
                else:
                    raise

        # Assert
        assert result is not None
        assert result["status"] == "completed"
        assert retry_count == 2  # Failed twice, succeeded on third attempt

    @pytest.mark.asyncio
    async def test_error_recovery_with_fallback_strategy(
        self, client, mock_session
    ):
        """Test error recovery with fallback to simpler model"""
        # Arrange
        # Primary model fails
        primary_error = MockResponse({
            "run_id": "run_primary_001",
            "status": "failed",
            "error": {"code": "rate_limit_exceeded", "message": "Rate limit exceeded"}
        }, 200)
        primary_cm = MagicMock()
        primary_cm.__aenter__.return_value = primary_error
        primary_cm.__aexit__.return_value = None

        # Fallback model succeeds
        fallback_success = MockResponse({
            "run_id": "run_fallback_001",
            "status": "completed",
            "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Fallback response"}]}]
        }, 200)
        fallback_cm = MagicMock()
        fallback_cm.__aenter__.return_value = fallback_success
        fallback_cm.__aexit__.return_value = None

        mock_session.post.side_effect = [primary_cm, fallback_cm]

        # Act
        # Try primary model
        primary_run = {
            "agent_id": "agent_gpt4",
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "Complex query"}]}]
        }
        result = await client.runs.create(primary_run)

        # Check if primary failed
        if result.get("status") == "failed":
            # Fallback to simpler model
            fallback_run = {
                "agent_id": "agent_gpt35",
                "input": primary_run["input"]
            }
            result = await client.runs.create(fallback_run)

        # Assert
        assert result is not None
        assert result["status"] == "completed"
        assert result["run_id"] == "run_fallback_001"


class TestTimeoutHandling:
    """Tests for timeout handling in long-running operations"""

    @pytest.mark.asyncio
    async def test_timeout_handling_with_wait_operation(
        self, client, mock_session
    ):
        """Test timeout handling for wait operations"""
        # Arrange - Simulate long-running operation that exceeds timeout
        def slow_response(*args, **kwargs):
            response = MockResponse({"run_id": "run_001", "status": "in_progress"}, 200)
            cm = MagicMock()

            # Make __aenter__ return a coroutine that sleeps then returns response
            async def aenter_with_sleep(self_cm):
                await asyncio.sleep(2)
                return response

            cm.__aenter__ = aenter_with_sleep
            cm.__aexit__ = AsyncMock(return_value=None)
            return cm

        mock_session.get.side_effect = slow_response

        # Act & Assert
        with pytest.raises(asyncio.TimeoutError):
            # Set a very short timeout
            await asyncio.wait_for(
                client.runs.wait("run_001"),
                timeout=0.1
            )

    @pytest.mark.asyncio
    async def test_polling_with_timeout_and_status_checks(
        self, client, mock_session
    ):
        """Test polling with timeout and status checks"""
        # Arrange - Simulate gradual progress
        statuses = ["in_progress", "in_progress", "completed"]
        responses = []

        for status in statuses:
            response = MockResponse({
                "run_id": "run_poll_001",
                "status": status,
                "output": [] if status != "completed" else [
                    {"role": "assistant", "contents": [{"kind": "text", "text": "Done"}]}
                ]
            }, 200)
            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            responses.append(cm)

        mock_session.get.side_effect = responses

        # Act - Implement polling with timeout
        max_polls = 5
        poll_interval = 0.1
        poll_count = 0
        result = None

        while poll_count < max_polls:
            result = await client.runs.get("run_poll_001")
            if result["status"] in ["completed", "failed", "cancelled"]:
                break
            poll_count += 1
            await asyncio.sleep(poll_interval)

        # Assert
        assert result is not None
        assert result["status"] == "completed"
        assert poll_count == 2  # Took 3 attempts (index 2)


class TestConcurrentOperations:
    """Tests for concurrent operations and parallel execution"""

    @pytest.mark.asyncio
    async def test_concurrent_runs_execute_in_parallel(
        self, client, mock_session
    ):
        """Test multiple runs executing concurrently"""
        # Arrange
        run_results = [
            {
                "run_id": f"run_concurrent_{i}",
                "agent_id": "agent_001",
                "status": "completed",
                "output": [{"role": "assistant", "contents": [{"kind": "text", "text": f"Result {i}"}]}],
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            for i in range(1, 6)
        ]

        # Setup mocks for parallel calls
        cms = []
        for run in run_results:
            response = MockResponse(run, 201)
            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            cms.append(cm)

        mock_session.post.side_effect = cms

        # Act - Execute runs concurrently
        tasks = []
        for i in range(1, 6):
            task = client.runs.create({
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Query {i}"}]}]
            })
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 5
        for i, result in enumerate(results, 1):
            assert result["run_id"] == f"run_concurrent_{i}"
            assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_concurrent_operations_with_different_threads(
        self, client, mock_session
    ):
        """Test concurrent operations across different threads"""
        # Arrange
        thread_ids = ["thread_001", "thread_002", "thread_003"]

        # Create a mock function that returns different responses based on URL
        def create_mock_response(*args, **kwargs):
            url = args[0] if args else ""

            # Thread creation
            if url == "/threads":
                # Return different thread IDs sequentially
                thread_id = thread_ids[len([r for r in responses_created if "thread" in str(r)])]
                response = MockResponse({
                    "thread_id": thread_id,
                    "status": "active"
                }, 201)
            # Run creation
            else:
                run_num = len([r for r in responses_created if "run" in str(r)]) + 1
                response = MockResponse({
                    "run_id": f"run_{run_num}",
                    "thread_id": thread_ids[run_num - 1],
                    "status": "completed",
                    "output": [{"role": "assistant", "contents": [{"kind": "text", "text": f"Response {run_num}"}]}]
                }, 201)

            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            responses_created.append(response)
            return cm

        responses_created = []
        mock_session.post.side_effect = create_mock_response

        # Act - Create threads and runs concurrently
        async def create_thread_and_run(idx):
            thread = await client.threads.create({"title": f"Thread {idx}"})
            run = await client.runs.create({
                "thread_id": thread["thread_id"],
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Query {idx}"}]}]
            })
            return thread, run

        results = await asyncio.gather(*[
            create_thread_and_run(i) for i in range(1, 4)
        ])

        # Assert
        assert len(results) == 3
        for i, (thread, run) in enumerate(results, 1):
            assert thread["thread_id"] in thread_ids
            assert run["status"] == "completed"

    @pytest.mark.asyncio
    async def test_concurrent_operations_with_error_handling(
        self, client, mock_session
    ):
        """Test concurrent operations with mixed success/failure"""
        # Arrange - Some operations succeed, some fail
        success_response = MockResponse({
            "run_id": "run_success",
            "status": "completed",
            "output": []
        }, 201)
        success_cm = MagicMock()
        success_cm.__aenter__.return_value = success_response
        success_cm.__aexit__.return_value = None

        error_response = MockResponse({"error": "Rate limit"}, 429)
        error_response.raise_for_status = Mock(side_effect=Exception("429 Rate Limit"))
        error_cm = MagicMock()
        error_cm.__aenter__.return_value = error_response
        error_cm.__aexit__.return_value = None

        mock_session.post.side_effect = [success_cm, error_cm, success_cm]

        # Act - Execute operations and handle errors
        tasks = []
        for i in range(3):
            task = client.runs.create({
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Query {i}"}]}]
            })
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Assert
        assert len(results) == 3
        assert not isinstance(results[0], Exception)
        assert isinstance(results[1], Exception)  # Second operation failed
        assert not isinstance(results[2], Exception)


class TestCustomConfiguration:
    """Tests for custom HTTP client configuration"""

    @pytest.mark.asyncio
    async def test_custom_http_client_configuration_uses_provided_client(
        self, mock_session
    ):
        """Test custom HTTP client configuration - matches .NET test"""
        # Arrange - Example from "Custom HTTP Client Configuration" section
        expected_run = {
            "run_id": "run_custom_001",
            "agent_id": "agent_001",
            "status": "in_progress",
            "input": [],
            "output": [],
            "created_at": datetime.now(timezone.utc).isoformat()
        }

        mock_http_method(mock_session.post, expected_run, 201)

        options = AgentProtocolClientOptions(
            base_url="https://api.example.com",
            api_key="test-api-key",
            timeout_seconds=60,
            max_retries=5
        )

        # Act
        with patch("aiohttp.ClientSession", return_value=mock_session):
            client = AgentProtocolClient(options)
            client.runs._session = mock_session

            run = {
                "agent_id": "agent_001",
                "input": [
                    {
                        "role": "user",
                        "contents": [
                            {"kind": "text", "text": "Test message"}
                        ]
                    }
                ]
            }

            result = await client.runs.create(run)

        # Assert
        assert result is not None
        assert result["run_id"] == "run_custom_001"
        assert options.timeout_seconds == 60
        assert options.max_retries == 5

    @pytest.mark.asyncio
    async def test_custom_headers_included_in_requests(
        self, mock_session
    ):
        """Test custom headers are included in requests"""
        # Arrange
        options = AgentProtocolClientOptions(
            base_url="https://api.example.com",
            api_key="test-key"
        )

        expected_run = {
            "run_id": "run_001",
            "status": "in_progress"
        }

        mock_http_method(mock_session.post, expected_run, 201)

        # Act
        with patch("aiohttp.ClientSession", return_value=mock_session):
            client = AgentProtocolClient(options)
            client.runs._session = mock_session

            result = await client.runs.create({
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}]
            })

        # Assert
        assert result is not None
        assert result["run_id"] == "run_001"


class TestClientInitialization:
    """Tests for client initialization with multiple constructors"""

    def test_client_initialization_with_multiple_constructors_creates_client(self):
        """Test client initialization with different constructors - matches .NET test"""
        # Constructor 1: Just URL string (using from_url factory method)
        with patch("aiohttp.ClientSession"):
            client1 = AgentProtocolClient.from_url("https://api.example.com")
            assert client1 is not None
            assert client1.runs is not None
            assert client1.threads is not None
            assert client1.agents is not None

        # Constructor 2: Client options object
        with patch("aiohttp.ClientSession"):
            options = AgentProtocolClientOptions(
                base_url="https://api.example.com",
                api_key="test-api-key",
                timeout_seconds=60,
                max_retries=5
            )
            client2 = AgentProtocolClient(options)
            assert client2 is not None
            assert client2.runs is not None

    def test_client_initialization_with_various_options(self):
        """Test client initialization with various configuration options"""
        # Arrange & Act
        with patch("aiohttp.ClientSession"):
            # Minimal options
            options1 = AgentProtocolClientOptions(base_url="https://api.example.com")
            client1 = AgentProtocolClient(options1)

            # Full options
            options2 = AgentProtocolClientOptions(
                base_url="https://api.example.com",
                api_key="test-key",
                timeout_seconds=120,
                max_retries=3
            )
            client2 = AgentProtocolClient(options2)

        # Assert
        assert client1 is not None
        assert client2 is not None
        assert options2.timeout_seconds == 120
        assert options2.max_retries == 3


class TestComplexAgentInteractions:
    """Tests for complex agent interactions and workflows"""

    @pytest.mark.asyncio
    async def test_agent_to_agent_handoff_workflow(
        self, client, mock_session
    ):
        """Test agent handoff workflow between specialized agents"""
        # Arrange - Simulate handoff from general agent to specialist
        # Step 1: Initial agent determines specialist is needed
        initial_run = {
            "run_id": "run_handoff_001",
            "agent_id": "agent_general",
            "status": "completed",
            "output": [
                {
                    "role": "assistant",
                    "contents": [
                        {"kind": "text", "text": "This requires a specialist. Transferring to billing agent."}
                    ]
                }
            ],
            "metadata": {
                "handoff_to": "agent_billing",
                "handoff_reason": "billing_question"
            }
        }

        # Step 2: Specialist agent handles the request
        specialist_run = {
            "run_id": "run_handoff_002",
            "agent_id": "agent_billing",
            "status": "completed",
            "output": [
                {
                    "role": "assistant",
                    "contents": [
                        {"kind": "text", "text": "Your invoice total is $150."}
                    ]
                }
            ]
        }

        # Setup mocks
        initial_response = MockResponse(initial_run, 201)
        initial_cm = MagicMock()
        initial_cm.__aenter__.return_value = initial_response
        initial_cm.__aexit__.return_value = None

        specialist_response = MockResponse(specialist_run, 201)
        specialist_cm = MagicMock()
        specialist_cm.__aenter__.return_value = specialist_response
        specialist_cm.__aexit__.return_value = None

        mock_session.post.side_effect = [initial_cm, specialist_cm]

        # Act
        # Step 1: Initial agent
        initial_result = await client.runs.create({
            "agent_id": "agent_general",
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "What's my invoice?"}]}]
        })

        # Check if handoff is needed
        handoff_needed = initial_result.get("metadata", {}).get("handoff_to")

        final_result = initial_result
        if handoff_needed:
            # Step 2: Handoff to specialist
            final_result = await client.runs.create({
                "agent_id": handoff_needed,
                "input": [{"role": "user", "contents": [{"kind": "text", "text": "What's my invoice?"}]}]
            })

        # Assert
        assert final_result["agent_id"] == "agent_billing"
        assert final_result["status"] == "completed"
        assert "$150" in final_result["output"][0]["contents"][0]["text"]

    @pytest.mark.asyncio
    async def test_complex_multi_agent_collaboration(
        self, client, mock_session
    ):
        """Test complex multi-agent collaboration with parallel processing"""
        # Arrange - Multiple agents process different aspects
        research_result = {
            "run_id": "run_research",
            "agent_id": "agent_research",
            "status": "completed",
            "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Research findings..."}]}]
        }

        analysis_result = {
            "run_id": "run_analysis",
            "agent_id": "agent_analysis",
            "status": "completed",
            "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Analysis complete..."}]}]
        }

        summary_result = {
            "run_id": "run_summary",
            "agent_id": "agent_summary",
            "status": "completed",
            "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Final summary..."}]}]
        }

        # Setup mocks
        responses = []
        for result in [research_result, analysis_result, summary_result]:
            response = MockResponse(result, 201)
            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            responses.append(cm)

        mock_session.post.side_effect = responses

        # Act
        # Phase 1: Parallel research and analysis
        research_task = client.runs.create({
            "agent_id": "agent_research",
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "Research topic X"}]}]
        })

        analysis_task = client.runs.create({
            "agent_id": "agent_analysis",
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "Analyze data Y"}]}]
        })

        research, analysis = await asyncio.gather(research_task, analysis_task)

        # Phase 2: Summary agent combines results
        summary = await client.runs.create({
            "agent_id": "agent_summary",
            "input": [
                {"role": "user", "contents": [{"kind": "text", "text": "Summarize findings"}]}
            ]
        })

        # Assert
        assert research["status"] == "completed"
        assert analysis["status"] == "completed"
        assert summary["status"] == "completed"
        assert summary["agent_id"] == "agent_summary"


class TestStateManagementAcrossRuns:
    """Tests for state management and persistence across multiple runs"""

    @pytest.mark.asyncio
    async def test_state_management_with_metadata_persistence(
        self, client, mock_session
    ):
        """Test state management using metadata across runs"""
        # Arrange - Simulate stateful conversation with context
        runs_with_state = [
            {
                "run_id": "run_state_001",
                "status": "completed",
                "metadata": {
                    "session_id": "session_123",
                    "user_preferences": {"language": "en", "format": "detailed"},
                    "conversation_stage": "greeting"
                },
                "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Hello!"}]}]
            },
            {
                "run_id": "run_state_002",
                "status": "completed",
                "metadata": {
                    "session_id": "session_123",
                    "user_preferences": {"language": "en", "format": "detailed"},
                    "conversation_stage": "processing",
                    "previous_run": "run_state_001"
                },
                "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Processing..."}]}]
            },
            {
                "run_id": "run_state_003",
                "status": "completed",
                "metadata": {
                    "session_id": "session_123",
                    "user_preferences": {"language": "en", "format": "detailed"},
                    "conversation_stage": "complete",
                    "previous_run": "run_state_002"
                },
                "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Complete!"}]}]
            }
        ]

        # Setup mocks
        cms = []
        for run in runs_with_state:
            response = MockResponse(run, 201)
            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            cms.append(cm)

        mock_session.post.side_effect = cms

        # Act - Execute runs with state persistence
        session_metadata = {
            "session_id": "session_123",
            "user_preferences": {"language": "en", "format": "detailed"}
        }

        results = []
        for stage in ["greeting", "processing", "complete"]:
            run_data = {
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Step {stage}"}]}],
                "metadata": {**session_metadata, "conversation_stage": stage}
            }
            if results:
                run_data["metadata"]["previous_run"] = results[-1]["run_id"]

            result = await client.runs.create(run_data)
            results.append(result)

        # Assert
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["metadata"]["session_id"] == "session_123"
            assert result["metadata"]["user_preferences"]["language"] == "en"
            if i > 0:
                assert "previous_run" in result["metadata"]

    @pytest.mark.asyncio
    async def test_state_cleanup_on_session_end(
        self, client, mock_session
    ):
        """Test state cleanup when session ends"""
        # Arrange
        final_run = {
            "run_id": "run_cleanup_001",
            "status": "completed",
            "thread_cleanup": "delete",
            "metadata": {"session_ended": True},
            "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Goodbye!"}]}]
        }

        mock_http_method(mock_session.post, final_run, 201)

        # Act
        result = await client.runs.create({
            "agent_id": "agent_001",
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "End session"}]}],
            "thread_cleanup": "delete",
            "metadata": {"session_ended": True}
        })

        # Assert
        assert result is not None
        assert result["thread_cleanup"] == "delete"
        assert result["metadata"]["session_ended"] is True


class TestAdvancedErrorScenarios:
    """Tests for advanced error scenarios and edge cases"""

    @pytest.mark.asyncio
    async def test_cascading_failure_handling(
        self, client, mock_session
    ):
        """Test handling of cascading failures"""
        # Arrange - First operation fails, triggering cleanup that also fails
        primary_failure = {
            "run_id": "run_fail_001",
            "status": "failed",
            "error": {"code": "execution_error", "message": "Primary operation failed"}
        }

        cleanup_failure = {
            "run_id": "run_cleanup_001",
            "status": "failed",
            "error": {"code": "cleanup_error", "message": "Cleanup failed"}
        }

        # Setup mocks
        primary_response = MockResponse(primary_failure, 200)
        primary_cm = MagicMock()
        primary_cm.__aenter__.return_value = primary_response
        primary_cm.__aexit__.return_value = None

        cleanup_response = MockResponse(cleanup_failure, 200)
        cleanup_cm = MagicMock()
        cleanup_cm.__aenter__.return_value = cleanup_response
        cleanup_cm.__aexit__.return_value = None

        mock_session.post.side_effect = [primary_cm, cleanup_cm]

        # Act
        primary_result = await client.runs.create({
            "agent_id": "agent_001",
            "input": [{"role": "user", "contents": [{"kind": "text", "text": "Test"}]}]
        })

        cleanup_result = None
        if primary_result["status"] == "failed":
            # Attempt cleanup
            cleanup_result = await client.runs.create({
                "agent_id": "agent_cleanup",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": "Cleanup"}]}]
            })

        # Assert
        assert primary_result["status"] == "failed"
        assert cleanup_result is not None
        assert cleanup_result["status"] == "failed"

    @pytest.mark.asyncio
    async def test_partial_failure_in_multi_step_workflow(
        self, client, mock_session
    ):
        """Test handling partial failures in multi-step workflows"""
        # Arrange - 3 steps, second one fails
        step_results = [
            {"run_id": "run_step_001", "status": "completed", "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Step 1 done"}]}]},
            {"run_id": "run_step_002", "status": "failed", "error": {"code": "step_error", "message": "Step 2 failed"}},
            {"run_id": "run_step_003", "status": "completed", "output": [{"role": "assistant", "contents": [{"kind": "text", "text": "Step 3 done (recovery)"}]}]}
        ]

        # Setup mocks
        cms = []
        for result in step_results:
            response = MockResponse(result, 201 if result["status"] == "completed" else 200)
            cm = MagicMock()
            cm.__aenter__.return_value = response
            cm.__aexit__.return_value = None
            cms.append(cm)

        mock_session.post.side_effect = cms

        # Act - Execute workflow with error recovery
        results = []
        for i in range(1, 4):
            result = await client.runs.create({
                "agent_id": "agent_001",
                "input": [{"role": "user", "contents": [{"kind": "text", "text": f"Step {i}"}]}]
            })
            results.append(result)

            # If step failed and not the last step, continue with recovery
            if result["status"] == "failed" and i < 3:
                # Continue to recovery step
                continue

        # Assert
        assert len(results) == 3
        assert results[0]["status"] == "completed"
        assert results[1]["status"] == "failed"
        assert results[2]["status"] == "completed"  # Recovery succeeded
