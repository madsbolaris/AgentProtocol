# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Core types and protocols for the hosting SDK."""

from typing import Protocol, Any, Optional, Awaitable, Callable, runtime_checkable
from dataclasses import dataclass, field
from datetime import datetime

# Import protocol types from microsoft-agents-abstractions
try:
    from microsoft.agents.models.chat_message import ChatMessage
    from microsoft.agents.models.user_message import UserMessage
    from microsoft.agents.models.agent_message import AgentMessage
    from microsoft.agents.models.a_i_content import AIContent
    from microsoft.agents.models.a_i_tool import AITool
    from microsoft.agents.models.text_content import TextContent
    from microsoft.agents.models.message_reaction import MessageReaction
except (ImportError, SyntaxError) as e:
    # If abstractions package has issues, create placeholder types
    # This allows development to continue while the abstractions package is being fixed
    import warnings
    warnings.warn(f"Could not import from microsoft.agents.models: {e}. Using placeholder types.")

    from typing import Protocol, runtime_checkable
    from dataclasses import dataclass

    @dataclass
    class ChatMessage:
        """Placeholder ChatMessage type."""
        message_id: str
        text: Optional[str] = None

    @dataclass
    class UserMessage(ChatMessage):
        """Placeholder UserMessage type."""
        pass

    @dataclass
    class AgentMessage(ChatMessage):
        """Placeholder AgentMessage type."""
        pass

    @dataclass
    class MessageReaction:
        """Placeholder MessageReaction type."""
        type: str

    class AIContent:
        """Placeholder AIContent type."""
        pass

    class AITool:
        """Placeholder AITool type."""
        pass

    class TextContent:
        """Placeholder TextContent type."""
        pass


class CancellationToken:
    """Token for cancelling async operations."""

    def __init__(self) -> None:
        self._cancelled = False

    def cancel(self) -> None:
        """Cancel the operation."""
        self._cancelled = True

    def is_cancelled(self) -> bool:
        """Check if the operation is cancelled."""
        return self._cancelled


@runtime_checkable
class IThreadState(Protocol):
    """Interface for managing thread state."""

    async def get_async(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        ...

    async def set_async(self, key: str, value: Any) -> None:
        """Set a state value."""
        ...

    async def delete_async(self, key: str) -> None:
        """Delete a state value."""
        ...

    async def get_all_async(self) -> dict[str, Any]:
        """Get all state."""
        ...

    async def clear_async(self) -> None:
        """Clear all state."""
        ...


@runtime_checkable
class IAgentContext(Protocol):
    """Context for agent turn processing."""

    @property
    def run_id(self) -> str:
        """Gets the current run ID."""
        ...

    @property
    def thread_id(self) -> str:
        """Gets the current thread ID."""
        ...

    @property
    def state(self) -> IThreadState:
        """Gets the state manager for this thread."""
        ...

    async def respond_async(
        self, content: str, cancellation_token: Optional[CancellationToken] = None
    ) -> None:
        """Send a response message to the user."""
        ...

    async def log_async(
        self,
        message: str,
        level: str = "INFO",
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """Log a message for debugging/observability."""
        ...

    async def pause_for_approval_async(
        self,
        summary: str,
        metadata: Optional[dict[str, Any]] = None,
        cancellation_token: Optional[CancellationToken] = None,
    ) -> None:
        """Pause the run and wait for approval before continuing."""
        ...


@runtime_checkable
class IStateStore(Protocol):
    """Interface for state storage backends."""

    async def initialize_async(self) -> None:
        """Initialize the state store (connect to database, etc.)."""
        ...

    async def get_async(self, thread_id: str, key: str) -> Optional[Any]:
        """Get a value from thread state."""
        ...

    async def set_async(
        self, thread_id: str, key: str, value: Any, ttl: Optional[int] = None
    ) -> None:
        """Set a value in thread state with optional TTL in seconds."""
        ...

    async def delete_async(self, thread_id: str, key: str) -> None:
        """Delete a value from thread state."""
        ...

    async def get_all_async(self, thread_id: str) -> dict[str, Any]:
        """Get all state for a thread."""
        ...

    async def clear_async(self, thread_id: str) -> None:
        """Clear all state for a thread."""
        ...

    async def close_async(self) -> None:
        """Close connections and clean up resources."""
        ...


@runtime_checkable
class IQueueAdapter(Protocol):
    """Interface for message queue adapters."""

    async def initialize_async(self) -> None:
        """Initialize the queue adapter."""
        ...

    async def enqueue_async(self, message: Any) -> None:
        """Enqueue a message."""
        ...

    async def dequeue_async(self) -> Optional[Any]:
        """Dequeue a message."""
        ...

    async def close_async(self) -> None:
        """Close connections and clean up resources."""
        ...


@dataclass
class FunctionDefinition:
    """Definition of a function/tool."""

    name: str
    description: str
    implementation: Callable[..., str] | Callable[..., Awaitable[str]]
    parameters: dict[str, type]
    timeout: float = 30.0
    require_approval: bool = False


@dataclass
class ConcurrencyConfig:
    """Configuration for concurrency limits."""

    max_concurrent_runs_per_thread: int = 1
    max_concurrent_requests: int = 100
    request_timeout: float = 300.0
    function_timeout: float = 30.0


@dataclass
class SandboxConfig:
    """Configuration for function sandboxing."""

    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    allow_network: bool = False
    allow_filesystem_write: bool = False
    allowed_modules: list[str] = field(default_factory=list)


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    backoff_base: float = 2.0
    retryable_errors: list[type[Exception]] = field(default_factory=list)
    non_retryable_errors: list[type[Exception]] = field(default_factory=list)


@dataclass
class TelemetryConfig:
    """Configuration for OpenTelemetry."""

    service_name: str
    exporter: Optional[Any] = None
    sample_rate: float = 1.0
    enable_metrics: bool = True
    enable_tracing: bool = True


@dataclass
class LoggingConfig:
    """Configuration for structured logging."""

    level: str = "INFO"
    format: str = "json"
    handlers: Optional[list[Any]] = None
    include_request_id: bool = True
    include_thread_id: bool = True
    mask_secrets: bool = True


@dataclass
class FailedMessage:
    """A message that failed processing."""

    message_id: str
    thread_id: str
    content: str
    error: str
    retry_count: int
    failed_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DLQConfig:
    """Configuration for dead letter queue."""

    max_size: int = 10000
    retention_days: int = 7
    alert_threshold: int = 100
    storage_backend: str = "sql"


# Type aliases for handlers
UserMessageHandler = Callable[
    [UserMessage, IAgentContext, Optional[CancellationToken]], Awaitable[Any]
]
ReactionHandler = Callable[
    [MessageReaction, IAgentContext, Optional[CancellationToken]], Awaitable[Any]
]
ErrorHandler = Callable[
    [Exception, IAgentContext, Optional[CancellationToken]], Awaitable[Any]
]


# Default allowed modules for sandboxing
DEFAULT_ALLOWED_MODULES = [
    "datetime",
    "json",
    "math",
    "random",
    "re",
    "string",
    "collections",
    "itertools",
    "functools",
    "typing",
]
