# Integration Tests for Agent Protocol Client

This directory contains comprehensive integration tests for the TypeScript Agent Protocol Client library. These tests mirror the .NET `EchoM365IntegrationTests.cs` implementation and ensure feature parity across language implementations.

## Test File

- `integration.test.ts` - Main integration test suite

## Test Coverage

### 1. End-to-End Run Creation (XML Pattern)
Tests the basic run creation flow:
- Processes XML input files from `test-data/input`
- Creates runs using the `/runs` endpoint
- Validates run creation and response structure
- Saves results to `test-data/results/samples/echom365/xml`

### 2. Full Conversation Workflows (Wait Pattern)
Tests synchronous conversation patterns:
- Uses `/runs/wait` endpoint for blocking requests
- Validates completed run status
- Tests thread context maintenance across messages
- Saves results to `test-data/results/samples/echom365/wait`

### 3. Tool Execution Integration
Tests tool calling capabilities:
- Function call message handling
- Tool result message processing
- Tool output submission

### 4. Streaming Integration
Tests real-time streaming capabilities:
- Run creation for streaming
- SSE stream connection and event handling
- Stream lifecycle management

### 5. Error Handling Integration
Tests error scenarios:
- HTTP error responses (404, 500, etc.)
- Network errors and timeouts
- Malformed response handling
- Graceful degradation

### 6. Timeout Scenarios
Tests timeout behavior:
- Request timeout with AbortController
- Run cancellation
- Long-running operation handling

### 7. Multi-Agent Interactions
Tests multiple agent scenarios:
- Different agent IDs
- Separate thread contexts per agent
- Agent-specific configurations

### 8. XML Parser Tests
Tests XML message parsing:
- System messages
- Developer messages
- User messages with text elements
- Agent thinking content
- Function calls and results
- Empty content handling

### 9. Client API Integration
Tests high-level client APIs:
- `AgentProtocolClient` usage
- `SimplifiedClient` usage
- Conversation context management

## Mock Server

The tests include a `MockEchoM365Server` class that simulates an echo bot server:

- **Endpoints**:
  - `GET /health` - Health check
  - `POST /runs` - Create run
  - `POST /runs/wait` - Create run and wait for completion
  - `GET /runs/:runId` - Retrieve run
  - `POST /runs/:runId/cancel` - Cancel run

- **Behavior**:
  - Echoes back user input with "you said:" prefix
  - Generates unique run and thread IDs
  - Returns completed status immediately
  - Supports thread context persistence

## XML Message Parser

The `XmlMessageParser` class handles various XML input formats:

1. **Text elements**: `<text>content</text>`
2. **Direct content**: System/developer messages with direct text
3. **Thinking elements**: `<thinking>reasoning</thinking>`
4. **Function calls**: `<function-call name="fn">args</function-call>`
5. **Function results**: `<function-result>result</function-result>`
6. **Thread messages**: Nested message elements

## Running the Tests

### Prerequisites

Install dependencies:
```bash
npm install
```

### Run All Tests

```bash
npm test
```

### Run Integration Tests Only

```bash
npm test integration.test.ts
```

### Run with Coverage

```bash
npm test -- --coverage
```

### Run in Watch Mode

```bash
npm test:watch
```

## Test Data Structure

```
test-data/
├── input/                  # XML input files (shared across languages)
│   ├── 01-system-message.xml
│   ├── 02-developer-message.xml
│   └── ...
└── results/
    └── echom365/          # Results directory (language-agnostic)
        ├── xml/           # XML pattern results (TypeScript output)
        ├── wait/          # Wait pattern results (TypeScript output)
        └── streaming/     # Streaming results (TypeScript output)
```

## Key Features

### Language Parity
- Matches .NET implementation feature-for-feature
- Uses shared test data and result directories
- Compatible output formats (JSON)

### Comprehensive Coverage
- Tests all three API patterns (XML, Wait, Streaming)
- Covers success and error scenarios
- Tests both low-level and high-level APIs

### Mock-Based Testing
- No external dependencies required
- Fast execution
- Deterministic results
- Easy debugging

### Integration with Real Data
- Uses actual XML test files
- Generates real JSON results
- Can be compared with .NET results for validation

## Test Patterns

### Async/Await
All tests use async/await for cleaner asynchronous code:

```typescript
it('should process messages', async () => {
  const result = await client.completeChat('Hello');
  expect(result).toBeDefined();
});
```

### Mock Fetch
Global fetch is mocked using Jest:

```typescript
global.fetch = jest.fn();
MockEchoM365Server.setupMockServer();
```

### File System Operations
Uses Node.js fs/promises for async file operations:

```typescript
const xmlContent = await fs.readFile(inputFile, 'utf-8');
await fs.writeFile(resultPath, json, 'utf-8');
```

### Error Scenarios
Tests include explicit error handling:

```typescript
it('should handle HTTP errors', async () => {
  (global.fetch as jest.Mock).mockResolvedValueOnce({
    ok: false,
    status: 404,
  });

  const response = await fetch(url);
  expect(response.ok).toBe(false);
});
```

## Extending the Tests

To add new test cases:

1. **Add XML input file** to `test-data/input/`
2. **Run tests** to process new file automatically
3. **Verify results** in `test-data/results/samples/echom365/`

To add new test scenarios:

1. **Create test block** in appropriate describe section
2. **Use mock server** or mock fetch directly
3. **Add assertions** for expected behavior
4. **Document** the test purpose

## Debugging

### Enable Debug Output

Set debug flag in client configuration:

```typescript
const client = new SimplifiedClient({
  baseUrl: ECHO_M365_URL,
  debug: true,
});
```

### View Mock Calls

Inspect fetch mock calls:

```typescript
console.log(global.fetch.mock.calls);
```

### Check Result Files

Results are saved to disk for inspection:
- `test-data/results/samples/echom365/xml/*.json`
- `test-data/results/samples/echom365/wait/*.json`

## CI/CD Integration

These tests are designed to run in CI/CD pipelines:
- No external service dependencies
- Fast execution (< 30 seconds)
- Deterministic results
- Clear pass/fail indicators

## Comparison with .NET Tests

| Feature | .NET | TypeScript |
|---------|------|------------|
| XML Pattern | ✅ | ✅ |
| Wait Pattern | ✅ | ✅ |
| Streaming | ✅ | ✅ |
| Tool Execution | ✅ | ✅ |
| Error Handling | ✅ | ✅ |
| Timeouts | ✅ | ✅ |
| Multi-Agent | ✅ | ✅ |
| XML Parser | ✅ | ✅ |
| Mock Server | ✅ | ✅ |
| Shared Test Data | ✅ | ✅ |

## Contributing

When adding new tests:
1. Follow existing test patterns
2. Use descriptive test names
3. Add comments for complex logic
4. Ensure tests are deterministic
5. Update this README if adding new test categories
