# Interactive Telegram Stop Hook System

This system provides intelligent, interactive notifications when Claude Code stops, with an AI agent that can automatically handle your responses.

**✨ NEW: Multi-Session Support** - Works with multiple concurrent Claude Code sessions! See [MULTI_SESSION_ARCHITECTURE.md](./MULTI_SESSION_ARCHITECTURE.md) for details.

## Architecture

### 1. Stop Hook (`stop_continue_analyzer_debug.py`)
- Analyzes conversation when Claude stops
- Sends verbose Telegram notification with 3 options
- Saves stop context to `/tmp/claude_stop_contexts/{session_id}.json`
- Tracks message_id → session_id mappings for multi-session support

### 2. Response Handler Agent (`telegram_response_handler.py`)
- Runs in the background, polling for Telegram messages
- Uses Claude Code SDK to take actions
- Can update prompts, analyze context, and more
- Reads its instructions from external prompt file

### 3. External Prompts
- **Stop Analyzer**: `stop_continue_analyzer_prompt.txt`
- **Response Handler**: `telegram_response_handler_prompt.txt`
- Both can be edited live without restarting!

## Setup

### 1. Telegram Credentials
Already configured in your `.env` file:
```bash
TELEGRAM_BOT_TOKEN=your-token-here
TELEGRAM_CHAT_ID=your-chat-id-here
```

### 2. Start the Response Handler
```bash
cd /Users/mabolan/AgentProtocol
./.claude/hooks/start_telegram_handler.sh
```

The handler will:
- Run in the background
- Log to `/tmp/telegram_handler.log`
- Send a startup message to Telegram

### 3. Stop the Response Handler
```bash
./.claude/hooks/stop_telegram_handler.sh
```

## Usage

### When Claude Stops

You'll receive a Telegram message like:

```
🤖 Claude Code Stopped

Why it stopped: Phase 2 complete, awaiting next phase decision

Type: Task appears complete or blocked
What this means: Claude believes the current task is done, or is uncertain how to proceed.

Original goal: Create integration tests for expert feedback workflow...

Analysis confidence: high

What would you like to do?

1️⃣ Continue - Auto-continue and teach prompt to not stop for this
2️⃣ More Info - Get detailed analysis of the situation
3️⃣ Respond - Send a custom message

Reply with: 1, 2, 3, or any text
```

### Option 1: Continue + Update Prompt

**What you do:**
- Reply with `1` or `continue`

**What the agent does:**
1. Analyzes why the stop happened
2. Updates `stop_continue_analyzer_prompt.txt` to be more lenient
3. Adds rules/examples to prevent similar stops
4. Reports what it changed
5. Reminds you to type "continue" in your terminal

**Example:**
```
You: 1

Bot: ✅ Updated prompt to auto-continue for phase transitions

Added rule: "When Claude asks 'Continue Phase X or review?',
always auto-continue with Phase X"

You can now type 'continue' in your Claude Code terminal.
```

### Option 2: More Info

**What you do:**
- Reply with `2` or `more info`

**What the agent does:**
1. Reads the full conversation transcript
2. Analyzes what Claude was doing
3. Determines if this was a valid stop
4. Provides suggestions
5. Sends detailed analysis via Telegram

**Example:**
```
You: 2

Bot: 📊 Analysis of Stop Event

What Claude was working on:
- Creating integration test files for expert feedback workflow
- Just completed Phase 2 (directory structure)
- Listed remaining Phases 3-9 with 13+ tests to create

Why it stopped:
- Asked "Continue with Phase 3 or review?"
- Analyzer incorrectly treated this as requiring user input

Assessment:
❌ FALSE POSITIVE - This should have auto-continued

Recommendation:
Choose option 1 to teach the prompt, then continue working.
```

### Option 3: Custom Message

**What you do:**
- Reply with `3` followed by your message
- Or just send any text that isn't `1` or `2`

**What the agent does:**
1. Saves your message
2. Provides guidance on next steps
3. May suggest if you meant option 1 or 2

**Example:**
```
You: Actually, I want to review the code first

Bot: 📝 Message received: "Actually, I want to review the code first"

This will require manual input in Claude Code terminal.
The agent cannot automatically send this message for you.

Please open your terminal and respond directly to Claude.
```

## Editing Prompts

### Stop Analyzer Prompt
```bash
vim .claude/hooks/stop_continue_analyzer_prompt.txt
```
Changes take effect on next stop event (no restart needed!)

### Response Handler Prompt
```bash
vim .claude/hooks/telegram_response_handler_prompt.txt
```
Changes take effect on next message (no restart needed!)

## Monitoring

### Check if handler is running:
```bash
ps aux | grep telegram_response_handler
```

### View logs in real-time:
```bash
tail -f /tmp/telegram_handler.log
```

### View stop hook logs:
```bash
tail -f /tmp/stop_hook_debug.log
```

### View stop context:
```bash
cat /tmp/claude_stop_context.json | jq
```

## Troubleshooting

### Handler not responding?

1. **Check if running:**
   ```bash
   cat /tmp/telegram_handler.pid
   ps -p $(cat /tmp/telegram_handler.pid)
   ```

2. **Check logs for errors:**
   ```bash
   tail -50 /tmp/telegram_handler.log
   ```

3. **Restart the handler:**
   ```bash
   ./.claude/hooks/stop_telegram_handler.sh
   ./.claude/hooks/start_telegram_handler.sh
   ```

### Agent not updating prompts?

- Check the agent has write access to `.claude/hooks/` directory
- Verify Claude Code SDK is installed: `pip list | grep anthropic-sdk-claude-code`
- Check logs for permission errors

### Not receiving notifications?

- Verify handler is running (see above)
- Check Telegram credentials in `.env`
- Test with: `python3 .claude/hooks/telegram_response_handler.py` (run in foreground)

## Advanced Usage

### Run handler in foreground (for debugging):
```bash
python3 .claude/hooks/telegram_response_handler.py
```
Press Ctrl+C to stop.

### Manual stop context inspection:
```bash
jq '.' /tmp/claude_stop_context.json
```

### Clear handler state:
```bash
rm /tmp/telegram_last_update_id.txt
rm /tmp/claude_stop_context.json
```

## Files Created

- `.claude/hooks/stop_continue_analyzer_debug.py` - Stop hook (updated)
- `.claude/hooks/telegram_response_handler.py` - Response handler agent
- `.claude/hooks/telegram_response_handler_prompt.txt` - Agent prompt
- `.claude/hooks/start_telegram_handler.sh` - Start script
- `.claude/hooks/stop_telegram_handler.sh` - Stop script
- `/tmp/claude_stop_context.json` - Current stop context
- `/tmp/telegram_handler.pid` - Handler process ID
- `/tmp/telegram_handler.log` - Handler logs
- `/tmp/telegram_last_update_id.txt` - Last processed Telegram update

## How It Works

```
┌─────────────────┐
│  Claude Stops   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│ Stop Hook Analyzes Conversation │
└────────┬───────────┬────────────┘
         │           │
         │           ├──► Saves context to /tmp/claude_stop_context.json
         │           │
         │           └──► Sends Telegram notification with options
         │
         ▼
┌──────────────────────┐
│ You reply via Telegram│
└────────┬─────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│ Response Handler (polling Telegram) │
└────────┬────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│ Claude Code SDK Agent                │
│ - Reads stop context                 │
│ - Interprets your response           │
│ - Takes action:                      │
│   * Updates prompt (option 1)        │
│   * Analyzes transcript (option 2)   │
│   * Saves message (option 3)         │
│ - Sends result via Telegram          │
└──────────────────────────────────────┘
```

## Benefits

- **Faster iteration**: Agent automatically updates prompts based on false positives
- **Better understanding**: Get detailed analysis when confused
- **Flexibility**: Custom responses for edge cases
- **No restart needed**: Edit prompts on the fly
- **Autonomous**: Agent can read files, update code, and more

## Next Steps

1. Start the handler: `./.claude/hooks/start_telegram_handler.sh`
2. Let Claude work on something
3. When it stops, try the different options
4. Watch the agent handle your responses!

Enjoy your interactive AI assistant! 🤖
