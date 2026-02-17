# Multi-Session Architecture

The Telegram stop hook system now supports **multiple concurrent Claude Code sessions**. You can have several Claude Code windows open, and the system intelligently routes your responses to the correct session.

## How It Works

### 1. Session Tracking

Each Claude Code session has a unique `session_id`. When Claude stops:

1. **Stop context saved** to `/tmp/claude_stop_contexts/{session_id}.json`
2. **Telegram notification sent** with session info (ID + working directory)
3. **Message mapping saved** (`message_id` → `session_id`)

### 2. Responding to Notifications

#### Option A: Reply to Specific Message (Recommended)
Use Telegram's **Reply** feature to respond to a specific stop notification:

```
Bot: 🤖 Claude Code Stopped
     Session: a1b2c3d4 (expert-feedback)
     Why it stopped: Phase 2 complete...

     1️⃣ Continue 2️⃣ More Info 3️⃣ Respond
     💡 Tip: Reply to this message for multi-session support

You: [Reply to that message] → 1
```

The agent automatically works on the session you replied to!

#### Option B: Respond Without Reply (Falls Back to Most Recent)
If you just send a message without replying, the agent uses the **most recent stop event**:

```
You: 1
Bot: 🔄 Processing request for session a1b2c3d4...
```

### 3. Session Context Storage

```
/tmp/claude_stop_contexts/
├── a1b2c3d4-5678-90ab-cdef-1234567890ab.json  # Session 1
├── e5f6g7h8-9012-34ij-klmn-5678901234op.json  # Session 2
└── q9r0s1t2-3456-78uv-wxyz-9012345678qr.json  # Session 3

/tmp/telegram_message_to_session.json
{
  "12345": "a1b2c3d4-5678-90ab-cdef-1234567890ab",  # Message 12345 → Session 1
  "12346": "e5f6g7h8-9012-34ij-klmn-5678901234op",  # Message 12346 → Session 2
  "12347": "q9r0s1t2-3456-78uv-wxyz-9012345678qr"   # Message 12347 → Session 3
}
```

## Notification Format

Each notification now includes session context:

```
🤖 Claude Code Stopped

Session: a1b2c3d4 (expert-feedback)
Why it stopped: Phase 2 complete, awaiting next phase decision

Type: Task appears complete or blocked
What this means: Claude believes the current task is done...

Original goal: Create integration tests for expert feedback...

Confidence: high

What would you like to do?

1️⃣ Continue - Auto-continue and teach prompt
2️⃣ More Info - Get detailed analysis
3️⃣ Respond - Send custom message

💡 Tip: Reply to this message for multi-session support
```

**Key info:**
- `Session: a1b2c3d4` - Short session ID (first 8 chars)
- `(expert-feedback)` - Current working directory name

## Examples

### Scenario 1: Two Sessions, Targeted Response

```
# Terminal 1: /Users/me/project-a
You: Claude, implement feature X
Claude: [stops after Phase 2]

# Terminal 2: /Users/me/project-b
You: Claude, fix bug Y
Claude: [stops asking a question]

# Telegram
Bot: 🤖 Claude Code Stopped
     Session: abc12345 (project-a)
     Phase 2 complete, awaiting next phase decision
     [options]

Bot: 🤖 Claude Code Stopped
     Session: def67890 (project-b)
     Real question: Which validation library?
     [options]

# You reply to the FIRST message
You: [Reply to abc12345 message] → 1

# Agent processes it correctly
Bot: 🔄 Processing request for session abc12345...
Bot: ✅ Updated prompt to auto-continue for phase transitions
     You can now type 'continue' in your project-a terminal.

# The other session (def67890) is unaffected!
```

### Scenario 2: No Reply, Uses Most Recent

```
# Two sessions stopped, but you just type "2" without replying

You: 2

# Agent uses the most recent stop (whichever happened last)
Bot: 🔄 Processing request for session def67890...
Bot: 📊 Analysis of Stop Event
     [detailed analysis of def67890 session]
```

### Scenario 3: Listing Active Sessions

```
# You send a message when no recent stops

You: status

# Agent lists all active stop contexts
Bot: ⚠️ No stop context found.

     Active sessions:
     • abc12345 (project-a) - Phase 2 complete, awaiting...
     • def67890 (project-b) - Real question: Which validation...
     • ghi34567 (project-c) - Tests not run yet...

     💡 Reply to a stop notification to target a specific session.
```

## Technical Details

### Stop Hook Changes

[stop_continue_analyzer_debug.py](.claude/hooks/stop_continue_analyzer_debug.py):
- Saves contexts to individual files per session
- Includes `cwd` (working directory) in context
- `send_telegram_notification()` now returns `message_id`
- Stores `message_id → session_id` mapping
- Notification includes session ID and directory name

### Response Handler Changes

[telegram_response_handler.py](.claude/hooks/telegram_response_handler.py):
- `get_session_from_reply()` - Looks up session from reply
- `load_stop_context(session_id)` - Loads specific session context
- `list_active_sessions()` - Lists all pending stop events
- Checks `reply_to_message_id` to determine target session
- Falls back to most recent if no reply

## Benefits

✅ **Multiple Projects** - Work on several projects simultaneously
✅ **Precise Targeting** - Reply feature ensures you act on the right session
✅ **Automatic Fallback** - Works without reply if you have one active session
✅ **Session Awareness** - See which project each notification is from
✅ **No Confusion** - Agent always knows which session you're addressing

## File Locations

- **Stop contexts**: `/tmp/claude_stop_contexts/{session_id}.json`
- **Message mappings**: `/tmp/telegram_message_to_session.json`
- **Handler logs**: `/tmp/telegram_handler.log`
- **Stop hook logs**: `/tmp/stop_hook_debug.log`

## Cleanup

Sessions persist until you clean them up manually:

```bash
# Remove all stop contexts
rm -rf /tmp/claude_stop_contexts

# Remove message mappings
rm /tmp/telegram_message_to_session.json

# They'll be recreated on next stop event
```

## Troubleshooting

### "No session found for reply_to X"
- The message mapping might have been cleared
- The notification was from before the system restart
- Just send your response without replying (falls back to most recent)

### "No stop context found"
- All stop contexts were cleared
- No recent stop events
- Check if handler is running: `tail -f /tmp/telegram_handler.log`

### Agent acts on wrong session
- Make sure you used **Reply** in Telegram (not just a new message)
- Check logs to see which session was targeted: `grep "Targeting session" /tmp/telegram_handler.log`

## Best Practices

1. **Use Reply** - Always reply to notifications when multiple sessions are active
2. **Check Session ID** - Verify the session ID in the notification matches your intent
3. **One Handler** - Run only one response handler instance
4. **Clean Up** - Periodically remove old stop contexts

Enjoy seamless multi-session support! 🚀
