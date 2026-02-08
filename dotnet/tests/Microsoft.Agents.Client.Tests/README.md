# Microsoft.Agents.Client Tests

Comprehensive test suite for the Microsoft.Agents.Client library, covering all examples from the documentation.

## Test Structure

### Test Files

1. **RunsClientTests.cs** - Tests for Runs API operations
   - Creating and executing runs
   - Waiting for completion (blocking)
   - Listing and filtering runs
   - Cancelling runs (interrupt/rollback)
   - Submitting tool outputs
   - Submitting user input
   - Submitting authentication

2. **ThreadsClientTests.cs** - Tests for Threads API operations
   - Creating threads with participants
   - Adding messages to threads
   - Getting thread messages
   - Creating runs within threads
   - Listing and filtering threads
   - Updating thread status
   - Copying threads
   - Watching threads (agent subscriptions)

3. **AgentsClientTests.cs** - Tests for Agents API operations
   - Getting agent cards
   - Inspecting ephemeral agents
   - Validating agent capabilities
   - Testing tool configurations

4. **AdvancedScenariosTests.cs** - Complex integration scenarios
   - Inline agent definitions
   - Working with images (vision models)
   - Tool execution with approval (HITL)
   - Custom HTTP client configuration
   - Error handling patterns
   - Multi-turn conversations

5. **ModelSerializationTests.cs** - JSON serialization validation
   - Run model serialization
   - ChatMessage with multiple content types
   - Polymorphic content types
   - Connection type serialization
   - Agent and tool serialization
   - Error model serialization

### Test Helpers

**MockHttpClientFactory.cs** - Utilities for creating mock HTTP clients
- Creates mock HTTP message handlers
- Sets up mock responses for different HTTP methods
- Provides consistent JSON serialization

## Running Tests

```bash
# Run all tests
dotnet test

# Run specific test class
dotnet test --filter "FullyQualifiedName~RunsClientTests"

# Run specific test
dotnet test --filter "FullyQualifiedName~RunsClientTests.CreateAsync_WithBasicRun_ReturnsCreatedRun"

# Run with verbose output
dotnet test --logger "console;verbosity=detailed"
```

## Test Coverage

The test suite covers:

### ✅ All Documentation Examples
- Every code example from the README is tested
- Quick start scenarios
- Basic operations
- Advanced scenarios

### ✅ All API Endpoints
- **Runs API**: Create, get, list, cancel, wait, submit_tool_outputs, submit_input, submit_auth
- **Threads API**: Create, get, list, update, delete, messages, runs, watch
- **Agents API**: Get card, inspect

### ✅ All Model Types
- Run, RunWaitResponse, RunError, RunStatus
- Thread, ThreadStatus, ThreadCopyRequest, ThreadWatch
- ChatMessage, Content types (Text, Image, FunctionCall, FunctionResult)
- AgentDefinition, PromptAgent, AITool, AgentCard
- Connection types (Reference, ApiKey, Remote, Anonymous)
- Participant, CompletionUsage

### ✅ Error Scenarios
- Failed runs with error details
- HTTP error handling
- Validation errors

### ✅ Edge Cases
- Null/optional fields
- Polymorphic type serialization
- Enum serialization
- Snake_case vs camelCase properties

## Test Patterns

### Mock HTTP Responses

```csharp
var mockHandler = MockHttpClientFactory.CreateMockHandler();
var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

var expectedRun = new Run { /* ... */ };
MockHttpClientFactory.SetupPostResponse(
    mockHandler,
    "https://api.example.com/runs",
    expectedRun,
    HttpStatusCode.Created
);
```

### Creating Test Client

```csharp
var options = new AgentProtocolClientOptions
{
    BaseUrl = new Uri("https://api.example.com"),
    HttpClient = httpClient
};

var client = new AgentProtocolClient(options);
```

### Testing Async Operations

```csharp
// Act
var result = await client.Runs.CreateAsync(run);

// Assert
Assert.NotNull(result);
Assert.Equal("run_001", result.RunId);
```

## Dependencies

- **xUnit** - Test framework
- **Moq** - Mocking framework
- **RichardSzalay.MockHttp** - HTTP mocking for HttpClient

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies
- Fast execution (all mocked)
- Deterministic results
- Clear failure messages

## Adding New Tests

When adding new features to the client:

1. Add corresponding tests to the appropriate test file
2. Follow the existing test patterns
3. Include documentation examples
4. Test both success and error cases
5. Validate JSON serialization if adding new models

## Example Test Template

```csharp
[Fact]
public async Task MethodName_WithScenario_ExpectedResult()
{
    // Arrange - Example from "Documentation Section" section
    var mockHandler = MockHttpClientFactory.CreateMockHandler();
    var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

    var expectedData = new ModelType { /* ... */ };
    MockHttpClientFactory.SetupPostResponse(
        mockHandler,
        "https://api.example.com/endpoint",
        expectedData
    );

    var options = new AgentProtocolClientOptions
    {
        BaseUrl = new Uri("https://api.example.com"),
        HttpClient = httpClient
    };

    var client = new AgentProtocolClient(options);

    // Act
    var result = await client.Category.MethodAsync(parameters);

    // Assert
    Assert.NotNull(result);
    Assert.Equal(expected, result.Property);
}
```
