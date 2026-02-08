# AgentProtocol Scripts

This directory contains scripts for API documentation generation and validation.

## Directory Structure

```
scripts/
├── generation/              # Documentation generation
│   ├── generate-api-reference.py    # Generate from TypeSpec
│   └── merge-api-docs.py            # Merge generated + manual
├── validation/              # Documentation validation
│   ├── check-routes.py              # Validate routes exist in TypeSpec
│   ├── check-typespec-terms.py      # Validate model names
│   ├── check-old-patterns.py        # Check for deprecated patterns
│   ├── check-cross-references.py    # Validate cross-references
│   ├── validate-docs-against-typespec.py
│   ├── check-line-references.py     # Check line number refs
│   ├── validate-consistency.py      # Overall consistency
│   ├── validate-enums.py            # Enum synchronization
│   └── validate-links.py            # Internal links
├── Makefile                 # Convenient make targets
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Quick Start

### Generate Documentation

```bash
# From project root
python3 scripts/generation/generate-api-reference.py
python3 scripts/generation/merge-api-docs.py

# Or use make (from scripts/ directory)
cd scripts
make docs
```

### Validate Documentation

```bash
# Run all validation checks
cd scripts
make validate

# Or run specific checks
make enums
make links
make line-refs
```

## Documentation Generation System

### Architecture

```
TypeSpec Files               Manual Overlays
    (typespec/*.tsp)        (docs-content/)
         ↓                       ↓
         ↓                   - Examples
         ↓                   - Use cases
  [generate-api-reference]  - Best practices
         ↓                   - Troubleshooting
         ↓                       ↓
    Generated                   ↓
 (.generated/api-reference/)    ↓
    - Endpoints              ←──┘
    - Parameters
    - Models              [merge-api-docs]
                                 ↓
                          Final Documentation
                          (docs/api-reference/)
                          Generated + Manual
```

### How It Works

1. **Generation** (`generate-api-reference.py`):
   - Parses TypeSpec files in `typespec/`
   - Extracts endpoints, models, enums
   - Generates markdown in `.generated/api-reference/`
   - Filters out TypeSpec metadata (BASE:, SOURCE:, etc.)

2. **Merge** (`merge-api-docs.py`):
   - Reads generated files from `.generated/api-reference/`
   - Reads manual overlays from `docs-content/`
   - Combines using `<!-- GENERATED_START/END -->` and `<!-- MANUAL_START/END -->` markers
   - Outputs to `docs/api-reference/`

3. **Manual Overlays** (`docs-content/`):
   - Human-written content (examples, use cases, best practices)
   - Uses section markers for hybrid merge
   - Preserved across regenerations

### Example Manual Overlay

```markdown
# Runs API

Operations for managing runs.

<!-- GENERATED_START -->
[Auto-generated endpoint documentation]
<!-- GENERATED_END -->

<!-- MANUAL_START: examples -->
## Examples

### POST /runs/wait - One-Shot Query
[Complete HTTP example]
<!-- MANUAL_END: examples -->

<!-- MANUAL_START: use-cases -->
## Use Cases
[When to use each endpoint]
<!-- MANUAL_END: use-cases -->
```

## Common Tasks

### Regenerate All Documentation

```bash
# From scripts/ directory
make docs
```

Or manually:

```bash
python3 generation/generate-api-reference.py
python3 generation/merge-api-docs.py
```

### Add Manual Content

1. Create file in `docs-content/` matching structure:
   ```
   docs-content/operations/runs.md
   ```

2. Add content with markers:
   ```markdown
   <!-- MANUAL_START: section-name -->
   Your content here
   <!-- MANUAL_END: section-name -->
   ```

3. Run merge:
   ```bash
   python3 generation/merge-api-docs.py
   ```

### Validate Changes

```bash
cd scripts
make validate
```

## Make Targets

Run from `scripts/` directory:

### Documentation Generation
- `make generate` - Generate from TypeSpec
- `make merge` - Merge generated + manual
- `make docs` - Complete workflow (generate + merge)

### Validation
- `make validate` - Run all validation checks
- `make enums` - Check enum synchronization
- `make links` - Validate internal links
- `make line-refs` - Check line number references

### Utilities
- `make install` - Install Python dependencies
- `make clean` - Remove generated reports
- `make help` - Show help message

## Workflow

### When TypeSpec Changes

```bash
cd scripts

# 1. Regenerate documentation
make docs

# 2. Validate
make validate

# 3. Commit (from project root)
cd ..
git add api-reference/ docs-content/
git commit -m "Update API reference from TypeSpec"
```

### When Adding Manual Content

```bash
# 1. Create/edit manual overlay
vim ../docs-content/operations/runs.md

# 2. Merge
cd scripts
make merge

# 3. Review merged output
ls -la ../api-reference/operations/runs.md

# 4. Commit
cd ..
git add docs-content/ api-reference/
git commit -m "Add examples to runs documentation"
```

## Benefits

✅ **Always accurate** - Generated from TypeSpec source
✅ **Complete coverage** - All 41 endpoints, 121 models
✅ **Rich examples** - Human-written use cases and tutorials
✅ **Fast updates** - 30 seconds to regenerate
✅ **No drift** - Always in sync with code
✅ **Clean separation** - Auto-generated vs manual content

## Dependencies

Install with:

```bash
cd scripts
make install
```

Or manually:

```bash
pip3 install -r requirements.txt
```

## Troubleshooting

### "No such file or directory" errors

Make sure you're running from the correct directory:
- Generation/merge scripts: Run from project root or use `make` from `scripts/`
- Make commands: Run from `scripts/` directory

### Manual content not appearing in merged docs

1. Check file structure matches: `docs-content/operations/runs.md`
2. Verify markers are correct: `<!-- MANUAL_START: section-name -->`
3. Run merge again: `python3 scripts/generation/merge-api-docs.py`

### TypeSpec changes not reflected

```bash
# Regenerate from scratch
python3 scripts/generation/generate-api-reference.py
python3 scripts/generation/merge-api-docs.py
```
