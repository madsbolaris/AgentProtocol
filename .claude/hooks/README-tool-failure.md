# Tool Failure Hook - Handle Interrupted Agents

## What This Does

The `tool_failure` hook fires when Claude encounters an error executing a tool (Bash, Read, Write, etc.) and gets interrupted. This is different from the normal `Stop` hook, which only fires when Claude finishes normally.

## Current Behavior

Right now, the hook:
1. **Logs the failure** to `/tmp/tool_failure_hook.log`
2. **Plays a beep** to alert you
3. **Allows the interruption** (Claude stops and waits for you)

## How to Continue After Interruption

When you see "Interrupted" status, just type:
```
continue
```

Or be more specific:
```
fix that bash error and continue
```

## Auto-Continue for Recoverable Errors (Optional)

You can modify the hook to automatically continue for certain types of errors:

```python
# In tool_failure hook, replace the return section:

# Classify error type
is_recoverable = False

# Example: Auto-continue on bash parsing errors
if tool_name == "Bash" and "substitution" in error_message.lower():
    is_recoverable = True
    continue_message = "Fix the bash syntax error and try the command again"

# Example: Auto-continue on file not found
if "not found" in error_message.lower():
    is_recoverable = True
    continue_message = "The file doesn't exist. Please check the path and try again"

if is_recoverable:
    # Block the interruption and send continue message
    print(json.dumps({
        "decision": "block",
        "continueMessage": continue_message
    }))
else:
    # Allow interruption for non-recoverable errors
    print(json.dumps({"decision": "allow"}))
```

## Logs

Check logs to see what errors are being caught:
```bash
tail -20 /tmp/tool_failure_hook.log
```

## Hook Configuration

The hook is configured in `.claude/settings.json`:
```json
"PostToolUseFailure": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/tool_failure",
        "timeout": 10,
        "statusMessage": "Tool failed - interrupted"
      }
    ]
  }
]
```

## Common Error Types to Handle

Based on your bash error, common patterns you might want to auto-continue:

1. **Bash parsing errors** - Syntax mistakes in heredocs, substitutions
2. **File not found** - Claude tries to read missing files
3. **Permission denied** - Missing execute permissions
4. **Timeout errors** - Commands taking too long

For each type, you can teach the hook to recognize it and send a helpful continue message.
