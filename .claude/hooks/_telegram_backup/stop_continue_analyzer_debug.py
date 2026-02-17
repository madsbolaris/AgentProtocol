#!/usr/bin/env python3
"""
Stop Hook: Continue Analyzer (Debug Version)

Logs execution details to /tmp/stop_hook_debug.log
"""

import json
import os
import subprocess
import sys
import warnings
from pathlib import Path
from datetime import datetime
import urllib.request
import urllib.parse

# Suppress deprecation warnings
warnings.filterwarnings('ignore')

# Add .claude directory to path to import sdk_auth
claude_dir = Path(__file__).parent.parent
sys.path.insert(0, str(claude_dir))

DEBUG_LOG = "/tmp/stop_hook_debug.log"
COUNTER_FILE = "/tmp/stop_hook_counter.json"
MAX_CONSECUTIVE_BLOCKS = 100  # Maximum auto-continues before forcing stop

def log(message):
    """Log to debug file with timestamp."""
    with open(DEBUG_LOG, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")

def load_env_file():
    """Load environment variables from .env file."""
    env_vars = {}
    # Look for .env in project root (parent of .claude directory)
    project_root = Path(__file__).parent.parent.parent
    env_file = project_root / ".env"

    if not env_file.exists():
        log(f".env file not found at {env_file}")
        return env_vars

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        log(f"Loaded {len(env_vars)} variables from .env")
    except Exception as e:
        log(f"Error loading .env: {e}")

    return env_vars

def wait_for_telegram_response(bot_token: str, chat_id: str, message_id: int, timeout_seconds: int = 300):
    """
    Wait for user to reply to a Telegram message.

    Returns:
        tuple: (response_text, success) - User's response text and whether we got a response
    """
    import time
    import ssl

    # Clear any existing webhook to avoid 409 Conflict
    try:
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        req = urllib.request.Request(url, data=b'')
        ssl_context = ssl._create_unverified_context()
        urllib.request.urlopen(req, timeout=5, context=ssl_context)
        log("Cleared Telegram webhook")
    except Exception as e:
        log(f"Warning: Could not clear webhook: {e}")

    log(f"Waiting for Telegram response (timeout: {timeout_seconds}s)...")
    start_time = time.time()
    last_update_file = Path("/tmp/telegram_last_update_id.txt")

    # Get starting update ID
    if last_update_file.exists():
        try:
            with open(last_update_file, 'r') as f:
                last_update_id = int(f.read().strip())
        except:
            last_update_id = None
    else:
        last_update_id = None

    while time.time() - start_time < timeout_seconds:
        try:
            # Poll for updates
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            if last_update_id:
                url += f"?offset={last_update_id + 1}&timeout=10"

            req = urllib.request.Request(url)
            import ssl
            ssl_context = ssl._create_unverified_context()

            with urllib.request.urlopen(req, timeout=15, context=ssl_context) as response:
                data = json.loads(response.read().decode('utf-8'))

                if data.get('ok') and data.get('result'):
                    updates = data.get('result', [])

                    for update in updates:
                        update_id = update.get('update_id')
                        message = update.get('message', {})
                        text = message.get('text', '').strip()
                        reply_to = message.get('reply_to_message', {}).get('message_id')
                        from_chat_id = str(message.get('chat', {}).get('id', ''))

                        # Update last processed ID
                        if update_id:
                            last_update_id = update_id
                            with open(last_update_file, 'w') as f:
                                f.write(str(update_id))

                        # Check if this is a reply to our notification from the correct chat
                        if from_chat_id == chat_id and reply_to == message_id and text:
                            log(f"Received Telegram response: {text}")
                            return (text, True)

            # Brief sleep before next poll
            time.sleep(1)

        except Exception as e:
            log(f"Error polling Telegram: {e}")
            time.sleep(2)

    log(f"Telegram response timeout after {timeout_seconds}s")
    return (None, False)

def send_telegram_notification(message: str, session_id: str = None):
    """Send a notification via Telegram bot and return message_id."""
    try:
        # Load environment variables
        env_vars = load_env_file()
        bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
        chat_id = env_vars.get('TELEGRAM_CHAT_ID')

        if not bot_token or not chat_id:
            log("Telegram credentials not configured, skipping notification")
            return None

        if bot_token == 'your-bot-token-here' or chat_id == 'your-chat-id-here':
            log("Telegram credentials not set (still using example values)")
            return None

        # Send message via Telegram Bot API
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data)

        # Create SSL context that doesn't verify certificates (for corporate/proxy environments)
        import ssl
        ssl_context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, timeout=5, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            if result.get('ok'):
                message_id = result.get('result', {}).get('message_id')
                log(f"Telegram notification sent successfully (message_id: {message_id})")

                # Save message_id -> session_id mapping if provided
                if session_id and message_id:
                    mapping_file = Path("/tmp/telegram_message_to_session.json")
                    mappings = {}
                    if mapping_file.exists():
                        try:
                            with open(mapping_file, 'r') as f:
                                mappings = json.load(f)
                        except:
                            pass

                    mappings[str(message_id)] = session_id

                    with open(mapping_file, 'w') as f:
                        json.dump(mappings, f, indent=2)
                    log(f"Saved message mapping: {message_id} -> {session_id}")

                return message_id
            else:
                log(f"Telegram API error: {result}")
                return None

    except Exception as e:
        log(f"Error sending Telegram notification: {e}")
        return None

def get_session_state(session_id: str) -> dict:
    """Get the session state including counter, recent reasons, confidence history, and original goal."""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                states = json.load(f)
                return states.get(session_id, {
                    "count": 0,
                    "recent_reasons": [],
                    "recent_confidences": [],
                    "original_goal": None
                })
    except Exception as e:
        log(f"Error reading state: {e}")
    return {"count": 0, "recent_reasons": [], "recent_confidences": [], "original_goal": None}

def increment_session_counter(session_id: str, reason: str, confidence: str) -> tuple:
    """Increment counter and track recent reasons/confidences. Returns (count, is_spinning, low_confidence_streak)."""
    try:
        states = {}
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                states = json.load(f)

        state = states.get(session_id, {
            "count": 0,
            "recent_reasons": [],
            "recent_confidences": [],
            "original_goal": None
        })
        state["count"] += 1

        # Keep last 3 reasons
        state["recent_reasons"].append(reason)
        if len(state["recent_reasons"]) > 10:
            state["recent_reasons"] = state["recent_reasons"][-10:]

        # Keep last 10 confidences
        state["recent_confidences"].append(confidence)
        if len(state["recent_confidences"]) > 10:
            state["recent_confidences"] = state["recent_confidences"][-10:]

        # Check if spinning (last 3 reasons are very similar)
        is_spinning = False
        if len(state["recent_reasons"]) >= 3:
            reasons = state["recent_reasons"][-3:]
            # Simple similarity check: if all 3 contain similar key words
            key_words = ["incomplete", "task", "work", "continue", "more", "not done"]
            matches = [sum(1 for word in key_words if word.lower() in r.lower()) for r in reasons]
            # If all 3 have similar keyword density, probably spinning
            if len(set(matches)) == 1 and matches[0] > 0:
                is_spinning = True
                log(f"Detected spinning: {reasons}")

        # Check for low confidence streak (3 low or 10 medium in a row)
        low_confidence_streak = False
        confidences = state["recent_confidences"]

        if len(confidences) >= 3 and confidences[-3:] == ["low", "low", "low"]:
            low_confidence_streak = True
            log(f"Detected 3 consecutive low confidence blocks")

        if len(confidences) >= 10 and confidences[-10:] == ["medium"] * 10:
            low_confidence_streak = True
            log(f"Detected 10 consecutive medium confidence blocks")

        states[session_id] = state

        with open(COUNTER_FILE, 'w') as f:
            json.dump(states, f)

        return state["count"], is_spinning, low_confidence_streak
    except Exception as e:
        log(f"Error incrementing counter: {e}")
        return 0, False, False

def reset_session_counter(session_id: str):
    """Reset the counter for this session (called when allowing stop)."""
    try:
        if os.path.exists(COUNTER_FILE):
            with open(COUNTER_FILE, 'r') as f:
                states = json.load(f)

            if session_id in states:
                del states[session_id]

            with open(COUNTER_FILE, 'w') as f:
                json.dump(states, f)
    except Exception as e:
        log(f"Error resetting counter: {e}")

def analyze_conversation(transcript_path: str, api_key: str, original_goal: str = None) -> dict:
    """Use Anthropic SDK to analyze if Claude stopped prematurely."""
    try:
        log("Starting conversation analysis")

        # Import anthropic here after we have the API key
        import anthropic

        # Read the transcript (JSONL format - one JSON object per line)
        log(f"Reading transcript from {transcript_path}")
        messages = []
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        # Each line is a message event, extract the message
                        if 'message' in obj:
                            messages.append(obj['message'])
                    except json.JSONDecodeError:
                        log(f"Skipping invalid JSON line: {line[:100]}")
                        continue

        # Extract recent conversation - more context for better analysis
        log(f"Found {len(messages)} messages in transcript")
        recent_messages = messages[-15:] if len(messages) > 15 else messages

        # Build a summary of the conversation for analysis
        conversation_summary = []
        for msg in recent_messages:
            role = msg.get('role', 'unknown')

            if role == 'user':
                content = msg.get('content', '')
                if isinstance(content, list):
                    text_parts = [part.get('text', '') for part in content if part.get('type') == 'text']
                    content = '\n'.join(text_parts)
                conversation_summary.append(f"User: {content[:800]}")

            elif role == 'assistant':
                content = msg.get('content', '')
                if isinstance(content, list):
                    text_parts = [part.get('text', '') for part in content if part.get('type') == 'text']
                    content = '\n'.join(text_parts)
                conversation_summary.append(f"Assistant: {content[:800]}")

        # Include more exchanges for pattern detection
        conversation_text = '\n\n'.join(conversation_summary[-10:])
        log(f"Conversation summary: {len(conversation_text)} chars")

        # Use Anthropic SDK to analyze
        log("Calling Anthropic API")
        client = anthropic.Anthropic(api_key=api_key)

        # Load prompt template from external file
        prompt_file = Path(__file__).parent / "stop_continue_analyzer_prompt.txt"
        try:
            with open(prompt_file, 'r') as f:
                prompt_template = f.read()
            log(f"Loaded prompt template from {prompt_file}")
        except Exception as e:
            log(f"Error loading prompt template: {e}, using fallback")
            prompt_template = "ERROR: Could not load prompt template"
            return {
                "should_continue": False,
                "reason": "Prompt template load failed",
                "conversation_context": "System error",
                "user_message": "Configuration error occurred",
                "confidence": "low"
            }

        # Build original goal context
        goal_context = ""
        if original_goal:
            goal_context = f"""
ORIGINAL USER REQUEST (the initial goal for this session):
"{original_goal}"
"""

        # Fill in the template
        analysis_prompt = prompt_template.format(
            goal_context=goal_context,
            conversation_summary_count=len(conversation_summary),
            conversation_summary_exchanges=len(conversation_summary[-10:]),
            conversation_text=conversation_text
        )

        # Define JSON schema for structured output
        output_schema = {
            "type": "object",
            "properties": {
                "should_continue": {"type": "boolean"},
                "reason": {"type": "string"},
                "conversation_context": {"type": "string"},
                "user_message": {"type": "string"},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
                "has_question": {"type": "boolean"}
            },
            "required": ["should_continue", "reason", "conversation_context", "user_message", "confidence", "has_question"],
            "additionalProperties": False
        }

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Sonnet 4.5 for smarter analysis
            max_tokens=300,
            messages=[{"role": "user", "content": analysis_prompt}],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": output_schema
                }
            }
        )

        log("API call completed")

        # Parse the guaranteed-valid JSON response
        response_text = response.content[0].text
        log(f"LLM response: {response_text[:200]}")

        try:
            result = json.loads(response_text)
            log(f"Parsed result: {result}")
            return result
        except json.JSONDecodeError as e:
            log(f"Unexpected JSON decode error (should not happen with structured outputs): {e}")
            return {
                "should_continue": False,
                "reason": "Invalid JSON in LLM response",
                "conversation_context": "System error",
                "user_message": "Analysis error occurred",
                "confidence": "low"
            }

    except Exception as e:
        log(f"Error in analyze_conversation: {type(e).__name__}: {e}")
        return {
            "should_continue": False,
            "reason": f"Analysis error: {str(e)}",
            "conversation_context": "System error",
            "user_message": "Analysis error occurred",
            "confidence": "low"
        }


def ensure_handler_running():
    """Check if Telegram handler is running, start it if not."""
    try:
        pid_file = Path("/tmp/telegram_handler.pid")

        # Check if PID file exists and process is alive
        if pid_file.exists():
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())

                # Check if process is still running
                result = subprocess.run(['ps', '-p', str(pid)], capture_output=True, timeout=2)
                if result.returncode == 0:
                    log(f"Handler already running (PID: {pid})")
                    return True
                else:
                    log(f"Handler PID file exists but process {pid} not running")
            except Exception as e:
                log(f"Error checking handler PID: {e}")

        # Handler not running, start it
        log("Starting Telegram handler...")
        script_dir = Path(__file__).parent
        start_script = script_dir / "start_telegram_handler.sh"

        if not start_script.exists():
            log(f"ERROR: Start script not found at {start_script}")
            return False

        # Run start script
        result = subprocess.run([str(start_script)], capture_output=True, timeout=5)
        if result.returncode == 0:
            log("Handler started successfully")
            return True
        else:
            log(f"ERROR starting handler: {result.stderr.decode()}")
            return False

    except Exception as e:
        log(f"Error ensuring handler is running: {e}")
        return False

def main():
    """Main hook entry point."""
    try:
        log("=== Hook execution started ===")

        # Read hook input from stdin
        hook_input_str = sys.stdin.read()
        log(f"Received input: {hook_input_str[:200]}")
        hook_input = json.loads(hook_input_str)

        session_id = hook_input.get('session_id', 'unknown')

        # Check our own counter to prevent truly infinite loops
        state = get_session_state(session_id)
        current_count = state["count"]
        recent_reasons = state.get("recent_reasons", [])
        log(f"Current consecutive blocks for session: {current_count}/{MAX_CONSECUTIVE_BLOCKS}")
        log(f"Recent reasons: {recent_reasons}")

        # If we've hit our limit, respect stop_hook_active
        if current_count >= MAX_CONSECUTIVE_BLOCKS:
            log(f"Hit max consecutive blocks limit ({MAX_CONSECUTIVE_BLOCKS}), allowing stop")
            reset_session_counter(session_id)
            print(json.dumps({"decision": "allow"}))
            return 0

        # Claude Code's safety flag - we'll ignore it unless we hit our own limit
        if hook_input.get('stop_hook_active', False):
            log(f"stop_hook_active=True, but overriding (count={current_count}/{MAX_CONSECUTIVE_BLOCKS})")

        # Get API key
        log("Getting API key from keychain")
        from sdk_auth import get_api_key_from_keychain
        api_key = get_api_key_from_keychain()

        if not api_key:
            log("ERROR: Could not get API key")
            print(json.dumps({"decision": "allow"}))
            return 0

        log("API key retrieved successfully")

        # Get transcript path
        transcript_path = hook_input.get('transcript_path')
        log(f"Transcript path: {transcript_path}")

        if not transcript_path or not os.path.exists(transcript_path):
            log(f"ERROR: Transcript not found at {transcript_path}")
            print(json.dumps({"decision": "allow"}))
            return 0

        # Get or update original goal (most recent user message)
        # This ensures we track the latest user request, not just the first one
        try:
            with open(transcript_path, 'r') as f:
                latest_user_msg = None
                for line in f:
                    line = line.strip()
                    if line:
                        obj = json.loads(line)
                        if 'message' in obj and obj['message'].get('role') == 'user':
                            content = obj['message'].get('content', '')
                            if isinstance(content, list):
                                text_parts = [part.get('text', '') for part in content if part.get('type') == 'text']
                                content = '\n'.join(text_parts)
                            if content:
                                latest_user_msg = content[:500]

                # Update goal if we found a user message and it's different
                if latest_user_msg and latest_user_msg != state.get("original_goal"):
                    state["original_goal"] = latest_user_msg
                    log(f"Updated original goal: {state['original_goal'][:100]}...")
                    # Save state with updated goal
                    states = {}
                    if os.path.exists(COUNTER_FILE):
                        with open(COUNTER_FILE, 'r') as cf:
                            states = json.load(cf)
                    states[session_id] = state
                    with open(COUNTER_FILE, 'w') as cf:
                        json.dump(states, cf)
        except Exception as e:
            log(f"Failed to extract/update original goal: {e}")

        # Analyze the conversation
        log("Starting analysis")
        analysis = analyze_conversation(transcript_path, api_key, state.get("original_goal"))
        log(f"Analysis result: {analysis}")

        # Make decision based on analysis
        has_question = analysis.get('has_question', False)
        should_continue = analysis.get('should_continue', False)
        confidence = analysis.get('confidence', 'low')

        log(f"Analysis: should_continue={should_continue}, has_question={has_question}, confidence={confidence}")

        # Never continue if Claude has a REAL question for the user
        if has_question:
            log("Claude has a REAL question for user, allowing stop")
            decision = {"decision": "allow"}
            reset_session_counter(session_id)
        elif should_continue and confidence in ['high', 'medium']:
            reason = analysis.get('reason', 'Continue working on the task')
            log(f"Planning to BLOCK with reason: {reason}")

            # Increment our counter and check if spinning or low confidence streak
            new_count, is_spinning, low_conf_streak = increment_session_counter(session_id, reason, confidence)
            log(f"Incremented counter to {new_count}, spinning={is_spinning}, low_conf_streak={low_conf_streak}")

            # If spinning on same problem or low confidence streak, stop and let user intervene
            if is_spinning:
                log("Detected spinning on same problem for 3 rounds, allowing stop")
                decision = {"decision": "allow"}
                reset_session_counter(session_id)
            elif low_conf_streak:
                log("Detected low confidence streak (3x low or 10x medium), allowing stop")
                decision = {"decision": "allow"}
                reset_session_counter(session_id)
            else:
                decision = {
                    "decision": "block",
                    "reason": f"Continue: {reason}"
                }
                log(f"BLOCKING with reason: {reason}")
        else:
            decision = {"decision": "allow"}
            log(f"ALLOWING (should_continue={should_continue}, confidence={confidence})")
            reset_session_counter(session_id)

        # Play beep and send Telegram notification ONLY if allowing stop (human intervention needed)
        if decision.get("decision") == "allow":
            try:
                log("Playing notification beep (human intervention needed)")
                subprocess.run(
                    ["afplay", "/System/Library/Sounds/Ping.aiff"],
                    timeout=1,
                    capture_output=True
                )
            except Exception as e:
                log(f"Failed to play beep: {e}")

            # Save stop event context for the response handler agent
            # Extract conversation snippet from transcript for context
            conversation_snippet = "Unable to load conversation snippet"
            try:
                with open(transcript_path, 'r') as f:
                    lines = f.readlines()
                    # Get last 20 lines and truncate to 500 chars
                    recent_lines = lines[-20:] if len(lines) > 20 else lines
                    snippet_text = ''.join(recent_lines)
                    conversation_snippet = snippet_text[-500:] if len(snippet_text) > 500 else snippet_text
            except Exception as e:
                log(f"Failed to extract conversation snippet: {e}")

            stop_context = {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "reason": analysis.get('reason', 'Unknown reason'),
                "conversation_context": analysis.get('conversation_context', 'Unknown task'),
                "user_message": analysis.get('user_message', analysis.get('reason', 'Unknown')),
                "confidence": confidence,
                "has_question": has_question,
                "original_goal": state.get("original_goal"),
                "transcript_path": transcript_path,
                "conversation_snippet": conversation_snippet,
                "cwd": hook_input.get('cwd', 'unknown')
            }

            # Save to session-specific file (supports multiple concurrent sessions)
            stop_contexts_dir = Path("/tmp/claude_stop_contexts")
            stop_contexts_dir.mkdir(exist_ok=True)

            session_context_file = stop_contexts_dir / f"{session_id}.json"
            try:
                with open(session_context_file, 'w') as f:
                    json.dump(stop_context, f, indent=2)
                log(f"Saved stop context to {session_context_file}")
            except Exception as e:
                log(f"Failed to save stop context: {e}")

            # Send verbose Telegram notification with options
            import html as html_escape

            reason = analysis.get('reason', 'Unknown reason')  # For logging
            conversation_context = analysis.get('conversation_context', 'Unknown task')  # What this conversation is about
            user_message = analysis.get('user_message', reason)  # User-friendly message, fallback to reason

            # Create clean, informative notification (escape dynamic content for HTML)
            # Add emoji indicator for question vs completion
            status_emoji = "❓" if has_question else "✅"

            notification_text = (
                f"{status_emoji} <b>{html_escape.escape(conversation_context)}</b>\n"
                f"{html_escape.escape(user_message)}\n\n"
                f"1️⃣ Continue\n"
                f"2️⃣ More info\n"
                f"3️⃣ Send reply\n"
                f"4️⃣ End conversation\n\n"
                f"💬 <i>Waiting for your response...</i>"
            )
            msg_id = send_telegram_notification(notification_text, session_id)

            if msg_id:
                # Wait for Telegram response
                env_vars = load_env_file()
                bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
                chat_id = env_vars.get('TELEGRAM_CHAT_ID')

                response_text, got_response = wait_for_telegram_response(bot_token, chat_id, msg_id, timeout_seconds=300)

                if got_response:
                    user_input = response_text.strip().lower()
                    log(f"User chose: {user_input}")

                    if user_input in ['1', 'continue']:
                        # Option 1: Continue
                        log("User chose to continue")
                        # Update decision to block (allow continuation)
                        decision = {"decision": "block"}

                        # Send confirmation
                        confirm_msg = "✅ <b>Continuing execution</b>"
                        send_telegram_notification(confirm_msg, session_id)

                    elif user_input in ['2', 'more info', 'info']:
                        # Option 2: More info
                        log("User requested more info")
                        info_msg = (
                            f"📊 <b>Detailed Analysis</b>\n\n"
                            f"<b>Reason:</b> {reason[:200]}\n"
                            f"<b>Confidence:</b> {confidence}\n"
                            f"<b>Has Question:</b> {has_question}\n"
                            f"<b>Working Directory:</b> {hook_input.get('cwd', 'unknown')}\n\n"
                            f"<b>Recent Context:</b>\n<pre>{html_escape.escape(conversation_snippet[:300])}...</pre>\n\n"
                            f"💡 <b>Next:</b>\n"
                            f"<b>1</b> - Continue | <b>3</b> - Reply | <b>4</b> - End"
                        )
                        send_telegram_notification(info_msg, session_id)

                        # Wait for another response
                        response_text, got_response = wait_for_telegram_response(bot_token, chat_id, msg_id, timeout_seconds=300)
                        if got_response:
                            user_input = response_text.strip().lower()
                            if user_input in ['1', 'continue']:
                                decision = {"decision": "block"}
                                send_telegram_notification("✅ <b>Continuing execution</b>", session_id)
                            elif user_input in ['4', 'end', 'stop']:
                                log("User chose to end conversation")
                                send_telegram_notification("🛑 <b>Conversation ended</b>", session_id)
                                # Keep decision as allow (stop)
                            else:
                                # Custom message - pass it to Claude as input
                                log(f"User sent custom message after more info: {response_text}")

                                # Output the user's message to stdout
                                print(response_text, flush=True)
                                log(f"Sent user input to Claude: {response_text}")

                                # Change decision to block so Claude continues
                                decision = {"decision": "block"}

                                send_telegram_notification(
                                    f"✅ <b>Response sent:</b> <i>{html_escape.escape(response_text)}</i>",
                                    session_id
                                )
                        else:
                            log("Timeout waiting for second response after more info")

                    elif user_input in ['4', 'end', 'stop']:
                        # Option 4: End conversation
                        log("User chose to end conversation")
                        send_telegram_notification("🛑 <b>Conversation ended</b>", session_id)
                        # Keep decision as allow (stop)

                    else:
                        # Option 3 or custom message - pass it to Claude as input
                        log(f"User sent custom message: {response_text}")

                        # Output the user's message to stdout so Claude Code reads it as input
                        print(response_text, flush=True)
                        log(f"Sent user input to Claude: {response_text}")

                        # Change decision to block so Claude continues with this input
                        decision = {"decision": "block"}

                        send_telegram_notification(
                            f"✅ <b>Response sent:</b> <i>{html_escape.escape(response_text)}</i>",
                            session_id
                        )
                else:
                    log("Timeout waiting for Telegram response, proceeding with original decision")
            else:
                log("No message ID returned from notification")
        else:
            log("Skipping beep and notification (auto-continuing)")

        # Output decision
        print(json.dumps(decision))
        log(f"Output: {json.dumps(decision)}")
        log("=== Hook execution completed successfully ===")
        return 0

    except Exception as e:
        log(f"FATAL ERROR: {type(e).__name__}: {e}")
        import traceback
        log(f"Traceback: {traceback.format_exc()}")
        print(json.dumps({"decision": "allow"}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
