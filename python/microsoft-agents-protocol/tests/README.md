# Microsoft Agents Protocol - Python Tests

## ⚠️ NO INTEGRATION TESTS HERE

**All integration tests must be written in .NET and run through the .NET test projects.**

This directory should only contain:
- ✅ Unit tests for Python protocol implementation
- ✅ Compliance tests (auto-generated from TypeSpec)
- ❌ **NO integration tests** - Use .NET tests instead

## Why?

The Agent Protocol must work consistently across all language implementations (Python, .NET, TypeScript). Integration tests that validate protocol behavior must test all implementations and are therefore maintained in .NET:

- **Cross-Language Tests**: `dotnet/tests/EchoM365.Tests/IntegrationTests/EchoM365GoldenFileTests.cs`
- **Client Tests**: `dotnet/tests/Microsoft.Agents.Client.Tests/EchoM365IntegrationTests.cs`
- **Protocol Compliance**: `dotnet/tests/Microsoft.Agents.Protocol.Tests/Compliance/`

## Test Organization

```
python/microsoft-agents-protocol/tests/
├── README.md (this file)
├── compliance/           # TypeSpec compliance tests
│   ├── test_echom365_compliance.py
│   └── test_basicm365_compliance.py
├── conftest.py          # Pytest configuration
└── [unit tests only]    # Python-specific unit tests
```

## Running Tests

```bash
# Python unit tests only
pytest python/microsoft-agents-protocol/tests/

# Integration tests (cross-language, run from .NET)
dotnet test --filter "Category=GoldenFileIntegration"
```

## What Goes Here?

- Unit tests for Python server implementation (`server.py`)
- Unit tests for Python client implementation
- Compliance tests (auto-generated)
- Mock-based tests that don't require running servers

## What DOES NOT Go Here?

- ❌ Integration tests that start servers
- ❌ End-to-end tests with real HTTP requests
- ❌ Cross-language validation tests
- ❌ Golden file tests
- ❌ Tests in `integration/` directory (removed)

**If you're testing protocol behavior with a running server, write the test in .NET!**
