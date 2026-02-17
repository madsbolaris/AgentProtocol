# Test Recording Infrastructure

## Overview

All quickstart tests use recording/replay to ensure deterministic, fast, and cost-free testing:

- **Client SDK Tests**: Record HTTP responses from Agent Protocol servers
- **Hosting SDK Tests**: Record LLM responses from language models

## Client SDK Tests (HTTP Recording)

### Infrastructure

- `HttpRecorder.cs` - Records HTTP request/response pairs with hash-based filenames
- `HttpPlayer.cs` - Replays recorded HTTP responses
- `RecordingHttpMessageHandler.cs` - HttpMessageHandler that records or replays
- `RecordingTestHelper.cs` - Helper for creating recording-enabled clients

### Usage

```csharp
[Fact]
public async Task Example_Test()
{
    // Create client with recording support
    var client = RecordingTestHelper.CreateRecordingClient("TestName");

    // Use client exactly as shown in quickstart
    var response = await client.CompleteChatAsync("Hello!");

    // Assert
    response.Should().NotBeNullOrEmpty();
}
```

### Running Tests

**Record Mode** (makes real HTTP calls to agent server):
```bash
RECORD_HTTP=true dotnet test
```

**Test Mode** (replays recordings - default):
```bash
dotnet test
```

### Recording Files

Stored in `/Recordings/{TestName}/`:
```
{hash}.request.json  - Request details (method, path, body)
{hash}.response.json - Response details (status, body)
```

## Hosting SDK Tests (LLM Recording)

### Infrastructure

- Uses existing `RecordingProtocolLLMClient` from `Microsoft.Agents.Protocol.Model.Testing`
- `LlmRecordingTestHelper.cs` - Helper for creating recording-enabled LLM clients
- `ReplayProtocolLlmClient.cs` - Replays recorded LLM responses

### Usage

```csharp
[Fact]
public async Task Example_HostingTest()
{
    // Create recording LLM client
    var llmClient = LlmRecordingTestHelper.CreateRecordingLlmClient("TestName");

    // Use in agent options
    var options = new AgentProtocolOptions
    {
        Model = "gpt-4",
        Instructions = "You are helpful.",
        LLMClient = llmClient  // Inject recording client
    };

    // Rest of test as shown in quickstart
    // ...
}
```

### Running Tests

**Record Mode** (makes real LLM API calls):
```bash
RECORD_LLM=true dotnet test
```

**Test Mode** (replays recordings - default):
```bash
dotnet test
```

### Recording Files

Stored in `/Recordings/{TestName}/`:
```
call-0001.request.json  - LLM request (conversation history, tools)
call-0001.response.json - LLM response (agent message)
call-0002.request.json  - Next call
call-0002.response.json - Next response
```

## Benefits

✅ **Deterministic** - Same input = same output every time
✅ **Fast** - No network calls, tests run in milliseconds
✅ **Free** - No API costs
✅ **CI/CD Ready** - No credentials needed in CI
✅ **Regression Testing** - Detect API changes immediately

## Workflow

### Initial Setup (One Time)

1. Have a running agent server (for Client SDK) or LLM API key (for Hosting SDK)
2. Run tests in record mode: `RECORD_HTTP=true dotnet test` or `RECORD_LLM=true dotnet test`
3. Recordings are saved to disk
4. Commit recordings to git

### Daily Development

1. Run tests normally: `dotnet test`
2. Tests replay recordings (no server/API needed)
3. If quickstart guide changes, re-record affected tests

### Updating Recordings

When quickstart samples change:

```bash
# Delete old recordings
rm -rf dotnet/tests/*/Recordings/{TestName}

# Re-record
RECORD_HTTP=true dotnet test --filter TestName

# Verify
dotnet test --filter TestName

# Commit new recordings
git add dotnet/tests/*/Recordings/
git commit -m "Update recordings for {TestName}"
```

## Example: Complete Test Rewrite

### Before (Mock-based)

```csharp
[Fact]
public async Task Step1_SimpleCompletion()
{
    // Arrange
    var mockHandler = new Mock<HttpMessageHandler>();
    var expectedResponse = new RunResponse { /* ... complex setup ... */ };
    mockHandler.Protected()
        .Setup<Task<HttpResponseMessage>>("SendAsync", ...)
        .ReturnsAsync(new HttpResponseMessage { /* ... */ });

    var httpClient = new HttpClient(mockHandler.Object);
    var client = new AgentProtocolClient("http://localhost:5000", httpClient);

    // Act
    var response = await client.CompleteChatAsync("What can you help me with?");

    // Assert
    response.Should().Contain("help");
}
```

### After (Recording-based)

```csharp
[Fact]
[DocExample("step1_simple_completion", "Client SDK Quickstart - Step 1")]
public async Task Step1_SimpleCompletion()
{
    // Arrange
    var client = RecordingTestHelper.CreateRecordingClient("Step1_SimpleCompletion");

    // Act - Exact code from quickstart
    string response = await client.CompleteChatAsync("What can you help me with?");

    // Assert
    response.Should().NotBeNullOrEmpty();
    response.Should().Contain("help");
}
```

**Benefits**:
- 75% less code
- Matches quickstart exactly
- No complex mock setup
- Deterministic responses
- Can re-record easily

## Python & TypeScript

The same pattern applies to Python and TypeScript tests:

### Python

```python
# Using VCR.py or similar HTTP recording library
@pytest.mark.vcr
async def test_step1_simple_completion():
    client = AgentProtocolClient("http://localhost:5000")
    response = await client.complete_chat("What can you help me with?")
    assert "help" in response.lower()
```

### TypeScript

```typescript
// Using nock or similar
it('step1: simple completion', async () => {
  const client = new AgentProtocolClient("http://localhost:5000");
  const response = await client.completeChatAsync("What can you help me with?");
  expect(response).toContain("help");
});
```

## Troubleshooting

### "Recordings directory not found"

You need to run in record mode first:
```bash
RECORD_HTTP=true dotnet test
```

### "No recorded response found for hash X"

Request parameters changed. Either:
1. Re-record: `RECORD_HTTP=true dotnet test`
2. Check if test request matches quickstart guide

### "Tests fail in record mode"

- Client SDK: Ensure agent server is running on `http://localhost:5000`
- Hosting SDK: Ensure `OPENAI_API_KEY` or similar is set

## Best Practices

1. **One recording per test** - Each test has its own recording directory
2. **Match quickstart exactly** - Tests should use exact code from quickstart guides
3. **Commit recordings** - Recordings are part of the test suite
4. **Re-record when needed** - Update recordings when quickstart changes
5. **Use descriptive test names** - Makes finding recordings easier
6. **Test both modes** - Occasionally run in record mode to verify real API compatibility

## Future Enhancements

- [ ] Automatic recording refresh in CI
- [ ] Recording validation (detect stale recordings)
- [ ] Recording diff tools
- [ ] Multi-language recording format sharing
