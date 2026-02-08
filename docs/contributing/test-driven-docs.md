# Test-Driven Documentation

This project uses a **test-driven documentation** system where all code examples in documentation are extracted from actual test files. This ensures that examples are always up-to-date and guaranteed to work.

## Overview

The system has three main components:

1. **Test Markers** - Mark tests for documentation inclusion
2. **Output Capture** - Capture test results for documentation
3. **Documentation Integration** - Include tests and results in docs

## Quick Start

### 1. Mark a Test for Documentation

**Python**:
```python
from test_helpers import doc_example

@doc_example(
    "my-example",
    "My Example Title",
    description="What this example demonstrates",
    category="serialization",
    tags=["basic", "xml"]
)
def test_my_feature(output_capture):
    """Example description"""

    # doc-example-start
    # Code to include in docs
    result = do_something()
    # doc-example-end

    # Capture output for docs
    output_capture.capture("my-example", result)

    # Regular assertions
    assert result is not None
```

**C#**:
```csharp
using Microsoft.Agents.Testing;

[Fact]
[DocExample("my-example",
    "My Example Title",
    Description = "What this example demonstrates",
    Category = "serialization",
    Tags = new[] { "basic", "xml" })]
public void TestMyFeature()
{
    // doc-example-start
    // Code to include in docs
    var result = DoSomething();
    // doc-example-end

    // Capture output for docs
    _outputCapture.Capture("my-example", result);

    // Regular assertions
    result.Should().NotBeNull();
}
```

### 2. Run Tests with Output Capture

**First time (generate golden files):**

```bash
# Python
cd python/microsoft-agents-xml
pytest --update-golden tests/

# .NET
cd dotnet
UPDATE_GOLDEN=1 dotnet test
```

Test outputs are saved to `test-data/results/shared/` (language-agnostic golden files shared across all implementations).

**Subsequent runs (validate against golden files):**

```bash
# Python
cd python/microsoft-agents-xml
pytest tests/

# .NET
cd dotnet
dotnet test
```

Tests will validate their outputs match the committed golden files. See [Golden File Testing](golden-files.md) for details.

### 3. Extract Code Snippets

```bash
python scripts/extract-doc-examples.py
```

This extracts marked code snippets to `docs/snippets/`.

### 4. Use in Documentation

In your markdown files:

```markdown
# My Feature

Here's how to use it:

{% include-test "my-example" language="python" %}

### Output

{% include-result "my-example" language="python" %}
```

### 5. Build Documentation

```bash
mkdocs serve  # Local preview
mkdocs build  # Production build
```

## Components

### Test Markers

**Purpose**: Mark tests to be extracted for documentation

**Python**: `@doc_example()` decorator in `python/test_helpers/doc_markers.py`

**C#**: `[DocExample]` attribute in `dotnet/tests/Shared/DocExampleAttribute.cs`

**Parameters**:
- `test_id`: Unique identifier (must match across Python and C#)
- `title`: Human-readable title
- `description`: Longer description (optional)
- `category`: Category for organization
- `tags`: List of tags for filtering

### Output Capture

**Purpose**: Capture test outputs in a structured format

**Python**: `OutputCapture` fixture in `python/test_helpers/output_capture.py`

**C#**: `OutputCapture` class in `dotnet/tests/Shared/OutputCapture.cs`

**Usage**:
```python
output_capture.capture("test-id", result, metadata={"key": "value"})
```

**Output Format**:
```json
{
  "testId": "test-id",
  "language": "python",
  "timestamp": "2026-02-07T10:00:00Z",
  "output": {
    "raw": "...",
    "normalized": "...",
    "hash": "..."
  },
  "metadata": {}
}
```

### Extraction Script

**Purpose**: Extract marked code snippets from test files

**Location**: `scripts/extract-doc-examples.py`

**Usage**:
```bash
# Extract all examples
python scripts/extract-doc-examples.py

# Extract only Python
python scripts/extract-doc-examples.py --language python

# Extract specific test
python scripts/extract-doc-examples.py --test-id my-example

# Verbose output
python scripts/extract-doc-examples.py --verbose
```

**Output**: Creates files in `docs/snippets/{language}/{test-id}_{section}.{ext}`

### Validation Script

**Purpose**: Validate that Python and .NET outputs match

**Location**: `scripts/validate-outputs.py`

**Usage**:
```bash
# Validate all outputs
python scripts/validate-outputs.py

# Validate specific test
python scripts/validate-outputs.py --test-id my-example

# Fail on first mismatch
python scripts/validate-outputs.py --fail-fast

# Verbose output
python scripts/validate-outputs.py --verbose
```

**Output**: Creates validation report in `test-data/results/validation/report.json`

### MkDocs Plugin

**Purpose**: Process custom tags in documentation

**Location**: `docs/plugins/test_examples.py`

**Configuration** (in `mkdocs.yml`):
```yaml
plugins:
  - test-examples:
      snippets_dir: docs/snippets
      results_dir: test-data/results
      enable_validation: true
      show_language_tabs: true
```

**Tags**:

Include code snippet:
```markdown
{% include-test "test-id" language="python" %}
{% include-test "test-id" section="setup" language="python" %}
```

Include test output:
```markdown
{% include-result "test-id" language="python" %}
{% include-result "test-id" format="xml" %}
```

## Workflow

### Local Development

1. Write or update test with `@doc_example` / `[DocExample]`
2. Add `doc-example-start` / `doc-example-end` markers around code
3. Add `output_capture.capture()` call
4. Run tests
5. Extract snippets: `python scripts/extract-doc-examples.py`
6. Update docs to use `{% include-test %}` tags
7. Build docs: `mkdocs serve`

### CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/test-and-docs.yml`):

1. Runs Python tests → uploads results
2. Runs .NET tests → uploads results
3. Downloads both results
4. Validates cross-platform consistency
5. Extracts code snippets
6. Builds documentation
7. Deploys to GitHub Pages (on main branch)

## Best Practices

### Test Markers

✅ **DO**:
- Use descriptive test IDs (`basic-serialization`, not `test1`)
- Write clear titles and descriptions
- Mark tests that demonstrate common use cases
- Keep marked code sections focused and concise

❌ **DON'T**:
- Mark tests with implementation details
- Include complex setup in marked sections
- Mark tests that are likely to change frequently

### Code Sections

✅ **DO**:
- Extract only the relevant code
- Use multiple sections for complex examples
- Keep sections under 20 lines when possible
- Include necessary imports

❌ **DON'T**:
- Include test assertions in marked sections
- Extract setup code unless it's part of the example
- Forget to close `doc-example-end` markers

### Output Capture

✅ **DO**:
- Capture representative outputs
- Include metadata to explain the output
- Sanitize sensitive data
- Keep outputs concise

❌ **DON'T**:
- Capture outputs with timestamps (they change)
- Capture very large outputs
- Include stack traces or error details

## Troubleshooting

### No Examples Extracted

**Problem**: `extract-doc-examples.py` finds 0 examples

**Solutions**:
- Check that `@doc_example` or `[DocExample]` is present
- Verify `doc-example-start` / `doc-example-end` markers are present
- Ensure test file naming matches pattern (`test_*.py` or `*Tests.cs`)
- Run with `--verbose` to see what files are being scanned

### Output Not Captured

**Problem**: No output files in `test-data/results/`

**Solutions**:
- Verify `output_capture` fixture is used
- Check that `output_capture.capture()` is called
- Ensure output directory exists and is writable
- Look for exceptions in test output

### Template Tags Not Replaced

**Problem**: `{% include-test %}` shows as-is in docs

**Solutions**:
- Verify `test-examples` plugin is enabled in `mkdocs.yml`
- Check that snippets were extracted: `ls docs/snippets/`
- Ensure metadata.json exists: `cat docs/snippets/metadata.json`
- Run extraction before building docs

### Cross-Platform Validation Fails

**Problem**: `validate-outputs.py` reports mismatches

**Solutions**:
- Check if both Python and .NET tests ran
- Compare normalized outputs (not raw)
- Look for platform-specific differences (line endings, etc.)
- Review validation report: `cat test-data/results/validation/report.json`

## File Structure

```
AgentProtocol/
├── python/
│   └── test_helpers/              # Test utilities
│       ├── doc_markers.py         # @doc_example decorator
│       ├── output_capture.py      # Output capture fixture
│       └── conftest_template.py   # Pytest fixture template
│
├── dotnet/
│   └── tests/
│       └── Shared/                # Shared test utilities
│           ├── DocExampleAttribute.cs
│           └── OutputCapture.cs
│
├── scripts/
│   ├── extract-doc-examples.py    # Extract code snippets
│   └── validate-outputs.py        # Validate outputs
│
├── docs/
│   ├── snippets/                  # Extracted code snippets
│   │   ├── python/
│   │   ├── csharp/
│   │   └── metadata.json
│   │
│   ├── plugins/                   # MkDocs plugins
│   │   └── test_examples.py
│   │
│   └── guides/
│       └── examples.md            # Example documentation page
│
├── test-data/
│   └── results/                   # Captured test outputs
│       ├── python/
│       ├── dotnet/
│       └── validation/
│           └── report.json
│
└── .github/
    └── workflows/
        └── test-and-docs.yml      # CI/CD workflow
```

## Examples

### Simple Example

**Test File** (`test_doc_examples.py`):
```python
@doc_example("basic-message", "Creating a Basic Message")
def test_basic_message(output_capture):
    # doc-example-start
    message = ChatMessage(role="user", contents=[TextContent(text="Hello!")])
    xml = serializer.serialize(message)
    # doc-example-end

    output_capture.capture("basic-message", xml)
    assert xml is not None
```

**Documentation** (`examples.md`):
```markdown
# Creating Messages

{% include-test "basic-message" language="python" %}

Output:
{% include-result "basic-message" language="python" %}
```

### Multi-Section Example

**Test File**:
```python
@doc_example("complex-workflow", "Complex Workflow")
def test_complex_workflow(output_capture):
    # doc-example-start: setup
    client = ApiClient("https://api.example.com")
    # doc-example-end: setup

    # doc-example-start: main
    response = client.post("/users", user_data)
    user_id = response.json()["id"]
    # doc-example-end: main

    output_capture.capture("complex-workflow", user_id)
```

**Documentation**:
```markdown
### Setup
{% include-test "complex-workflow" section="setup" language="python" %}

### Main Code
{% include-test "complex-workflow" section="main" language="python" %}
```

## Contributing

When adding new documentation:

1. Write the test first with `@doc_example`
2. Extract the code: `python scripts/extract-doc-examples.py`
3. Update documentation with `{% include-test %}` tags
4. Verify locally: `mkdocs serve`
5. Submit PR - CI will validate everything

## Further Reading

- [Implementation Details](.workspace/test-driven-docs-strategy.md)
- [Code Examples](.workspace/implementation-examples.md)
- [Workflows](.workspace/workflows-and-diagrams.md)
