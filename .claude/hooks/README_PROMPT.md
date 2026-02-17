# Stop Continue Analyzer - Prompt Configuration

## Overview

The Stop Continue Analyzer hook uses an external prompt file that can be updated without restarting your Claude Code session.

## Files

- **stop_continue_analyzer_debug.py** - The hook script that runs on Stop events
- **stop_continue_analyzer_prompt.txt** - The prompt template (EDIT THIS FILE)

## How to Update the Prompt

1. Edit [stop_continue_analyzer_prompt.txt](./stop_continue_analyzer_prompt.txt)
2. Save your changes
3. The new prompt takes effect immediately on the next Stop event

**No need to restart your conversation!**

## Prompt Template Variables

The prompt template uses Python format strings with these placeholders:

- `{goal_context}` - The original user request (if available)
- `{conversation_summary_count}` - Number of messages in the summary
- `{conversation_summary_exchanges}` - Number of exchanges shown
- `{conversation_text}` - The actual conversation text

## Testing Your Changes

After editing the prompt:

1. Trigger a Stop event (let Claude finish a response)
2. Check `/tmp/stop_hook_debug.log` to see:
   - If the prompt loaded successfully
   - The LLM's decision and reasoning
   - Any errors

## Tips for Prompt Editing

- Keep the JSON response format unchanged
- Test changes incrementally
- Check the debug log after each test
- Use the Examples section to add new patterns
- Keep instructions clear and unambiguous

## Example Workflow

```bash
# Edit the prompt
vim .claude/hooks/stop_continue_analyzer_prompt.txt

# Let Claude respond to something...
# (hook runs automatically)

# Check what happened
tail -50 /tmp/stop_hook_debug.log
```
