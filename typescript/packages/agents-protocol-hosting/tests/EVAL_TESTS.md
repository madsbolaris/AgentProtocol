# Evaluation Integration Tests

This directory contains integration tests for the Agent Protocol evaluation system using mock LLM responses.

## Overview

These tests validate that the evaluation framework works correctly by:

1. **Loading Eval XML Files** - Reading evaluation definitions from `test-data/input/evals/`
2. **Running Evaluations** - Executing evals using deterministic mock LLM responses
3. **Validating Results** - Comparing outputs against golden files in `test-data/results/evals/`

**Key Benefits:**
- ✅ **Deterministic** - Same results every time
- ⚡ **Fast** - No real LLM API calls
- 💰 **Free** - No API costs
- 🔒 **No API Keys Required** - Works offline

## Test Architecture

### Mock LLM System

The tests use a recording/replay system for LLM interactions:

```
┌─────────────────┐
│  Eval Test      │
│  (TypeScript)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MockLLMClient   │  Replays recorded responses
│                 │  based on request hash
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Recordings  │  test-data/llm-recordings/evals/
│ {hash}.json     │  - Request/response pairs
└─────────────────┘
```

### Directory Structure

```
typescript/packages/agents-hosting/
├── tests/
│   ├── EvalIntegration.test.ts    ← Integration tests
│   └── EVAL_TESTS.md              ← This file
│
typescript/packages/test-helpers/
├── src/
│   ├── llmRecorder.ts             ← Hash-based request matching
│   ├── mockLLMClient.ts           ← Mock LLM client
│   └── evalTestHelpers.ts         ← Golden file utilities
│
test-data/                          ← At repository root
├── input/
│   └── evals/                     ← Eval XML definitions
│       ├── 01-simple-text-expect.xml
│       ├── 02-multiple-expects.xml
│       └── ...
├── results/
│   └── evals/
│       └── json/                  ← Golden result files
│           ├── 01-simple-text-expect-result.json
│           └── ...
└── llm-recordings/
    └── evals/                     ← Recorded LLM interactions
        ├── a1b2c3d4e5f6g7h8.request.json
        ├── a1b2c3d4e5f6g7h8.response.json
        └── ...
```

## Running Tests

### Test Mode (Default)

Runs tests using existing golden files and LLM recordings:

```bash
# Run all eval integration tests
npm test -- EvalIntegration.test.ts

# Run with verbose output
npm test -- EvalIntegration.test.ts --verbose

# Run specific test suite
npm test -- EvalIntegration.test.ts -t "Mock LLM Client"
```

**Requirements:**
- Golden files must exist in `test-data/results/evals/json/`
- LLM recordings must exist in `test-data/llm-recordings/evals/`

If these don't exist, run generation mode first.

### Generation Mode

Generates golden files and LLM recordings by running live evals:

```bash
# Generate golden files and recordings
TEST_MODE=generate npm test -- EvalIntegration.test.ts

# Or set environment variable
export TEST_MODE=generate
npm test -- EvalIntegration.test.ts
```

**Requirements:**
- Valid LLM API key configured
- Network connectivity
- Costs real API credits

⚠️ **Note:** Generation mode should only be run when:
- Adding new eval test cases
- Updating expected behavior
- Regenerating after eval framework changes

## Test Categories

### Environment Setup Tests
Validates test environment configuration:
- Test mode is set correctly
- Test data directory exists
- Eval XML files are present

### Input File Loading Tests
Tests loading and parsing eval XML files:
- Loads XML from `test-data/input/evals/`
- Validates XML structure
- Confirms required elements exist

### Mock LLM Client Tests
Tests the mock LLM replay system:
- Creates MockLLMClient with recordings directory
- Replays recorded LLM responses
- Matches requests using SHA256 hash
- Returns deterministic results

### Eval Structure Tests
Validates eval XML structure:
- Correct thread ID format
- User messages present
- Expectations defined
- Judges and asserts configured

### Golden File Tests
Tests golden file management:
- Checks for existing golden files
- Loads and compares results
- Reports missing golden files

### Data-Driven Tests
Parameterized tests for all eval files:
- Dynamically discovers eval XML files
- Runs validation for each file
- Provides comprehensive coverage

## How It Works

### 1. Request Hashing

When an LLM request is made, `LLMRecorder` generates a deterministic hash:

```typescript
const hash = recorder.hashRequest(
  model,        // e.g., "gpt-4"
  messages,     // conversation history
  tools,        // function definitions
  temperature,  // 0.0 for deterministic
  seed          // random seed
);
// → "a1b2c3d4e5f6g7h8"
```

The hash is based on:
- Model name
- Message content (roles and text)
- Tool definitions
- Temperature setting
- Random seed

**Same inputs → Same hash → Same response**

### 2. Response Replay

`MockLLMClient` uses the hash to load recorded responses:

```typescript
const mockClient = new MockLLMClient(recordingsDir);

// Replays response from a1b2c3d4e5f6g7h8.response.json
const completion = await mockClient.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: 'Hello' }],
  temperature: 0.0,
  seed: 42
});
```

### 3. Golden File Validation

Test results are compared against golden files:

```typescript
import { loadGoldenFile, assertEvalResultsSimilar } from '@microsoft/agents-test-helpers';

// Load expected result
const expected = loadGoldenFile('01-simple-text-expect', 'json', 'evals');

// Run eval and get actual result
const actual = await runEval(evalXml);

// Compare
assertEvalResultsSimilar(actual, expected);
```

## Eval Test Files

Current eval scenarios (from `test-data/input/evals/`):

| File | Description | Tests |
|------|-------------|-------|
| `01-simple-text-expect.xml` | Basic text expectation | Exact text matching |
| `02-multiple-expects.xml` | Multiple expectations | Multiple validation points |
| `03-with-run-config.xml` | Custom run configuration | Config handling |
| `04-tool-call-expect.xml` | Tool/function calls | Tool invocation |
| `05-llm-judge.xml` | LLM-based judging | Semantic evaluation |
| `06-regex-judge.xml` | Regex pattern matching | Pattern validation |
| `07-multi-turn-conversation.xml` | Multi-turn dialogue | Conversation flow |
| `08-multiple-asserts.xml` | Multiple assertions | Complex validation |
| `09-json-output-expect.xml` | JSON output validation | Structured output |
| `10-numeric-comparison.xml` | Numeric comparisons | Number validation |
| ... | ... | ... |

*See `test-data/input/evals/` for complete list (01-50)*

## Common Issues

### "Recordings directory not found"

**Cause:** LLM recordings haven't been generated yet.

**Solution:** Run generation mode first:
```bash
TEST_MODE=generate npm test -- EvalIntegration.test.ts
```

### "Golden file not found"

**Cause:** Expected result files don't exist.

**Solution:** Generate golden files:
```bash
TEST_MODE=generate npm test -- EvalIntegration.test.ts
```

### "No recorded LLM response found for request hash"

**Cause:** Request parameters changed, creating a different hash.

**Solution:**
1. Check if request parameters match recordings
2. Regenerate recordings in generation mode
3. Verify temperature=0.0 and seed are consistent

### Test failures after code changes

**Cause:** Behavior changed, golden files outdated.

**Solution:**
1. Review changes to ensure they're intentional
2. Regenerate golden files if behavior is correct:
   ```bash
   TEST_MODE=generate npm test -- EvalIntegration.test.ts
   ```
3. Commit updated golden files

## Adding New Eval Tests

1. **Create Eval XML File**
   ```bash
   # Add to test-data/input/evals/
   touch test-data/input/evals/51-my-new-test.xml
   ```

2. **Define Evaluation**
   ```xml
   <thread threadId="eval-051">
     <message role="user">
       <text>Your test prompt</text>
     </message>
     <expect name="check_response">
       <referenceOutput>Expected behavior</referenceOutput>
       <judges>
         <judge agent="regex" pattern="your.*pattern"/>
       </judges>
     </expect>
   </thread>
   ```

3. **Generate Golden Files and Recordings**
   ```bash
   TEST_MODE=generate npm test -- EvalIntegration.test.ts -t "51-my-new-test"
   ```

4. **Verify Tests Pass**
   ```bash
   npm test -- EvalIntegration.test.ts -t "51-my-new-test"
   ```

5. **Commit Everything**
   ```bash
   git add test-data/input/evals/51-my-new-test.xml
   git add test-data/results/evals/json/51-my-new-test-result.json
   git add test-data/llm-recordings/evals/*.json
   git commit -m "Add eval test: my new test"
   ```

## Best Practices

### For Test Authors

1. **Use Deterministic Settings**
   - Always set `temperature: 0.0`
   - Always set a consistent `seed`
   - This ensures reproducible results

2. **Keep Evals Focused**
   - One eval = one scenario
   - Clear test names
   - Descriptive expectations

3. **Document Expectations**
   - Explain what behavior is being tested
   - Include context in XML comments
   - Update EVAL_TESTS.md

### For Reviewers

1. **Review Eval Definitions**
   - Check XML files make sense
   - Verify expectations are clear
   - Ensure patterns are correct

2. **Review Golden Files**
   - Check results are reasonable
   - Verify success/failure states
   - Confirm error messages are helpful

3. **Review LLM Recordings**
   - Spot-check recorded responses
   - Verify they match expectations
   - Check for sensitive data

## TypeScript-Specific Notes

### Module System

Tests use ES modules (`.mjs`):
- Import with `.js` extensions in TypeScript
- Use `import` instead of `require`
- Configured in `jest.config.js`

### Type Safety

All test utilities are fully typed:
```typescript
import type {
  EvalResult,
  ExpectResult,
  MockChatCompletion
} from '@microsoft/agents-test-helpers';
```

### Async/Await

All LLM operations are async:
```typescript
const completion = await mockClient.chat.completions.create({...});
```

## Related Documentation

- **Python Implementation:** `python/microsoft-agents-protocol/tests/integration/`
- **.NET Implementation:** `dotnet/tests/Microsoft.Agents.Evaluators.Tests/Integration/`
- **Eval Framework:** `docs/evaluation-framework.md`
- **Test Data:** `test-data/README.md`

## Support

For questions or issues:
1. Check this documentation
2. Review existing tests as examples
3. Check test output for detailed error messages
4. Consult team documentation
