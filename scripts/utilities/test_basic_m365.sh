#!/bin/bash

set -e

echo "🧪 Running Function Tools Integration Tests"
echo "==========================================="
echo ""

# Get repository root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Repository root: $REPO_ROOT"
echo ""

# Check for golden files
GOLDEN_DIR="$REPO_ROOT/test-data/results/function-tools/json"
if [ ! -d "$GOLDEN_DIR" ] || [ -z "$(ls -A "$GOLDEN_DIR" 2>/dev/null)" ]; then
    echo "❌ No golden files found"
    echo ""
    echo "Run generation first:"
    echo "  ./scripts/generate_function_tools_golden_files.sh"
    echo ""
    exit 1
fi

GOLDEN_COUNT=$(ls "$GOLDEN_DIR"/*.json 2>/dev/null | wc -l)
echo "✅ Found $GOLDEN_COUNT golden files"
echo ""

# Check for LLM recordings
RECORDINGS_DIR="$REPO_ROOT/test-data/llm-recordings/function-tools"
if [ ! -d "$RECORDINGS_DIR" ] || [ -z "$(ls -A "$RECORDINGS_DIR" 2>/dev/null)" ]; then
    echo "❌ No LLM recordings found"
    echo ""
    echo "Run generation first:"
    echo "  ./scripts/generate_function_tools_golden_files.sh"
    echo ""
    exit 1
fi

RECORDING_COUNT=$(ls "$RECORDINGS_DIR"/*.response.json 2>/dev/null | wc -l)
echo "✅ Found $RECORDING_COUNT LLM recordings"
echo ""

# Start Basic M365 Agent
echo "📦 Starting Python Basic M365 Agent..."
cd "$REPO_ROOT/python/samples/agents/basic_m365_agent"

# Check if requirements are installed
if ! python -c "import openai" 2>/dev/null; then
    echo "📥 Installing requirements..."
    pip install -r requirements.txt -q
fi

# Start agent in background
python -m src.main &
AGENT_PID=$!

echo "   Agent PID: $AGENT_PID"
echo "   Waiting for agent to start..."
sleep 5

# Check if agent is running
if ! kill -0 $AGENT_PID 2>/dev/null; then
    echo "❌ Agent failed to start"
    exit 1
fi

echo "✅ Agent started successfully"
echo ""

# Run tests
echo "🧪 Running integration tests..."
cd "$REPO_ROOT/python/microsoft-agents-protocol"

# Make sure TEST_MODE is not set (default is "test")
unset TEST_MODE

# Run tests with verbose output
pytest tests/integration/test_function_tools_integration.py -v -s

TEST_EXIT_CODE=$?

echo ""

# Stop agent
echo "🛑 Stopping agent (PID: $AGENT_PID)..."
kill $AGENT_PID 2>/dev/null || true
wait $AGENT_PID 2>/dev/null || true

echo ""

# Check test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo ""
    echo "🎉 Success! Basic M365 Agent is working correctly with mocked LLM."
else
    echo "❌ Tests failed with exit code $TEST_EXIT_CODE"
    exit $TEST_EXIT_CODE
fi
