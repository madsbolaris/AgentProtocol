# Testing Client SDK Applications

Unit testing, integration testing, and mocking strategies for Client SDK applications.

## Overview

Testing applications that use the Client SDK requires strategies for mocking agent responses, testing tool execution, and validating conversation flows. This guide covers unit testing, integration testing, and best practices for testing agent-powered applications.

---

## Unit Testing with Mocks

### Mocking Client Responses

=== "Python"

    ```python
    from unittest.mock import AsyncMock, patch
    import pytest
    from microsoft.agents.protocol import AgentProtocolClient

    @pytest.mark.asyncio
    async def test_process_user_query():
        """Test processing user query with mocked client."""
        # Create mock client
        mock_client = AsyncMock(spec=AgentProtocolClient)
        mock_client.complete_chat.return_value = "The capital of France is Paris."

        # Test your application code
        async def process_query(client, query):
            response = await client.complete_chat(query)
            return response.upper()

        result = await process_query(mock_client, "What is the capital of France?")

        # Assertions
        assert result == "THE CAPITAL OF FRANCE IS PARIS."
        mock_client.complete_chat.assert_called_once_with("What is the capital of France?")
    ```

=== "TypeScript"

    ```typescript
    import { jest } from '@jest/globals';
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    describe('processUserQuery', () => {
        it('should process query correctly', async () => {
            // Create mock client
            const mockClient = {
                completeChat: jest.fn().mockResolvedValue("The capital of France is Paris.")
            } as unknown as AgentProtocolClient;

            // Test your application code
            async function processQuery(client: AgentProtocolClient, query: string) {
                const response = await client.completeChat(query);
                return response.toUpperCase();
            }

            const result = await processQuery(mockClient, "What is the capital of France?");

            // Assertions
            expect(result).toBe("THE CAPITAL OF FRANCE IS PARIS.");
            expect(mockClient.completeChat).toHaveBeenCalledWith("What is the capital of France?");
        });
    });
    ```

=== "C#"

    ```csharp
    using Moq;
    using Xunit;
    using Microsoft.Agents.Protocol.Client;

    public class ClientTests
    {
        [Fact]
        public async Task ProcessUserQuery_ReturnsUppercaseResponse()
        {
            // Arrange
            var mockClient = new Mock<IAgentProtocolClient>();
            mockClient
                .Setup(c => c.CompleteChatAsync(
                    It.IsAny<string>(),
                    It.IsAny<CancellationToken>()))
                .ReturnsAsync("The capital of France is Paris.");

            // Act
            async Task<string> ProcessQuery(IAgentProtocolClient client, string query)
            {
                var response = await client.CompleteChatAsync(query);
                return response.ToUpper();
            }

            var result = await ProcessQuery(mockClient.Object, "What is the capital of France?");

            // Assert
            Assert.Equal("THE CAPITAL OF FRANCE IS PARIS.", result);
            mockClient.Verify(c => c.CompleteChatAsync(
                "What is the capital of France?",
                It.IsAny<CancellationToken>()), Times.Once);
        }
    }
    ```

### Mocking Streaming Responses

```python
@pytest.mark.asyncio
async def test_streaming_handler():
    """Test streaming with mocked chunks."""
    mock_client = AsyncMock(spec=AgentProtocolClient)

    # Simulate streaming chunks
    async def mock_stream(message, on_text_chunk=None, **kwargs):
        chunks = ["Hello", " ", "world", "!"]
        for chunk in chunks:
            if on_text_chunk:
                on_text_chunk(chunk)

    mock_client.stream_chat.side_effect = mock_stream

    # Test streaming handler
    collected = []
    await mock_client.stream_chat(
        "Test message",
        on_text_chunk=lambda chunk: collected.append(chunk)
    )

    assert collected == ["Hello", " ", "world", "!"]
    assert "".join(collected) == "Hello world!"
```

### Mocking Tool Execution

```python
@pytest.mark.asyncio
async def test_tool_execution():
    """Test tool execution with mocked client."""
    from microsoft.agents.protocol import ToolCollection

    # Create tools
    tools = ToolCollection()

    @tools.register("get_weather")
    def get_weather(city: str) -> str:
        return f"Sunny in {city}"

    # Mock client that calls tool
    mock_client = AsyncMock(spec=AgentProtocolClient)
    mock_client.complete_chat.return_value = "The weather in Paris is sunny!"

    # Test
    result = await mock_client.complete_chat(
        "What's the weather in Paris?",
        tools=tools
    )

    assert "sunny" in result.lower()
```

---

## Integration Testing

### Testing with Real Agent

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_with_real_agent():
    """Integration test with actual agent."""
    client = AgentProtocolClient("http://localhost:5000")

    try:
        response = await client.complete_chat("What is 2+2?")
        assert "4" in response
    except Exception as e:
        pytest.skip(f"Agent not available: {e}")
```

### Testing Conversation Flow

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_conversation_flow():
    """Test multi-turn conversation."""
    client = AgentProtocolClient("http://localhost:5000")
    conversation = client.create_conversation()

    # First turn
    response1 = await conversation.send("Hi, I'm learning about space")
    assert len(response1) > 0

    # Second turn (context preserved)
    response2 = await conversation.send("Tell me about Mars")
    assert "mars" in response2.lower()

    # Third turn (reference previous context)
    response3 = await conversation.send("What about its moons?")
    assert len(response3) > 0
```

### Testing Tool Integration

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_tool_integration():
    """Test tools with real agent."""
    client = AgentProtocolClient("http://localhost:5000")

    tools = ToolCollection()
    call_count = 0

    @tools.register("get_current_time")
    def get_current_time() -> str:
        nonlocal call_count
        call_count += 1
        return "2025-01-15 10:30:00"

    response = await client.complete_chat(
        "What time is it?",
        tools=tools
    )

    assert call_count == 1  # Tool was called
    assert "10:30" in response  # Response includes time
```

---

## Test Fixtures

### Client Fixture

```python
import pytest
from microsoft.agents.protocol import AgentProtocolClient

@pytest.fixture
def client():
    """Provide agent client for tests."""
    return AgentProtocolClient("http://localhost:5000")

@pytest.fixture
def mock_client():
    """Provide mocked client for unit tests."""
    return AsyncMock(spec=AgentProtocolClient)

# Usage
@pytest.mark.asyncio
async def test_with_fixture(client):
    response = await client.complete_chat("Hello")
    assert isinstance(response, str)
```

### Conversation Fixture

```python
@pytest.fixture
async def conversation(client):
    """Provide conversation for tests."""
    conv = client.create_conversation()
    yield conv
    # Cleanup: optionally delete thread
    # await client.delete_thread(conv.thread_id)

# Usage
@pytest.mark.asyncio
async def test_conversation(conversation):
    response = await conversation.send("Test message")
    assert len(response) > 0
```

---

## Snapshot Testing

Test against known good outputs:

```python
import json
from pathlib import Path

class SnapshotTester:
    """Helper for snapshot testing."""
    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir
        self.snapshot_dir.mkdir(exist_ok=True)

    def assert_matches_snapshot(self, test_name: str, actual: str):
        """Compare actual output to snapshot."""
        snapshot_file = self.snapshot_dir / f"{test_name}.txt"

        if not snapshot_file.exists():
            # Create snapshot on first run
            snapshot_file.write_text(actual)
            pytest.skip("Snapshot created, rerun test")

        expected = snapshot_file.read_text()
        assert actual == expected, f"Output differs from snapshot {snapshot_file}"

# Usage
@pytest.fixture
def snapshots():
    return SnapshotTester(Path(__file__).parent / "snapshots")

@pytest.mark.asyncio
async def test_summary_output(client, snapshots):
    """Test summary matches expected format."""
    response = await client.complete_chat("Summarize the benefits of testing")
    snapshots.assert_matches_snapshot("test_summary_output", response)
```

---

## Golden Dataset Testing

Test with curated input/output pairs:

```python
import json
from pathlib import Path

@pytest.fixture
def golden_dataset():
    """Load golden dataset."""
    path = Path(__file__).parent / "golden_data.json"
    with open(path) as f:
        return json.load(f)

@pytest.mark.parametrize("example", [
    {"input": "What is 2+2?", "expected_contains": "4"},
    {"input": "Capital of France?", "expected_contains": "Paris"},
])
@pytest.mark.asyncio
async def test_golden_examples(client, example):
    """Test against golden examples."""
    response = await client.complete_chat(example["input"])
    assert example["expected_contains"] in response
```

---

## Performance Testing

### Response Time Testing

```python
import time

@pytest.mark.asyncio
async def test_response_time(client):
    """Ensure response time is acceptable."""
    start = time.time()
    response = await client.complete_chat("Hello")
    duration = time.time() - start

    assert duration < 5.0, f"Response took {duration:.2f}s (expected < 5s)"
```

### Throughput Testing

```python
@pytest.mark.asyncio
async def test_throughput(client):
    """Test concurrent request handling."""
    import asyncio

    requests = ["Test query"] * 10
    start = time.time()

    responses = await asyncio.gather(*[
        client.complete_chat(req) for req in requests
    ])

    duration = time.time() - start
    throughput = len(requests) / duration

    assert throughput > 1.0, f"Throughput: {throughput:.2f} req/s (expected > 1)"
    assert all(len(r) > 0 for r in responses)
```

---

## Error Scenario Testing

### Testing Error Handling

```python
from microsoft.agents.protocol import (
    AgentNotFoundException,
    AgentTimeoutException
)

@pytest.mark.asyncio
async def test_agent_not_found():
    """Test handling of missing agent."""
    client = AgentProtocolClient("http://localhost:5000")

    with pytest.raises(AgentNotFoundException):
        await client.complete_chat("Hello", agent_id="nonexistent")

@pytest.mark.asyncio
async def test_timeout_handling():
    """Test timeout handling."""
    client = AgentProtocolClient("http://localhost:5000")

    with pytest.raises(AgentTimeoutException):
        await client.complete_chat(
            "Very long task...",
            timeout=0.001  # Very short timeout
        )
```

### Testing Retry Logic

```python
@pytest.mark.asyncio
async def test_retry_on_failure():
    """Test automatic retry on transient errors."""
    mock_client = AsyncMock(spec=AgentProtocolClient)

    # Fail twice, succeed on third try
    mock_client.complete_chat.side_effect = [
        Exception("Network error"),
        Exception("Network error"),
        "Success!"
    ]

    # Implement retry logic
    async def call_with_retry(client, max_retries=3):
        for attempt in range(max_retries):
            try:
                return await client.complete_chat("Test")
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(0.1)

    result = await call_with_retry(mock_client)
    assert result == "Success!"
    assert mock_client.complete_chat.call_count == 3
```

---

## Test Organization

### Directory Structure

```
tests/
├── unit/
│   ├── test_client.py
│   ├── test_tools.py
│   └── test_conversations.py
├── integration/
│   ├── test_agent_integration.py
│   ├── test_streaming.py
│   └── test_multimodal.py
├── fixtures/
│   ├── __init__.py
│   └── common.py
├── snapshots/
│   ├── test_summary_output.txt
│   └── test_format_response.txt
└── conftest.py
```

### conftest.py

```python
import pytest
from microsoft.agents.protocol import AgentProtocolClient

def pytest_addoption(parser):
    """Add custom command line options."""
    parser.addoption(
        "--agent-url",
        action="store",
        default="http://localhost:5000",
        help="Agent server URL"
    )
    parser.addoption(
        "--run-integration",
        action="store_true",
        help="Run integration tests"
    )

def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )

def pytest_collection_modifyitems(config, items):
    """Skip integration tests by default."""
    if not config.getoption("--run-integration"):
        skip_integration = pytest.mark.skip(reason="need --run-integration option to run")
        for item in items:
            if "integration" in item.keywords:
                item.add_marker(skip_integration)

@pytest.fixture
def agent_url(request):
    """Get agent URL from command line."""
    return request.config.getoption("--agent-url")

@pytest.fixture
def client(agent_url):
    """Provide agent client."""
    return AgentProtocolClient(agent_url)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Client SDK

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      agent:
        image: agent-protocol-server:latest
        ports:
          - 5000:5000

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio

      - name: Run unit tests
        run: pytest tests/unit -v

      - name: Run integration tests
        run: |
          pytest tests/integration -v --run-integration \
            --agent-url http://localhost:5000

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Best Practices

1. **Separate Unit and Integration Tests**
   - Unit tests: Fast, mocked, run always
   - Integration tests: Slower, real agent, run on CI

2. **Use Fixtures for Common Setup**
   ```python
   @pytest.fixture
   def tools():
       return create_test_tools()

   def test_with_tools(client, tools):
       # Test uses both fixtures
       pass
   ```

3. **Test Edge Cases**
   - Empty responses
   - Very long responses
   - Special characters in input
   - Tool execution failures

4. **Mock External Dependencies**
   - Don't call real APIs in unit tests
   - Mock database connections
   - Mock file system operations

5. **Use Parametrized Tests**
   ```python
   @pytest.mark.parametrize("input,expected", [
       ("2+2", "4"),
       ("capital of France", "Paris"),
       ("hello", "greeting"),
   ])
   def test_responses(client, input, expected):
       response = await client.complete_chat(input)
       assert expected in response.lower()
   ```

6. **Monitor Test Performance**
   ```python
   @pytest.mark.timeout(5)  # Fail if test takes > 5s
   async def test_fast_response(client):
       response = await client.complete_chat("Quick question")
       assert len(response) > 0
   ```

---

## Next Steps

<div class="grid cards" markdown>

- **:material-bug: Error Handling**

    Test error scenarios

    [:octicons-arrow-right-24: Error Handling](../concepts/error-handling.md)

- **:material-tools: Tools Testing**

    Test tool implementations

    [:octicons-arrow-right-24: Tools Guide](tools.md)

- **:material-speedometer: Best Practices**

    Testing best practices

    [:octicons-arrow-right-24: Best Practices](best-practices/)

</div>
