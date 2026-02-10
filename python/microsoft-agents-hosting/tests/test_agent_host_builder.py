# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Tests for AgentHostBuilder."""

import os
import pytest
from typing import Any
from microsoft.agents.hosting import AgentHostBuilder, ConfigurationError
from microsoft.agents.hosting.core import (
    IStateStore,
    IQueueAdapter,
    RateLimitError,
    TimeoutError,
    NetworkError,
    AuthenticationError,
    ValidationError,
)
from microsoft.agents.hosting.state import MemoryStateStore


@pytest.fixture(autouse=True)
def setup_test_env(monkeypatch):
    """Set up test environment variables for all tests."""
    monkeypatch.setenv("FOUNDRY_ENDPOINT", "https://test.api.com")
    monkeypatch.setenv("FOUNDRY_API_KEY", "test-key-123")


class MockStateStore(IStateStore):
    """Mock state store for testing."""

    async def initialize_async(self) -> None:
        """Initialize the store."""
        pass

    async def close_async(self) -> None:
        """Close the store."""
        pass

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
        pass


def test_agent_host_builder_creation():
    """Test creating an AgentHostBuilder."""
    builder = AgentHostBuilder()
    assert builder is not None


def test_agent_host_builder_add_default_agent():
    """Test adding a default agent."""
    builder = AgentHostBuilder()
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    assert builder is not None


def test_agent_host_builder_build_without_agent():
    """Test that build fails without agents."""
    builder = AgentHostBuilder()
    with pytest.raises(ConfigurationError, match="At least one agent must be configured"):
        builder.build()


def test_agent_host_builder_production_defaults():
    """Test enabling production defaults."""
    builder = AgentHostBuilder()
    builder = builder.use_production_defaults()
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_concurrency():
    """Test configuring concurrency."""
    builder = AgentHostBuilder()
    builder = builder.configure_concurrency(
        max_concurrent_requests=200,
        request_timeout=60.0
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_concurrency_all_params():
    """Test configuring concurrency with all parameters."""
    builder = AgentHostBuilder()
    builder = builder.configure_concurrency(
        max_concurrent_runs_per_thread=2,
        max_concurrent_requests=150,
        request_timeout=120.0,
        function_timeout=45.0
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_sandbox():
    """Test configuring sandbox."""
    builder = AgentHostBuilder()
    builder = builder.configure_sandbox(
        max_memory_mb=256,
        allow_network=True
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_sandbox_all_params():
    """Test configuring sandbox with all parameters."""
    builder = AgentHostBuilder()
    builder = builder.configure_sandbox(
        max_memory_mb=1024,
        max_cpu_percent=75.0,
        allow_network=True,
        allow_filesystem_write=True,
        allowed_modules=["os", "sys", "json"]
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_retries():
    """Test configuring retry behavior."""
    builder = AgentHostBuilder()
    builder = builder.configure_retries(
        max_attempts=5,
        backoff_base=3.0
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_retries_with_custom_errors():
    """Test configuring retries with custom error lists."""
    builder = AgentHostBuilder()
    builder = builder.configure_retries(
        max_attempts=3,
        backoff_base=2.0,
        retryable_errors=[RateLimitError, TimeoutError, NetworkError],
        non_retryable_errors=[AuthenticationError, ValidationError]
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_telemetry():
    """Test configuring telemetry."""
    builder = AgentHostBuilder()
    builder = builder.configure_telemetry(
        service_name="test-service",
        sample_rate=0.5
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_telemetry_all_params():
    """Test configuring telemetry with all parameters."""
    builder = AgentHostBuilder()
    builder = builder.configure_telemetry(
        service_name="test-service",
        exporter=None,
        sample_rate=0.75,
        enable_metrics=False,
        enable_tracing=True
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_logging():
    """Test configuring logging."""
    builder = AgentHostBuilder()
    builder = builder.configure_logging(
        level="DEBUG",
        format="json"
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_configure_logging_all_params():
    """Test configuring logging with all parameters."""
    builder = AgentHostBuilder()
    builder = builder.configure_logging(
        level="WARN",
        format="text",
        handlers=None,
        include_request_id=False,
        include_thread_id=False,
        mask_secrets=False
    )
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_use_state_store():
    """Test using custom state store."""
    builder = AgentHostBuilder()
    store = MockStateStore()
    builder = builder.use_state_store(store)
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_use_queue_adapter():
    """Test using custom queue adapter."""
    builder = AgentHostBuilder()
    adapter = MockQueueAdapter()
    builder = builder.use_queue_adapter(adapter)
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = builder.build()
    assert host is not None


def test_agent_host_builder_immutability():
    """Test that builder is immutable."""
    builder1 = AgentHostBuilder()
    builder2 = builder1.use_production_defaults()
    builder3 = builder2.configure_concurrency(max_concurrent_requests=100)

    # Each should be a different instance
    assert builder1 is not builder2
    assert builder2 is not builder3


def test_agent_host_builder_chaining():
    """Test chaining multiple configuration methods."""
    builder = (
        AgentHostBuilder()
        .use_production_defaults()
        .configure_concurrency(max_concurrent_requests=200)
        .configure_retries(max_attempts=5)
        .configure_telemetry(service_name="test")
        .configure_logging(level="INFO")
        .configure_sandbox(max_memory_mb=1024)
        .use_state_store(MockStateStore())
        .use_queue_adapter(MockQueueAdapter())
        .add_default_agent(lambda agent: agent.use_llm("gpt-4", "You are helpful."))
    )
    host = builder.build()
    assert host is not None


@pytest.mark.asyncio
async def test_agent_host_builder_build_async():
    """Test building host asynchronously."""
    builder = AgentHostBuilder()
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = await builder.build_async()
    assert host is not None


@pytest.mark.asyncio
async def test_agent_host_builder_build_async_with_custom_stores():
    """Test building host asynchronously with custom stores."""
    builder = AgentHostBuilder()
    builder = builder.use_state_store(MockStateStore())
    builder = builder.use_queue_adapter(MockQueueAdapter())
    builder = builder.add_default_agent(
        lambda agent: agent.use_llm("gpt-4", "You are helpful.")
    )
    host = await builder.build_async()
    assert host is not None


@pytest.mark.asyncio
async def test_memory_queue_adapter_enqueue():
    """Test MemoryQueueAdapter enqueue_async method."""
    from microsoft.agents.hosting.builder.agent_host_builder import MemoryQueueAdapter

    adapter = MemoryQueueAdapter()
    await adapter.initialize_async()
    await adapter.enqueue_async({"message": "test"})
    # Should complete without error
    assert True


@pytest.mark.asyncio
async def test_memory_queue_adapter_dequeue():
    """Test MemoryQueueAdapter dequeue_async method."""
    from microsoft.agents.hosting.builder.agent_host_builder import MemoryQueueAdapter

    adapter = MemoryQueueAdapter()
    result = await adapter.dequeue_async()
    assert result is None


@pytest.mark.asyncio
async def test_memory_queue_adapter_close():
    """Test MemoryQueueAdapter close_async method."""
    from microsoft.agents.hosting.builder.agent_host_builder import MemoryQueueAdapter

    adapter = MemoryQueueAdapter()
    await adapter.close_async()
    # Should complete without error
    assert True
