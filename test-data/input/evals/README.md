# Evaluation Test Suite

This directory contains a comprehensive evaluation test suite organized into logical categories.

## Directory Structure

```
evals/
├── basic/                    # Fundamental evaluation tests (01-03, 09)
├── judges/                   # Judge-based evaluations
│   ├── text/                 # Text judges (05, 06, 23)
│   ├── tool-calls/           # Tool call validation (04, 15, 22)
│   └── semantic/             # Semantic analysis (28, 46)
├── cel/                      # CEL expression tests
│   ├── operators/            # Boolean and numeric operators (51, 52)
│   ├── complex/              # Complex expressions (53, 54, 59)
│   ├── judges/               # Judge combination logic (55-57)
│   └── math/                 # Mathematical operations (58, 60)
├── multi-turn/               # Multi-turn conversations (07, 13, 35)
├── assertions/               # Assertion types (08, 10, 11, 16)
├── content-types/            # Multimodal content (14, 19, 20, 31-33)
├── domain/                   # Domain-specific tests
│   ├── math/                 # Mathematical reasoning (36)
│   ├── code/                 # Code generation (27, 44)
│   ├── language/             # Multi-language (30, 39, 40, 48)
│   └── creative/             # Creative tasks (37, 45)
├── advanced/                 # Advanced features
│   ├── streaming/            # Streaming responses (41, 42)
│   ├── reasoning/            # Reasoning processes (18, 43)
│   └── quality/              # Quality assessment (34, 38, 47)
└── edge-cases/               # Edge case handling
    ├── empty/                # Empty responses (21)
    ├── errors/               # Error handling (12, 17)
    ├── limits/               # System limits (24-26)
    └── special/              # Special content (29, 49, 50)
```

## Categories

### Basic Tests
Fundamental evaluation functionality including text matching, multiple expectations, and JSON validation.

### Judge Tests
Various judge types for automated quality assessment including LLM-based, regex, tool call, and semantic judges.

### CEL Tests
Common Expression Language tests for flexible assertion logic without full scripting capabilities.

### Multi-Turn Tests
Conversational flows with context management and topic transitions.

### Assertion Tests
Different assertion types including numeric comparisons, length validation, and repeatability.

### Content Types
Multimodal content handling including images, audio, video, adaptive cards, and documents.

### Domain-Specific Tests
Tests organized by knowledge domain: math, code, language, and creative tasks.

### Advanced Features
Complex capabilities including streaming, reasoning transparency, and quality metrics.

### Edge Cases
Robust handling of boundaries, errors, empty data, and special characters.

## Usage

All tests are automatically discovered by the test runners in:
- Python: `python/microsoft-agents-protocol/tests/integration/test_eval_integration.py`
- TypeScript: `typescript/packages/agents-hosting/tests/EvalIntegration.test.ts`
- .NET: `dotnet/tests/Microsoft.Agents.Evaluators.Tests/Integration/EvalIntegrationTests.cs`

The test runners recursively scan this directory structure, preserving the organization in generated results.

## Adding New Tests

1. Create your test XML file in the appropriate category directory
2. Run the generation script to create golden results:
   ```bash
   python scripts/testgen/generate_eval_datasets.py
   ```
3. Run the test suite across all platforms:
   ```bash
   pytest python/microsoft-agents-protocol/tests/integration/test_eval_integration.py
   npm test -- EvalIntegration.test.ts
   dotnet test --filter Category=Integration
   ```

## File Naming Convention

Test files follow the pattern: `NN-descriptive-name.xml` where:
- `NN` is a two-digit number (01-60)
- `descriptive-name` briefly describes the test
- Files retain their original names when moved to category directories

## Golden Results

Golden results are generated in `test-data/results/evals/json/` with the same directory structure, enabling cross-platform validation of evaluation implementations.
