"""
Tests for all Hosting SDK Quickstart Guide samples (Python)

These tests demonstrate the intended API design for the Hosting SDK as described
in the quickstart documentation, using mocks to simulate the AgentHost behavior.
"""

import pytest
import asyncio
import time
import httpx
import os
from unittest.mock import AsyncMock, Mock, patch, MagicMock, call
from typing import AsyncIterable, Callable, Awaitable, TypeAlias, TypeVar
from datetime import datetime, timezone

# Import protocol models from the abstractions package
from microsoft.agents.models import (
    TextContent,
    ImageContent,
    ChatMessage,
    UserMessage,
    AgentMessage,
    DeveloperMessage,
    MessageReactionContent,
    MessageReaction,
    Thread,
)


# Mock classes to represent the intended Hosting SDK API
class AgentConfig:
    """Mock AgentConfig class representing the intended API"""
    def __init__(
        self,
        model: str,
        instructions: str,
        api_key: str,
        functions: list = None,
        allow_client_functions: bool = False,
        middleware: list = None,
        storage=None
    ):
        self.model = model
        self.instructions = instructions
        self.api_key = api_key
        self.functions = functions or []
        self.allow_client_functions = allow_client_functions
        self.middleware = middleware or []
        self.storage = storage


class AgentHost:
    """Mock AgentHost class representing the intended API"""
    def __init__(self, config: AgentConfig):
        self.config = config
        self._server = None

    def run(self, port: int = 5000):
        """Start the server"""
        pass

    async def process_message(self, message: str, thread: Thread = None) -> str:
        """Process a message through the agent"""
        pass


class InMemoryStorage:
    """Mock in-memory storage"""
    def __init__(self):
        self.threads = {}


class SqlStorageProvider:
    """Mock SQL storage provider"""
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.threads = {}


class IStreamable:
    """Base interface for streamable content"""
    pass


# Type aliases for middleware signatures
T = TypeVar('T', bound='IStreamable')

# Simple middleware (default case - 80%)
Middleware: TypeAlias = Callable[
    [AsyncIterable[T], Thread],
    AsyncIterable[IStreamable]
]

# Chained middleware (advanced case - 20%)
ChainedMiddleware: TypeAlias = Callable[
    [AsyncIterable[T], Thread, Callable[[AsyncIterable[IStreamable]], Awaitable[AsyncIterable[T]]]],
    Awaitable[AsyncIterable[IStreamable]]
]

MessageMiddleware: TypeAlias = Callable[[ChatMessage, Thread, Callable[[], Awaitable[None]]], Awaitable[None]]


class TestHostingQuickstartSamples:
    """Tests for all Python Hosting SDK Quickstart samples"""

    # ========================================================================
    # Step 1: Hello World
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-hello-world")
    async def test_step1_hello_world(self):
        """Test basic agent setup from Step 1"""
        # Arrange - Example from quickstart
        # <snippet>
        from dotenv import load_dotenv
        import os

        load_dotenv()

        config = AgentConfig(
            model="gpt-4",
            instructions="You are a helpful assistant.",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        agent = AgentHost(config)

        if __name__ == "__main__":
            agent.run()  # Starts server on http://localhost:5000
        # </snippet>

        # Assert - Verify configuration
        assert agent.config.model == "gpt-4"
        assert agent.config.instructions == "You are a helpful assistant."
        assert agent.config.api_key == "test-api-key"
        assert len(agent.config.functions) == 0
        assert agent.config.allow_client_functions is False

    # ========================================================================
    # Step 2: Adding Tools
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-adding-tools")
    async def test_step2_adding_tools(self):
        """Test adding tool functions from Step 2"""
        # Arrange - Define tools as shown in quickstart
        # <snippet>
        def get_weather(location: str) -> str:
            """Get current weather for a location"""
            return f"The weather in {location} is sunny and 72°F"

        def get_time() -> str:
            """Get current time in UTC"""
            return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        config = AgentConfig(
            model="gpt-4",
            instructions="You are a helpful assistant.",
            api_key=os.getenv("OPENAI_API_KEY"),
            functions=[get_weather, get_time]
        )

        agent = AgentHost(config)
        # </snippet>

        # Assert - Verify tools are registered
        assert len(agent.config.functions) == 2
        assert agent.config.functions[0] == get_weather
        assert agent.config.functions[1] == get_time

        # Test tool execution
        weather_result = get_weather("Seattle")
        assert "Seattle" in weather_result
        assert "sunny" in weather_result
        assert "72°F" in weather_result

        time_result = get_time()
        assert "UTC" in time_result

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-tool-error-handling")
    async def test_step2_tool_error_handling(self):
        """Test tool error handling with httpx.HTTPError"""
        # Arrange - Define async tool with error handling (example from quickstart)
        # <snippet>
        async def get_weather(location: str) -> str:
            """Get current weather for a location"""
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"https://api.weather.com/v1/current",
                        params={"location": location}
                    )
                    response.raise_for_status()
                    return f"Weather in {location}: {response.json()['temp']}°F"
            except httpx.HTTPError as e:
                # Return error message - LLM will explain to user
                return f"Sorry, couldn't fetch weather: {str(e)}"
        # </snippet>

        # Act & Assert - Test error handling with mocked HTTP error
        with patch('httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=httpx.HTTPError("Connection timeout")
            )

            result = await get_weather("Seattle")
            assert "couldn't fetch weather" in result
            assert "Connection timeout" in result

    # ========================================================================
    # Step 3: Client-Provided Functions
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-client-functions")
    async def test_step3_client_provided_functions(self):
        """Test enabling client-provided functions from Step 3"""
        # Arrange - Example from quickstart
        # <snippet>
        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            allow_client_functions=True  # Enable client functions
        )

        agent = AgentHost(config)
        # </snippet>

        # Assert - Verify client functions are enabled
        assert agent.config.allow_client_functions is True

    # ========================================================================
    # Step 4: Command Router Middleware
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-command-router")
    async def test_step4_command_router_middleware(self):
        """Test command router middleware with async generator"""
        # Arrange - Define command router middleware (example from quickstart)
        # <snippet>
        async def command_router(
            content: TextContent,
            thread: Thread
        ):
            # Check if it's the /help command
            if content.text.strip() == "/help":
                # Handle command - return result without calling LLM
                yield TextContent(text="Available commands:\n/help - Show this help")
            else:
                # Pass through to LLM
                yield content

        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            middleware=[
                (TextContent, command_router)
            ]
        )

        agent = AgentHost(config)
        # </snippet>

        # Assert - Verify middleware is registered
        assert len(agent.config.middleware) == 1
        assert agent.config.middleware[0][0] == TextContent
        assert agent.config.middleware[0][1] == command_router

        # Act - Test command routing
        mock_thread = Thread(
            thread_id="thread_123",
            created_at=datetime.now(timezone.utc)
        )
        help_content = TextContent(text="/help")

        results = []
        async for item in command_router(help_content, mock_thread):
            results.append(item)

        # Assert - Command was intercepted
        assert len(results) == 1
        assert isinstance(results[0], TextContent)
        assert "Available commands" in results[0].text

        # Act - Test pass-through
        normal_content = TextContent(text="Hello, how are you?")
        results = []
        async for item in command_router(normal_content, mock_thread):
            results.append(item)

        # Assert - Content passed through
        assert len(results) == 1
        assert results[0] == normal_content

    # ========================================================================
    # Step 4: Reaction Handler Middleware
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-reaction-handler")
    async def test_step4_reaction_handler_middleware(self):
        """Test reaction handler middleware for MessageReactionContent"""
        # Arrange - Define reaction handler (example from quickstart)
        # <snippet>
        async def handle_reactions(
            reaction: MessageReactionContent,
            thread: Thread
        ):
            # Convert reaction to a message the agent can understand
            emoji = reaction.reactions_added[0].type if reaction.reactions_added else "unknown"
            developer_msg = DeveloperMessage(
                message_id="msg_dev",
                contents=[
                    TextContent(text=f"User reacted with {emoji} to a previous message.")
                ]
            )
            yield reaction
            yield developer_msg  # Yield so LLM can process the notification

        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            middleware=[
                (MessageReactionContent, handle_reactions),
            ]
        )

        agent = AgentHost(config)
        # </snippet>

        # Assert - Verify middleware is registered
        assert len(agent.config.middleware) == 1

        # Act - Test reaction handling
        mock_thread = Thread(
            thread_id="thread_123",
            created_at=datetime.now(timezone.utc)
        )
        reaction = MessageReactionContent(
            referenced_message_id="msg_001",
            reactions_added=[MessageReaction(type="👍")]
        )

        results = []
        async for item in handle_reactions(reaction, mock_thread):
            results.append(item)

        # Assert - Reaction was processed and developer message was yielded
        assert len(results) == 2
        assert results[0] == reaction
        assert isinstance(results[1], DeveloperMessage)
        assert "reacted with 👍" in results[1].contents[0].text

    # ========================================================================
    # Step 4: Uppercase Content Streaming Middleware
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-streaming-middleware")
    async def test_step4_uppercase_streaming_middleware(self):
        """Test uppercase content streaming middleware"""
        # Arrange - Define uppercase middleware (example from quickstart)
        # <snippet>
        async def uppercase_content(
            stream: AsyncIterable[TextContentChunk],
            thread: Thread
        ):
            async for chunk in stream:
                chunk.text = chunk.text.upper()
                yield chunk

        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            middleware=[
                (TextContent, uppercase_content),
            ]
        )
        # </snippet>

        # Act - Simulate streaming content
        async def mock_chunks():
            yield TextContent(text="Hello")
            yield TextContent(text=" world")
            yield TextContent(text="!")

        mock_thread = Thread(
            thread_id="thread_123",
            created_at=datetime.now(timezone.utc)
        )
        results = []
        async for chunk in uppercase_content(mock_chunks(), mock_thread):
            results.append(chunk)

        # Assert - Content was uppercased
        assert len(results) == 3
        assert results[0].text == "HELLO"
        assert results[1].text == " WORLD"
        assert results[2].text == "!"

    # ========================================================================
    # Step 4: Time Streaming Middleware (Before/After with next)
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-before-after")
    async def test_step4_time_streaming_middleware(self):
        """Test time streaming middleware with next callback"""
        # Arrange - Define timing middleware (example from quickstart)
        captured_logs = []

        # <snippet>
        async def time_streaming(
            stream: AsyncIterable[TextContentChunk],
            thread: Thread,
            next: Callable[[AsyncIterable[IStreamable]], Awaitable[AsyncIterable[TextContentChunk]]]
        ):
            start = time.time()
            captured_logs.append("🚀 Starting stream")

            result = await next(stream)

            elapsed = time.time() - start
            captured_logs.append(f"✅ Stream completed in {elapsed:.2f}s")

            return result

        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            middleware=[
                (TextContent, time_streaming),
            ]
        )
        # </snippet>

        # Act - Simulate middleware execution
        async def mock_chunks():
            yield TextContent(text="Hello")
            yield TextContent(text=" world")

        async def mock_next(stream):
            # Consume the stream
            async for _ in stream:
                pass
            await asyncio.sleep(0.01)  # Simulate some processing time

        mock_thread = Thread(
            thread_id="thread_123",
            created_at=datetime.now(timezone.utc)
        )
        await time_streaming(mock_chunks(), mock_thread, mock_next)

        # Assert - Timing logs were captured
        assert len(captured_logs) == 2
        assert "Starting stream" in captured_logs[0]
        assert "Stream completed" in captured_logs[1]
        assert "s" in captured_logs[1]

    # ========================================================================
    # Step 4: Message Middleware (Message-level timing)
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-message-middleware")
    async def test_step4_message_middleware(self):
        """Test message middleware for message-level timing"""
        # Arrange - Define message timing middleware (example from quickstart)
        captured_logs = []

        # <snippet>
        async def timing_middleware(
            message: ChatMessage,
            thread: Thread,
            next: Callable[[], Awaitable[None]]
        ) -> None:
            start = time.time()
            captured_logs.append(f"⏱️ Processing started for thread {thread.thread_id}")

            await next()  # Let other middleware and LLM process

            elapsed = time.time() - start
            captured_logs.append(f"✅ Completed in {elapsed:.2f}s")

        # Type annotation shows the signature matches MessageMiddleware
        _: MessageMiddleware = timing_middleware

        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            middleware=[timing_middleware]
        )
        # </snippet>

        # Act - Simulate message processing
        mock_message = UserMessage(
            message_id="msg_001",
            contents=[TextContent(text="Hello")]
        )
        mock_thread = Thread(
            thread_id="thread_abc123",
            created_at=datetime.now(timezone.utc)
        )

        async def mock_next():
            await asyncio.sleep(0.01)  # Simulate processing

        await timing_middleware(mock_message, mock_thread, mock_next)

        # Assert - Timing logs were captured
        assert len(captured_logs) == 2
        assert "Processing started for thread thread_abc123" in captured_logs[0]
        assert "Completed in" in captured_logs[1]

    # ========================================================================
    # Step 4: Error Middleware (try/except with next)
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-error-handling")
    async def test_step4_error_middleware(self):
        """Test error handling middleware with try/except"""
        # Arrange - Define error middleware (example from quickstart)
        captured_errors = []

        # <snippet>
        async def error_middleware(
            message: ChatMessage,
            thread: Thread,
            next: Callable[[], Awaitable[None]]
        ):
            try:
                await next()
            except Exception as e:
                captured_errors.append(f"❌ Error processing message: {e}")
                # Add error message to thread
                error_msg = AgentMessage(
                    message_id="msg_error",
                    contents=[
                        TextContent(text="Sorry, something went wrong. Please try again.")
                    ]
                )
                thread.add_message(error_msg)

        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            middleware=[error_middleware]
        )
        # </snippet>

        # Act - Simulate error during processing
        mock_message = UserMessage(
            message_id="msg_001",
            contents=[TextContent(text="Hello")]
        )
        mock_thread = Mock()
        mock_thread.thread_id = "thread_123"
        mock_thread.add_message = Mock()
        mock_thread.messages = []

        async def failing_next():
            raise Exception("Simulated LLM error")

        await error_middleware(mock_message, mock_thread, failing_next)

        # Assert - Error was caught and handled
        assert len(captured_errors) == 1
        assert "Error processing message" in captured_errors[0]
        assert "Simulated LLM error" in captured_errors[0]
        mock_thread.add_message.assert_called_once()

        # Verify error message was added to thread
        error_call = mock_thread.add_message.call_args[0][0]
        assert isinstance(error_call, AgentMessage)
        assert "something went wrong" in error_call.contents[0].text

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-content-filter")
    async def test_step4_content_filter_middleware(self):
        """Test content filtering middleware"""
        # <snippet>
        async def content_filter(
            content: TextContent,
            thread: Thread
        ):
            """Filter profanity and sensitive information"""
            # Check for profanity
            filtered_text = content.text.replace("badword", "***")

            # Check for sensitive patterns (SSN, credit cards)
            if any(pattern in content.text.lower() for pattern in ["ssn:", "credit card:"]):
                yield TextContent(text="[REDACTED - Sensitive information removed]")
            else:
                content.text = filtered_text
                yield content
        # </snippet>

        # Test the filter
        thread = Thread(thread_id="test_thread")
        content = TextContent(text="This contains badword and normal text")

        result = [item async for item in content_filter(content, thread)]
        assert len(result) == 1
        assert "***" in result[0].text

        # Test sensitive data redaction
        sensitive_content = TextContent(text="My SSN: 123-45-6789")
        result2 = [item async for item in content_filter(sensitive_content, thread)]
        assert len(result2) == 1
        assert "REDACTED" in result2[0].text

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-metadata-enrichment")
    async def test_step4_metadata_enrichment_middleware(self):
        """Test metadata enrichment middleware"""
        # <snippet>
        async def metadata_enricher(
            content: TextContent,
            thread: Thread
        ):
            """Add contextual metadata to messages"""
            # Get user context from thread metadata
            user_timezone = thread.metadata.get("user_timezone", "UTC")
            session_start = thread.metadata.get("session_start_time")

            # Add context as developer message
            context_msg = DeveloperMessage(
                contents=[
                    TextContent(text=f"[Context: User timezone={user_timezone}, session_active=True]")
                ]
            )
            yield context_msg
            yield content  # Pass through original message
        # </snippet>

        # Test the enricher
        thread = Thread(thread_id="test_thread", metadata={"user_timezone": "PST"})
        content = TextContent(text="Hello")

        result = [item async for item in metadata_enricher(content, thread)]
        assert len(result) == 2
        assert isinstance(result[0], DeveloperMessage)
        assert "PST" in result[0].contents[0].text
        assert result[1] == content

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-response-formatter")
    async def test_step4_response_formatter_middleware(self):
        """Test response formatting middleware"""
        # <snippet>
        async def response_formatter(
            stream: AsyncIterable[TextContentChunk],
            thread: Thread
        ):
            """Format agent responses with branding and markdown"""
            first_chunk = True
            async for chunk in stream:
                if first_chunk:
                    # Add branding to first chunk
                    chunk.text = f"🤖 **Agent Response:**\n\n{chunk.text}"
                    first_chunk = False
                yield chunk
        # </snippet>

        # Test the formatter
        async def mock_stream():
            yield TextContentChunk(text="Hello")
            yield TextContentChunk(text=" world")

        thread = Thread(thread_id="test_thread")
        result = [item async for item in response_formatter(mock_stream(), thread)]
        assert len(result) == 2
        assert "🤖" in result[0].text
        assert "Agent Response" in result[0].text
        assert result[1].text == " world"

    # ========================================================================
    # Step 6: Persistent Conversations (In-Memory Storage)
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-inmemory-storage")
    async def test_step6_in_memory_storage(self):
        """Test default in-memory storage configuration"""
        # Arrange - Default configuration (example from quickstart)
        # <snippet>
        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        # Conversations stored in memory (lost on restart)
        # </snippet>

        agent = AgentHost(config)

        # Assert - Default storage is None (in-memory)
        assert agent.config.storage is None

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Hosting SDK Quickstart - Step 6: Conversation Persistence")
    async def test_step6_conversation_persistence(self):
        """Test conversation persistence with thread IDs"""
        # This test demonstrates how conversations persist across messages
        # using thread IDs, as shown in the quickstart client example

        # Simulate first message creating a thread
        thread_id = "thread_abc123"
        conversation_history = {}

        # First message
        first_message = "My name is Alice"
        conversation_history[thread_id] = [
            UserMessage(
                message_id="msg_001",
                contents=[TextContent(text=first_message)]
            ),
            AgentMessage(
                message_id="msg_002",
                contents=[TextContent(text="Nice to meet you, Alice! How can I help you today?")]
            )
        ]

        # Assert - Thread has context
        assert len(conversation_history[thread_id]) == 2
        assert "Alice" in conversation_history[thread_id][1].contents[0].text

        # Second message using same thread
        second_message = "What's my name?"
        conversation_history[thread_id].append(
            UserMessage(
                message_id="msg_003",
                contents=[TextContent(text=second_message)]
            )
        )
        conversation_history[thread_id].append(
            AgentMessage(
                message_id="msg_004",
                contents=[TextContent(text="Your name is Alice.")]
            )
        )

        # Assert - Agent remembered context from previous message
        assert len(conversation_history[thread_id]) == 4
        assert "Alice" in conversation_history[thread_id][3].contents[0].text

    # ========================================================================
    # Step 6: Durable Storage (SqlStorageProvider)
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("hosting-durable-storage")
    async def test_step6_durable_storage(self):
        """Test durable storage with SqlStorageProvider"""
        # Arrange - Example from quickstart
        # <snippet>
        config = AgentConfig(
            model="gpt-4",
            instructions="You are helpful.",
            api_key=os.getenv("OPENAI_API_KEY"),
            storage=SqlStorageProvider(os.getenv("DATABASE_URL"))
        )

        agent = AgentHost(config)
        # </snippet>

        # Assert - SQL storage is configured
        assert agent.config.storage is not None
        assert isinstance(agent.config.storage, SqlStorageProvider)
        assert agent.config.storage.connection_string == "postgresql://localhost/agents"

    # ========================================================================
    # Integration Tests
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Hosting SDK Quickstart - Complete Integration")
    async def test_complete_agent_with_tools_and_middleware(self):
        """Test complete agent setup with tools, middleware, and storage"""
        # Arrange - Complete example combining multiple quickstart features

        # Define tools
        def get_weather(location: str) -> str:
            """Get current weather for a location"""
            return f"The weather in {location} is sunny and 72°F"

        def get_time() -> str:
            """Get current time in UTC"""
            return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        # Define middleware
        captured_logs = []

        async def logging_middleware(message, thread, next):
            captured_logs.append(f"Processing message in thread {thread.thread_id}")
            await next()
            captured_logs.append("Message processing complete")

        async def command_router(content: TextContent, thread: Thread) -> AsyncIterable[IStreamable]:
            if content.text.strip() == "/help":
                yield TextContent(text="Available commands:\n/help - Show this help")
            else:
                yield content

        # Create complete configuration
        config = AgentConfig(
            model="gpt-4",
            instructions="You are a helpful assistant.",
            api_key="test-api-key",
            functions=[get_weather, get_time],
            allow_client_functions=True,
            middleware=[
                logging_middleware,
                (TextContent, command_router)
            ],
            storage=SqlStorageProvider("postgresql://localhost/agents")
        )

        agent = AgentHost(config)

        # Assert - All features are configured correctly
        assert agent.config.model == "gpt-4"
        assert len(agent.config.functions) == 2
        assert agent.config.allow_client_functions is True
        assert len(agent.config.middleware) == 2
        assert agent.config.storage is not None

        # Test middleware execution
        mock_thread = Thread(
            thread_id="thread_test",
            created_at=datetime.now(timezone.utc)
        )

        async def mock_next():
            pass

        await logging_middleware(
            UserMessage(
                message_id="msg_001",
                contents=[TextContent(text="Hello")]
            ),
            mock_thread,
            mock_next
        )

        assert len(captured_logs) == 2
        assert "Processing message" in captured_logs[0]
        assert "complete" in captured_logs[1]

        # Test command router
        mock_thread = Thread(
            thread_id="thread_test",
            created_at=datetime.now(timezone.utc)
        )
        help_content = TextContent(text="/help")
        results = []
        async for item in command_router(help_content, mock_thread):
            results.append(item)

        assert len(results) == 1
        assert "Available commands" in results[0].text


# Helper to run async tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
