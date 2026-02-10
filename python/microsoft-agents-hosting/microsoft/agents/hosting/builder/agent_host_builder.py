# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Agent host builder for creating agent hosts."""

import asyncio
from typing import Callable, Optional, Any

from ..core import (
    IStateStore,
    IQueueAdapter,
    ConcurrencyConfig,
    RetryConfig,
    TelemetryConfig,
    LoggingConfig,
    SandboxConfig,
    ConfigurationError,
    RateLimitError,
    TimeoutError,
    NetworkError,
    AuthenticationError,
    ValidationError,
    DEFAULT_ALLOWED_MODULES,
)
from ..state import MemoryStateStore
from ..hosting import AgentHost
from .agent_builder import AgentBuilder


class MemoryQueueAdapter(IQueueAdapter):
    """Simple in-memory queue adapter."""

    async def initialize_async(self) -> None:
        """Initialize the queue adapter."""
        pass

    async def enqueue_async(self, message: Any) -> None:
        """Enqueue a message."""
        pass

    async def dequeue_async(self) -> Optional[Any]:
        """Dequeue a message."""
        return None

    async def close_async(self) -> None:
        """Close connections."""
        pass


class AgentHostBuilder:
    """Builder for configuring an Agent Protocol host."""

    def __init__(self) -> None:
        """Initialize a new agent host builder."""
        self._agent_configurations: list[Callable[[AgentBuilder], AgentBuilder]] = []
        self._services: dict[type, Any] = {}
        self._production_defaults: bool = False
        self._concurrency_config: Optional[ConcurrencyConfig] = None
        self._retry_config: Optional[RetryConfig] = None
        self._telemetry_config: Optional[TelemetryConfig] = None
        self._logging_config: Optional[LoggingConfig] = None
        self._state_store: Optional[IStateStore] = None
        self._queue_adapter: Optional[IQueueAdapter] = None
        self._sandbox_config: SandboxConfig = SandboxConfig(
            allowed_modules=DEFAULT_ALLOWED_MODULES.copy()
        )

    def add_default_agent(
        self, configure: Callable[[AgentBuilder], AgentBuilder]
    ) -> "AgentHostBuilder":
        """
        Add a default agent with the specified configuration.

        Args:
            configure: A function that configures an AgentBuilder.

        Returns:
            A new AgentHostBuilder with the agent added.

        Example:
            ```python
            builder.add_default_agent(lambda agent: agent
                .use_llm("gpt-4", "You are helpful.")
            )
            ```
        """
        new_builder = self._copy()
        new_builder._agent_configurations = self._agent_configurations + [configure]
        return new_builder

    def use_production_defaults(self) -> "AgentHostBuilder":
        """
        Configure production defaults (logging, retries, queues, etc.).

        Returns:
            A new AgentHostBuilder with production defaults enabled.
        """
        new_builder = self._copy()
        new_builder._production_defaults = True
        return new_builder

    def configure_concurrency(
        self,
        max_concurrent_runs_per_thread: int = 1,
        max_concurrent_requests: int = 100,
        request_timeout: float = 300.0,
        function_timeout: float = 30.0,
    ) -> "AgentHostBuilder":
        """
        Configure concurrency limits and timeouts.

        Args:
            max_concurrent_runs_per_thread: Maximum concurrent runs per thread (default: 1).
            max_concurrent_requests: Maximum total concurrent requests (default: 100).
            request_timeout: Maximum time for a request in seconds (default: 300).
            function_timeout: Maximum time for a function execution in seconds (default: 30).

        Returns:
            A new AgentHostBuilder with concurrency configured.
        """
        new_builder = self._copy()
        new_builder._concurrency_config = ConcurrencyConfig(
            max_concurrent_runs_per_thread=max_concurrent_runs_per_thread,
            max_concurrent_requests=max_concurrent_requests,
            request_timeout=request_timeout,
            function_timeout=function_timeout,
        )
        return new_builder

    def configure_sandbox(
        self,
        max_memory_mb: int = 512,
        max_cpu_percent: float = 50.0,
        allow_network: bool = False,
        allow_filesystem_write: bool = False,
        allowed_modules: Optional[list[str]] = None,
    ) -> "AgentHostBuilder":
        """
        Configure function sandboxing for security.

        Args:
            max_memory_mb: Maximum memory per function in MB (default: 512).
            max_cpu_percent: Maximum CPU usage per function (default: 50%).
            allow_network: Allow network access (default: False).
            allow_filesystem_write: Allow filesystem writes (default: False).
            allowed_modules: List of allowed import modules (default: safe stdlib).

        Returns:
            A new AgentHostBuilder with sandbox configured.
        """
        new_builder = self._copy()
        new_builder._sandbox_config = SandboxConfig(
            max_memory_mb=max_memory_mb,
            max_cpu_percent=max_cpu_percent,
            allow_network=allow_network,
            allow_filesystem_write=allow_filesystem_write,
            allowed_modules=allowed_modules or DEFAULT_ALLOWED_MODULES.copy(),
        )
        return new_builder

    def configure_retries(
        self,
        max_attempts: int = 3,
        backoff_base: float = 2.0,
        retryable_errors: Optional[list[type[Exception]]] = None,
        non_retryable_errors: Optional[list[type[Exception]]] = None,
    ) -> "AgentHostBuilder":
        """
        Configure retry behavior for transient failures.

        Args:
            max_attempts: Maximum retry attempts (default: 3).
            backoff_base: Exponential backoff base in seconds (default: 2.0).
            retryable_errors: List of exception types to retry.
            non_retryable_errors: List of exception types to never retry.

        Returns:
            A new AgentHostBuilder with retry configured.
        """
        new_builder = self._copy()
        new_builder._retry_config = RetryConfig(
            max_attempts=max_attempts,
            backoff_base=backoff_base,
            retryable_errors=retryable_errors
            or [RateLimitError, TimeoutError, NetworkError],
            non_retryable_errors=non_retryable_errors
            or [AuthenticationError, ValidationError],
        )
        return new_builder

    def configure_telemetry(
        self,
        service_name: str,
        exporter: Optional[Any] = None,
        sample_rate: float = 1.0,
        enable_metrics: bool = True,
        enable_tracing: bool = True,
    ) -> "AgentHostBuilder":
        """
        Configure OpenTelemetry observability.

        Args:
            service_name: Name of this service for telemetry.
            exporter: OpenTelemetry exporter (OTLP, Jaeger, etc.).
            sample_rate: Trace sampling rate (0.0 to 1.0).
            enable_metrics: Enable metrics collection.
            enable_tracing: Enable distributed tracing.

        Returns:
            A new AgentHostBuilder with telemetry configured.
        """
        new_builder = self._copy()
        new_builder._telemetry_config = TelemetryConfig(
            service_name=service_name,
            exporter=exporter,
            sample_rate=sample_rate,
            enable_metrics=enable_metrics,
            enable_tracing=enable_tracing,
        )
        return new_builder

    def configure_logging(
        self,
        level: str = "INFO",
        format: str = "json",
        handlers: Optional[list[Any]] = None,
        include_request_id: bool = True,
        include_thread_id: bool = True,
        mask_secrets: bool = True,
    ) -> "AgentHostBuilder":
        """
        Configure structured logging.

        Args:
            level: Log level (DEBUG, INFO, WARN, ERROR).
            format: Log format ("json" or "text").
            handlers: Custom log handlers (default: stdout).
            include_request_id: Include request ID in logs.
            include_thread_id: Include thread ID in logs.
            mask_secrets: Mask API keys and secrets in logs.

        Returns:
            A new AgentHostBuilder with logging configured.
        """
        new_builder = self._copy()
        new_builder._logging_config = LoggingConfig(
            level=level,
            format=format,
            handlers=handlers,
            include_request_id=include_request_id,
            include_thread_id=include_thread_id,
            mask_secrets=mask_secrets,
        )
        return new_builder

    def use_state_store(self, store: IStateStore) -> "AgentHostBuilder":
        """
        Configure state storage backend.

        Args:
            store: State store implementation.

        Returns:
            A new AgentHostBuilder with state store configured.
        """
        new_builder = self._copy()
        new_builder._state_store = store
        return new_builder

    def use_queue_adapter(self, adapter: IQueueAdapter) -> "AgentHostBuilder":
        """
        Configure message queue adapter.

        Args:
            adapter: Queue adapter implementation.

        Returns:
            A new AgentHostBuilder with queue configured.
        """
        new_builder = self._copy()
        new_builder._queue_adapter = adapter
        return new_builder

    async def build_async(self) -> AgentHost:
        """
        Build the configured agent host asynchronously.

        Returns:
            An AgentHost instance ready to run.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        # Validate configuration
        if not self._agent_configurations:
            raise ConfigurationError("At least one agent must be configured")

        # Build agents
        agents = []
        for configure in self._agent_configurations:
            agent_builder = AgentBuilder(self._services)
            configured = configure(agent_builder)
            agents.append(configured._build())

        # Initialize services
        state_store = self._state_store or MemoryStateStore()
        await state_store.initialize_async()

        queue_adapter = self._queue_adapter or MemoryQueueAdapter()
        await queue_adapter.initialize_async()

        # Create host
        return AgentHost(
            agents=agents,
            services=self._services,
            production_defaults=self._production_defaults,
            concurrency_config=self._concurrency_config or ConcurrencyConfig(),
            retry_config=self._retry_config or RetryConfig(),
            telemetry_config=self._telemetry_config,
            logging_config=self._logging_config or LoggingConfig(),
            sandbox_config=self._sandbox_config,
            state_store=state_store,
            queue_adapter=queue_adapter,
        )

    def build(self) -> AgentHost:
        """
        Build the configured agent host synchronously.

        Returns:
            An AgentHost instance ready to run.
        """
        return asyncio.run(self.build_async())

    def _copy(self) -> "AgentHostBuilder":
        """Create a copy of this builder."""
        new_builder = AgentHostBuilder()
        new_builder._agent_configurations = self._agent_configurations.copy()
        new_builder._services = self._services.copy()
        new_builder._production_defaults = self._production_defaults
        new_builder._concurrency_config = self._concurrency_config
        new_builder._retry_config = self._retry_config
        new_builder._telemetry_config = self._telemetry_config
        new_builder._logging_config = self._logging_config
        new_builder._sandbox_config = self._sandbox_config
        new_builder._state_store = self._state_store
        new_builder._queue_adapter = self._queue_adapter
        return new_builder
