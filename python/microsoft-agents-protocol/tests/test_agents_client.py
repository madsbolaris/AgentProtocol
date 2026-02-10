# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
Comprehensive tests for AgentsClient covering all low-level API operations.
Mirrors the .NET AgentsClientTests.cs implementation.

Tests cover:
- get_card() - Getting agent capability cards
- inspect() - Inspecting agent capabilities before running
- Agent validation and capabilities
- Error handling for each method
"""

import pytest
from unittest.mock import AsyncMock, Mock, MagicMock
from datetime import datetime, UTC
from typing import Dict, Any, List

from microsoft.agents.protocol.client import AgentProtocolClient
from microsoft.agents.protocol.client.client_options import AgentProtocolClientOptions
from microsoft.agents.protocol.client.agents_client import AgentsClient


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
def agents_client(mock_session, client_options):
    """Creates an AgentsClient with mocked session"""
    return AgentsClient(mock_session, client_options)


# Test: Get Agent Card
@pytest.mark.asyncio
async def test_get_card_with_agent_id_returns_agent_card(agents_client, mock_session):
    """Test getting agent card - matches GetCardAsync_WithAgentId_ReturnsAgentCard"""
    # Arrange - Example from "Get Agent Card" section
    expected_card = {
        "agent_id": "agent_001",
        "name": "Support Agent",
        "description": "A helpful customer support agent",
        "capabilities": {
            "vision": True,
            "thinking": False,
            "tools": True,
            "max_tokens": 128000,
            "content_types": ["text", "image"]
        },
        "tools": [
            {
                "name": "search_orders",
                "description": "Search customer orders",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "Customer ID"
                        }
                    },
                    "required": ["customer_id"]
                }
            }
        ]
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_001")

    # Assert
    assert result is not None
    assert result["agent_id"] == "agent_001"
    assert result["name"] == "Support Agent"
    assert result["capabilities"] is not None
    assert result["capabilities"]["vision"] is True
    assert result["capabilities"]["max_tokens"] == 128000
    assert len(result["tools"]) > 0
    assert result["tools"][0]["name"] == "search_orders"
    mock_session.get.assert_called_once_with("/agents/agent_001/card")


@pytest.mark.asyncio
async def test_get_card_with_invalid_agent_id_raises_error(agents_client, mock_session):
    """Test getting card for non-existent agent raises error"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Agent not found"}, 404)

    # Act & Assert
    with pytest.raises(Exception):
        await agents_client.get_card("invalid_agent")


@pytest.mark.asyncio
async def test_get_card_with_minimal_capabilities(agents_client, mock_session):
    """Test getting agent card with minimal capabilities"""
    # Arrange
    expected_card = {
        "agent_id": "agent_002",
        "name": "Basic Agent",
        "capabilities": {
            "vision": False,
            "thinking": False,
            "tools": False,
            "max_tokens": 4096
        }
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_002")

    # Assert
    assert result is not None
    assert result["agent_id"] == "agent_002"
    assert result["capabilities"]["vision"] is False
    assert result["capabilities"]["tools"] is False
    assert result["capabilities"]["max_tokens"] == 4096


@pytest.mark.asyncio
async def test_get_card_with_multiple_tools(agents_client, mock_session):
    """Test getting agent card with multiple tools defined"""
    # Arrange
    expected_card = {
        "agent_id": "agent_003",
        "name": "Multi-tool Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 100000
        },
        "tools": [
            {
                "name": "search_database",
                "description": "Search the database",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "send_email",
                "description": "Send an email",
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "create_ticket",
                "description": "Create a support ticket",
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_003")

    # Assert
    assert len(result["tools"]) == 3
    assert result["tools"][0]["name"] == "search_database"
    assert result["tools"][1]["name"] == "send_email"
    assert result["tools"][2]["name"] == "create_ticket"


# Test: Inspect Agent
@pytest.mark.asyncio
async def test_inspect_with_agent_definition_returns_capabilities(agents_client, mock_session):
    """Test inspecting agent - matches InspectAsync_WithAgentDefinition_ReturnsCapabilities"""
    # Arrange - Example from "Inspect Agent Before Running" section
    agent = {
        "model": "gpt-4o",
        "instructions": "You are a helpful assistant",
        "temperature": 0.7,
        "tools": [
            {
                "name": "get_weather",
                "description": "Get current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "City name"
                        }
                    },
                    "required": ["location"]
                }
            }
        ]
    }

    expected_card = {
        "agent_id": None,  # Ephemeral inspection - not persisted
        "name": "Ephemeral Agent",
        "capabilities": {
            "vision": True,
            "thinking": False,
            "tools": True,
            "max_tokens": 128000
        },
        "tools": agent["tools"]
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["agent_id"] is None  # Ephemeral - not persisted
    assert result["capabilities"] is not None
    assert result["capabilities"]["vision"] is True
    assert result["capabilities"]["tools"] is True
    assert result["capabilities"]["max_tokens"] == 128000
    mock_session.post.assert_called_once_with("/agents/inspect", json=agent)


@pytest.mark.asyncio
async def test_inspect_with_model_capabilities_returns_model_info(agents_client, mock_session):
    """Test inspecting model capabilities - matches InspectAsync_WithModelCapabilities_ReturnsModelInfo"""
    # Arrange - Validate model capabilities before running
    agent = {
        "model": "claude-3-sonnet",
        "instructions": "You are a research analyst"
    }

    expected_card = {
        "name": "Claude 3 Sonnet",
        "capabilities": {
            "vision": True,
            "thinking": True,  # Extended thinking support
            "tools": True,
            "max_tokens": 200000,
            "content_types": ["text", "image"]
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["capabilities"] is not None
    assert result["capabilities"]["thinking"] is True  # Extended thinking capability
    assert result["capabilities"]["max_tokens"] == 200000


@pytest.mark.asyncio
async def test_inspect_with_tool_definitions_validates_tool_support(agents_client, mock_session):
    """Test inspecting tool definitions - matches InspectAsync_WithToolDefinitions_ValidatesToolSupport"""
    # Arrange - Validate tool configuration
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

    expected_card = {
        "name": "File Manager Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        },
        "tools": agent["tools"]
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["capabilities"]["tools"] is True
    assert len(result["tools"]) > 0
    assert result["tools"][0]["name"] == "delete_file"
    assert result["tools"][0]["requires_approval"] is True


@pytest.mark.asyncio
async def test_inspect_with_empty_agent_definition(agents_client, mock_session):
    """Test inspecting with minimal agent definition"""
    # Arrange
    agent = {
        "model": "gpt-3.5-turbo"
    }

    expected_card = {
        "name": "GPT-3.5 Turbo",
        "capabilities": {
            "vision": False,
            "thinking": False,
            "tools": True,
            "max_tokens": 4096
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["name"] == "GPT-3.5 Turbo"
    assert result["capabilities"]["max_tokens"] == 4096


@pytest.mark.asyncio
async def test_inspect_with_vision_enabled_model(agents_client, mock_session):
    """Test inspecting a vision-enabled model"""
    # Arrange
    agent = {
        "model": "gpt-4-vision",
        "instructions": "You can analyze images"
    }

    expected_card = {
        "name": "GPT-4 Vision",
        "capabilities": {
            "vision": True,
            "thinking": False,
            "tools": True,
            "max_tokens": 128000,
            "content_types": ["text", "image"]
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["capabilities"]["vision"] is True
    assert "image" in result["capabilities"]["content_types"]


@pytest.mark.asyncio
async def test_inspect_with_high_max_tokens(agents_client, mock_session):
    """Test inspecting a model with high token limit"""
    # Arrange
    agent = {
        "model": "claude-3-opus",
        "instructions": "You can handle large contexts"
    }

    expected_card = {
        "name": "Claude 3 Opus",
        "capabilities": {
            "vision": True,
            "thinking": True,
            "tools": True,
            "max_tokens": 200000
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["capabilities"]["max_tokens"] == 200000


@pytest.mark.asyncio
async def test_inspect_with_complex_tool_schema(agents_client, mock_session):
    """Test inspecting with complex nested tool parameters"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "tools": [
            {
                "name": "search_database",
                "description": "Search database with complex filters",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "filters": {
                            "type": "object",
                            "properties": {
                                "date_range": {
                                    "type": "object",
                                    "properties": {
                                        "start": {"type": "string"},
                                        "end": {"type": "string"}
                                    }
                                },
                                "categories": {
                                    "type": "array",
                                    "items": {"type": "string"}
                                }
                            }
                        }
                    },
                    "required": ["query"]
                }
            }
        ]
    }

    expected_card = {
        "name": "Database Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        },
        "tools": agent["tools"]
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert len(result["tools"]) == 1
    assert "filters" in result["tools"][0]["parameters"]["properties"]
    assert "date_range" in result["tools"][0]["parameters"]["properties"]["filters"]["properties"]


# Test: Error Handling
@pytest.mark.asyncio
async def test_get_card_with_unauthorized_error(agents_client, mock_session):
    """Test handling unauthorized error when getting agent card"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Unauthorized"}, 401)

    # Act & Assert
    with pytest.raises(Exception):
        await agents_client.get_card("agent_001")


@pytest.mark.asyncio
async def test_get_card_with_forbidden_error(agents_client, mock_session):
    """Test handling forbidden error when getting agent card"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Forbidden"}, 403)

    # Act & Assert
    with pytest.raises(Exception):
        await agents_client.get_card("agent_001")


@pytest.mark.asyncio
async def test_get_card_with_server_error(agents_client, mock_session):
    """Test handling server error when getting agent card"""
    # Arrange
    mock_http_method(mock_session.get, {"error": "Internal server error"}, 500)

    # Act & Assert
    with pytest.raises(Exception):
        await agents_client.get_card("agent_001")


@pytest.mark.asyncio
async def test_inspect_with_validation_error(agents_client, mock_session):
    """Test handling validation error when inspecting agent"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {
            "error": "Validation failed",
            "details": "model is required"
        },
        400
    )

    agent = {
        "instructions": "Missing model field"
    }

    # Act & Assert
    with pytest.raises(Exception):
        await agents_client.inspect(agent)


@pytest.mark.asyncio
async def test_inspect_with_unsupported_model_error(agents_client, mock_session):
    """Test handling unsupported model error"""
    # Arrange
    mock_http_method(
        mock_session.post,
        {
            "error": "Unsupported model",
            "details": "Model 'invalid-model' is not supported"
        },
        400
    )

    agent = {
        "model": "invalid-model"
    }

    # Act & Assert
    with pytest.raises(Exception):
        await agents_client.inspect(agent)


# Test: Agent Capabilities
@pytest.mark.asyncio
async def test_get_card_with_thinking_capability(agents_client, mock_session):
    """Test getting card for agent with thinking capability"""
    # Arrange
    expected_card = {
        "agent_id": "agent_thinking",
        "name": "Thinking Agent",
        "capabilities": {
            "vision": True,
            "thinking": True,
            "tools": True,
            "max_tokens": 200000
        }
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_thinking")

    # Assert
    assert result["capabilities"]["thinking"] is True


@pytest.mark.asyncio
async def test_get_card_with_content_types(agents_client, mock_session):
    """Test getting card with specific content types"""
    # Arrange
    expected_card = {
        "agent_id": "agent_multimodal",
        "name": "Multimodal Agent",
        "capabilities": {
            "vision": True,
            "tools": True,
            "max_tokens": 128000,
            "content_types": ["text", "image", "audio", "video"]
        }
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_multimodal")

    # Assert
    assert "content_types" in result["capabilities"]
    assert "text" in result["capabilities"]["content_types"]
    assert "image" in result["capabilities"]["content_types"]
    assert "audio" in result["capabilities"]["content_types"]


@pytest.mark.asyncio
async def test_get_card_with_metadata(agents_client, mock_session):
    """Test getting card with agent metadata"""
    # Arrange
    expected_card = {
        "agent_id": "agent_meta",
        "name": "Agent with Metadata",
        "description": "An agent with rich metadata",
        "capabilities": {
            "tools": True,
            "max_tokens": 50000
        },
        "metadata": {
            "version": "1.0.0",
            "author": "Microsoft",
            "tags": ["support", "customer-service"]
        }
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_meta")

    # Assert
    assert "metadata" in result
    assert result["metadata"]["version"] == "1.0.0"
    assert "support" in result["metadata"]["tags"]


@pytest.mark.asyncio
async def test_inspect_with_temperature_setting(agents_client, mock_session):
    """Test inspecting agent with temperature configuration"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "instructions": "You are creative",
        "temperature": 0.9
    }

    expected_card = {
        "name": "Creative Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        },
        "configuration": {
            "temperature": 0.9
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert "configuration" in result
    assert result["configuration"]["temperature"] == 0.9


@pytest.mark.asyncio
async def test_inspect_with_max_tokens_setting(agents_client, mock_session):
    """Test inspecting agent with max_tokens configuration"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "instructions": "You are concise",
        "max_tokens": 500
    }

    expected_card = {
        "name": "Concise Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        },
        "configuration": {
            "max_tokens": 500
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert "configuration" in result
    assert result["configuration"]["max_tokens"] == 500


# Test: Tool Validation
@pytest.mark.asyncio
async def test_get_card_with_tool_requiring_approval(agents_client, mock_session):
    """Test getting card with tools that require approval"""
    # Arrange
    expected_card = {
        "agent_id": "agent_approval",
        "name": "Approval Required Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        },
        "tools": [
            {
                "name": "delete_data",
                "description": "Delete important data",
                "requires_approval": True,
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_approval")

    # Assert
    assert result["tools"][0]["requires_approval"] is True


@pytest.mark.asyncio
async def test_inspect_with_multiple_tools_mixed_approval(agents_client, mock_session):
    """Test inspecting with some tools requiring approval"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "tools": [
            {
                "name": "read_file",
                "description": "Read a file",
                "requires_approval": False,
                "parameters": {"type": "object", "properties": {}}
            },
            {
                "name": "write_file",
                "description": "Write to a file",
                "requires_approval": True,
                "parameters": {"type": "object", "properties": {}}
            }
        ]
    }

    expected_card = {
        "name": "File Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        },
        "tools": agent["tools"]
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert len(result["tools"]) == 2
    assert result["tools"][0]["requires_approval"] is False
    assert result["tools"][1]["requires_approval"] is True


@pytest.mark.asyncio
async def test_get_card_with_no_tools(agents_client, mock_session):
    """Test getting card for agent with no tools defined"""
    # Arrange
    expected_card = {
        "agent_id": "agent_no_tools",
        "name": "Simple Agent",
        "capabilities": {
            "vision": False,
            "thinking": False,
            "tools": False,
            "max_tokens": 4096
        },
        "tools": []
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_no_tools")

    # Assert
    assert result["capabilities"]["tools"] is False
    assert len(result["tools"]) == 0


@pytest.mark.asyncio
async def test_inspect_with_no_tools_defined(agents_client, mock_session):
    """Test inspecting agent without tools"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "instructions": "You are a helpful assistant with no tools"
    }

    expected_card = {
        "name": "No Tools Agent",
        "capabilities": {
            "vision": True,
            "tools": False,
            "max_tokens": 128000
        },
        "tools": []
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result["capabilities"]["tools"] is False
    assert len(result.get("tools", [])) == 0


# Test: Special Cases
@pytest.mark.asyncio
async def test_get_card_with_unicode_description(agents_client, mock_session):
    """Test getting card with unicode characters in description"""
    # Arrange
    expected_card = {
        "agent_id": "agent_unicode",
        "name": "国际化 Agent",
        "description": "Supports 中文, 日本語, and Emoji 🌍",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        }
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_unicode")

    # Assert
    assert result["name"] == "国际化 Agent"
    assert "🌍" in result["description"]


@pytest.mark.asyncio
async def test_inspect_with_empty_instructions(agents_client, mock_session):
    """Test inspecting agent with empty instructions"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "instructions": ""
    }

    expected_card = {
        "name": "No Instructions Agent",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result is not None
    assert result["name"] == "No Instructions Agent"


@pytest.mark.asyncio
async def test_get_card_with_large_token_limit(agents_client, mock_session):
    """Test getting card with very large token limit"""
    # Arrange
    expected_card = {
        "agent_id": "agent_large",
        "name": "Large Context Agent",
        "capabilities": {
            "vision": True,
            "thinking": True,
            "tools": True,
            "max_tokens": 1000000
        }
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_large")

    # Assert
    assert result["capabilities"]["max_tokens"] == 1000000


@pytest.mark.asyncio
async def test_inspect_returns_null_agent_id_for_ephemeral(agents_client, mock_session):
    """Test that inspect returns null agent_id for ephemeral agents"""
    # Arrange
    agent = {
        "model": "gpt-4o",
        "instructions": "Ephemeral agent"
    }

    expected_card = {
        "agent_id": None,
        "name": "Ephemeral",
        "capabilities": {
            "tools": True,
            "max_tokens": 128000
        }
    }

    mock_http_method(mock_session.post, expected_card)

    # Act
    result = await agents_client.inspect(agent)

    # Assert
    assert result["agent_id"] is None


@pytest.mark.asyncio
async def test_get_card_preserves_all_fields(agents_client, mock_session):
    """Test that get_card preserves all response fields"""
    # Arrange
    expected_card = {
        "agent_id": "agent_full",
        "name": "Full Details Agent",
        "description": "Agent with all fields",
        "version": "2.0.0",
        "capabilities": {
            "vision": True,
            "thinking": True,
            "tools": True,
            "max_tokens": 150000,
            "content_types": ["text", "image"]
        },
        "tools": [
            {"name": "tool1", "description": "First tool", "parameters": {}}
        ],
        "metadata": {
            "custom_field": "custom_value"
        },
        "created_at": datetime.now(UTC).isoformat(),
        "updated_at": datetime.now(UTC).isoformat()
    }

    mock_http_method(mock_session.get, expected_card)

    # Act
    result = await agents_client.get_card("agent_full")

    # Assert
    assert result["agent_id"] == "agent_full"
    assert result["name"] == "Full Details Agent"
    assert result["description"] == "Agent with all fields"
    assert result["version"] == "2.0.0"
    assert "created_at" in result
    assert "updated_at" in result
    assert "metadata" in result
