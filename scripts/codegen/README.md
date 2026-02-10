# Code Generation Scripts

Scripts for generating code, API documentation, and SDKs from TypeSpec definitions.

## Overview

These scripts generate:
- **SDK Types**: Python, C#, and TypeScript type definitions
- **API Documentation**: Generated from TypeSpec with manual overlays
- **Code Examples**: Extracted from test files

## Execution Order

### Full Generation (Recommended)

```bash
# Generate all SDK types
python3 generate_sdk.py
```

This generates SDK types for all languages:
1. C# types
2. TypeScript types
3. Python types

### Individual Generation

When you only need specific outputs:

```bash
# SDK Type Generation
python3 generate_sdk.py              # All languages (default)
python3 generate_sdk.py --lang python     # Python only
python3 generate_sdk.py --lang csharp     # C# only
python3 generate_sdk.py --lang typescript # TypeScript only

# For TypeScript packages specifically
python3 generate_for_typescript.py   # Wrapper that copies to TS package structure

# API Documentation
python3 generate_api_reference.py    # → .generated/api-docs/
python3 merge_api_docs.py            # Merge generated + manual docs
python3 extract_doc_examples.py      # Extract examples from tests
```

## Scripts Reference

### generate_sdk.py
**Purpose**: Generate SDK types for all languages from TypeSpec
**Technology**: Uses .NET Microsoft.Agents.CodeGen project
**Output**: Generated types in all language packages
**Usage**:
- `python3 generate_sdk.py` - Generate all languages (default)
- `python3 generate_sdk.py --lang python` - Python only
- `python3 generate_sdk.py --lang csharp` - C# only
- `python3 generate_sdk.py --lang typescript` - TypeScript only

### generate_for_typescript.py
**Purpose**: Generate and copy types to TypeScript packages
**What it does**: Calls generate_sdk.py for TypeScript, then copies to TS package locations
**When to use**: When working on TypeScript packages
**Output**: Same as generate_sdk.py + package index files

### generate_api_reference.py
**Purpose**: Generate API reference documentation from TypeSpec
**Output**: `.generated/api-docs/*.md`
**Format**: Markdown files, one per endpoint/model
**Note**: These are skeletons; use merge_api_docs.py to add manual content

### merge_api_docs.py
**Purpose**: Merge generated docs with manual overlays
**Input**: Generated docs + manual docs
**Output**: Final API reference with examples
**Strategy**: Interleaves manual content (examples, best practices) with generated structure

### extract_doc_examples.py
**Purpose**: Extract code examples from test files
**Input**: Python/C#/TypeScript test files with special markers
**Output**: `docs/snippets/*.{py,cs,ts}`
**Used by**: Documentation build system

## Dependencies

All scripts require:
- **.NET SDK**: For code generation (tested with .NET 8.0+)
- **TypeSpec files**: Located in `../../typespec/`
- **Microsoft.Agents.CodeGen**: Our custom code generator project

Python scripts additionally require:
- Python 3.8+
- Dependencies from `../requirements.txt`

## Generated Output Locations

```
Repository Root
├── typespec/                          # Source TypeSpec definitions (INPUT)
│
├── .generated/                        # Generated artifacts
│   └── api-docs/                     # Generated API docs (skeletons)
│
├── dotnet/src/
│   └── Microsoft.Agents.*/Generated/ # C# generated types
│
├── typescript/packages/agents/
│   └── src/generated/                # TypeScript generated types
│
└── python/microsoft-agents-*/
    └── microsoft/agents/models/      # Python generated types
```

## Common Workflows

### After TypeSpec Changes

```bash
# 1. Generate all code
python3 scripts/codegen/generate_sdk.py

# 2. Build and test
cd dotnet && dotnet build
cd ../typescript && npm run build
cd ../python && pytest

# 3. If tests pass, commit
git add .
git commit -m "Regenerate code from TypeSpec"
```

### Updating API Documentation

```bash
# 1. Generate skeleton docs
python generate-api-reference.py

# 2. Edit manual overlays in ../../api-reference-manual/

# 3. Merge generated + manual
python merge-api-docs.py

# 4. Review merged docs in ../../api-reference/
```

### TypeScript Package Development

```bash
# Use this for TypeScript-specific generation
./generate-for-typescript.sh

# Then build the package
cd ../../typescript/packages/agents
npm run build
```

## Troubleshooting

### "dotnet not found"
Install .NET SDK from https://dotnet.microsoft.com/download

### "Permission denied"
Make scripts executable:
```bash
chmod +x *.sh
```

### Generated files not updating
1. Clean generated directories
2. Rebuild CodeGen project: `cd ../../dotnet/src/Microsoft.Agents.CodeGen && dotnet build`
3. Run generation again

### Merge conflicts in generated code
**Never manually edit generated files!** Instead:
1. Update TypeSpec definitions
2. Regenerate all code
3. Generated code should not be edited by hand

## Best Practices

1. **Always regenerate after TypeSpec changes**: Generated code must stay in sync
2. **Run generate-all.sh before committing**: Ensures consistency across languages
3. **Don't edit generated files**: They will be overwritten on next generation
4. **Test after generation**: Run language-specific tests to catch issues early
5. **Version control TypeSpec, not generated code**: Consider .gitignore for generated files

## Related Documentation

- [TypeSpec Definitions](../../typespec/README.md)
- [Test Generation](../testgen/README.md)
- [API Reference Guide](../../api-reference/README.md)
