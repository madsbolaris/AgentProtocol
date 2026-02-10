# Test Generation Scripts

Scripts for generating test code and golden datasets from TypeSpec definitions.

## Overview

These scripts generate:

- **Compliance Tests**: Verify implementations conform to Agent Protocol
- **Property Tests**: Validate object properties and types
- **Enum Tests**: Check enum value correctness
- **Golden Datasets**: Reference outputs for cross-language testing
- **Evaluation Datasets**: Golden EvalResult outputs for evaluation tests

## Execution Order

### Generate Tests from TypeSpec

```bash
# Generate all test types
python generate-tests.py

# Generate specific test types
python generate-tests.py --compliance-only
python generate-tests.py --phase1-only
python generate-tests.py --validation-only
```

### Generate Golden Datasets

```bash
# Generate for all samples
python generate_golden_datasets.py

# Generate for specific sample
python generate_golden_datasets.py --sample echo-m365

# With LLM recording capture
python generate_golden_datasets.py --record-llm
```

### Generate Evaluation Datasets

```bash
# Generate for all eval files
python generate_eval_datasets.py

# Generate for specific eval file
python generate_eval_datasets.py --eval-file 01-simple-text-expect.xml

# With LLM recording for semantic judges
python generate_eval_datasets.py --record-llm
```

## Scripts Reference

### generate-tests.py

**Purpose**: Generate test code from TypeSpec definitions

**What it does**:

- Parses TypeSpec schema
- Generates C# xUnit tests
- Generates Python pytest tests
- Generates TypeScript tests
- Creates XML test files

**When to use**: After TypeSpec changes, to ensure test coverage

**Output**:

- `dotnet/tests/**/Generated/`
- `python/microsoft-agents-protocol/tests/`
- `typescript/packages/*/tests/`
- `test-data/input/*.xml`

**Options**:

- `--all`: Regenerate all tests
- `--compliance-only`: Only compliance tests
- `--phase1-only`: Only property/enum tests
- `--validation-only`: Only validation tests
- `--check`: CI mode - verify generated tests match committed files

### generate_golden_datasets.py

**Purpose**: Generate golden datasets for cross-language validation

**What it does**:

1. Reads agent-config.json to discover samples
2. Sends test inputs to running agents
3. Captures outputs as golden files
4. Optionally records LLM interactions

**When to use**: After agent implementation changes, to update reference outputs

**Output**:

- `test-data/results/{sample}/json/*.json`
- `test-data/results/{sample}/xml/*.xml`
- `test-data/llm-recordings/{sample}/*.json` (if --record-llm)

**Options**:

- `--sample NAME`: Generate for specific sample only
- `--record-llm`: Capture LLM interactions for replay
- `--inputs DIR`: Custom inputs directory
- `--results DIR`: Custom results directory

**Prerequisites**:

- Agent bots must be running on configured ports

### generate_eval_datasets.py

**Purpose**: Generate golden evaluation datasets from eval XML files

**What it does**:

1. Reads eval XML files from test-data/input/evals/
2. Runs evaluations using mock agent responses
3. Generates golden EvalResult files
4. Optionally records LLM interactions for semantic judges

**When to use**: After creating new eval files or updating evaluation logic

**Output**:

- `test-data/results/evals/json/*.json`
- `test-data/llm-recordings/evals/*.json` (if --record-llm)

**Options**:

- `--eval-file NAME`: Generate for specific eval file only
- `--record-llm`: Capture LLM interactions for semantic judges
- `--inputs DIR`: Custom inputs directory (default: test-data/input/evals)
- `--results DIR`: Custom results directory (default: test-data/results/evals)

**Prerequisites**:

- None - uses mock agent responses defined in the script
- Or use with samples that auto-start

## Library Modules (lib/)

The `lib/` directory contains reusable Python modules:

- `compliance_test_generator.py`: Generate protocol compliance tests
- `property_test_generator.py`: Generate property validation tests
- `enum_test_generator.py`: Generate enum value tests
- `validation_test_generator.py`: Generate validation logic tests
- `typescript_test_generator.py`: TypeScript-specific test generation
- `test_code_generator.py`: Base test code generation
- `typespec_parser.py`: Parse TypeSpec definitions
- `xml_generator.py`: Generate XML test files
- `test_utilities.py`: Shared utilities
- `code_utils.py`: Code generation helpers

These modules can be imported for custom test generators.

## Common Workflows

### After TypeSpec Changes

```bash
# 1. Generate new tests
python testgen/generate-tests.py

# 2. Run tests to verify
cd ../../dotnet && dotnet test
cd ../../python && pytest
cd ../../typescript && npm test

# 3. If tests pass, commit
git add .
git commit -m "Regenerate tests from TypeSpec"
```

### Updating Golden Datasets

```bash
# 1. Ensure agents are running
python scripts/ci/start_samples.py echo-m365

# 2. Generate golden files
python testgen/generate_golden_datasets.py --sample echo-m365

# 3. Verify outputs look correct
ls -lh ../../test-data/results/echo-m365/

# 4. Run validation tests
pytest ../../python/microsoft-agents-protocol/tests/ -k golden

# 5. If valid, commit
git add ../../test-data/
git commit -m "Update golden datasets for echo-m365"
```

### Creating New Test Sample

```bash
# 1. Add sample to agent-config.json
# 2. Implement agent in python/dotnet/typescript
# 3. Add test inputs to test-data/input/
# 4. Generate golden files
python generate_golden_datasets.py --sample new-sample

# 5. Generate tests
python generate-tests.py
```

## Dependencies

- **Python 3.8+**: For test generation
- **pytest**: For running generated tests
- **TypeSpec files**: Source definitions in `../../typespec/`
- **lxml**: For XML processing

Install dependencies:

```bash
pip install -r ../requirements.txt
```

## Generated Output Locations

```
Repository Root
├── test-data/
│   ├── input/                         # Test input files (XML)
│   ├── results/{sample}/              # Golden datasets
│   │   ├── json/*.json               # JSON format outputs
│   │   └── xml/*.xml                 # XML format outputs
│   └── llm-recordings/{sample}/      # LLM interaction recordings
│
├── dotnet/tests/
│   └── **/Generated/                  # Generated C# tests
│
├── python/microsoft-agents-protocol/tests/
│   ├── test_*.py                     # Generated Python tests
│   └── integration/                  # Integration tests
│
└── typescript/packages/*/tests/
    └── *.test.ts                     # Generated TypeScript tests
```

## Troubleshooting

### Tests fail after generation

1. Check TypeSpec syntax
2. Rebuild SDKs: `dotnet build`, `npm run build`
3. Clear test caches
4. Regenerate from clean state

### Golden files don't match

This means agent behavior changed:

1. Review agent implementation changes
2. If intentional, regenerate: `python generate_golden_datasets.py`
3. If unintentional, fix agent and regenerate

### "Agent not responding"

1. Check agents are running: `ps aux | grep echo-m365`
2. Check ports: `lsof -i :3978,3979,3980`
3. Start agents: `python ../ci/start_samples.py echo-m365`
4. Check agent logs in `../../.logs/`

## Best Practices

1. **Regenerate tests after TypeSpec changes**: Keep tests in sync with definitions
2. **Version control golden files**: They are the source of truth for behavior
3. **Use LLM recordings for deterministic tests**: Replay instead of calling real LLMs
4. **Don't edit generated tests manually**: Will be overwritten on next generation
5. **Run all language tests**: Ensure cross-language consistency

## Related Documentation

- [Code Generation](../codegen/README.md)
- [Validation Scripts](../validation/README.md)
- [Golden Dataset Guide](../../.workspace/GOLDEN_DATASET_UPDATES.md)
- [Agent Configuration](../../agent-config.json)
