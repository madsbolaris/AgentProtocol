# TypeScript Snippet Extraction Setup

## Status: Ready (Needs Test Updates)

The universal snippet extractor in `scripts/extract-snippets.py` is configured for TypeScript and ready to use.

## Required Test Structure

### 1. JSDoc Comments for Snippet Metadata

Tests need JSDoc-style comments with `@docExample` and `@docTitle` tags:

```typescript
/**
 * @docExample hosting-hello-world
 * @docTitle Hosting SDK Quickstart - Step 1: Hello World
 */
it('should create basic agent configuration', async () => {
  // Arrange - Test setup (not in snippet)

  // Act - Exact code from quickstart
  // Create agent configuration
  const config = new AgentConfig({
    model: 'gpt-4',
    instructions: 'You are a helpful assistant.',
    apiKey: 'test-api-key'
  });

  // Initialize agent host
  const agent = new AgentHost(config);

  // Assert - Test validation (not in snippet)
  expect(agent.config.model).toBe('gpt-4');
});
```

### 2. Arrange/Act/Assert Comments

Similar to C# and Python, tests need structured comments:

```typescript
// Arrange - Test setup (not in snippet)
const setup = createTestEnvironment();

// Act - Exact code from quickstart
// User-facing code that will be extracted
const result = await client.processMessage('Hello');

// Assert - Test validation (not in snippet)
expect(result).toBeDefined();
```

## Extractor Configuration

The universal extractor is already configured for TypeScript in [`scripts/extract-snippets.py`](../../../scripts/extract-snippets.py):

```python
'typescript': {
    'comment': '//',
    'test_dirs': [
        'typescript/packages/agents-protocol-client/tests',
        'typescript/packages/agents-protocol-hosting/tests'
    ],
    'test_pattern': '**/*.test.ts',
    'marker_pattern': r'\*\s*@docExample\s+([^\s]+)\s*\n\s*\*\s*@docTitle\s+([^\n]+)',
    'output_dir': 'docs/snippets/typescript',
    'extension': '.ts'
}
```

## Extraction Process

Once tests are updated:

```bash
# Extract TypeScript snippets
python3 scripts/extract-snippets.py typescript

# Or extract all languages
python3 scripts/extract-snippets.py all
```

Snippets will be created in `docs/snippets/typescript/` with format:
- `hosting-hello-world_main.ts`
- `hosting-adding-tools_main.ts`
- etc.

## Test File Updates Needed

TypeScript test files need:

1. **JSDoc comments with metadata**:
   ```typescript
   /**
    * @docExample snippet-id
    * @docTitle Display Title
    */
   ```

2. **Arrange/Act/Assert structure**:
   ```typescript
   // Arrange - Test setup (not in snippet)
   // Act - Exact code from quickstart
   // Assert - Test validation (not in snippet)
   ```

## Testing Framework

Assuming Jest or similar:

```typescript
describe('Hosting SDK Quickstart', () => {
  /**
   * @docExample hosting-hello-world
   * @docTitle Step 1: Hello World
   */
  it('creates basic agent', async () => {
    // Arrange - Test setup (not in snippet)

    // Act - Exact code from quickstart
    const config = new AgentConfig({
      model: 'gpt-4',
      instructions: 'You are helpful.'
    });
    const agent = new AgentHost(config);

    // Assert - Test validation (not in snippet)
    expect(agent).toBeDefined();
  });
});
```

## Benefits

Once updated:
- ✅ Docs automatically stay in sync with tested code
- ✅ No manual snippet maintenance
- ✅ Type-safe examples (TypeScript compiler catches errors)
- ✅ Breaking changes caught by tests
- ✅ Single source of truth

## See Also

- [Universal Extractor Documentation](../../../scripts/README.md)
- [Snippet System Overview](../../../docs/snippets/README.md)
- [.NET Example](../../../dotnet/tests/README.md)
- [Python Example](../../../python/microsoft-agents-protocol-hosting/tests/README_SNIPPET_EXTRACTION.md)
