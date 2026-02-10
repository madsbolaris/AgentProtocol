# Validation Scripts

Scripts for validating documentation, code, and infrastructure against specifications.

## Overview

These scripts validate:

- **Documentation**: Check docs match TypeSpec definitions
- **API Reference**: Validate completeness and quality
- **Cross-references**: Ensure internal links are valid
- **Type Consistency**: Verify TypeSpec ↔ Docs alignment
- **Infrastructure**: Check test setup and file structure

## Execution Order

Most validation scripts are independent and can run in any order. Use the Makefile for common workflows:

```bash
# From scripts/ directory
make validate     # Run all validations
make enums        # Check enum sync
make links        # Validate links
make api-ref      # Check API reference quality
```

## Scripts Reference

### validate-docs-against-typespec.py

**Purpose**: Ensure documentation matches TypeSpec definitions

**What it checks**:

- All TypeSpec models documented
- Property descriptions match
- Type definitions consistent

**When to use**: After TypeSpec or doc changes

### validate-api-reference.py

**Purpose**: Validate API reference documentation quality

**What it checks**:

- Complete parameter descriptions
- Example code present
- HTTP methods correct
- Response codes documented

**When to use**: Before releasing docs

### validate-typespec-docs.py

**Purpose**: Check TypeSpec inline documentation

**What it checks**:

- All models have doc comments
- Properties have descriptions
- Enums documented

**When to use**: During TypeSpec development

### validate-consistency.py

**Purpose**: Master validator running multiple checks

**What it does**: Orchestrates other validation scripts

**When to use**: CI/CD, pre-commit

### validate-enums.py

**Purpose**: Check enum synchronization across languages

**What it checks**:

- TypeSpec enum values
- C# enum values
- Python enum values
- TypeScript enum values

**When to use**: After adding/modifying enums

### validate-links.py

**Purpose**: Validate internal documentation links

**What it checks**:

- Relative links resolve
- Anchors exist
- No broken links

**When to use**: Before publishing docs

### validate-api-docs-completeness.py

**Purpose**: Check API docs have all required sections

**What it checks**:

- Overview sections present
- Examples included
- Error responses documented

**When to use**: Doc review process

### validate-model-docs.py

**Purpose**: Validate model documentation completeness

**What it checks**:

- All properties documented
- Example objects provided
- Related models linked

**When to use**: After model changes

### check-cross-references.py

**Purpose**: Validate cross-references between docs

**What it checks**:

- Referenced sections exist
- Links point to correct anchors
- Bidirectional references

**When to use**: Large doc restructuring

### check-line-references.py

**Purpose**: Check line number references in docs

**What it checks**:

- Code snippets reference valid lines
- Line numbers still accurate

**When to use**: After code changes

### check-old-patterns.py

**Purpose**: Detect deprecated patterns in code/docs

**What it checks**:

- Old API usage
- Deprecated types
- Outdated examples

**When to use**: Before major releases

### check-routes.py

**Purpose**: Validate API route definitions

**What it checks**:

- Routes defined in TypeSpec
- Routes implemented in code
- Route parameters match

**When to use**: After API changes

### check-typespec-terms.py

**Purpose**: Check terminology consistency

**What it checks**:

- Standard terms used
- Naming conventions followed

**When to use**: Documentation review

### detect-misplaced-content.py

**Purpose**: Find content in wrong documentation sections

**What it checks**:

- API reference vs. guides
- Examples vs. reference material

**When to use**: Content organization cleanup

### check_annotations.py

**Purpose**: Check TypeSpec annotation usage

**What it checks**:

- ContentAnnotations model exists
- Proper annotation usage
- Required annotations present

**When to use**: After TypeSpec structure changes

### extract_content_types.py

**Purpose**: Extract content types from TypeSpec

**What it does**: Generates list of AIContent union types

**Output**: `.workspace/content-types-current.txt`

**When to use**: Before running compare_content_types.py

### compare_content_types.py

**Purpose**: Compare TypeSpec types vs. documented types

**What it checks**:

- All TypeSpec types documented
- No extra undocumented types

**Output**: `.workspace/content-type-comparison.json`

**When to use**: After type changes

### validate_test_infrastructure.py

**Purpose**: Validate test infrastructure setup

**What it checks**:

- Test directories exist
- Test files present
- Golden files available
- Path configurations correct

**When to use**: CI setup, new developer onboarding

### validate-echo-m365s.py

**Purpose**: Validate echo bot samples haven't drifted

**What it checks**:

- Echo bots match baseline
- Only protocol changes added
- No unintended modifications

**When to use**: Before committing echo bot changes

**Options**:

- `--update`: Update baseline snapshots

## Common Workflows

### Pre-Commit Validation

```bash
# Quick checks before committing
python validate-consistency.py
python validate-links.py
python check-typespec-terms.py
```

### Full Documentation Review

```bash
# Comprehensive validation
make validate

# Or manually:
python validate-docs-against-typespec.py
python validate-api-reference.py
python validate-api-docs-completeness.py
python validate-model-docs.py
python check-cross-references.py
```

### After TypeSpec Changes

```bash
# 1. Extract current types
python extract_content_types.py

# 2. Compare with docs
python compare_content_types.py

# 3. Validate consistency
python validate-docs-against-typespec.py

# 4. Check enums
python validate-enums.py
```

### CI/CD Pipeline

```bash
# Run all validations
make validate

# Or specific checks:
make enums        # Enum consistency
make links        # Link validation
make api-ref      # API docs quality
make misplaced    # Content placement
```

## Dependencies

- **Python 3.8+**: For running validation scripts
- **lxml**: For XML parsing
- **requests**: For link checking (optional)

Install dependencies:

```bash
pip install -r ../requirements.txt
```

## Output and Reporting

Most scripts output to stdout with color-coded results:

- ✅ Green: Checks passed
- ❌ Red: Validation errors
- ⚠️ Yellow: Warnings

Some scripts generate reports in `.workspace/`:

- `content-type-comparison.json`
- `validation-report.txt`
- `link-check-results.json`

## Troubleshooting

### Validation fails after TypeSpec changes

1. Regenerate code: `cd ../codegen && ./generate-all.sh`
2. Update documentation to match new types
3. Run validation again

### False positives

Some validators may flag intentional differences:

1. Check if the flagged issue is intentional
2. Update validator exceptions if needed
3. Document exceptions in code comments

### Link validation errors

1. Check if file was moved/renamed
2. Update links in documentation
3. Run `validate-links.py` again

## Best Practices

1. **Run validations before committing**: Catch issues early
2. **Fix TypeSpec first**: Then update docs and code
3. **Use CI integration**: Automate validation in pipelines
4. **Don't ignore warnings**: They indicate potential issues
5. **Keep validators updated**: As spec evolves, update checks

## Related Documentation

- [Code Generation](../codegen/README.md)
- [Test Generation](../testgen/README.md)
- [TypeSpec Definitions](../../typespec/README.md)
