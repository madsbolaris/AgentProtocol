#!/bin/bash

set -e

echo "🚀 Generating Basic M365 Agent Golden Files"
echo "============================================"
echo ""

# Check environment variables
if [ -z "$FOUNDRY_ENDPOINT" ] || [ -z "$FOUNDRY_API_KEY" ]; then
    echo "❌ Error: FOUNDRY_ENDPOINT and FOUNDRY_API_KEY must be set"
    echo ""
    echo "Set them before running:"
    echo "  export FOUNDRY_ENDPOINT=https://..."
    echo "  export FOUNDRY_API_KEY=..."
    echo ""
    exit 1
fi

echo "✅ Environment check passed"
echo "   Endpoint: $FOUNDRY_ENDPOINT"
echo "   Model: ${FOUNDRY_MODEL_DEPLOYMENT:-gpt-5-nano}"
echo ""

# Get repository root (script is in scripts/ directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

echo "📁 Repository root: $REPO_ROOT"
echo ""

# Start Basic M365 Agent
echo "📦 Starting Python Basic M365 Agent..."
cd "$REPO_ROOT/python/samples/agents/function_tools_agent"

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

# Run generation tests
echo "🏗️  Running tests in GENERATION mode..."
cd "$REPO_ROOT/python/microsoft-agents-protocol"

export TEST_MODE=generate
export LLM_TEMPERATURE=0.0
export LLM_SEED=42

# Run tests with verbose output
pytest tests/integration/test_function_tools_generation.py -v -s

TEST_EXIT_CODE=$?

echo ""

# Stop agent
echo "🛑 Stopping agent (PID: $AGENT_PID)..."
kill $AGENT_PID 2>/dev/null || true
wait $AGENT_PID 2>/dev/null || true

echo ""

# Check test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Generation complete!"
    echo ""
    echo "📂 Generated files:"
    echo ""
    echo "   Golden files (json):"
    ls -lh "$REPO_ROOT/test-data/results/basic-m365/json/" 2>/dev/null || echo "      (none yet)"
    echo ""
    echo "   Golden files (xml):"
    ls -lh "$REPO_ROOT/test-data/results/basic-m365/xml/" 2>/dev/null || echo "      (none yet)"
    echo ""
    echo "   LLM recordings:"
    RECORDING_COUNT=$(ls "$REPO_ROOT/test-data/llm-recordings/basic-m365/"*.response.json 2>/dev/null | wc -l)
    echo "      $RECORDING_COUNT recordings"
    echo ""
    echo "🎉 Success! You can now run validation tests:"
    echo "   pytest tests/integration/test_function_tools_integration.py -v"
else
    echo "❌ Generation failed with exit code $TEST_EXIT_CODE"
    exit $TEST_EXIT_CODE
fi
