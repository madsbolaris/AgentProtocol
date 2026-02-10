# C# Unit Testing

Unit testing patterns for C# Client SDK applications.

## Overview

Best practices for unit testing Client SDK code in C# using xUnit, NUnit, or MSTest - the most popular testing frameworks for .NET.

---

## Prerequisites

- .NET 8+
- xUnit, NUnit, or MSTest
- Moq for mocking

### Installation

=== "xUnit"
    ```bash
    dotnet add package xunit
    dotnet add package xunit.runner.visualstudio
    dotnet add package Moq
    ```

=== "NUnit"
    ```bash
    dotnet add package NUnit
    dotnet add package NUnit3TestAdapter
    dotnet add package Moq
    ```

=== "MSTest"
    ```bash
    dotnet add package MSTest.TestFramework
    dotnet add package MSTest.TestAdapter
    dotnet add package Moq
    ```

---

## Basic Test Structure

### Test Project Organization

```
MyApp.Tests/
├── Unit/
│   ├── ClientTests.cs       # Client tests
│   ├── ConversationTests.cs # Conversation tests
│   └── ToolTests.cs         # Tool tests
├── Integration/
│   └── AgentFlowTests.cs    # Integration tests
└── Fixtures/
    └── TestFixtures.cs      # Shared test fixtures
```

### Test Class Structure

=== "xUnit"
    ```csharp
    using Xunit;
    using Microsoft.Agents.Client;

    namespace Microsoft.Agents.Client.Tests
    {
        public class ClientTests : IDisposable
        {
            private readonly AgentProtocolClient _client;

            public ClientTests()
            {
                _client = new AgentProtocolClient("http://localhost:5000");
            }

            public void Dispose()
            {
                _client?.Dispose();
            }

            [Fact]
            public async Task SendMessage_ReturnsResponse()
            {
                // Arrange, Act, Assert
            }
        }
    }
    ```

=== "NUnit"
    ```csharp
    using NUnit.Framework;
    using Microsoft.Agents.Client;

    namespace Microsoft.Agents.Client.Tests
    {
        [TestFixture]
        public class ClientTests
        {
            private AgentProtocolClient _client;

            [SetUp]
            public void Setup()
            {
                _client = new AgentProtocolClient("http://localhost:5000");
            }

            [TearDown]
            public void TearDown()
            {
                _client?.Dispose();
            }

            [Test]
            public async Task SendMessage_ReturnsResponse()
            {
                // Arrange, Act, Assert
            }
        }
    }
    ```

---

## Complete Test Examples

### Basic Conversation Tests

=== "ClientTests.cs"
    ```csharp
    using Xunit;
    using Moq;
    using Microsoft.Agents.Client;
    using Microsoft.Agents.Client.Exceptions;

    namespace Microsoft.Agents.Client.Tests
    {
        public class BasicConversationTests
        {
            private readonly AgentProtocolClient _client;
            private readonly Mock<AgentProtocolClient> _mockClient;

            public BasicConversationTests()
            {
                _client = new AgentProtocolClient("http://localhost:5000");
                _mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
            }

            [Fact]
            public async Task SendMessage_ReturnsResponse()
            {
                // Arrange
                var mockResponse = new Response
                {
                    Text = "Hello, world!",
                    Role = "assistant"
                };
                
                _mockClient
                    .Setup(c => c.SendOneOffAsync(It.IsAny<string>()))
                    .ReturnsAsync(mockResponse);

                // Act
                var response = await _mockClient.Object.SendOneOffAsync("Hello");

                // Assert
                Assert.NotNull(response);
                Assert.Equal("Hello, world!", response.Text);
                Assert.Equal("assistant", response.Role);
            }

            [Fact]
            public void CreateConversation_ReturnsConversation()
            {
                // Act
                var conversation = _client.CreateConversation();

                // Assert
                Assert.NotNull(conversation);
                Assert.NotNull(conversation.ThreadId);
            }

            [Fact]
            public async Task SendMultipleMessages_ReturnsSequentialResponses()
            {
                // Arrange
                var conversation = _client.CreateConversation();
                var mockConversation = new Mock<IConversation>();
                
                mockConversation
                    .SetupSequence(c => c.SendAsync(It.IsAny<string>()))
                    .ReturnsAsync(new Response { Text = "Response 1", Role = "assistant" })
                    .ReturnsAsync(new Response { Text = "Response 2", Role = "assistant" });

                // Act
                var response1 = await mockConversation.Object.SendAsync("Message 1");
                var response2 = await mockConversation.Object.SendAsync("Message 2");

                // Assert
                Assert.Equal("Response 1", response1.Text);
                Assert.Equal("Response 2", response2.Text);
            }
        }

        public class ErrorHandlingTests
        {
            [Fact]
            public async Task SendMessage_ConnectionError_ThrowsNetworkException()
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

            [Fact]
            public async Task SendMessage_RateLimit_ThrowsRateLimitException()
            {
                // Arrange
                var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
                mockClient
                    .Setup(c => c.SendOneOffAsync(It.IsAny<string>()))
                    .ThrowsAsync(new RateLimitException("Rate limit exceeded"));

                // Act & Assert
                await Assert.ThrowsAsync<RateLimitException>(
                    () => mockClient.Object.SendOneOffAsync("Hello")
                );
            }

            [Fact]
            public async Task SendMessage_Timeout_ThrowsTimeoutException()
            {
                // Arrange
                var client = new AgentProtocolClient("http://localhost:5000", 
                    new ClientOptions { Timeout = TimeSpan.FromMilliseconds(100) });
                
                var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
                mockClient
                    .Setup(c => c.SendOneOffAsync(It.IsAny<string>()))
                    .ThrowsAsync(new TimeoutException("Request timeout"));

                // Act & Assert
                await Assert.ThrowsAsync<TimeoutException>(
                    () => mockClient.Object.SendOneOffAsync("Hello")
                );
            }
        }
    }

    // Run with: dotnet test
    ```

### Tool Testing

=== "ToolTests.cs"
    ```csharp
    using Xunit;
    using Moq;
    using Microsoft.Agents.Client;
    using Microsoft.Agents.Abstractions;

    namespace Microsoft.Agents.Client.Tests
    {
        public class ToolExecutionTests
        {
            private readonly AgentProtocolClient _client;
            private readonly ToolCollection _tools;

            public ToolExecutionTests()
            {
                _client = new AgentProtocolClient("http://localhost:5000");
                _tools = new ToolCollection();

                // Simple calculator tool
                _tools.Add("calculate", "Perform basic calculations", 
                    (string expression) => {
                        // Simple eval replacement for testing
                        return expression switch
                        {
                            "2+2" => 4,
                            "10+5" => 15,
                            "20*2" => 40,
                            _ => 0
                        };
                    });

                // Weather tool (mocked)
                _tools.Add("get_weather", "Get weather for a location",
                    async (string location) => {
                        return new
                        {
                            Location = location,
                            Temperature = 72,
                            Condition = "Sunny"
                        };
                    });
            }

            [Fact]
            public async Task ExecuteSimpleTool_ReturnsResult()
            {
                // Arrange
                var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
                var mockResponse = new Response
                {
                    Text = "The answer is 4",
                    ToolCalls = new List<ToolCall>
                    {
                        new ToolCall { Name = "calculate", Args = new { expression = "2+2" } }
                    }
                };

                mockClient
                    .Setup(c => c.SendOneOffAsync(It.IsAny<string>(), It.IsAny<ToolCollection>()))
                    .ReturnsAsync(mockResponse);

                // Act
                var response = await mockClient.Object.SendOneOffAsync(
                    "What is 2+2?",
                    _tools
                );

                // Assert
                Assert.NotNull(response.ToolCalls);
                Assert.Single(response.ToolCalls);
                Assert.Equal("calculate", response.ToolCalls[0].Name);
            }

            [Fact]
            public async Task ExecuteAsyncTool_ReturnsResult()
            {
                // Arrange
                var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
                var mockResponse = new Response
                {
                    Text = "It's sunny and 72°F",
                    ToolCalls = new List<ToolCall>
                    {
                        new ToolCall { Name = "get_weather", Args = new { location = "Seattle" } }
                    }
                };

                mockClient
                    .Setup(c => c.SendOneOffAsync(It.IsAny<string>(), It.IsAny<ToolCollection>()))
                    .ReturnsAsync(mockResponse);

                // Act
                var response = await mockClient.Object.SendOneOffAsync(
                    "What's the weather in Seattle?",
                    _tools
                );

                // Assert
                Assert.NotNull(response.ToolCalls);
                Assert.Equal("get_weather", response.ToolCalls[0].Name);
            }

            [Fact]
            public void ToolExecution_Error_ThrowsException()
            {
                // Arrange
                _tools.Add("failing_tool", "A tool that fails", () =>
                {
                    throw new InvalidOperationException("Tool execution failed");
                });

                // Act & Assert
                var tool = _tools.Get("failing_tool");
                Assert.Throws<InvalidOperationException>(() => tool.Execute());
            }

            [Fact]
            public async Task ExecuteMultipleTools_ReturnsResults()
            {
                // Arrange
                var mockClient = new Mock<AgentProtocolClient>("http://localhost:5000");
                var mockResponse = new Response
                {
                    Text = "Results calculated",
                    ToolCalls = new List<ToolCall>
                    {
                        new ToolCall { Name = "calculate", Args = new { expression = "10+5" } },
                        new ToolCall { Name = "calculate", Args = new { expression = "20*2" } }
                    }
                };

                mockClient
                    .Setup(c => c.SendOneOffAsync(It.IsAny<string>(), It.IsAny<ToolCollection>()))
                    .ReturnsAsync(mockResponse);

                // Act
                var response = await mockClient.Object.SendOneOffAsync(
                    "Calculate 10+5 and 20*2",
                    _tools
                );

                // Assert
                Assert.Equal(2, response.ToolCalls.Count);
                Assert.All(response.ToolCalls, tc => Assert.Equal("calculate", tc.Name));
            }
        }

        public class ToolValidationTests
        {
            [Fact]
            public void ToolWithParameters_ValidatesSchema()
            {
                // Arrange
                var tools = new ToolCollection();
                tools.Add("search", "Search for information",
                    (string query) => $"Results for: {query}",
                    parameters: new
                    {
                        type = "object",
                        properties = new
                        {
                            query = new { type = "string", minLength = 1 }
                        },
                        required = new[] { "query" }
                    });

                // Act
                var tool = tools.Get("search");

                // Assert
                Assert.NotNull(tool);
                Assert.NotNull(tool.Parameters);
            }
        }
    }
    ```

---

## Mocking Patterns

### Mocking with Moq

```csharp
using Moq;

// Mock interface
var mockConversation = new Mock<IConversation>();

// Setup method return value
mockConversation
    .Setup(c => c.SendAsync(It.IsAny<string>()))
    .ReturnsAsync(new Response { Text = "Mocked response" });

// Setup sequential returns
mockConversation
    .SetupSequence(c => c.SendAsync(It.IsAny<string>()))
    .ReturnsAsync(new Response { Text = "First" })
    .ReturnsAsync(new Response { Text = "Second" });

// Setup exception throwing
mockConversation
    .Setup(c => c.SendAsync(It.IsAny<string>()))
    .ThrowsAsync(new InvalidOperationException("Mock error"));

// Verify method was called
mockConversation.Verify(
    c => c.SendAsync(It.IsAny<string>()),
    Times.Once
);
```

### Mocking Streaming Responses

```csharp
[Fact]
public async Task StreamingResponse_YieldsEvents()
{
    // Arrange
    var mockConversation = new Mock<IConversation>();
    
    async IAsyncEnumerable<StreamEvent> MockStream()
    {
        yield return new StreamEvent { Type = "text", Text = "Hello " };
        yield return new StreamEvent { Type = "text", Text = "world!" };
    }
    
    mockConversation
        .Setup(c => c.StreamAsync(It.IsAny<string>()))
        .Returns(MockStream());

    // Act
    var chunks = new List<string>();
    await foreach (var @event in mockConversation.Object.StreamAsync("Test"))
    {
        if (@event.Type == "text")
        {
            chunks.Add(@event.Text);
        }
    }

    // Assert
    Assert.Equal("Hello world!", string.Join("", chunks));
}
```

---

## Running Tests

### Run All Tests

```bash
dotnet test
```

### Run Specific Test File

```bash
dotnet test --filter "FullyQualifiedName~ClientTests"
```

### Run With Coverage

```bash
dotnet test /p:CollectCoverage=true /p:CoverageReporter=html
```

### Run in Parallel

```bash
dotnet test --parallel
```

---

## Test Configuration

### xUnit Configuration

```xml
<!-- xunit.runner.json -->
{
  "parallelizeTestCollections": true,
  "maxParallelThreads": 4
}
```

### Test Project File

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
    <IsTestProject>true</IsTestProject>
  </PropertyGroup>

  <ItemGroup>
    <PackageReference Include="xunit" Version="2.6.0" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.5.3" />
    <PackageReference Include="Moq" Version="4.20.69" />
    <PackageReference Include="coverlet.collector" Version="6.0.0" />
  </ItemGroup>

  <ItemGroup>
    <ProjectReference Include="..\MyApp\MyApp.csproj" />
  </ItemGroup>
</Project>
```

---

## Best Practices

### ✅ Do

- Use constructor injection for dependencies
- Follow AAA pattern (Arrange, Act, Assert)
- Use descriptive test names
- Test one thing per test
- Mock external dependencies
- Use async/await properly
- Dispose resources properly

### ❌ Don't

- Test private methods
- Share state between tests
- Ignore async in test methods
- Use Thread.Sleep in tests
- Catch and ignore exceptions

---

## Debugging Tests

### Visual Studio

1. Set breakpoints in test code
2. Right-click test → Debug Test(s)
3. Use Test Explorer to run/debug tests

### Visual Studio Code

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": ".NET Core Test",
      "type": "coreclr",
      "request": "launch",
      "program": "dotnet",
      "args": ["test", "${workspaceFolder}/tests"],
      "cwd": "${workspaceFolder}",
      "console": "internalConsole"
    }
  ]
}
```

---

## Advanced Patterns

### Theory Tests (xUnit)

```csharp
[Theory]
[InlineData("2+2", 4)]
[InlineData("10+5", 15)]
[InlineData("20*2", 40)]
public void Calculate_VariousInputs_ReturnsCorrectResult(
    string expression, 
    int expected)
{
    // Arrange
    var tool = _tools.Get("calculate");

    // Act
    var result = tool.Execute(expression);

    // Assert
    Assert.Equal(expected, result);
}
```

### Custom Test Fixtures

```csharp
public class ClientFixture : IDisposable
{
    public AgentProtocolClient Client { get; }

    public ClientFixture()
    {
        Client = new AgentProtocolClient("http://localhost:5000");
    }

    public void Dispose()
    {
        Client?.Dispose();
    }
}

public class ClientTests : IClassFixture<ClientFixture>
{
    private readonly ClientFixture _fixture;

    public ClientTests(ClientFixture fixture)
    {
        _fixture = fixture;
    }

    [Fact]
    public async Task Test()
    {
        var response = await _fixture.Client.SendOneOffAsync("Test");
        Assert.NotNull(response);
    }
}
```

---

## See Also

- [Unit Testing Overview](index.md)
- [Testing Guide](../../guides/testing.md)
- [Integration Testing](../integration-testing/index.md)
- [Mocking Patterns](../integration-testing/mocking.md)
