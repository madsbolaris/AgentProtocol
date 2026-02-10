# Unit Testing

Test individual components in isolation with language-specific testing frameworks.

## Overview

Unit testing is the foundation of a robust testing strategy. This section provides comprehensive guides for unit testing Client SDK applications in Python, TypeScript, and C#.

---

## Language Guides

### [Python Unit Testing](python.md)

Test your Python Client SDK code with pytest.

**Framework:** pytest + pytest-asyncio + pytest-mock

**You'll learn:**
- Setting up pytest for async testing
- Creating test fixtures
- Mocking agent responses
- Testing tools and error handling

[View Python Guide →](python.md){ .md-button }

### [TypeScript Unit Testing](typescript.md)

Test your TypeScript/JavaScript Client SDK code with Jest or Vitest.

**Frameworks:** Jest or Vitest

**You'll learn:**
- Configuring Jest/Vitest for TypeScript
- Type-safe testing patterns
- Mocking with Jest
- Testing async code and streams

[View TypeScript Guide →](typescript.md){ .md-button }

### [C# Unit Testing](csharp.md)

Test your C# Client SDK code with xUnit, NUnit, or MSTest.

**Frameworks:** xUnit, NUnit, or MSTest + Moq

**You'll learn:**
- Setting up .NET test projects
- Using Moq for mocking
- Testing async/await code
- Test fixtures and lifecycle

[View C# Guide →](csharp.md){ .md-button }

---

## Quick Comparison

| Feature | Python | TypeScript | C# |
|---------|--------|------------|-----|
| **Framework** | pytest | Jest/Vitest | xUnit/NUnit/MSTest |
| **Mocking** | pytest-mock | jest.fn() | Moq |
| **Async** | pytest-asyncio | Native | Native |
| **Coverage** | pytest-cov | jest --coverage | coverlet |
| **Watch Mode** | pytest-watch | jest --watch | dotnet watch test |

---

## Common Testing Patterns

### Basic Message Test

=== "Python"
    ```python
    import pytest
    from microsoft.agents.client import AgentProtocolClient

    @pytest.fixture
    def mock_client(mocker):
        client = AgentProtocolClient(base_url="http://localhost:3978")
        mock_response = mocker.Mock()
        mock_response.text = "Hello, world!"
        mocker.patch.object(client, 'send_one_off', return_value=mock_response)
        return client

    async def test_send_message(mock_client):
        response = await mock_client.send_one_off("Hello")
        assert response.text == "Hello, world!"
    ```

=== "TypeScript"
    ```typescript
    import { describe, it, expect, jest } from '@jest/globals';
    import { AgentProtocolClient } from '@microsoft/agents-protocol-client';

    describe('Message Tests', () => {
      it('should send a message', async () => {
        const client = new AgentProtocolClient({ baseUrl: 'http://localhost:3978' });
        
        jest.spyOn(client, 'sendOneOff').mockResolvedValue({
          text: 'Hello, world!',
          role: 'assistant'
        });

        const response = await client.sendOneOff('Hello');
        expect(response.text).toBe('Hello, world!');
      });
    });
    ```

=== "C#"
    ```csharp
    using Xunit;
    using Moq;
    using Microsoft.Agents.Client;

    public class MessageTests
    {
        [Fact]
        public async Task SendMessage_ReturnsResponse()
        {
            // Arrange
            var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
            mockClient
                .Setup(c => c.SendOneOffAsync(It.IsAny<string>()))
                .ReturnsAsync(new Response { Text = "Hello, world!", Role = "assistant" });

            // Act
            var response = await mockClient.Object.SendOneOffAsync("Hello");

            // Assert
            Assert.Equal("Hello, world!", response.Text);
        }
    }
    ```

### Testing Tools

=== "Python"
    ```python
    from microsoft.agents.abstractions import ToolCollection

    @pytest.fixture
    def tools():
        tools = ToolCollection()
        tools.add("calculate", "Perform calculations", lambda expr: eval(expr))
        return tools

    async def test_tool_call(mock_client, tools, mocker):
        mock_response = mocker.Mock()
        mock_response.tool_calls = [
            mocker.Mock(name="calculate", args={"expr": "2+2"})
        ]
        mocker.patch.object(mock_client, 'send_one_off', return_value=mock_response)

        response = await mock_client.send_one_off("What is 2+2?", tools=tools)
        assert response.tool_calls[0].name == "calculate"
    ```

=== "TypeScript"
    ```typescript
    import { ToolCollection } from '@microsoft/agents-protocol-client';

    it('should execute a tool', async () => {
      const client = new AgentProtocolClient({ baseUrl: 'http://localhost:3978' });
      const tools = new ToolCollection();
      
      tools.add({
        name: 'calculate',
        description: 'Perform calculations'
      }, ({ expr }: { expr: string }) => eval(expr));

      jest.spyOn(client, 'sendOneOff').mockResolvedValue({
        text: 'Result: 4',
        toolCalls: [{ name: 'calculate', args: { expr: '2+2' } }]
      });

      const response = await client.sendOneOff('What is 2+2?', tools);
      expect(response.toolCalls![0].name).toBe('calculate');
    });
    ```

=== "C#"
    ```csharp
    using Microsoft.Agents.Abstractions;

    [Fact]
    public async Task ToolCall_ExecutesTool()
    {
        // Arrange
        var tools = new ToolCollection();
        tools.Add("calculate", "Perform calculations", (string expr) => 4);

        var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
        mockClient
            .Setup(c => c.SendOneOffAsync(It.IsAny<string>(), It.IsAny<ToolCollection>()))
            .ReturnsAsync(new Response
            {
                Text = "Result: 4",
                ToolCalls = new[] { new ToolCall { Name = "calculate" } }
            });

        // Act
        var response = await mockClient.Object.SendOneOffAsync("What is 2+2?", tools);

        // Assert
        Assert.Equal("calculate", response.ToolCalls[0].Name);
    }
    ```

### Testing Errors

=== "Python"
    ```python
    from microsoft.agents.client.exceptions import NetworkError

    async def test_connection_error(mocker):
        client = AgentProtocolClient(base_url="http://invalid:9999")
        mocker.patch.object(
            client, 'send_one_off',
            side_effect=NetworkError("Connection failed")
        )

        with pytest.raises(NetworkError):
            await client.send_one_off("Hello")
    ```

=== "TypeScript"
    ```typescript
    it('should handle connection errors', async () => {
      const client = new AgentProtocolClient({ baseUrl: 'http://invalid:9999' });
      
      jest.spyOn(client, 'sendOneOff').mockRejectedValue(
        new Error('Connection failed')
      );

      await expect(client.sendOneOff('Hello'))
        .rejects.toThrow('Connection failed');
    });
    ```

=== "C#"
    ```csharp
    [Fact]
    public async Task ConnectionError_ThrowsException()
    {
        // Arrange
        var mockClient = new Mock<AgentProtocolClient>("http://invalid:9999");
        mockClient
            .Setup(c => c.SendOneOffAsync(It.IsAny<string>()))
            .ThrowsAsync(new NetworkException("Connection failed"));

        // Act & Assert
        await Assert.ThrowsAsync<NetworkException>(
            () => mockClient.Object.SendOneOffAsync("Hello")
        );
    }
    ```

---

## Best Practices

### Test Structure

Follow the **AAA pattern** (Arrange, Act, Assert):

```
// Arrange - Set up test data and mocks
// Act - Execute the code under test  
// Assert - Verify the results
```

### Test Naming

Use descriptive names that explain what is being tested:

✅ Good:
- `test_send_message_returns_response`
- `should_handle_connection_errors`
- `SendMessage_WithValidInput_ReturnsResponse`

❌ Bad:
- `test1`
- `test_send`
- `TestMethod`

### Test Independence

Each test should be independent and not rely on other tests:

```python
# ✅ Good - Self-contained test
async def test_send_message(mock_client):
    response = await mock_client.send_one_off("Hello")
    assert response is not None

# ❌ Bad - Depends on shared state
_shared_response = None

async def test_send():
    global _shared_response
    _shared_response = await client.send_one_off("Hello")

async def test_response():
    assert _shared_response is not None  # Depends on test_send
```

---

## Running Tests

### Quick Reference

| Action | Python | TypeScript | C# |
|--------|--------|------------|-----|
| Run all tests | `pytest` | `npm test` | `dotnet test` |
| Run specific file | `pytest test_file.py` | `npm test file` | `dotnet test --filter File` |
| Watch mode | `pytest-watch` | `npm test -- --watch` | `dotnet watch test` |
| Coverage | `pytest --cov` | `npm test -- --coverage` | `dotnet test /p:CollectCoverage=true` |

---

## Next Steps

1. Choose your language and follow the specific guide
2. Set up your testing framework
3. Write your first unit tests
4. Progress to [Integration Testing](../integration-testing/index.md)

---

## See Also

- [Testing Overview](../index.md)
- [Testing Guide](../../guides/testing.md)
- [Integration Testing](../integration-testing/index.md)
- [Mocking Patterns](../integration-testing/mocking.md)
