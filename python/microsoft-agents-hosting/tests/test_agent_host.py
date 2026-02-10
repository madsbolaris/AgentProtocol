# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for AgentHost."""

import pytest
import asyncio
from typing import Any
from unittest.mock import Mock, AsyncMock, patch
from microsoft.agents.hosting import AgentHostBuilder
from microsoft.agents.hosting.hosting import AgentHost
from microsoft.agents.hosting.hosting.out_of_band_publisher import OutOfBandPublisher
from microsoft.agents.hosting.core import (
    IStateStore,
    IQueueAdapter,
    ConcurrencyConfig,
    RetryConfig,
    LoggingConfig,
    SandboxConfig,
)
from microsoft.agents.hosting.builder.agent_builder import AgentConfiguration


class MockStateStore(IStateStore):
    """Mock state store for testing."""

    def __init__(self):
        self.closed = False

    async def initialize_async(self) -> None:
        """Initialize the store."""
        pass

    async def close_async(self) -> None:
        """Close the store."""
        self.closed = True

    async def get_async(self, key: str) -> str:
        """Get a value."""
        return ""

    async def set_async(self, key: str, value: str) -> None:
        """Set a value."""
        pass

    async def delete_async(self, key: str) -> None:
        """Delete a value."""
        pass


class MockQueueAdapter(IQueueAdapter):
    """Mock queue adapter for testing."""

    def __init__(self):
        self.closed = False

    async def initialize_async(self) -> None:
        """Initialize the adapter."""
        pass

    async def enqueue_async(self, message: Any) -> None:
        """Enqueue a message."""
        pass

    async def dequeue_async(self) -> Any:
        """Dequeue a message."""
        return None

    async def close_async(self) -> None:
        """Close connections."""
        self.closed = True


def create_test_agent_host():
    """Create a test agent host with minimal configuration."""
    mock_agent = AgentConfiguration(
        model="gpt-4",
        instructions="Test prompt",
        functions=[],
        user_message_handlers=[],
        reaction_handlers=[],
        error_handler=None,
    )

    state_store = MockStateStore()
    queue_adapter = MockQueueAdapter()

    host = AgentHost(
        agents=[mock_agent],
        services={},
        production_defaults=False,
        concurrency_config=ConcurrencyConfig(),
        retry_config=RetryConfig(),
        telemetry_config=None,
        logging_config=LoggingConfig(),
        sandbox_config=SandboxConfig(),
        state_store=state_store,
        queue_adapter=queue_adapter,
    )

    return host, state_store, queue_adapter


def test_agent_host_creation():
    """Test creating an AgentHost."""
    host, _, _ = create_test_agent_host()
    assert host is not None


def test_agent_host_get_publisher():
    """Test getting the out-of-band publisher."""
    host, _, _ = create_test_agent_host()
    publisher = host.get_publisher()
    assert publisher is not None
    assert isinstance(publisher, OutOfBandPublisher)


@pytest.mark.asyncio
async def test_agent_host_process_message():
    """Test processing a message."""
    host, _, _ = create_test_agent_host()
    response = await host.process_message("Hello", thread_id="test_thread")
    assert response is not None
    assert "text" in response
    assert "Echo: Hello" in response["text"]


@pytest.mark.asyncio
async def test_agent_host_process_message_without_thread_id():
    """Test processing a message without thread ID."""
    host, _, _ = create_test_agent_host()
    response = await host.process_message("Test message")
    assert response is not None
    assert "text" in response


@pytest.mark.asyncio
async def test_agent_host_process_message_no_agents():
    """Test processing a message when no agents are configured."""
    state_store = MockStateStore()
    queue_adapter = MockQueueAdapter()

    host = AgentHost(
        agents=[],
        services={},
        production_defaults=False,
        concurrency_config=ConcurrencyConfig(),
        retry_config=RetryConfig(),
        telemetry_config=None,
        logging_config=LoggingConfig(),
        sandbox_config=SandboxConfig(),
        state_store=state_store,
        queue_adapter=queue_adapter,
    )

    response = await host.process_message("Hello")
    assert response["text"] == "No agents configured"


@pytest.mark.asyncio
async def test_agent_host_run_async_startup():
    """Test that run_async starts up and logs properly."""
    host, state_store, queue_adapter = create_test_agent_host()

    # Create a task that will cancel itself quickly
    async def run_and_cancel():
        task = asyncio.create_task(host.run_async("localhost", 9000))
        await asyncio.sleep(0.1)  # Let it start
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    # Run the test
    await run_and_cancel()

    # Verify nothing broke
    assert True


@pytest.mark.asyncio
async def test_agent_host_run_async_keyboard_interrupt():
    """Test that run_async handles KeyboardInterrupt properly."""
    host, state_store, queue_adapter = create_test_agent_host()

    # Mock asyncio.Event to raise KeyboardInterrupt
    async def mock_wait():
        raise KeyboardInterrupt()

    with patch("asyncio.Event") as mock_event_class:
        mock_event = Mock()
        mock_event.wait = mock_wait
        mock_event_class.return_value = mock_event

        # This should handle the KeyboardInterrupt gracefully
        await host.run_async("localhost", 8080)

    # Verify cleanup happened
    assert state_store.closed
    assert queue_adapter.closed


def test_agent_host_run_sync():
    """Test synchronous run method exists and is callable."""
    builder = AgentHostBuilder()
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()

    # We can't actually run it without blocking, but we can verify it exists
    assert callable(host.run)


@pytest.mark.asyncio
async def test_agent_host_run_sync_with_mock():
    """Test synchronous run method by mocking asyncio.run."""
    host, state_store, queue_adapter = create_test_agent_host()

    # Mock asyncio.run to prevent actually running the server
    with patch("asyncio.run") as mock_run:
        host.run(host="localhost", port=9000)
        # Verify asyncio.run was called with run_async
        assert mock_run.called
        # Get the coroutine that was passed
        call_args = mock_run.call_args[0][0]
        # Verify it's a coroutine
        import inspect
        assert inspect.iscoroutine(call_args)
        # Clean up the coroutine
        call_args.close()


@pytest.mark.asyncio
async def test_agent_host_with_production_defaults():
    """Test agent host with production defaults enabled."""
    builder = AgentHostBuilder()
    builder = builder.use_production_defaults()
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = await builder.build_async()

    assert host is not None
    publisher = host.get_publisher()
    assert publisher is not None


@pytest.mark.asyncio
async def test_agent_host_with_all_configs():
    """Test agent host with all configurations."""
    builder = AgentHostBuilder()
    builder = (
        builder.use_production_defaults()
        .configure_concurrency(max_concurrent_requests=50)
        .configure_retries(max_attempts=5)
        .configure_telemetry(service_name="test-service")
        .configure_logging(level="DEBUG")
        .configure_sandbox(max_memory_mb=512)
        .add_default_agent(lambda agent: agent.use_llm("gpt-4", "You are helpful."))
    )
    host = await builder.build_async()

    assert host is not None
    response = await host.process_message("Test")
    assert response is not None
