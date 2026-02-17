# Test Fixtures

Test fixtures for the expert-feedback skill test suite.

## Directory Structure

```
fixtures/
├── README.md                          # This file
├── mock_experts/                      # Mock expert responses
│   ├── typescript_review_sample.json  # Sample TypeScript expert review
│   ├── python_review_sample.json      # Sample Python expert review
│   └── ...                            # More mock responses
└── sample_workspaces/                 # Sample workspace states
    └── ...                            # Coming soon
```

## Mock Expert Responses

Mock expert responses are pre-generated JSON files that simulate expert feedback without requiring API calls. These are useful for:

- **Unit testing** - Test synthesizion logic without spawning real experts
- **Integration testing** - Test workflow without API costs
- **Development** - Iterate on features without waiting for experts

### Format

Each mock expert response includes:

- `expert` - Expert identifier (e.g., "typescript", "python")
- `iteration` - Iteration number
- `session_id` - Mock session ID
- `status` - "completed", "failed", or "timeout"
- `duration_seconds` - Simulated execution time
- `token_count` - Simulated token usage
- `rating` - DX rating (1-5)
- `confidence` - Confidence level ("high", "medium", "low")
- `strengths` - List of strengths
- `concerns` - List of concerns with severity
- `recommendations` - List of actionable recommendations
- `questions` - List of clarifying questions

### Usage in Tests

```python
import json
from pathlib import Path

fixtures_dir = Path(__file__).parent / "fixtures"
typescript_review = json.loads((fixtures_dir / "mock_experts/typescript_review_sample.json").read_text())

# Use in test
assert typescript_review["expert"] == "typescript"
assert typescript_review["rating"] == 4
```

## Sample Workspaces

Sample workspace states at various stages of the workflow:

- **Initial state** - Fresh workspace after initialization
- **After iteration 1** - State after first expert run
- **After synthesizion** - State with convergence metrics
- **Final state** - State after consensus reached

### Coming Soon

Sample workspace fixtures will be added to demonstrate:

- Single iteration workflow
- Multi-iteration workflow
- Artifact review phase
- Session resumption

## Creating New Fixtures

To create new test fixtures:

1. **Run real workflow** - Execute expert-feedback with desired configuration
2. **Copy outputs** - Copy relevant JSON files from workspace
3. **Sanitize data** - Remove any sensitive information
4. **Add to fixtures/** - Place in appropriate subdirectory
5. **Document** - Add description to this README

### Example

```bash
# Run workflow
/expert-feedback "Test topic" typescript python

# Copy outputs
cp .workspace/2026/02/14/expert-feedback-test-topic/state-typescript-1.json \
   tests/fixtures/mock_experts/typescript_custom.json

# Sanitize and edit as needed
vim tests/fixtures/mock_experts/typescript_custom.json
```

## Guidelines

- **Keep it realistic** - Fixtures should represent actual expert outputs
- **Keep it small** - Don't include huge files
- **Keep it generic** - Remove project-specific details
- **Keep it documented** - Add comments explaining special cases

---

**Need more fixtures?** Run real workflows and save the outputs!
