# Evaluation System Integration Tests

## Overview

This directory contains integration tests for the Agent Protocol evaluation system using the mock LLM pattern for deterministic, fast, cost-free testing.

## Architecture

The integration tests follow the pattern established in the Python test suite:

1. **Mock LLM Client** (`Mocks/MockLLMClient.cs`): Replays recorded LLM responses instead of making real API calls
2. **Test Helpers** (`Helpers/TestHelpers.cs`): Utilities for loading test data and golden files
3. **Integration Tests** (`Integration/EvalIntegrationTests.cs`): Test cases that run evaluations using mock responses

## How It Works

### 1. Test Data Structure

```
test-data/
├── input/evals/              # Evaluation XML files
│   ├── 01-simple-text-expect.xml
│   ├── 02-multiple-expects.xml
│   └── ...
├── llm-recordings/evals/     # Recorded LLM request/response pairs
│   ├── abc123def456.request.json
│   ├── abc123def456.response.json
│   └── ...
└── results/evals/            # Golden files (expected results)
    ├── json/
    │   ├── 01-simple-text-expect-result.json
    │   └── ...
    └── xml/
        └── ...
```

### 2. Mock LLM Pattern

The `MockLLMClient` uses deterministic hashing to match requests to recorded responses:

- **Request Hash**: SHA256 hash of normalized request (model, messages, tools, temperature, seed)
- **Recording Lookup**: `{hash}.response.json` files contain pre-recorded LLM responses
- **Deterministic**: Same request always gets same response (no randomness, no API calls)

### 3. Test Flow

```
Load Eval XML → Parse with EvalXmlSerializer
                ↓
                Run with EvalRunner (uses recorded agent responses in XML)
                ↓
                Validate with TestHelpers → Compare against golden files
```

## Running Tests

### Run all integration tests:
```bash
dotnet test --filter Category=Integration
```

### Run specific test:
```bash
dotnet test --filter "FullyQualifiedName~EvalIntegrationTests.CanLoadAndDeserializeEvalXml"
```

### Run with verbose output:
```bash
dotnet test --filter Category=Integration --logger "console;verbosity=detailed"
```

## Test Cases

The integration tests cover:

- **01-simple-text-expect**: Simple text expectation with exact match
- **02-multiple-expects**: Multiple expectations in one evaluation
- **05-llm-judge**: LLM-based semantic similarity judging
- **06-regex-judge**: Regex pattern matching

Tests validate:
- ✅ XML deserialization
- ✅ Evaluation execution
- ✅ Judge evaluation (text match, regex, semantic similarity)
- ✅ Assert evaluation
- ✅ Result structure and correctness

## Key Features

### 🚀 Fast
- No real LLM API calls
- Tests run in milliseconds
- Suitable for CI/CD pipelines

### 💰 Free
- No API costs
- No credentials needed
- Can run anywhere

### 🎯 Deterministic
- Same input = same output always
- No flakiness from LLM variability
- Reliable for regression testing

### 📊 Comprehensive
- Tests actual eval XML files from test-data
- Validates full evaluation pipeline
- Covers various judge types and assertions

## Mock LLM Client Implementation

The `MockLLMClient` closely mirrors the Python `MockLLMClient` and the `LLMPlayer` used in `BasicM365Agent`:

```csharp
// Create mock client
var mockClient = new MockLLMClient("/path/to/recordings");

// Create completion (replays recording)
var completion = await mockClient.CreateChatCompletionAsync(
    model: "gpt-5-nano",
    messages: messages,
    tools: tools,
    temperature: 0.0f,
    seed: 42
);
```

### Request Hashing Algorithm

1. Normalize request parameters (messages, tools, etc.)
2. Serialize to stable JSON (sorted keys)
3. SHA256 hash → take first 16 chars
4. Load `{hash}.response.json`

This ensures:
- Same request parameters = same hash
- Consistent lookups across test runs
- Compatibility with Python recordings

## Test Helper Utilities

### `TestHelpers` class provides:

```csharp
// Get test mode (generate vs test)
var mode = TestHelpers.GetTestMode();

// Load test data
var inputXml = TestHelpers.LoadInputFile("01-simple-text-expect");
var golden = TestHelpers.LoadGoldenFile<EvalResult>("01-simple-text-expect");

// Create mock LLM client
var mockClient = TestHelpers.CreateMockLLMClient();

// Validate results
TestHelpers.AssertEvalResultStructure(result);
TestHelpers.AssertExpectPassed(expectResult, "correct-answer");
TestHelpers.AssertEvalResultsSimilar(actual, expected);
```

## Creating New Test Cases

1. **Add eval XML**: Create new file in `test-data/input/evals/`
2. **Generate recordings**: Run agent with `RECORD_LLM=true` (if needed)
3. **Generate golden files**: Run with `TEST_MODE=generate` (if needed)
4. **Add test case**: Add `[InlineData("new-test-name")]` to test methods

## Environment Variables

- `TEST_MODE`: Set to `"test"` for validation (default), `"generate"` for golden file creation
- `USE_LLM_RECORDINGS`: Set to `"true"` to use mock LLM (automatic in tests)

## Comparison with Python Tests

The .NET integration tests mirror the Python implementation:

| Feature | Python | .NET |
|---------|--------|------|
| Mock LLM Client | `MockLLMClient` | `MockLLMClient` |
| Test Helpers | `test_helpers.py` | `TestHelpers.cs` |
| Integration Tests | `test_basic_m365_integration.py` | `EvalIntegrationTests.cs` |
| Framework | pytest | xUnit |
| Test Data | `test-data/` | `test-data/` |
| Recordings | `llm-recordings/` | `llm-recordings/` |

## Troubleshooting

### "Recordings directory not found"
Ensure `test-data/llm-recordings/evals/` exists with recording files.

### "No recorded LLM response found"
- Request parameters changed (different hash)
- Recording file missing or deleted
- Run generation mode first to create recordings

### "Golden file not found"
Run tests with `TEST_MODE=generate` to create golden files.

## See Also

- Python tests: `python/microsoft-agents-protocol/tests/integration/`
- BasicM365Agent: `dotnet/samples/agents/BasicM365Agent/` (LLMPlayer/LLMRecorder)
- Test data: `test-data/input/evals/`
