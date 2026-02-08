# Scripts Directory

Utility scripts for code generation, validation, testing, and bot management.

## Quick Reference

### Golden Dataset Generation

Generate golden files from .NET implementations (canonical source):

```bash
# Generate for all samples (auto-starts .NET bots)
python scripts/generate_golden_datasets.py

# Generate for specific sample
python scripts/generate_golden_datasets.py --sample echom365

# Full documentation: test-data/results/README.md
```

### Code Generation

Generate code and tests from TypeSpec schemas:

```bash
# Generate all (TypeSpec → Python, .NET, TypeScript)
./scripts/generation/generate-all.sh

# Generate specific language
./scripts/generation/generate-python.sh      # Python bindings
./scripts/generation/generate-csharp.sh      # .NET bindings
./scripts/generation/generate-typescript.sh  # TypeScript bindings

# Generate tests
python scripts/generation/generate-tests.py
```

### Documentation Validation

Validate documentation against TypeSpec schemas:

```bash
cd scripts/validation

# Main validations
python validate-docs-against-typespec.py
python validate-api-reference.py
python validate-typespec-docs.py

# Specific checks
python check-cross-references.py
python check-typespec-terms.py
python validate-links.py
```

## Directory Structure

```
scripts/
├── README.md                          # This file
├── generate_golden_datasets.py       # Main golden file generator
├── cleanup_deprecated_results.sh     # Cleanup old result directories
├── cleanup_and_organize.sh           # Cleanup scripts directory
│
├── generation/                       # Code generation from TypeSpec
│   ├── generate-all.sh              # Generate all languages
│   ├── generate-python.sh
│   ├── generate-csharp.sh
│   ├── generate-typescript.sh
│   ├── generate-tests.py            # Generate tests
│   ├── generate-api-reference.py
│   └── test_gen/                    # Test generation modules
│
├── validation/                       # Documentation validation
│   ├── validate-*.py                # Validation scripts
│   └── check-*.py                   # Specific checkers
│
├── utilities/                        # General utilities
│   ├── README.md                    # Utilities documentation
│   ├── start-all-echo-bots.sh      # Bot management
│   ├── validate-echo-bots.py        # Bot validation
│   └── *.sh, *.py                   # Other utilities
│
├── typescript/                       # TypeScript-specific utilities
│   └── *.sh
│
└── .archive/                         # Deprecated scripts
    ├── README.md                    # Why scripts are archived
    └── [obsolete scripts]
```

## Common Tasks

### Generate Golden Files
```bash
python scripts/generate_golden_datasets.py --sample echom365
```

### Validate Tests
```bash
SAMPLE_NAME=echom365 pytest python/tests/
SAMPLE_NAME=echom365 npm test
```

### Generate All Code
```bash
./scripts/generation/generate-all.sh
```

### Start All Bots
```bash
./scripts/utilities/start-all-echo-bots.sh
```

### Cleanup Old Results
```bash
./scripts/cleanup_deprecated_results.sh
```

## Adding New Scripts

When adding new scripts:

1. **Choose the right directory:**
   - `generation/` - Code/test generation from schemas
   - `validation/` - Documentation validation
   - `utilities/` - General development utilities
   - Root - Major standalone tools

2. **Follow conventions:**
   - Add shebang line: `#!/usr/bin/env python3` or `#!/bin/bash`
   - Include description comment block
   - Add usage examples
   - Make executable: `chmod +x script.sh`

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
