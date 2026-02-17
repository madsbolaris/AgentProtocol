# Recording Verification Guide

This document explains how to verify that generated recordings show agents behaving correctly according to their prompts.

## What to Check After Recording Generation

After generating recordings with `EXPERT_FEEDBACK_TEST_MODE=record`, verify:

### 1. Prompt Quality

**Use the analyzer:**
```bash
python3 tests/integration/analyze_recordings.py --recent 3
```

**Check that prompts:**
- ✅ Are focused and clear about the task
- ✅ Don't include unnecessary context
- ✅ Include relevant workspace information
- ✅ Are appropriate length (not too verbose, not too terse)
- ❌ Don't contain debugging artifacts or test-specific instructions
- ❌ Don't ask agents to do things outside their role

### 2. Agent Behavior - TypeScript Expert

**Expected behaviors:**
- ✅ Reviews TypeScript code in the mock project
- ✅ Identifies type safety issues (code uses `any` types)
- ✅ Identifies lack of input validation
- ✅ Provides `dx_rating` with 2-4 stars (code has obvious issues)
- ✅ Raises concerns about missing tests
- ✅ Asks clarifying questions about requirements

**Red flags:**
- ❌ Reviews Python code instead of TypeScript
- ❌ Gives 5-star DX rating (code is intentionally flawed)
- ❌ Provides generic feedback not specific to the calculator
- ❌ Refuses to complete the review
- ❌ Output is too short (<200 chars) or malformed

### 3. Agent Behavior - Python Expert

**Expected behaviors:**
- ✅ Reviews Python code in the mock project
- ✅ Identifies security issue (uses `eval()`)
- ✅ Identifies lack of error handling
- ✅ Identifies missing type hints
- ✅ Provides `dx_rating` with 2-4 stars
- ✅ Asks about error handling preferences

**Red flags:**
- ❌ Reviews TypeScript code instead of Python
- ❌ Misses the `eval()` security vulnerability
- ❌ Gives 5-star DX rating
- ❌ Generic feedback not project-specific
- ❌ Malformed or incomplete output

### 4. Agent Behavior - Synthesis

**Expected behaviors:**
- ✅ Consolidates feedback from both experts
- ✅ Calculates convergence percentage
- ✅ Extracts and deduplicates questions
- ✅ Identifies common themes across experts
- ✅ Provides structured output

**Red flags:**
- ❌ Only mentions one expert
- ❌ Convergence calculation is wrong or missing
- ❌ Questions are not properly extracted
- ❌ Output doesn't show synthesis across experts

## Using the Analysis Script

### Quick check (3 most recent):
```bash
cd /Users/mabolan/AgentProtocol/.claude/skills/expert-feedback
python3 tests/integration/analyze_recordings.py
```

### Check specific recording:
```bash
python3 tests/integration/analyze_recordings.py --hash 344dbeddc140ac96
```

### Detailed analysis (saves full prompts/outputs to files):
```bash
python3 tests/integration/analyze_recordings.py --recent 5 --verbose
```

### Check all recordings:
```bash
python3 tests/integration/analyze_recordings.py --all
```

## What the Analyzer Shows

For each recording, you'll see:
- **Expert identified** (typescript, python, synthesis)
- **Prompt preview** (first 500 chars)
- **Output preview** (first 1000 chars)
- **Analysis warnings** for concerning patterns:
  - Agent refused task
  - Output too short
  - Missing expected structure
  - Expert reviewing wrong language
  - Missing key information

## Common Issues and Fixes

### Issue: Agent gives 5-star rating for flawed code
**Root cause:** Prompt doesn't emphasize critical review
**Fix:** Update expert prompt to be more critical/thorough

### Issue: Agent doesn't find security issues
**Root cause:** Prompt doesn't include security focus
**Fix:** Add security review to expert prompt

### Issue: Agent output is too short
**Root cause:** Prompt may be confusing or agent hit limit
**Fix:** Check prompt clarity, ensure workspace context is included

### Issue: TypeScript expert reviews Python code
**Root cause:** Workspace path or context passing issue
**Fix:** Verify mock project is copied correctly to workspace

### Issue: No questions are asked
**Root cause:** Code appears complete to agent or prompt doesn't encourage questions
**Fix:** Ensure mock project has ambiguous requirements

## Recording File Structure

Each recording consists of two files:

### `{hash}.request.json`
```json
{
  "prompt": "Full compiled prompt sent to agent...",
  "system": [...],
  "messages": [...],
  "options": {...}
}
```

### `{hash}.response.json`
```json
{
  "events": [
    {"type": "content", "content": {"text": "Agent output..."}},
    {"type": "message", "message": {...}}
  ]
}
```

## Next Steps After Verification

Once recordings are verified:

1. ✅ Commit recordings if agents behaved correctly
2. ✅ Run tests in replay mode to ensure they pass
3. ✅ Move to next phase (Phase 4: Q1 branch)

If recordings show issues:
1. ❌ Update prompts to fix agent behavior
2. ❌ Regenerate recordings
3. ❌ Verify again before proceeding
