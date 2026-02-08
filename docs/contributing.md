# Contributing to Agent Protocol

Thank you for your interest in contributing to the Agent Protocol project!

## Table of Contents

- [Getting Started](#getting-started)
- [Documentation Guidelines](#documentation-guidelines)
- [Validation Workflow](#validation-workflow)
- [Making Changes](#making-changes)
- [Submitting Pull Requests](#submitting-pull-requests)

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a new branch for your changes
4. Make your changes
5. Run validation checks
6. Submit a pull request

## Documentation Guidelines

### TypeSpec as Source of Truth

The TypeSpec files in `/typespec/` are the **single source of truth** for the API specification. All documentation must stay synchronized with TypeSpec definitions.

### Documentation Structure

```
AgentProtocol/
├── typespec/              # Source of truth (TypeSpec definitions)
├── specifications/        # Specification documents
├── api-reference/         # API reference documentation
├── guides/                # User guides and tutorials
└── doc-validation/ # Validation tools
```

### Writing Documentation

When documenting TypeSpec models, enums, or other definitions:

**DO** - Use symbolic references:
```markdown
**TypeSpec**: See `RunStatus` enum in `typespec/execution.tsp`
```

**DON'T** - Use line number references (they break when code changes):
```markdown
**TypeSpec**: `typespec/execution.tsp:324-354`  ❌ FRAGILE
```

## Validation Workflow

### Before Committing

**Always run validation before committing changes:**

```bash
cd doc-validation
make validate
```

This runs three checks:

1. **Enum Synchronization**: Ensures enum values in documentation match TypeSpec
2. **Link Validation**: Checks all internal cross-references are valid
3. **Line Reference Check**: Warns about fragile line number references

### Individual Validation Commands

Run specific validators:

```bash
# Check enum synchronization
python scripts/validate-enums.py

# Check internal links
python scripts/validate-links.py

# Check for line number references
python scripts/check-line-references.py

# Run all checks
python scripts/validate-consistency.py
```

### Fixing Validation Errors

#### Enum Synchronization Errors

If you see: `RunStatus missing values: timeout`

1. Check the TypeSpec definition in `/typespec/`
2. Update the documentation to match
3. Ensure all enum values are documented in the same order

Example fix:
```markdown
<!-- Add missing 'timeout' state -->
| `timeout` | Run exceeded time limit |
```

#### Broken Link Errors

If you see: `Target file not found: ../specifications/run-lifecycle.md`

1. Check that the target file exists
2. Verify the relative path is correct
3. Use absolute paths from project root when possible

Example fix:
```markdown
<!-- Before -->
[Run Lifecycle](../../specifications/run-lifecycle.md)

<!-- After -->
[Run Lifecycle](../specifications/run-lifecycle.md)
```

**Note:** With MkDocs, use relative paths from the current file location.

#### Line Number Reference Warnings

If you see: `Found 5 line number references that should be updated`

Replace line references with symbolic references:

```markdown
<!-- Before (FRAGILE) -->
**TypeSpec** (`typespec/execution.tsp:324-354`):

<!-- After (ROBUST) -->
**TypeSpec** (See `RunStatus` enum in `typespec/execution.tsp`):
```

### CI/CD Integration

All pull requests automatically run validation checks via GitHub Actions. PRs with validation failures will be blocked from merging.

The CI workflow runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop` branches
- Changes to `specifications/`, `api-reference/`, `guides/`, or `typespec/` directories

View the workflow: `.github/workflows/docs-consistency.yml`

## Making Changes

### TypeSpec Changes

When updating TypeSpec definitions:

1. Make your changes to `.tsp` files
2. Update related documentation in `specifications/` and `api-reference/`
3. Run `make validate` to check consistency
4. Fix any validation errors

### Documentation Changes

When updating documentation:

1. Ensure your changes align with TypeSpec definitions
2. Use symbolic references (not line numbers)
3. Maintain consistent terminology
4. Run `make validate` before committing
5. Fix any validation errors

### Common Scenarios

#### Adding a New Enum Value

1. Add the value to TypeSpec:
   ```typescript
   enum RunStatus {
     queued,
     in_progress,
     // ... existing values
     new_value,  // NEW
   }
   ```

2. Update ALL documentation files that reference this enum:
   - `specifications/run-lifecycle.md`
   - `api-reference/models.md`
   - Any guides that mention the enum

3. Run validation: `make validate`

#### Adding a New Model

1. Define the model in TypeSpec
2. Document it in `api-reference/models.md`
3. Add specification details in `specifications/`
4. Include examples in `guides/` if appropriate
5. Run validation: `make validate`

#### Updating Field Descriptions

1. Update TypeSpec comments
2. Update corresponding documentation
3. Run validation: `make validate`

## Submitting Pull Requests

### PR Checklist

Before submitting your pull request:

- [ ] All changes are committed
- [ ] Validation passes locally (`make validate` returns 0)
- [ ] Documentation is updated to match TypeSpec changes
- [ ] No fragile line number references used
- [ ] All links are valid
- [ ] Commit messages are clear and descriptive

### PR Description Template

```markdown
## Summary
Brief description of changes

## Changes Made
- Updated `RunStatus` enum to add `timeout` state
- Updated specifications/run-lifecycle.md
- Updated api-reference/models.md

## Validation
- [x] `make validate` passes
- [x] All enum values synchronized
- [x] All links valid
- [x] No line number references

## Testing
Describe how you tested your changes
```

### Review Process

1. CI validation runs automatically
2. Reviewers check:
   - Documentation accuracy
   - Consistency with TypeSpec
   - Clarity and completeness
3. Address review feedback
4. Merge after approval

## Questions?

If you have questions or need help:

1. Check existing documentation in `specifications/` and `guides/`
2. Review TypeSpec definitions in `typespec/`
3. Run validation tools for specific guidance
4. Open an issue for clarification

Thank you for contributing! 🎉
