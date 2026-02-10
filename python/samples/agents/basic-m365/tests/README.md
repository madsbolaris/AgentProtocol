# BasicM365 Python Tests

## ⚠️ NO INTEGRATION TESTS HERE

**All integration tests must be written in .NET and run through the .NET test projects.**

This directory should only contain:
- ✅ Unit tests for Python-specific functionality
- ✅ Compliance tests (auto-generated from TypeSpec)
- ❌ **NO integration tests** - Use .NET golden file tests instead

## Why?

Integration tests validate cross-language behavior and must test all implementations (Python, .NET, TypeScript) consistently. The .NET golden file tests provide comprehensive cross-language integration testing:

- **Golden File Tests**: `dotnet/tests/BasicM365Agent.Tests/IntegrationTests/BasicM365AgentGoldenFileTests.cs`
  - Tests Python, .NET, and TypeScript implementations
  - Validates responses against shared golden files in `test-data/results/`
  - Ensures all three implementations behave identically

## Running Tests

```bash
# Python unit tests only
pytest python/samples/agents/basic-m365/tests/

# Integration tests (runs against all languages)
dotnet test dotnet/tests/BasicM365Agent.Tests --filter "Category=GoldenFileIntegration"
```

## What Goes Here?

- `test_compliance.py` - Auto-generated TypeSpec compliance tests
- Unit tests for Python-specific utilities (if any)

## What DOES NOT Go Here?

- ❌ Integration tests
- ❌ End-to-end tests
- ❌ Cross-language validation tests
- ❌ Tests that start servers or make HTTP requests

**Remember: If you're testing the bot behavior, use .NET golden file tests!**
