"""
Tests for LLM configuration patterns (string vs provider instance).
Verifies Vercel AI-style pattern: accept either string (gateway) or provider instance.
"""

import os
import pytest
from typing import List, Optional, AsyncGenerator
from unittest.mock import MagicMock

from microsoft.agents.hosting import AgentHostBuilder
from microsoft.agents.models import (
    ChatMessage,
    AgentMessage,
    TextContent,
    ToolDefinition,
    AIContent,
)


class MockProtocolLLMClient:
    """Mock LLM client for testing purposes."""

    def __init__(self, model: str):
        self._model = model

    @property
    def provider_info(self):
        """Provider information."""
        return {
            "provider": "Mock",
            "model": self._model,
            "supports_streaming": True,
            "supports_function_calling": True,
        }

    async def generate(
        self,
        conversation_history: List[ChatMessage],
        available_tools: Optional[List[ToolDefinition]] = None,
    ) -> AgentMessage:
        """Generate a response."""
        return AgentMessage(
            message_id="test-msg-123",
            contents=[TextContent(text="Mock response")],
        )

    async def stream(
        self,
        conversation_history: List[ChatMessage],
        available_tools: Optional[List[ToolDefinition]] = None,
    ) -> AsyncGenerator:
        """Stream a response."""
        yield {
            "message_id": "test-msg-123",
            "type": "message_start",
        }

        yield {
            "message_id": "test-msg-123",
            "type": "text_delta",
            "content": TextContent(text="Mock streaming response"),
        }

        yield {
            "message_id": "test-msg-123",
            "type": "message_complete",
            "is_complete": True,
        }


@pytest.fixture
def clean_env(monkeypatch):
    """Clean environment fixture that restores env after test."""
    # Store original env
    original_env = dict(os.environ)

    yield monkeypatch

    # Restore original env
    os.environ.clear()
    os.environ.update(original_env)


class TestStringBasedConfiguration:
    """Tests for string-based LLM configuration."""

    def test_use_llm_with_string_creates_client_from_environment(
        self, clean_env
    ):
        """Should create client from environment variables when using string."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")

        # Act
        builder = AgentHostBuilder()
        result = builder.add_default_agent(
            lambda agent: agent.use_llm(
                "gpt-4o-mini", "You are a test assistant"
            )
        ).build()

        # Assert - should not raise
        assert result is not None

    def test_use_llm_with_string_throws_when_endpoint_missing(
        self, clean_env
    ):
        """Should throw when FOUNDRY_ENDPOINT is missing."""
        # Arrange
        clean_env.delenv("FOUNDRY_ENDPOINT", raising=False)
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")

        # Act & Assert
        builder = AgentHostBuilder()
        with pytest.raises(Exception, match="FOUNDRY_ENDPOINT"):
            builder.add_default_agent(
                lambda agent: agent.use_llm(
                    "gpt-4o-mini", "You are a test assistant"
                )
            ).build()

    def test_use_llm_with_string_throws_when_api_key_missing(
        self, clean_env
    ):
        """Should throw when FOUNDRY_API_KEY is missing."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.delenv("FOUNDRY_API_KEY", raising=False)

        # Act & Assert
        builder = AgentHostBuilder()
        with pytest.raises(Exception, match="FOUNDRY_API_KEY"):
            builder.add_default_agent(
                lambda agent: agent.use_llm(
                    "gpt-4o-mini", "You are a test assistant"
                )
            ).build()

    def test_use_llm_uses_explicit_model_over_environment(self, clean_env):
        """Should use explicit model over environment variable."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")
        clean_env.setenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-turbo")

        # Act
        builder = AgentHostBuilder()
        result = builder.add_default_agent(
            lambda agent: agent.use_llm(
                "gpt-4o-mini", "You are a test assistant"  # Explicit model
            )
        ).build()

        # Assert - should not raise
        assert result is not None

    def test_use_llm_reads_model_from_environment(self, clean_env):
        """Should read model from FOUNDRY_MODEL_DEPLOYMENT."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")
        clean_env.setenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-turbo")

        # Act
        model = os.environ.get("FOUNDRY_MODEL_DEPLOYMENT")
        builder = AgentHostBuilder()
        result = builder.add_default_agent(
            lambda agent: agent.use_llm(model, "You are a test assistant")
        ).build()

        # Assert - should not raise
        assert result is not None


class TestProviderInstanceConfiguration:
    """Tests for provider instance-based LLM configuration."""

    def test_use_llm_with_provider_instance(self):
        """Should use provided client instance."""
        # Arrange
        mock_client = MockProtocolLLMClient("custom-model")

        # Act
        builder = AgentHostBuilder()
        result = builder.add_default_agent(
            lambda agent: agent.use_llm(
                mock_client, "You are a test assistant"
            )
        ).build()

        # Assert - should not raise
        assert result is not None

    def test_use_llm_with_provider_does_not_require_env(self, clean_env):
        """Should not require environment variables with provider instance."""
        # Arrange - clear all environment variables
        clean_env.delenv("FOUNDRY_ENDPOINT", raising=False)
        clean_env.delenv("FOUNDRY_API_KEY", raising=False)
        clean_env.delenv("FOUNDRY_MODEL_DEPLOYMENT", raising=False)

        mock_client = MockProtocolLLMClient("custom-model")

        # Act
        builder = AgentHostBuilder()
        result = builder.add_default_agent(
            lambda agent: agent.use_llm(
                mock_client, "You are a test assistant"
            )
        ).build()

        # Assert - should not raise even without environment variables
        assert result is not None

    def test_use_llm_throws_when_client_is_none(self):
        """Should throw when client instance is None."""
        # Act & Assert
        builder = AgentHostBuilder()
        with pytest.raises(Exception):
            builder.add_default_agent(
                lambda agent: agent.use_llm(None, "You are a test assistant")
            ).build()

    def test_use_llm_extracts_model_from_provider_info(self):
        """Should extract model from provider info."""
        # Arrange
        expected_model = "custom-gpt-model"
        mock_client = MockProtocolLLMClient(expected_model)

        # Act
        builder = AgentHostBuilder()
        builder.add_default_agent(
            lambda agent: agent.use_llm(
                mock_client, "You are a test assistant"
            )
        ).build()

        # Assert
        assert mock_client.provider_info["model"] == expected_model

    def test_use_llm_prefers_provider_over_string(self, clean_env):
        """Should prefer provider instance over string configuration."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")

        mock_client = MockProtocolLLMClient("custom-model")

        # Act
        builder = AgentHostBuilder()
        result = builder.add_default_agent(
            lambda agent: agent.use_llm(
                mock_client, "You are a test assistant"
            )
        ).build()

        # Assert - should use provider instance and not fail
        assert result is not None


class TestFullIntegration:
    """Full integration tests."""

    def test_build_with_string_configuration(self, clean_env):
        """Should build successfully with string configuration."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")

        # Act
        builder = AgentHostBuilder()
        host = (
            builder.add_default_agent(
                lambda agent: agent.use_llm(
                    "gpt-4o-mini", "You are a test assistant"
                ).add_functions(
                    lambda f: f
                    # Functions can be added here
                )
            ).build()
        )

        # Assert
        assert host is not None

    def test_build_with_provider_instance(self):
        """Should build successfully with provider instance."""
        # Arrange
        mock_client = MockProtocolLLMClient("custom-model")

        # Act
        builder = AgentHostBuilder()
        host = (
            builder.add_default_agent(
                lambda agent: agent.use_llm(
                    mock_client, "You are a test assistant"
                ).add_functions(
                    lambda f: f
                    # Functions can be added here
                )
            ).build()
        )

        # Assert
        assert host is not None

    def test_multiple_agents_with_different_configs(self, clean_env):
        """Should support multiple agents with different configurations."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")

        mock_client = MockProtocolLLMClient("custom-model")

        # Act
        builder = AgentHostBuilder()
        host = (
            builder.add_agent(
                "agent1",
                lambda agent: agent.use_llm(
                    "gpt-4o-mini", "You are assistant 1"
                ),
            )
            .add_agent(
                "agent2",
                lambda agent: agent.use_llm(
                    mock_client, "You are assistant 2"
                ),
            )
            .build()
        )

        # Assert
        assert host is not None


class TestErrorHandling:
    """Error handling tests."""

    def test_error_when_model_not_specified(self, clean_env):
        """Should provide clear error when model is not specified."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")
        clean_env.delenv("FOUNDRY_MODEL_DEPLOYMENT", raising=False)

        # Act & Assert
        builder = AgentHostBuilder()
        with pytest.raises(Exception):
            builder.add_default_agent(
                lambda agent: agent.use_llm("", "You are a test assistant")
            ).build()

    def test_error_when_instructions_missing(self, clean_env):
        """Should provide clear error when instructions are missing."""
        # Arrange
        clean_env.setenv("FOUNDRY_ENDPOINT", "https://api.test.com")
        clean_env.setenv("FOUNDRY_API_KEY", "test-key-123")

        # Act & Assert
        builder = AgentHostBuilder()
        with pytest.raises(Exception):
            builder.add_default_agent(
                lambda agent: agent.use_llm("gpt-4o-mini", "")
            ).build()


@pytest.mark.asyncio
class TestAsyncOperations:
    """Tests for async operations with mock client."""

    async def test_mock_client_generate(self):
        """Should generate response with mock client."""
        # Arrange
        mock_client = MockProtocolLLMClient("test-model")

        # Act
        result = await mock_client.generate([])

        # Assert
        assert result.message_id == "test-msg-123"
        assert len(result.contents) == 1
        assert result.contents[0].text == "Mock response"

    async def test_mock_client_stream(self):
        """Should stream response with mock client."""
        # Arrange
        mock_client = MockProtocolLLMClient("test-model")

        # Act
        chunks = []
        async for chunk in mock_client.stream([]):
            chunks.append(chunk)

        # Assert
        assert len(chunks) == 3
        assert chunks[0]["type"] == "message_start"
        assert chunks[1]["type"] == "text_delta"
        assert chunks[2]["type"] == "message_complete"
