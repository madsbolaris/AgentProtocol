# .NET Test Suite - Complete System

## ✅ What's Complete

### 1. Client SDK Tests
- **File**: `Microsoft.Agents.Client.Tests/QuickstartSamplesTests.cs`
- **Tests**: 9 tests covering all quickstart scenarios
- **Features**:
  - ✅ HTTP recording/replay infrastructure
  - ✅ Snippet extraction markers (`[DocExample]`)
  - ✅ Proper Arrange/Act/Assert structure
  - ✅ Act sections contain only user-facing code
  - ✅ All tests use actual SDK APIs

### 2. Recording Infrastructure
- **HttpRecorder.cs** - Records HTTP request/response pairs
- **HttpPlayer.cs** - Replays recorded HTTP responses
- **RecordingHttpMessageHandler.cs** - HttpMessageHandler for recording
- **RecordingTestHelper.cs** - Helper for creating recording clients
- **LlmRecordingTestHelper.cs** - Helper for LLM recording (Hosting SDK)
- **ReplayProtocolLlmClient.cs** - Replays LLM responses

### 3. Snippet Extraction
- **Universal extractor**: `scripts/extract-snippets.py` (works for all languages)
- **Verification script**: `scripts/verify-snippets.sh`
- **Documentation**: `docs/snippets/README.md`, `scripts/README.md`

## 🎯 Test Coverage

| Step | Test | Snippet ID | Status |
|------|------|-----------|---------|
| 1 | Simple Completion | `client-simple-completion` | ✅ |
| 2 | Multimodal Content | `client-multimodal` | ✅ |
| 3 | Persistent Conversations | `client-persistent-conversations` | ✅ |
| 3 | Resume Conversation | `client-resume-conversation` | ✅ |
| 4 | Tools/Functions | `client-tools` | ✅ |
| 5 | Simple Streaming | `client-simple-streaming` | ✅ |
| 5 | Rich Streaming | `client-rich-streaming` | ✅ |
| 5 | Thread Messages | `client-thread-messages` | ✅ |
| - | Error Handling | `client-error-handling` | ✅ |

## 🚀 Usage

### Run Tests

```bash
# Replay mode (default) - uses recordings
cd dotnet/tests/Microsoft.Agents.Client.Tests
dotnet test

# Record mode - makes real HTTP calls
RECORD_HTTP=true dotnet test
```

### Extract Snippets

```bash
# Extract C# snippets for docs
python3 scripts/extract-snippets.py csharp

# Or extract all languages
python3 scripts/extract-snippets.py all
```

### Verify Snippets

```bash
# Check if snippets are up-to-date
./scripts/verify-snippets.sh
```

## 📝 Test Structure

Each test follows this pattern:

```csharp
[Fact]
[DocExample("snippet-id", "Display Title")]
public async Task TestName()
{
    // Arrange - Test setup (not in snippet)
    var client = RecordingTestHelper.CreateRecordingClient("TestName");

    // Act - Exact code from quickstart
    // This section is extracted to docs/snippets/csharp/snippet-id_main.cs
    var result = await client.SomeMethod();
    Console.WriteLine(result);

    // Assert - Test validation (not in snippet)
    result.Should().NotBeNull();
}
```

## 🔄 Workflow

### Adding a New Test

1. **Write the test** with proper structure:
   ```csharp
   [DocExample("client-new-feature", "New Feature")]
   public async Task NewFeature_Works()
   {
       // Arrange - Test setup (not in snippet)
       var client = RecordingTestHelper.CreateRecordingClient("NewFeature");

       // Act - Exact code from quickstart
       var result = await client.NewFeatureAsync();
       Console.WriteLine(result);

       // Assert - Test validation (not in snippet)
       result.Should().NotBeNull();
   }
   ```

2. **Record HTTP interactions**:
   ```bash
   RECORD_HTTP=true dotnet test --filter NewFeature
   ```

3. **Extract snippet**:
   ```bash
   python3 scripts/extract-snippets.py csharp
   ```

4. **Update docs** to reference the snippet:
   ```markdown
   ```csharp
   --8<-- "docs/snippets/csharp/client-new-feature_main.cs"
   ```
   ```

5. **Commit**:
   ```bash
   git add dotnet/tests/ docs/snippets/csharp/
   git commit -m "Add new feature example"
   ```

### 4. Hosting SDK Tests (Conceptual)

- **File**: `Microsoft.Agents.Protocol.Hosting.Tests/HostingQuickstartSamplesTests.cs`
- **Tests**: 13 tests covering hosting quickstart scenarios
- **Features**:
  - ✅ Snippet extraction markers (`[DocExample]`)
  - ✅ Proper Arrange/Act/Assert structure
  - ✅ Act sections contain user-facing code
  - ⚠️ **Design intent tests** - demonstrate intended API (not current implementation)
- **Note**: See [README_QUICKSTART_TESTS.md](Microsoft.Agents.Protocol.Hosting.Tests/README_QUICKSTART_TESTS.md) for API mismatch details

## 🎯 Hosting Test Coverage

| Step | Test                    | Snippet ID                     | Status        |
|------|-------------------------|--------------------------------|---------------|
| 1    | Hello World             | `hosting-hello-world`          | ⚠️ Conceptual |
| 2    | Adding Tools            | `hosting-adding-tools`         | ⚠️ Conceptual |
| 3    | Client Functions        | `hosting-client-functions`     | ⚠️ Conceptual |
| 4    | Command Router          | `hosting-command-router`       | ⚠️ Conceptual |
| 4    | Reaction Handler        | `hosting-reaction-handler`     | ⚠️ Conceptual |
| 4    | Streaming Middleware    | `hosting-streaming-middleware` | ⚠️ Conceptual |
| 4    | Before/After Middleware | `hosting-before-after`         | ⚠️ Conceptual |
| 4    | Message Middleware      | `hosting-message-middleware`   | ⚠️ Conceptual |
| 4    | Error Handling          | `hosting-error-handling`       | ⚠️ Conceptual |
| 6    | In-Memory Storage       | `hosting-inmemory-storage`     | ⚠️ Conceptual |
| 6    | Durable Storage         | `hosting-durable-storage`      | ⚠️ Conceptual |
| -    | Tool Error Handling     | `hosting-tool-error-handling`  | ⚠️ Conceptual |

## ⏭️ Next Steps

### Hosting SDK

- [ ] Align SDK implementation with conceptual API shown in tests, OR
- [ ] Rewrite tests to use actual `AgentBuilder` fluent API

### CI Integration

- [ ] Add snippet verification to GitHub Actions
- [ ] Add pre-commit hook for snippet extraction
- [ ] Run tests in both record and replay modes

## 📚 Documentation

- **Recording**: [dotnet/tests/README_RECORDING.md](README_RECORDING.md)
- **Snippets**: [docs/snippets/README.md](../../docs/snippets/README.md)
- **Universal Extractor**: [scripts/README.md](../../scripts/README.md)

## 🎉 Benefits

✅ **Docs always match tested code** - No drift between docs and reality
✅ **Fast tests** - No network calls in replay mode
✅ **Free tests** - No API costs
✅ **Deterministic** - Same input = same output
✅ **CI-friendly** - No credentials needed
✅ **Easy to update** - Re-record when SDK changes

---

**Status**:

- ✅ Client SDK tests complete and fully functional
- ⚠️ Hosting SDK tests complete (conceptual/design intent)
- ✅ Universal snippet extraction system ready
- ✅ Recording infrastructure in place
