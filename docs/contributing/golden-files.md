# Golden File Testing

This project uses **golden file testing** (also known as snapshot testing) to ensure that test outputs remain consistent over time and across Python and .NET implementations.

## Overview

Golden files are pre-generated test output files stored in `test-data/results/` that serve as the source of truth for what your tests should produce. Tests automatically validate their outputs against these golden files and fail if there's a mismatch.

## How It Works

### 1. Normal Test Runs (Validation Mode)

By default, tests **validate** against existing golden files:

```bash
# Python
cd python/microsoft-agents-xml
pytest tests/test_doc_examples.py -v

# C#
cd dotnet/tests/Microsoft.Agents.Xml.Tests
dotnet test
```

**What happens:**
- Test runs and produces output
- Output is compared against golden file using normalized hash
- ✅ Test passes if hashes match
- ❌ Test fails with diff if hashes don't match

### 2. Updating Golden Files (Update Mode)

When you intentionally change output, update the golden files:

```bash
# Python
cd python/microsoft-agents-xml
pytest --update-golden tests/test_doc_examples.py

# Or using environment variable
UPDATE_GOLDEN=1 pytest tests/test_doc_examples.py

# C#
cd dotnet/tests/Microsoft.Agents.Xml.Tests
UPDATE_GOLDEN=1 dotnet test
```

**What happens:**
- Test runs and produces output
- Golden file is overwritten with new output
- Test always passes (no validation)
- You should review and commit the changes

## Directory Structure

```
test-data/
├── results/
│   ├── python/           # Python golden files
│   │   ├── basic-xml-serialization.json
│   │   ├── multimodal-message.json
│   │   └── read-xml-file.json
│   └── dotnet/           # .NET golden files (if any)
│       └── ...
└── validation/
    └── report.json       # Cross-platform validation report
```

## Golden File Format

Each golden file is a JSON document with this structure:

```json
{
  "testId": "basic-xml-serialization",
  "language": "python",
  "timestamp": "2025-02-07T12:34:56.789Z",
  "output": {
    "raw": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
    "normalized": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>...",
    "hash": "a1b2c3d4e5f6..."
  },
  "metadata": {
    "testFile": "test_doc_examples.py",
    "testFunction": "test_basic_xml_serialization"
  }
}
```

- **raw**: Original output exactly as produced by the test
- **normalized**: Output with whitespace normalized for comparison
- **hash**: SHA-256 hash of normalized output (used for validation)

## Workflow Examples

### Adding a New Test

1. Write your test with `@doc_example` decorator:

```python
@doc_example("new-feature", "New Feature Test")
def test_new_feature(output_capture):
    result = my_new_feature()
    output_capture.capture("new-feature", result)
```

2. Run test in update mode to create golden file:

```bash
pytest --update-golden tests/test_doc_examples.py::test_new_feature
```

3. Review the generated golden file:

```bash
cat test-data/results/shared/new-feature.json
```

4. Commit both the test and golden file:

```bash
git add tests/test_doc_examples.py
git add test-data/results/shared/new-feature.json
git commit -m "Add new feature test with golden file"
```

### Intentionally Changing Output

1. Make your code changes

2. Run tests - they will fail with a diff:

```bash
$ pytest tests/test_doc_examples.py::test_basic_xml_serialization
...
❌ Output mismatch for test: basic-xml-serialization
   Expected hash: a1b2c3d4...
   Actual hash:   e5f6g7h8...

   Diff:
   - <oldElement>value</oldElement>
   + <newElement>value</newElement>
```

3. Review the diff to confirm the change is intentional

4. Update the golden file:

```bash
pytest --update-golden tests/test_doc_examples.py::test_basic_xml_serialization
```

5. Review and commit:

```bash
git diff test-data/results/shared/basic-xml-serialization.json
git add test-data/results/shared/basic-xml-serialization.json
git commit -m "Update golden file for XML format change"
```

### Unintentional Output Change

If a test fails and you didn't intend to change the output:

1. Review the diff shown in the test failure
2. Fix your code to restore the expected behavior
3. Run tests again to verify they pass
4. **Do NOT** update the golden file

## Best Practices

### ✅ Do

- **Commit golden files to git** - They are the source of truth
- **Review diffs carefully** - Understand why output changed
- **Update intentionally** - Only use update mode when changes are deliberate
- **Keep outputs small** - Large outputs make diffs hard to review
- **Use meaningful test IDs** - Makes golden files easy to identify

### ❌ Don't

- **Update without reviewing** - Always check the diff first
- **Ignore test failures** - Investigate why output changed
- **Update in CI** - Golden files should only be updated locally
- **Use update mode by default** - It defeats the purpose of validation

## Cross-Platform Validation

Since Python and .NET should produce identical outputs, we store outputs in language-specific directories but validate they match:

```bash
# Run validation script
python scripts/validate-outputs.py

# Output:
✅ Validation PASSED
All outputs match across Python and .NET implementations!
```

This ensures both implementations remain in sync.

## CI/CD Integration

In CI/CD pipelines:

1. Tests run in **validation mode** (default)
2. Golden files must exist in repository
3. Tests fail if outputs don't match golden files
4. **Never** run update mode in CI

Example GitHub Actions workflow:

```yaml
- name: Run Python tests
  run: |
    cd python/microsoft-agents-xml
    pytest tests/test_doc_examples.py -v
  # No --update-golden flag - validates only!

- name: Run .NET tests
  run: |
    cd dotnet/tests/Microsoft.Agents.Xml.Tests
    dotnet test
  # No UPDATE_GOLDEN=1 - validates only!
```

## Troubleshooting

### Test fails with "Golden file not found"

**Problem:** Test is trying to validate but no golden file exists.

**Solution:** Run test in update mode to create it:

```bash
pytest --update-golden tests/test_doc_examples.py::test_name
```

### Test fails with "Output mismatch"

**Problem:** Test output doesn't match golden file.

**Solution:**
1. Review the diff shown in the error
2. If change is intentional: update golden file
3. If change is unintentional: fix your code

### Golden file has wrong content

**Problem:** You updated a golden file with incorrect output.

**Solution:**
1. Fix your code to produce correct output
2. Re-run update mode to regenerate golden file
3. Or restore from git if needed

## Related Documentation

- [Test-Driven Documentation](test-driven-docs.md) - How tests feed documentation
- [Code Examples](../guides/examples.md) - View live examples from tests
- [Cross-Platform Validation](../guides/xml-serialization.md) - Python/C# consistency
