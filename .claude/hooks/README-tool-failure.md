# Tool Failure Hook - Auto-Continue on Interruptions

## What This Does

When Claude encounters a tool error (bash parsing error, file not found, permission denied, etc.), it gets "Interrupted". This hook **automatically tells Claude to continue** so it can handle the error itself.

**No LLM needed** - Claude already knows what went wrong from the error message, so we just tell it to keep going.

## How It Works

1. Tool fails (e.g., bash syntax error)
2. Claude would normally show "Interrupted" and wait
3. Hook intercepts and sends "continue" automatically
4. Claude sees the error and can fix it or try another approach

## Example

**Before (without hook):**
```
OUT: Failed to parse command: Bad substitution: i

Interrupted  ← You have to manually type "continue"
```

**After (with hook):**
```
OUT: Failed to parse command: Bad substitution: i

← Hook auto-continues, Claude keeps working
I see the bash syntax error. Let me fix that heredoc...
```

## Logs

Check what errors are being auto-continued:
```bash
tail -20 /tmp/tool_failure_hook.log
```

## When This Helps

- **Bash syntax errors** - Claude can fix and retry
- **File not found** - Claude can create the file or try another path
- **Permission denied** - Claude can try with sudo or different approach
- **Timeouts** - Claude can adjust timeout or simplify command

## When to Disable

If you want to manually review every tool failure before continuing, remove this hook from `.claude/settings.json`:

```json
"PostToolUseFailure": [...]  ← Delete this section
```

## Hook Configuration

Location: `.claude/settings.json`
```json
"PostToolUseFailure": [
  {
    "hooks": [
      {
        "type": "command",
        "command": "\"$CLAUDE_PROJECT_DIR\"/.claude/hooks/tool_failure",
        "timeout": 10,
        "statusMessage": "Tool failed - auto-continuing"
      }
    ]
  }
]
```
