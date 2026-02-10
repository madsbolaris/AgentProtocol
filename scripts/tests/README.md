# Script Tests

Tests for all scripts in the `scripts/` directory to ensure proper interfaces, error handling, and safety.

## Purpose

These tests validate that:
- ✅ All scripts have proper `--help` documentation
- ✅ Scripts handle errors gracefully with actionable messages
- ✅ Scripts use correct exit codes
- ✅ Generators have `--dry-run` modes
- ✅ Scripts don't pollute project directories during testing

## Critical: Isolation from Project Artifacts

**IMPORTANT:** These tests MUST NOT write to actual project directories:

### Protected Directories
- `test-data/results/` - Golden test results
- `llm-recordings/` - LLM interaction recordings
- `.generated/` - Generated code/docs
- `api-reference/` - Generated API documentation
- SDK test directories - Generated SDK tests

### How Isolation Works

1. **Temporary Directories** (`conftest.py`)
   - All tests use `temp_project_root` fixture
   - Creates isolated project structure in `/tmp`
   - Automatically cleaned up after tests

2. **Mocked Files** (`conftest.py`)
   - `mock_typespec_file` - Minimal TypeSpec for testing
   - `mock_api_reference_dir` - Sample API reference structure
   - Scripts run against mocks, not real files

3. **Working Directory Isolation**
   - Tests change to temp directory
   - Scripts can't accidentally write to real project
   - `monkeypatch` ensures environment isolation

## Running Tests

### Run All Script Tests
```bash
cd scripts
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Validation scripts
pytest tests/test_validation_scripts.py -v

# Code generation scripts
pytest tests/test_codegen_scripts.py -v

# Test generation scripts
pytest tests/test_testgen_scripts.py -v
```

### Run Individual Test Classes
```bash
# Test check_annotations.py
pytest tests/test_validation_scripts.py::TestCheckAnnotations -v

# Test generate_api_reference.py
pytest tests/test_codegen_scripts.py::TestGenerateApiReference -v
```

### Run Specific Tests
```bash
# Test that --help works
pytest tests/ -k "test_help_flag_works" -v

# Test that scripts don't modify files
pytest tests/ -k "test_doesnt_modify_files" -v

# Test dry-run modes
pytest tests/ -k "test_dry_run" -v
```

### Verbose Output
```bash
pytest tests/ -vv -s  # Show print statements and verbose output
```

## Test Structure

```
tests/
├── conftest.py                    # Fixtures for isolation
├── test_validation_scripts.py     # Validation script tests
├── test_codegen_scripts.py        # Code generation tests
├── test_testgen_scripts.py        # Test generation tests
└── README.md                      # This file
```

## Test Categories

### Interface Tests
- `--help` flag works
- Help text includes examples
- Flags are properly documented
- Error messages are actionable

### Safety Tests
- Scripts don't modify files when they shouldn't
- `--dry-run` doesn't create files
- Read-only scripts remain read-only
- Exit codes are correct

### Error Handling Tests
- Invalid paths show helpful errors
- Missing files provide guidance
- Invalid arguments fail gracefully
- Error messages include solutions

## Adding Tests for New Scripts

When adding a new script, create tests following this pattern:

```python
class TestMyNewScript:
    """Test my_new_script.py interface"""

    def test_help_flag_works(self):
        """--help should show usage"""
        result = run_script(SCRIPTS_DIR / "my_new_script.py", ["--help"])

        assert result.returncode == 0
        assert "Usage" in result.stdout or "usage:" in result.stdout
        assert "Examples:" in result.stdout

    def test_handles_invalid_input(self, temp_project_root):
        """Invalid input should show actionable error"""
        result = run_script(
            SCRIPTS_DIR / "my_new_script.py",
            ["--input", "nonexistent"],
            cwd=temp_project_root
        )

        assert result.returncode == 1
        assert "not found" in result.stdout.lower()
        assert "To fix:" in result.stdout or "Try:" in result.stdout

    def test_dry_run_doesnt_write_files(self, temp_project_root):
        """--dry-run should not create files"""
        # Your test here
        pass
```

## Fixtures Available

From `conftest.py`:

- **`temp_project_root`** - Isolated project directory in `/tmp`
- **`mock_typespec_file`** - Minimal TypeSpec for testing
- **`mock_api_reference_dir`** - Sample API reference structure
- **`isolated_environment`** - Changes to temp dir, sets env vars
- **`capture_script_output`** - Capture stdout/stderr from scripts
- **`mock_subprocess_run`** - Mock subprocess calls

## CI Integration

These tests run in GitHub Actions:

```yaml
test-scripts:
  name: Script Interface Tests
  runs-on: ubuntu-latest

  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.11"

    - name: Install pytest
      run: pip install pytest

    - name: Run script tests
      run: |
        cd scripts
        pytest tests/ -v
```

## Benefits

✅ **Regression Prevention** - Catch interface breakage automatically
✅ **Safety** - Ensure scripts don't pollute project
✅ **Documentation** - Tests serve as usage examples
✅ **Confidence** - Safe to refactor scripts
✅ **Quality** - Enforce consistent interfaces

## Current Coverage

| Category | Scripts | Tested | Coverage |
|----------|---------|--------|----------|
| Validation | 8 | 3 | 37% |
| Codegen | 5 | 1 | 20% |
| Testgen | 1 | 1 | 100% |
| **Total** | **40** | **5** | **12%** |

## Roadmap

### Phase 1: High-Priority Scripts ✅ (This Week)
- [x] check_annotations.py
- [x] validate_api_reference.py
- [x] generate_api_reference.py
- [x] generate_tests.py

### Phase 2: All Scripts (This Month)
- [ ] All validation scripts
- [ ] All codegen scripts
- [ ] Utility scripts
- [ ] CI scripts

### Phase 3: Integration Tests (This Quarter)
- [ ] Full workflow tests
- [ ] Cross-script integration
- [ ] End-to-end validation

## Troubleshooting

### Tests Fail with "Permission Denied"
- Ensure scripts have execute permissions
- Check that temp directories are writable

### Tests Write to Real Project
- Verify using `temp_project_root` fixture
- Check that `cwd=temp_project_root` is set
- Use `isolated_environment` fixture

### Tests Timeout
- Reduce scope of generated tests in mocks
- Use `--dry-run` in tests when possible
- Mock subprocess calls for long operations

## Best Practices

1. **Always use temp_project_root** - Never test against real project
2. **Test --help first** - Simplest interface test
3. **Test error cases** - Most valuable tests
4. **Test --dry-run** - Ensure generators are safe
5. **Check exit codes** - Validate proper error handling
6. **Verify no file writes** - Safety is critical

## Questions?

See:
- `.workspace/script-validation-report.md` - Full validation report
- `.workspace/script-improvements-summary.md` - Recent improvements
- `.workspace/script-interface-review.md` - Interface review

---

**Last Updated:** 2026-02-09
**Test Coverage:** 12% (5/40 scripts)
**Status:** Phase 1 Complete ✅
