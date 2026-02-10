# Python Unit Testing

Unit testing patterns for Python Client SDK applications.

## Overview

Best practices for unit testing Client SDK code in Python using pytest, the de facto standard testing framework for Python.

---

## Prerequisites

- Python 3.9+
- pytest test framework
- pytest-asyncio for async tests
- pytest-mock for mocking

### Installation

```bash
pip install pytest pytest-asyncio pytest-mock
```

---

## Basic Test Structure

### Test File Organization

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_client.py      # Client tests
│   ├── test_conversation.py # Conversation tests
│   └── test_tools.py       # Tool tests
└── integration/
    └── test_agent_flows.py # Integration tests
```

### Fixtures

Use pytest fixtures to set up reusable test components:

```python
import pytest
from microsoft.agents.client import AgentProtocolClient

@pytest.fixture
def client():
    """Create a test client instance"""
    return AgentProtocolClient(base_url="http://localhost:3978")

@pytest.fixture
def mock_client(mocker):
    """Create a mocked client for unit tests"""
    client = AgentProtocolClient(base_url="http://localhost:3978")
    mock_response = mocker.Mock()
    mock_response.text = "Hello, world!"
    mock_response.role = "assistant"
    mocker.patch.object(
        client, 'send_one_off', 
        return_value=mock_response
    )
    return client
```

---

## Complete Test Examples

### Basic Conversation Tests

=== "test_client.py"
    ```python
    import pytest
    from microsoft.agents.client import AgentProtocolClient

    @pytest.fixture
    def client():
        """Create a test client instance"""
        return AgentProtocolClient(base_url="http://localhost:3978")

    @pytest.fixture
    def mock_client(mocker):
        """Create a mocked client for unit tests"""
        client = AgentProtocolClient(base_url="http://localhost:3978")
        mock_response = mocker.Mock()
        mock_response.text = "Hello, world!"
        mock_response.role = "assistant"
        mocker.patch.object(
            client, 'send_one_off', 
            return_value=mock_response
        )
        return client

    class TestBasicConversation:
        """Test basic conversation functionality"""
        
        async def test_send_message(self, mock_client):
            """Test sending a simple message"""
            response = await mock_client.send_one_off("Hello")
            
            assert response is not None
            assert response.text == "Hello, world!"
            assert response.role == "assistant"
        
        async def test_conversation_creation(self, client):
            """Test conversation creation"""
            conversation = client.create_conversation()
            
            assert conversation is not None
            assert conversation.thread_id is not None
        
        async def test_multiple_messages(self, mock_client, mocker):
            """Test sending multiple messages in sequence"""
            conversation = mock_client.create_conversation()
            
            # Mock multiple responses
            responses = [
                mocker.Mock(text="Response 1", role="assistant"),
                mocker.Mock(text="Response 2", role="assistant"),
            ]
            mocker.patch.object(
                conversation, 'send',
                side_effect=responses
            )
            
            response1 = await conversation.send("Message 1")
            response2 = await conversation.send("Message 2")
            
            assert response1.text == "Response 1"
            assert response2.text == "Response 2"

    class TestErrorHandling:
        """Test error handling scenarios"""
        
        async def test_connection_error(self, mocker):
            """Test handling of connection errors"""
            from microsoft.agents.client.exceptions import NetworkError
            
            client = AgentProtocolClient(base_url="http://invalid:9999")
            mocker.patch.object(
                client, 'send_one_off',
                side_effect=NetworkError("Connection failed")
            )
            
            with pytest.raises(NetworkError):
                await client.send_one_off("Hello")
        
        async def test_rate_limit_error(self, mock_client, mocker):
            """Test handling of rate limit errors"""
            from microsoft.agents.client.exceptions import RateLimitError
            
            mocker.patch.object(
                mock_client, 'send_one_off',
                side_effect=RateLimitError("Rate limit exceeded")
            )
            
            with pytest.raises(RateLimitError):
                await mock_client.send_one_off("Hello")

    # Run with: pytest test_client.py -v
    ```

### Tool Testing

=== "test_tools.py"
    ```python
    import pytest
    from microsoft.agents.client import AgentProtocolClient
    from microsoft.agents.abstractions import ToolCollection

    @pytest.fixture
    def tools():
        """Create a tool collection for testing"""
        tools = ToolCollection()
        
        # Simple calculator tool
        tools.add(
            "calculate",
            "Perform basic calculations",
            lambda expression: eval(expression)
        )
        
        # Weather tool (mocked)
        async def get_weather(location: str):
            return {"location": location, "temperature": 72, "condition": "Sunny"}
        
        tools.add(
            "get_weather",
            "Get weather for a location",
            get_weather
        )
        
        return tools

    class TestToolExecution:
        """Test tool execution and validation"""
        
        async def test_simple_tool_call(self, mock_client, tools, mocker):
            """Test executing a simple tool"""
            mock_response = mocker.Mock()
            mock_response.text = "The answer is 4"
            mock_response.tool_calls = [
                mocker.Mock(name="calculate", args={"expression": "2+2"})
            ]
            
            mocker.patch.object(
                mock_client, 'send_one_off',
                return_value=mock_response
            )
            
            response = await mock_client.send_one_off(
                "What is 2+2?",
                tools=tools
            )
            
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].name == "calculate"
        
        async def test_async_tool_call(self, mock_client, tools, mocker):
            """Test executing an async tool"""
            mock_response = mocker.Mock()
            mock_response.text = "It's sunny and 72°F"
            mock_response.tool_calls = [
                mocker.Mock(name="get_weather", args={"location": "Seattle"})
            ]
            
            mocker.patch.object(
                mock_client, 'send_one_off',
                return_value=mock_response
            )
            
            response = await mock_client.send_one_off(
                "What's the weather in Seattle?",
                tools=tools
            )
            
            assert response.tool_calls is not None
            assert response.tool_calls[0].name == "get_weather"
        
        async def test_tool_error_handling(self, tools):
            """Test error handling in tools"""
            # Add a tool that raises an error
            def failing_tool():
                raise ValueError("Tool execution failed")
            
            tools.add("failing_tool", "A tool that fails", failing_tool)
            
            with pytest.raises(ValueError):
                tool = tools.get("failing_tool")
                tool.execute()
        
        async def test_multiple_tool_calls(self, mock_client, tools, mocker):
            """Test multiple tool calls in sequence"""
            mock_response = mocker.Mock()
            mock_response.tool_calls = [
                mocker.Mock(name="calculate", args={"expression": "10+5"}),
                mocker.Mock(name="calculate", args={"expression": "20*2"}),
            ]
            
            mocker.patch.object(
                mock_client, 'send_one_off',
                return_value=mock_response
            )
            
            response = await mock_client.send_one_off(
                "Calculate 10+5 and 20*2",
                tools=tools
            )
            
            assert len(response.tool_calls) == 2
            assert all(tc.name == "calculate" for tc in response.tool_calls)

    class TestToolValidation:
        """Test tool parameter validation"""
        
        def test_tool_parameter_validation(self, tools):
            """Test that tool parameters are validated"""
            # Tool with parameter schema
            tools.add(
                "search",
                "Search for information",
                lambda query: f"Results for: {query}",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "minLength": 1}
                    },
                    "required": ["query"]
                }
            )
            
            tool = tools.get("search")
            assert tool is not None
            assert tool.parameters["required"] == ["query"]
    ```

---

## Mocking Patterns

### Mocking Responses

```python
@pytest.fixture
def mock_response(mocker):
    """Create a mock response"""
    response = mocker.Mock()
    response.text = "Mocked response"
    response.role = "assistant"
    response.tool_calls = []
    return response

async def test_with_mock_response(mock_client, mock_response, mocker):
    mocker.patch.object(
        mock_client, 'send_one_off',
        return_value=mock_response
    )
    
    response = await mock_client.send_one_off("Test")
    assert response.text == "Mocked response"
```

### Mocking Streaming

```python
async def test_streaming(mock_client, mocker):
    """Test streaming responses"""
    async def mock_stream():
        yield {"type": "text", "text": "Hello "}
        yield {"type": "text", "text": "world!"}
    
    conversation = mock_client.create_conversation()
    mocker.patch.object(
        conversation, 'stream',
        return_value=mock_stream()
    )
    
    chunks = []
    async for event in conversation.stream("Test"):
        if event["type"] == "text":
            chunks.append(event["text"])
    
    assert "".join(chunks) == "Hello world!"
```

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/unit/test_client.py -v
```

### Run With Coverage

```bash
pytest tests/ --cov=microsoft.agents.client --cov-report=html
```

### Run Async Tests

```bash
# Install pytest-asyncio
pip install pytest-asyncio

# Run tests
pytest tests/ -v --asyncio-mode=auto
```

---

## Configuration

### pytest.ini

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --cov=microsoft.agents.client
    --cov-report=term-missing
    --cov-report=html
```

### conftest.py

```python
import pytest
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_client(mocker):
    """Shared mock client fixture"""
    from microsoft.agents.client import AgentProtocolClient
    client = AgentProtocolClient(base_url="http://localhost:3978")
    return client
```

---

## Best Practices

### ✅ Do

- Use descriptive test names
- Test one thing per test
- Use fixtures for setup
- Mock external dependencies
- Test error cases
- Use parametrized tests for similar cases

### ❌ Don't

- Test implementation details
- Share state between tests
- Make tests depend on each other
- Forget to test async code
- Skip error cases

---

## See Also

- [Unit Testing Overview](index.md)
- [Testing Guide](../../guides/testing.md)
- [Integration Testing](../integration-testing/index.md)
- [Mocking Patterns](../integration-testing/mocking.md)
