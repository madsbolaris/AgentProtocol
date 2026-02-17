# Python Snippet Extraction Setup

## Status: Ready (Needs Test Updates)

The universal snippet extractor in `scripts/extract-snippets.py` is configured for Python and ready to use.

## Required Test Structure

### 1. Two-Parameter Decorator

**Current (needs updating)**:
```python
@pytest.mark.doc_example("Hosting SDK Quickstart - Step 1: Hello World")
```

**Required**:
```python
@pytest.mark.doc_example("hosting-hello-world", "Hosting SDK Quickstart - Step 1: Hello World")
```

### 2. Arrange/Act/Assert Comments

Tests need structured comments to mark extraction boundaries:

```python
@pytest.mark.asyncio
@pytest.mark.doc_example("hosting-hello-world", "Hosting SDK Quickstart - Step 1")
async def test_step1_hello_world(self):
    """Test basic agent setup"""
    # Arrange - Test setup (not in snippet)

    # Act - Exact code from quickstart
    # Create agent configuration
    config = AgentConfig(
        model="gpt-4",
        instructions="You are a helpful assistant.",
        api_key="test-api-key"
    )

    # Initialize agent host
    agent = AgentHost(config)

    # Assert - Test validation (not in snippet)
    assert agent.config.model == "gpt-4"
```

## Extractor Configuration

The universal extractor is already configured for Python in [`scripts/extract-snippets.py`](../../../scripts/extract-snippets.py):

```python
'python': {
    'comment': '#',
    'test_dirs': [
        'python/microsoft-agents-protocol-client/tests',
        'python/microsoft-agents-protocol-hosting/tests'
    ],
    'test_pattern': '**/test_*.py',
    'marker_pattern': r'@pytest\.mark\.doc_example\("([^"]+)",\s*"([^"]+)"\)',
    'output_dir': 'docs/snippets/python',
    'extension': '.py'
}
```

## Extraction Process

Once tests are updated:

```bash
# Extract Python snippets
python3 scripts/extract-snippets.py python

# Or extract all languages
python3 scripts/extract-snippets.py all
```

Snippets will be created in `docs/snippets/python/` with format:
- `hosting-hello-world_main.py`
- `hosting-adding-tools_main.py`
- etc.

## Test File Updates Needed

The following test files need updating:

1. **`test_hosting_quickstart_samples.py`** (17+ tests)
   - Update all `@pytest.mark.doc_example()` decorators to use two parameters
   - Add Arrange/Act/Assert comment structure

2. **`test_client_quickstart_samples.py`** (if exists)
   - Same updates as above

## Update Pattern

For each test method:

1. Change decorator from one to two parameters:
   ```python
   # Before
   @pytest.mark.doc_example("Title")

   # After
   @pytest.mark.doc_example("snippet-id", "Title")
   ```

2. Add comment structure:
   ```python
   async def test_example(self):
       # Arrange - Test setup (not in snippet)

       # Act - Exact code from quickstart
       # User-facing code here

       # Assert - Test validation (not in snippet)
       assert something
   ```

## Benefits

Once updated:
- ✅ Docs automatically stay in sync with tested code
- ✅ No manual snippet maintenance
- ✅ Breaking changes caught by tests
- ✅ Single source of truth

## See Also

- [Universal Extractor Documentation](../../../scripts/README.md)
- [Snippet System Overview](../../../docs/snippets/README.md)
- [.NET Example](../../../dotnet/tests/README.md)
