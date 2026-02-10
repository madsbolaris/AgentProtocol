# Microsoft Agents XML - Python Tests

## ⚠️ NO INTEGRATION TESTS HERE

**All integration tests must be written in .NET and run through the .NET test projects.**

This directory should only contain:
- ✅ Unit tests for Python XML serialization/deserialization
- ✅ Property validation tests (auto-generated from TypeSpec)
- ✅ Round-trip tests (XML → object → XML)
- ❌ **NO integration tests** - Use .NET tests instead

## Why?

XML serialization must be consistent across all language implementations. Integration tests are maintained in .NET to ensure cross-language compatibility.

## Test Organization

```
python/microsoft-agents-xml/tests/
├── README.md (this file)
├── conftest.py
├── test_error_handling.py
├── test_generated_property_validation.py
├── test_generated_roundtrip.py
└── [unit tests only]
```

## Running Tests

```bash
# Python unit tests only
pytest python/microsoft-agents-xml/tests/

# Integration tests (if needed, run from .NET)
dotnet test dotnet/tests/Microsoft.Agents.Xml.Tests/
```

## What Goes Here?

- Unit tests for XML serialization logic
- Property validation tests (auto-generated)
- Round-trip serialization tests
- Error handling tests
- Tests that use in-memory XML (no HTTP)

## What DOES NOT Go Here?

- ❌ Integration tests with running servers
- ❌ End-to-end tests with HTTP requests
- ❌ Cross-language validation tests
- ❌ Tests in `test_*_integration.py` files (removed)

**Focus on testing the XML serialization logic, not the full protocol stack!**
