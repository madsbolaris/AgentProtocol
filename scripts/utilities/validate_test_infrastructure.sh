#!/bin/bash

set -e

echo "🔍 Validating Test Infrastructure"
echo "=================================="
echo ""

# Get repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Repository root: $REPO_ROOT"
echo ""

# Check directory structure
echo "📂 Checking directory structure..."

# Test data directories
if [ -d "$REPO_ROOT/test-data" ]; then
    echo "   ✅ test-data/ exists"
else
    echo "   ❌ test-data/ missing"
    exit 1
fi

if [ -d "$REPO_ROOT/test-data/input" ]; then
    echo "   ✅ test-data/input/ exists"
else
    echo "   ❌ test-data/input/ missing"
    exit 1
fi

if [ -d "$REPO_ROOT/test-data/results/function-tools/json" ]; then
    echo "   ✅ test-data/results/function-tools/json/ exists"
else
    echo "   ❌ test-data/results/function-tools/json/ missing"
    exit 1
fi

if [ -d "$REPO_ROOT/test-data/results/function-tools/xml" ]; then
    echo "   ✅ test-data/results/function-tools/xml/ exists"
else
    echo "   ❌ test-data/results/function-tools/xml/ missing"
    exit 1
fi

if [ -d "$REPO_ROOT/test-data/llm-recordings/function-tools" ]; then
    echo "   ✅ test-data/llm-recordings/function-tools/ exists"
else
    echo "   ❌ test-data/llm-recordings/function-tools/ missing"
    exit 1
fi

echo ""

# Check input files
echo "📄 Checking input files..."
INPUT_COUNT=$(ls "$REPO_ROOT/test-data/input/"5*.xml 2>/dev/null | wc -l)
echo "   Found $INPUT_COUNT input test files"

if [ "$INPUT_COUNT" -ge 4 ]; then
    echo "   ✅ All 4 test input files present"
else
    echo "   ⚠️  Expected 4 input files, found $INPUT_COUNT"
fi

echo ""

# Check test files
echo "🧪 Checking test files..."

if [ -f "$REPO_ROOT/python/microsoft-agents-protocol/tests/integration/test_function_tools_generation.py" ]; then
    echo "   ✅ test_function_tools_generation.py exists"
else
    echo "   ❌ test_function_tools_generation.py missing"
    exit 1
fi

if [ -f "$REPO_ROOT/python/microsoft-agents-protocol/tests/integration/test_function_tools_integration.py" ]; then
    echo "   ✅ test_function_tools_integration.py exists"
else
    echo "   ❌ test_function_tools_integration.py missing"
    exit 1
fi

if [ -f "$REPO_ROOT/python/microsoft-agents-protocol/tests/utils/test_helpers.py" ]; then
    echo "   ✅ test_helpers.py exists"
else
    echo "   ❌ test_helpers.py missing"
    exit 1
fi

echo ""

# Verify test_helpers.py uses "json" not "wait"
echo "🔧 Verifying path updates..."
if grep -q 'pattern: Literal\["json", "xml"\]' "$REPO_ROOT/python/microsoft-agents-protocol/tests/utils/test_helpers.py"; then
    echo "   ✅ test_helpers.py uses 'json' pattern"
else
    echo "   ❌ test_helpers.py still uses 'wait' pattern"
    exit 1
fi

if grep -q 'results/function-tools/json' "$REPO_ROOT/scripts/test_function_tools.sh"; then
    echo "   ✅ test_function_tools.sh uses json path"
else
    echo "   ❌ test_function_tools.sh still uses wait path"
    exit 1
fi

if grep -q 'results/function-tools/json' "$REPO_ROOT/scripts/generate_function_tools_golden_files.sh"; then
    echo "   ✅ generate_function_tools_golden_files.sh uses json path"
else
    echo "   ❌ generate_function_tools_golden_files.sh still uses wait path"
    exit 1
fi

echo ""

# Check golden files and recordings status
echo "📊 Checking golden files and recordings..."
JSON_COUNT=$(ls "$REPO_ROOT/test-data/results/function-tools/json/"*.json 2>/dev/null | wc -l)
XML_COUNT=$(ls "$REPO_ROOT/test-data/results/function-tools/xml/"*.xml 2>/dev/null | wc -l)
RECORDING_COUNT=$(ls "$REPO_ROOT/test-data/llm-recordings/function-tools/"*.response.json 2>/dev/null | wc -l)

echo "   JSON golden files: $JSON_COUNT"
echo "   XML golden files: $XML_COUNT"
echo "   LLM recordings: $RECORDING_COUNT"

if [ "$JSON_COUNT" -eq 0 ] && [ "$RECORDING_COUNT" -eq 0 ]; then
    echo ""
    echo "   ℹ️  No golden files or recordings yet"
    echo "   Run generation to create them:"
    echo "      ./scripts/generate_function_tools_golden_files.sh"
else
    echo "   ✅ Golden files and/or recordings exist"
fi

echo ""
echo "=================================="
echo "✅ Infrastructure validation complete!"
echo ""
echo "Next steps:"
echo "  1. Generate golden files (requires Foundry credentials):"
echo "     ./scripts/generate_function_tools_golden_files.sh"
echo ""
echo "  2. Run tests (no credentials needed):"
echo "     ./scripts/test_function_tools.sh"
echo ""
