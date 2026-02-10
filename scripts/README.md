# Scripts Directory

Utility scripts for code generation, validation, testing, and bot management.

## Quick Reference

### Golden Dataset Generation

Generate golden files from .NET implementations (canonical source):

```bash
# Generate for all samples (auto-starts .NET bots)
python scripts/testgen/generate_golden_datasets.py

# Generate for specific sample
python scripts/testgen/generate_golden_datasets.py --sample echom365

# Full documentation: test-data/results/README.md
```

### Code Generation

Generate code and tests from TypeSpec schemas:

```bash
# Generate all SDKs (Python, .NET, TypeScript)
python scripts/codegen/generate_sdk.py

# Or generate specific language only
python scripts/codegen/generate_sdk.py --lang python
python scripts/codegen/generate_sdk.py --lang csharp
python scripts/codegen/generate_sdk.py --lang typescript

# Generate tests
python scripts/testgen/generate_tests.py
```

### Documentation Validation

Validate documentation against TypeSpec schemas:

```bash
cd scripts/validation

# Main validations
python validate_docs_against_typespec.py
python validate_api_reference.py
python validate_typespec_docs.py

# Specific checks
python check_cross_references.py
python check_typespec_terms.py
python validate_links.py
```

## Directory Structure

```
scripts/
├── README.md                          # This file
├── Makefile                           # Build targets for common tasks
│
├── codegen/                          # Code & doc generation from TypeSpec
│   ├── generate_sdk.py              # Generate SDKs (all or --lang python|csharp|typescript)
│   ├── generate_for_typescript.py   # Special TS package generation
│   ├── generate_api_reference.py    # Generate API docs
│   ├── merge_api_docs.py            # Merge generated + manual docs
│   └── extract_doc_examples.py      # Extract examples from tests
│
├── testgen/                          # Test generation & golden datasets
│   ├── generate_tests.py            # Generate tests from TypeSpec
│   ├── generate_golden_datasets.py  # Main golden file generator
│   └── lib/                         # Test generation library modules
│       ├── compliance_test_generator.py
│       ├── property_test_generator.py
│       └── ...
│
├── validation/                       # Documentation & code validation
│   ├── validate_*.py                # Validation scripts
│   ├── check_*.py                   # Specific checkers
│   ├── validate_echo_m365s.py       # Sample validation
│   └── validate_test_infrastructure.py  # Infrastructure checks
│
├── ci/                               # CI & development utilities
│   ├── install_git_hooks.py         # Setup git hooks
│   └── start_samples.py             # Start any sample + chat UI
│
└── .archive/                         # Deprecated scripts
    ├── README.md                    # Why scripts are archived
    └── [obsolete scripts]
```

## Common Tasks

### Generate Golden Files
```bash
python scripts/testgen/generate_golden_datasets.py --sample echom365
```

### Validate Tests
```bash
SAMPLE_NAME=echom365 pytest python/tests/
SAMPLE_NAME=echom365 npm test
```

### Generate All Code
```bash
python scripts/codegen/generate_sdk.py
```

### Start Samples (with Chat UI)
```bash
# Start specific sample with UI
python scripts/ci/start_samples.py basic-m365 --ui

# Start all echo-m365 samples
python scripts/ci/start_samples.py echo-m365

# Start everything
python scripts/ci/start_samples.py all --ui
```

## Adding New Scripts

When adding new scripts:

1. **Choose the right directory:**
   - `codegen/` - Code & documentation generation from schemas
   - `testgen/` - Test generation & golden datasets
   - `validation/` - Documentation & code validation
   - `ci/` - CI scripts & development utilities

2. **Follow conventions:**
   - Add shebang line: `#!/usr/bin/env python3`
   - Include description docstring
   - Add usage examples
   - Use underscores in filenames: `my_script.py` not `my-script.py`
   - Make executable: `chmod +x script.py`

3. **Update documentation:**
   - Add entry to appropriate README.md
   - Include usage examples
   - Document prerequisites

4. **Test thoroughly:**
   - Test on clean checkout
   - Verify all paths work from repo root
   - Check error messages are helpful

## Script Guidelines

### Python Scripts
- Use `pathlib.Path` for file paths
- Include `argparse` for command-line arguments
- Add `--help` flag
- Use type hints
- Include docstrings

### Shell Scripts
- Use `set -e` to exit on errors
- Validate required tools exist
- Print progress messages
- Support `--help` flag
- Quote variable expansions

### Naming
- Python: `snake_case.py`
- Shell: `kebab-case.sh`
- Be descriptive: `generate_golden_datasets.py` not `gen.py`

## Maintenance

### Archiving Scripts

If a script becomes obsolete:
1. Move to `.archive/`
2. Update `.archive/README.md` explaining why
3. Update this README.md to remove references
4. Consider if replacement exists

### Updating Scripts

When updating scripts:
1. Test with current codebase
2. Update help text and documentation
3. Check all related README files
4. Verify examples still work

## Related Documentation

- [Golden Dataset Guide](../.workspace/GOLDEN_DATASET_UPDATES.md)
- [Test Results Structure](../test-data/results/README.md)
- [Migration Guide](../.workspace/GOLDEN_DATASET_MIGRATION.md)
- [Agent Configuration](../agent-config.json)

## Questions or Issues?

- Check script's `--help` output
- Review script source code (they're well-documented)
- Check related README.md files
- Review git history for context
