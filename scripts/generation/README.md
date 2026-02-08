# Code Generation Scripts

Generate Python, .NET, and TypeScript code from TypeSpec schemas.

## Main Scripts

### generate-all.sh
Generate code for all languages:
```bash
./scripts/generation/generate-all.sh
```

### Language-Specific Generation

```bash
# Python
./scripts/generation/generate-python.sh

# .NET / C#
./scripts/generation/generate-csharp.sh

# TypeScript
./scripts/generation/generate-typescript.sh
```

### Test Generation

```bash
# Generate tests from TypeSpec
python scripts/generation/generate-tests.py

# Generate specific test types
python scripts/generation/generate-tests.py --compliance-only
python scripts/generation/generate-tests.py --phase1-only
```

## test_gen/ Module

The `test_gen/` directory contains reusable modules for test generation:

- `typespec_parser.py` - Parse TypeSpec schemas
- `test_code_generator.py` - Generate test code
- `compliance_test_generator.py` - Generate compliance tests
- `property_test_generator.py` - Generate property validation tests
- `enum_test_generator.py` - Generate enum tests
- And more...

These are used by `generate-tests.py` and can be imported for custom generators.
