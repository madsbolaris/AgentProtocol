# Testing Quick Start

This guide shows you how to run the new integration tests that prevent authentication and CORS issues.

## Quick Test Commands

### Python Echo Bot
```bash
cd python/samples/agents/echo-bot

# Run integration tests
pytest tests/test_integration_anonymous.py -v

# Run with detailed output
pytest tests/test_integration_anonymous.py -v -s

# Run specific test
pytest tests/test_integration_anonymous.py::TestCORSHeaders::test_root_endpoint_has_cors_headers -v
```

### TypeScript Echo Bot
```bash
cd typescript/samples/EchoBot

# Run integration tests
npm test -- Anonymous.test.ts

# Run with verbose output
npm test -- Anonymous.test.ts --verbose

# Run specific test suite
npm test -- Anonymous.test.ts -t "CORS Headers"
```

## What These Tests Catch

✅ **Authentication Issues**
- Verifies bot works without Azure credentials
- Tests anonymous mode configuration
- Catches auth failures before production

✅ **CORS Errors**
- Checks CORS headers on all endpoints
- Validates OPTIONS preflight requests
- Ensures browser compatibility

✅ **Route Conflicts**
- Detects duplicate route registration
- Verifies all endpoints are accessible
- Catches startup errors

✅ **Message Processing**
- Tests end-to-end message flow
- Validates Bot Framework Activity format
- Checks response structure

## Running All Tests

### Run Everything (Python + TypeScript)
```bash
# From repository root
pytest python/samples/agents/echo-bot/tests/test_integration_anonymous.py -v && \
  (cd typescript/samples/EchoBot && npm test -- Anonymous.test.ts)
```

## Test Output Examples

### ✅ Successful Test Run (Python)
```
tests/test_integration_anonymous.py::TestAnonymousModeEndpoints::test_root_endpoint_returns_ok PASSED
tests/test_integration_anonymous.py::TestAnonymousModeEndpoints::test_health_endpoint_returns_healthy PASSED
tests/test_integration_anonymous.py::TestCORSHeaders::test_root_endpoint_has_cors_headers PASSED
tests/test_integration_anonymous.py::TestEchoBotFunctionality::test_echo_bot_echoes_simple_message PASSED

====== 4 passed in 2.34s ======
```

### ✅ Successful Test Run (TypeScript)
```
PASS tests/Anonymous.test.ts
  Anonymous Mode Integration Tests
    Endpoint Tests
      ✓ should return 200 OK from root endpoint (45ms)
      ✓ should accept and process Bot Framework Activity messages (38ms)
    CORS Headers
      ✓ should include CORS headers in root endpoint (21ms)
      ✓ should handle OPTIONS preflight request (19ms)

Test Suites: 1 passed, 1 total
Tests:       4 passed, 4 total
```

## Troubleshooting

### Python: ModuleNotFoundError
```bash
# Install dependencies
pip install -r requirements.txt

# Or use virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### TypeScript: Cannot find module
```bash
# Install dependencies
npm install

# Rebuild
npm run build
```

### Tests fail with "Address already in use"
```bash
# Kill existing bot processes
pkill -f "python.*src.main"
pkill -f "node.*dist.*index"

# Or use specific ports
lsof -ti:3979 | xargs kill -9  # Python
lsof -ti:3980 | xargs kill -9  # TypeScript
```

## CI/CD Integration

These tests are designed to run in CI/CD pipelines. Add to your workflow:

**GitHub Actions:**
```yaml
- name: Run Python Integration Tests
  run: |
    cd python/samples/agents/echo-bot
    pytest tests/test_integration_anonymous.py -v

- name: Run TypeScript Integration Tests
  run: |
    cd typescript/samples/EchoBot
    npm test -- Anonymous.test.ts
```

## Next Steps

- 📖 Read full documentation: [`docs/testing/integration-testing.md`](docs/testing/integration-testing.md)
- 🔍 See test implementation:
  - Python: `python/samples/agents/echo-bot/tests/test_integration_anonymous.py`
  - TypeScript: `typescript/samples/EchoBot/tests/Anonymous.test.ts`
- 🚀 Add tests for your custom bots using these as templates

## Issues Fixed by These Tests

| Issue | Before | After |
|-------|--------|-------|
| Route collision | ❌ Not tested | ✅ Detected at test time |
| CORS errors | ❌ Found in browser | ✅ Caught by tests |
| Auth failures | ❌ Runtime error | ✅ Test failure |
| Anonymous mode | ❌ Not verified | ✅ Fully tested |

---

**Questions?** See [docs/testing/integration-testing.md](docs/testing/integration-testing.md) for detailed information.
