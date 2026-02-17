#!/bin/bash
# Run all context gap fix tests

set -e

echo "🧪 Running Context Gap Fix Tests"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

# Add scripts to PYTHONPATH
export PYTHONPATH="$SCRIPT_DIR/../scripts:$PYTHONPATH"

echo -e "${YELLOW}Phase 1: Unit Tests${NC}"
echo "-------------------"
echo ""

echo "Test 1: Iteration Context Loading (Fix 1.1)"
python3 -m pytest "$SCRIPT_DIR/unit/test_iteration_context.py" -v

echo ""
echo "Test 2: Iteration Diff Generation (Fix 1.2)"
python3 -m pytest "$SCRIPT_DIR/unit/test_iteration_diff.py" -v

echo ""
echo "Test 3: StateManager Extensions (Fixes 1.1 & 2.1)"
python3 -m pytest "$SCRIPT_DIR/unit/test_state_manager_extensions.py" -v

echo ""
echo "Test 4: Regeneration Context (Fix 1.3)"
python3 -m pytest "$SCRIPT_DIR/unit/test_regeneration_context.py" -v

echo ""
echo -e "${YELLOW}Phase 2: Integration Tests${NC}"
echo "-------------------------"
echo ""

echo "Test 5: Expert Context Propagation (Fixes 1.1 & 1.2)"
python3 -m pytest "$SCRIPT_DIR/integration/test_expert_context_propagation.py" -v

echo ""
echo "Test 6: Veto Regeneration Workflow (Fixes 1.3, 2.1, 2.2)"
python3 -m pytest "$SCRIPT_DIR/integration/test_veto_regeneration.py" -v

echo ""
echo -e "${GREEN}✅ All Context Gap Tests Passed!${NC}"
echo ""
echo "Summary:"
echo "- Fix 1.1: Iteration context loading ✓"
echo "- Fix 1.2: Iteration diff generation ✓"
echo "- Fix 2.1: Artifact attempt tracking ✓"
echo "- Fix 1.3: Synthesized concerns ✓"
echo "- Fix 2.2: User concern feedback ✓"
