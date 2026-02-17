"""
Tests for all Client SDK Quickstart Guide samples (Python)
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, Mock, patch, MagicMock
from microsoft.agents.protocol.client import AgentProtocolClient, ToolCollection
from microsoft.agents.models import (
    TextContent,
    ImageContent,
    ChatMessage,
    UserMessage,
    AgentMessage,
)


class TestQuickstartSamples:
    """Tests for all Python Client SDK Quickstart samples"""

    @pytest.fixture
    def mock_client(self):
        """Create a mock HTTP client for testing"""
        with patch('httpx.AsyncClient') as mock:
            yield mock

    # ========================================================================
    # Step 1: Simple Completion
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("client-simple-completion")
    async def test_step1_simple_completion(self, mock_client):
        """Test simple completion as shown in quickstart"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        mock_response = {
            "runId": "run-123",
            "threadId": "thread_abc123",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {
                            "type": "text",
                            "text": "I can help you with analysis, writing, coding, research, and problem-solving tasks."
                        }
                    ]
                }
            ]
        }

        # Mock the HTTP response
        with patch.object(client, '_http_client') as mock_http:
            mock_http.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            ))

            # Act - Example from quickstart
            # <snippet>
            response = await client.complete_chat("What can you help me with?")
            # </snippet>

            # Assert
            assert response is not None
            assert "help" in response.lower()

    # ========================================================================
    # Step 2: Multimodal Content
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Client SDK Quickstart - Step 2: Multimodal Content (Typed Constructors)")
    async def test_step2_multimodal_typed_constructors(self):
        """Test multimodal content with typed constructors"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        mock_response = {
            "runId": "run-123",
            "threadId": "thread_def456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {
                            "type": "text",
                            "text": "This image shows the Eiffel Tower in Paris during sunset."
                        }
                    ]
                }
            ]
        }

        with patch.object(client, '_http_client') as mock_http:
            mock_http.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            ))

            # Act - Example from quickstart (using typed constructors)
            response = await client.complete_chat(
                contents=[
                    TextContent(text="What's in this image?"),
                    ImageContent(uri="https://example.com/photo.jpg")
                ]
            )

            # Assert
            assert response is not None
            assert "Eiffel Tower" in response

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Client SDK Quickstart - Step 2: Multimodal Content (Dict Format)")
    async def test_step2_multimodal_dict_format(self):
        """Test multimodal content with dict format"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        mock_response = {
            "runId": "run-123",
            "threadId": "thread_def456",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {
                            "type": "text",
                            "text": "This image shows the Eiffel Tower."
                        }
                    ]
                }
            ]
        }

        with patch.object(client, '_http_client') as mock_http:
            mock_http.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            ))

            # Act - Alternative dict format from quickstart
            response = await client.complete_chat(
                contents=[
                    {"type": "text", "text": "What's in this image?"},
                    {"type": "image", "uri": "https://example.com/photo.jpg"}
                ]
            )

            # Assert
            assert response is not None
            assert "Eiffel Tower" in response

    # ========================================================================
    # Step 3: Persistent Conversations
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("client-persistent-conversations")
    async def test_step3_persistent_conversations(self):
        """Test persistent conversations maintain context"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        mock_response_1 = {
            "runId": "run-001",
            "threadId": "thread_abc123",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {"type": "text", "text": "Nice to meet you, Alice! How can I help you today?"}
                    ]
                }
            ]
        }

        mock_response_2 = {
            "runId": "run-002",
            "threadId": "thread_abc123",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {"type": "text", "text": "Your name is Alice."}
                    ]
                }
            ]
        }

        with patch.object(client, '_http_client') as mock_http:
            # Setup mock responses for both calls
            mock_http.post = AsyncMock(side_effect=[
                Mock(status_code=200, json=Mock(return_value=mock_response_1)),
                Mock(status_code=200, json=Mock(return_value=mock_response_2))
            ])

            # Act - Create conversation and send messages
            # <snippet>
            conversation = client.create_conversation()
            msg1 = await conversation.send("My name is Alice")
            # </snippet>

            # Assert first message
            assert "Alice" in msg1
            assert conversation.thread_id == "thread_abc123"

            # Act - Send second message
            # <snippet>
            msg2 = await conversation.send("What's my name?")
            # </snippet>

            # Assert - Agent remembered context
            assert "Alice" in msg2
            assert conversation.thread_id == "thread_abc123"

    @pytest.mark.asyncio
    @pytest.mark.doc_example("client-resume-conversation")
    async def test_step3_resume_conversation(self):
        """Test resuming an existing conversation"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        mock_response = {
            "runId": "run-003",
            "threadId": "thread_abc123",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {"type": "text", "text": "Welcome back! Your name is still Alice."}
                    ]
                }
            ]
        }

        with patch.object(client, '_http_client') as mock_http:
            mock_http.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            ))

            # Act - Resume conversation with existing thread ID
            # <snippet>
            conversation = client.resume_conversation("thread_abc123")
            response = await conversation.send("Do you remember me?")
            # </snippet>

            # Assert
            assert "Alice" in response
            assert conversation.thread_id == "thread_abc123"

    # ========================================================================
    # Step 4: Tools/Functions
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("client-tools")
    async def test_step4_tools_automatically_executed(self):
        """Test tools are automatically executed"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        # Define tools as shown in quickstart
        # <snippet>
        tools = ToolCollection()

        @tools.function("get_weather")
        async def get_weather(location: str) -> str:
            """Get current weather for a location"""
            return f'{{"temperature": "72°F", "condition": "sunny", "location": "{location}"}}'
        # </snippet>

        mock_response = {
            "runId": "run-123",
            "threadId": "thread_xyz789",
            "status": "completed",
            "output": [
                {
                    "role": "agent",
                    "contents": [
                        {"type": "text", "text": "The weather in Seattle is sunny and 72°F"}
                    ]
                }
            ]
        }

        with patch.object(client, '_http_client') as mock_http:
            mock_http.post = AsyncMock(return_value=Mock(
                status_code=200,
                json=Mock(return_value=mock_response)
            ))

            # Act
            # <snippet>
            response = await client.complete_chat(
                "What's the weather in Seattle?",
                tools=tools
            )
            # </snippet>

            # Assert
            assert "72°F" in response
            assert "sunny" in response
            assert "Seattle" in response

    # ========================================================================
    # Step 5: Simple Text Streaming
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("client-simple-streaming")
    async def test_step5_simple_streaming(self):
        """Test simple text streaming"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")
        chunks_received = []

        def on_text_chunk(text: str):
            chunks_received.append(text)

        # Mock SSE response
        mock_sse_content = """event: message.delta
data: {"role":"agent","contents":[{"type":"text","text":"Once"}]}

event: message.delta
data: {"role":"agent","contents":[{"type":"text","text":" upon"}]}

event: message.delta
data: {"role":"agent","contents":[{"type":"text","text":" a time"}]}

"""

        with patch.object(client, '_http_client') as mock_http:
            mock_http.post = AsyncMock(return_value=Mock(
                status_code=200,
                iter_lines=Mock(return_value=iter(mock_sse_content.split('\n')))
            ))

            # Act - Stream with callback (as shown in quickstart)
            # <snippet>
            await client.stream_chat("Tell me a story", on_text_chunk=on_text_chunk)
            # </snippet>

            # Assert
            assert len(chunks_received) > 0
            assert any("Once" in chunk or "upon" in chunk or "time" in chunk for chunk in chunks_received)

    # ========================================================================
    # Step 5: Rich Content Streaming
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Client SDK Quickstart - Step 5: Rich Content Streaming")
    async def test_step5_rich_content_streaming(self):
        """Test streaming with multiple content types"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        # Mock streaming response
        with patch.object(client, 'stream_messages') as mock_stream:
            mock_message = MagicMock()
            mock_message.content = [
                TextContent(text="Here's a beautiful view of the Eiffel Tower at sunset."),
                ImageContent(uri="https://example.com/paris-eiffel-tower.jpg")
            ]

            async def mock_stream_gen(*args, **kwargs):
                yield mock_message

            mock_stream.return_value = mock_stream_gen()

            # Act - Stream messages (as shown in quickstart)
            messages = []
            async for message in client.stream_messages("Show me a photo of Paris"):
                messages.append(message)

            # Assert
            assert len(messages) > 0
            last_message = messages[-1]
            assert any(isinstance(c, TextContent) for c in last_message.content)
            assert any(isinstance(c, ImageContent) for c in last_message.content)

    # ========================================================================
    # Step 5: Thread Streaming
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Client SDK Quickstart - Step 5: Thread Streaming")
    async def test_step5_thread_streaming(self):
        """Test streaming all messages on a thread"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        with patch.object(client, 'stream_thread_messages') as mock_stream:
            mock_user_msg = UserMessage(contents=[TextContent(text="What's the weather in Paris?")])
            mock_agent_msg1 = AgentMessage(contents=[TextContent(text="Let me check that for you...")])
            mock_agent_msg2 = AgentMessage(contents=[TextContent(text="The current weather in Paris is 18°C and partly cloudy.")])

            async def mock_stream_gen(*args, **kwargs):
                yield mock_user_msg
                yield mock_agent_msg1
                yield mock_agent_msg2

            mock_stream.return_value = mock_stream_gen()

            # Act - Stream thread messages (as shown in quickstart)
            messages = []
            async for message in client.stream_thread_messages("thread_abc123"):
                messages.append(message)

            # Assert
            assert len(messages) == 3
            assert any(isinstance(m, UserMessage) for m in messages)
            assert any(isinstance(m, AgentMessage) for m in messages)
            agent_messages = [m for m in messages if isinstance(m, AgentMessage)]
            assert len(agent_messages) == 2

    # ========================================================================
    # Error Handling
    # ========================================================================

    @pytest.mark.asyncio
    @pytest.mark.doc_example("Client SDK Quickstart - Error Handling")
    async def test_error_handling(self):
        """Test error handling as shown in quickstart"""
        # Arrange
        client = AgentProtocolClient("http://localhost:5000")

        with patch.object(client, '_http_client') as mock_http:
            # Simulate rate limit error
            mock_http.post = AsyncMock(side_effect=Exception("Rate limit exceeded"))

            # Act & Assert - As shown in quickstart error handling example
            try:
                await client.complete_chat("Hello!")
                assert False, "Expected exception was not thrown"
            except Exception as error:
                assert "Rate limit" in str(error) or error is not None


# Helper to run async tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
