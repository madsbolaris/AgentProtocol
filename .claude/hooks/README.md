# Claude Code Stop Hook: Continue Analyzer

This hook uses an LLM to automatically detect when Claude stops responding prematurely and should be told "continue" to keep working.

## How It Works

When Claude finishes responding (Stop event), this hook:

1. **Reads the conversation transcript** from the session
2. **Calls Claude Haiku** (fast, cheap model) to analyze the last few conversation exchanges
3. **Determines if Claude has unfinished work** based on signals like:
   - Explicit mentions of next steps ("I'll do X next", "then I'll...")
   - Incomplete implementations
   - Tests that weren't run
   - Code that wasn't verified
   - Clear tasks mentioned but not completed
4. **Blocks the stop** if Claude should continue, providing a reason
5. **Allows the stop** if the task appears complete

## Files

- `stop_continue_analyzer.py` - Main hook script that does LLM analysis
- `test_stop_hook.py` - Test suite to verify hook behavior
- `/Users/mabolan/AgentProtocol/.claude/hooks.json` - Hook configuration

## Configuration

The hook is configured in `.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/stop_continue_analyzer.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

**Important**: Hooks are loaded at session startup. After editing settings, start a new session or run `/hooks` to reload.

## Key Features

### 1. Infinite Loop Prevention

The hook checks `stop_hook_active` to prevent recursive triggers:

```python
if hook_input.get('stop_hook_active', False):
    # Already in a Stop hook, allow the stop
    print(json.dumps({"decision": "allow"}))
    return 0
```

### 2. Confidence-Based Decisions

Only blocks if the LLM analysis has medium or high confidence:

```python
if analysis.get('should_continue', False):
    confidence = analysis.get('confidence', 'low')
    if confidence in ['high', 'medium']:
        # Block with reason
    else:
        # Allow stop (not confident enough)
```

### 3. Fail-Open Design

If anything goes wrong (API error, transcript not found, etc.), the hook allows the stop rather than blocking indefinitely.

## Testing

Run the test suite:

```bash
python3 .claude/hooks/test_stop_hook.py
```

Tests verify:
- ✅ Detects when Claude has unfinished work (blocks)
- ✅ Detects when task is complete (allows)
- ✅ Prevents infinite loops (stop_hook_active)

## Authentication

The hook uses `.claude/sdk_auth.py` to extract the Anthropic API key from Claude Code's macOS Keychain entry. No manual configuration needed.

## Cost Considerations

- Uses `claude-3-5-haiku-latest` (fastest, cheapest model)
- Each hook trigger costs ~$0.0001-0.0003
- 30-second timeout prevents runaway costs
- Typical analysis completes in 1-3 seconds

## Customization

### Adjust Analysis Prompt

Edit the `analysis_prompt` in `stop_continue_analyzer.py` to tune what signals indicate "continue":

```python
analysis_prompt = f"""Analyze this conversation...

Look for signs Claude should continue:
- Your custom criteria here
- ...
"""
```

### Change Model

Switch to a different model in `stop_continue_analyzer.py`:

```python
response = client.messages.create(
    model="claude-3-opus-latest",  # More capable, more expensive
    max_tokens=300,
    messages=[{"role": "user", "content": analysis_prompt}]
)
```

### Adjust Confidence Threshold

Require only low confidence to block:

```python
if confidence in ['high', 'medium', 'low']:  # More aggressive
    decision = {"decision": "block", "reason": f"Continue: {reason}"}
```

Or require high confidence:

```python
if confidence == 'high':  # More conservative
    decision = {"decision": "block", "reason": f"Continue: {reason}"}
```

## Disabling the Hook

To temporarily disable:

```bash
# Rename hooks.json
mv .claude/hooks.json .claude/hooks.json.disabled
```

Or remove the Stop hook from `.claude/hooks.json`.

## Troubleshooting

### Hook not triggering

Check logs when Claude Code runs:
```bash
# Hook errors appear in stderr
# Check your terminal output for hook messages
```

### Hook always allows/blocks

Run the test suite to verify behavior:
```bash
python3 .claude/hooks/test_stop_hook.py
```

Check the LLM analysis prompt is appropriate for your use case.

### API errors

Verify API key is accessible:
```bash
python3 .claude/sdk_auth.py
```

Should show: `✅ API key configured: sk-ant-api03-...`

## Example Output

When Claude stops prematurely:

```
Hook decision: block
Reason: Continue: Claude mentioned plans to add comprehensive tests and
        documentation but did not actually show the implementation or tests.
        The tasks described seem incomplete.
```

Claude will see this reason and continue working on the tests and documentation.
