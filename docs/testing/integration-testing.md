# Integration Testing Strategy

This document outlines the integration testing strategy for Agent Protocol implementations, focusing on catching real-world issues before they reach production.

## Overview

Integration tests verify that the complete system works correctly, including:
- HTTP endpoints and routing
- Authentication and authorization (or lack thereof in anonymous mode)
- CORS configuration
- Message processing end-to-end
- Error handling

## Why Integration Tests Matter

### Issues Caught by Integration Tests

The following production issues were discovered and would have been caught by proper integration tests:

1. **Route Collision** - Both Python and TypeScript bots registered `/api/messages` twice, causing 500 errors
2. **Authentication Failures** - Bots failed in anonymous mode due to missing auth credentials
3. **CORS Errors** - Browser requests failed due to missing CORS headers on root endpoint
4. **Namespace Package Issues** - Python package imports failed due to incomplete namespace configuration

### Test Coverage Gaps (Before Fix)

| Area | Previous Coverage | Issue |
|------|------------------|-------|
| HTTP Endpoints | ❌ None | Route conflicts not detected |
| Anonymous Mode | ❌ None | Auth failures not tested |
| CORS Headers | ❌ None | Browser compatibility issues |
| End-to-End | ❌ Limited | Only tested with mocks |

## Integration Test Suites

### Python: `test_integration_anonymous.py`

**Location:** `python/samples/agents/echo-m365/tests/test_integration_anonymous.py`

**Run Tests:**
```bash
cd python/samples/agents/echo-m365
pytest tests/test_integration_anonymous.py -v
```

**Test Categories:**

1. **Anonymous Mode Endpoints** - Verifies bot works without authentication
   - ✅ Root endpoint returns 200 OK
   - ✅ Health check endpoint works
   - ✅ `/api/messages` accepts Bot Framework activities

2. **CORS Headers** - Ensures browser compatibility
   - ✅ All endpoints include CORS headers
   - ✅ OPTIONS preflight requests succeed
   - ✅ Access-Control-Allow-Origin is set to `*`

3. **Echo M365 Functionality** - Validates message processing
   - ✅ Bot echoes back user messages
   - ✅ Bot responds to special commands (e.g., "hello")

4. **Route Configuration** - Checks for conflicts
   - ✅ No duplicate route registration
   - ✅ Agent Protocol routes are registered

### TypeScript: `Anonymous.test.ts`

**Location:** `typescript/samples/EchoM365/tests/Anonymous.test.ts`

**Run Tests:**
```bash
cd typescript/samples/EchoM365
npm test -- Anonymous.test.ts
```

**Test Categories:**

1. **Endpoint Tests** - Verifies HTTP responses
   - ✅ Root endpoint returns correct response
   - ✅ Health endpoint works
   - ✅ `/api/messages` processes activities

2. **CORS Headers** - Browser compatibility
   - ✅ All endpoints include CORS headers
   - ✅ OPTIONS preflight handling

3. **Echo M365 Functionality** - Message processing
   - ✅ Messages are echoed correctly
   - ✅ Message count is tracked

4. **Anonymous Mode Configuration** - Auth testing
   - ✅ Bot works without clientId/clientSecret
   - ✅ No authentication headers required

5. **Error Handling** - Graceful failures
   - ✅ Malformed messages handled correctly

## Running All Integration Tests

### Python
```bash
# Run all integration tests
pytest python/samples/agents/echo-m365/tests/test_integration_anonymous.py -v

# Run with coverage
pytest python/samples/agents/echo-m365/tests/test_integration_anonymous.py --cov=src --cov-report=html

# Run specific test class
pytest python/samples/agents/echo-m365/tests/test_integration_anonymous.py::TestAnonymousModeEndpoints -v
```

### TypeScript
```bash
# Run all integration tests
npm test -- Anonymous.test.ts

# Run specific test suite
npm test -- Anonymous.test.ts -t "CORS Headers"

# Run with coverage
npm test -- --coverage Anonymous.test.ts
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pytest python/samples/agents/echo-m365/tests/test_integration_anonymous.py -v

  test-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: npm ci
      - run: npm test -- Anonymous.test.ts
```

## Test Development Guidelines

### Writing Effective Integration Tests

1. **Test Real HTTP Requests** - Use actual HTTP clients, not mocks
```python
# ✅ Good: Tests actual HTTP endpoint
response = await test_client.post("/api/messages", json=message)

# ❌ Bad: Mocks bypass routing issues
mock_handler = MagicMock()
```

2. **Verify CORS Headers** - Check actual response headers
```typescript
// ✅ Good: Verifies actual headers
expect(response.headers['access-control-allow-origin']).toBe('*')

// ❌ Bad: Assumes CORS works
```

3. **Test Anonymous Mode** - Verify auth is optional
```python
# ✅ Good: Tests without credentials
authConfig.clientId = ''
authConfig.clientSecret = ''

# ❌ Bad: Always provides credentials
```

4. **Check Route Configuration** - Ensure no conflicts
```typescript
// ✅ Good: Tests route registration
await testServer.get('/health').expect(200)

// ❌ Bad: Skips route testing
```

## Common Issues and Solutions

### Issue: Tests Pass but Production Fails

**Problem:** Tests use mocks that don't match production behavior

**Solution:** Use real HTTP requests in tests
```python
# Instead of:
mock_adapter.process = MagicMock()

# Use:
async with test_client.post('/api/messages') as response:
    assert response.status == 200
```

### Issue: CORS Works in Tests but Fails in Browser

**Problem:** Tests don't verify actual CORS headers

**Solution:** Check response headers explicitly
```typescript
expect(response.headers['access-control-allow-origin']).toBe('*')
expect(response.headers['access-control-allow-methods']).toContain('POST')
```

### Issue: Route Conflicts Not Detected

**Problem:** Tests don't verify route registration

**Solution:** Test that server starts without errors
```python
# Server startup with duplicate routes would fail
await test_client.start_server()  # Would raise if routes conflict
```

## Test Maintenance

### When to Update Tests

- ✅ When adding new endpoints
- ✅ When changing authentication logic
- ✅ When modifying CORS configuration
- ✅ When updating route registration
- ✅ When changing message formats

### Test Review Checklist

Before merging code:
- [ ] All integration tests pass
- [ ] New endpoints have integration tests
- [ ] CORS headers are tested
- [ ] Anonymous mode is tested (if applicable)
- [ ] Error cases are covered

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [supertest documentation](https://github.com/ladjs/supertest)
- [CORS documentation](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Bot Framework Activity schema](https://docs.microsoft.com/en-us/azure/bot-service/rest-api/bot-framework-rest-connector-activities)

## See Also

- [Golden Files Testing](../contributing/golden-files.md)
- [Test-Driven Documentation](../contributing/test-driven-docs.md)
- [Contributing Guide](../../CONTRIBUTING.md)
