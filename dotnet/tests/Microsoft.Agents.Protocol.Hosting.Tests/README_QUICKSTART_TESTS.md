# Hosting SDK Quickstart Tests - Design Intent

## Status: Conceptual / Pending Implementation

The tests in `HostingQuickstartSamplesTests.cs` demonstrate the **intended API design** for the Hosting SDK quickstart guides, similar to the Python tests.

## API Mismatch

**Current Test API (Conceptual)**:
```csharp
var agentOptions = new AgentOptions
{
    Model = "gpt-4",
    Instructions = "You are helpful.",
    ApiKey = "test-key"
};

builder.Services
    .AddAgentHost()
    .AddDefaultAgent(agentOptions);
```

**Actual Hosting SDK API**:
```csharp
builder.Services
    .AddAgentHost()
    .AddDefaultAgent(agent => {
        agent.UseLLM("gpt-4", "You are helpful.");
    });
```

## Next Steps

1. **Option A**: Align Hosting SDK implementation to match the conceptual API shown in tests
2. **Option B**: Rewrite tests to use the actual `AgentBuilder` fluent API
3. **Option C**: Keep as conceptual tests for documentation purposes

## Test Structure

All tests follow the pattern:
- **Arrange** section - test setup (not extracted to docs)
- **Act** section - user-facing code (extracted to docs with `// Act - Exact code from quickstart`)
- **Assert** section - validation (not extracted to docs)

Tests are marked with `[DocExample("snippet-id", "title")]` for snippet extraction.

## Snippet Extraction

Once the API is aligned, run:
```bash
python3 scripts/extract-snippets.py csharp
```

This will extract the Act sections to `docs/snippets/csharp/hosting-*.cs` files.
