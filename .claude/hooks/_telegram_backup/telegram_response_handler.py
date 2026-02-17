#!/usr/bin/env python3
"""
Telegram Response Handler for Claude Code Stop Hook

This agent polls for Telegram messages and handles user responses to stop notifications.
It uses the Claude Code SDK to take actions like updating prompts, analyzing context, etc.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse
import ssl
from pathlib import Path
from datetime import datetime

# Setup paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
STOP_CONTEXT_FILE = Path("/tmp/claude_stop_context.json")
LAST_UPDATE_FILE = Path("/tmp/telegram_last_update_id.txt")
HANDLER_LOG = Path("/tmp/telegram_handler.log")

def log(message):
    """Log to file with timestamp."""
    with open(HANDLER_LOG, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{timestamp}] {message}\n")
    print(message)  # Also print to console

def load_env():
    """Load environment variables from .env file."""
    env_vars = {}
    env_file = PROJECT_ROOT / ".env"

    if not env_file.exists():
        log(f"ERROR: .env file not found at {env_file}")
        return env_vars

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
        log(f"Loaded {len(env_vars)} environment variables")
    except Exception as e:
        log(f"ERROR loading .env: {e}")

    return env_vars

def get_telegram_updates(bot_token, offset=None):
    """Get new messages from Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
        if offset:
            url += f"?offset={offset}&timeout=30"

        req = urllib.request.Request(url)
        ssl_context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, timeout=35, context=ssl_context) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data.get('ok'):
                return data.get('result', [])
            else:
                log(f"Telegram API error: {data}")
                return []
    except Exception as e:
        log(f"Error getting updates: {e}")
        return []

def send_telegram_message(bot_token, chat_id, text):
    """Send a message via Telegram."""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        data = urllib.parse.urlencode({
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'HTML'
        }).encode('utf-8')

        req = urllib.request.Request(url, data=data)
        ssl_context = ssl._create_unverified_context()

        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get('ok', False)
    except Exception as e:
        log(f"Error sending message: {e}")
        return False

def get_session_from_reply(reply_to_message_id):
    """Get session_id from a reply to a previous notification."""
    mapping_file = Path("/tmp/telegram_message_to_session.json")
    if not mapping_file.exists():
        return None

    try:
        with open(mapping_file, 'r') as f:
            mappings = json.load(f)
            return mappings.get(str(reply_to_message_id))
    except Exception as e:
        log(f"Error loading message mappings: {e}")
        return None

def load_stop_context(session_id=None):
    """Load stop context for a specific session, or the most recent one."""
    stop_contexts_dir = Path("/tmp/claude_stop_contexts")

    if not stop_contexts_dir.exists():
        return None

    try:
        # If session_id provided, load that specific context
        if session_id:
            context_file = stop_contexts_dir / f"{session_id}.json"
            if context_file.exists():
                with open(context_file, 'r') as f:
                    return json.load(f)
                log(f"No context found for session {session_id}")
            return None

        # Otherwise, find the most recent context
        context_files = list(stop_contexts_dir.glob("*.json"))
        if not context_files:
            return None

        # Get the most recently modified file
        latest_file = max(context_files, key=lambda p: p.stat().st_mtime)
        with open(latest_file, 'r') as f:
            context = json.load(f)
            log(f"Using most recent context from {latest_file.name}")
            return context

    except Exception as e:
        log(f"Error loading stop context: {e}")
        return None

def list_active_sessions():
    """List all active stop contexts."""
    stop_contexts_dir = Path("/tmp/claude_stop_contexts")
    if not stop_contexts_dir.exists():
        return []

    contexts = []
    for context_file in stop_contexts_dir.glob("*.json"):
        try:
            with open(context_file, 'r') as f:
                context = json.load(f)
                contexts.append({
                    "session_id": context.get("session_id"),
                    "timestamp": context.get("timestamp"),
                    "reason": context.get("reason", "Unknown"),
                    "cwd": context.get("cwd", "unknown")
                })
        except Exception as e:
            log(f"Error reading {context_file}: {e}")

    return sorted(contexts, key=lambda x: x["timestamp"], reverse=True)

def get_last_update_id():
    """Get the last processed update ID."""
    if not LAST_UPDATE_FILE.exists():
        return None

    try:
        with open(LAST_UPDATE_FILE, 'r') as f:
            return int(f.read().strip())
    except Exception as e:
        log(f"Error reading last update ID: {e}")
        return None

def save_last_update_id(update_id):
    """Save the last processed update ID."""
    try:
        with open(LAST_UPDATE_FILE, 'w') as f:
            f.write(str(update_id))
    except Exception as e:
        log(f"Error saving last update ID: {e}")

def run_agent_with_context(user_message, stop_context, env_vars):
    """Handle the user's response using Claude Agent SDK."""
    try:
        # Unset CLAUDECODE=1 to allow SDK usage within Claude Code
        if 'CLAUDECODE' in os.environ:
            del os.environ['CLAUDECODE']
            log("Unset CLAUDECODE environment variable for SDK usage")

        from anthropic import Anthropic

        # Get API key from keychain (same method as stop hook)
        sys.path.insert(0, str(SCRIPT_DIR.parent))
        from sdk_auth import get_api_key_from_keychain

        api_key = get_api_key_from_keychain()
        if not api_key:
            log("ERROR: Could not get API key from keychain")
            return "ERROR: Could not get API key from keychain"

        log("API key retrieved from keychain")
        client = Anthropic(api_key=api_key)

        # Load the agent prompt
        prompt_file = SCRIPT_DIR / "telegram_response_handler_prompt.txt"
        if not prompt_file.exists():
            log(f"ERROR: Prompt file not found at {prompt_file}")
            return f"ERROR: Prompt file not found"

        with open(prompt_file, 'r') as f:
            system_prompt = f.read()

        # Define tools for the agent
        tools = [
            {
                "name": "read_file",
                "description": "Read the contents of a file. Use this to read transcripts, prompt files, or stop context.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                }
            },
            {
                "name": "edit_file",
                "description": "Edit a file by replacing old_string with new_string. Use this to update the stop_continue_analyzer_prompt.txt file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "Absolute path to the file to edit"
                        },
                        "old_string": {
                            "type": "string",
                            "description": "The exact string to replace"
                        },
                        "new_string": {
                            "type": "string",
                            "description": "The replacement string"
                        }
                    },
                    "required": ["file_path", "old_string", "new_string"]
                }
            },
            {
                "name": "send_telegram",
                "description": "Send a message to the user via Telegram. ALWAYS use this to respond to the user.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "The message to send (HTML formatting supported)"
                        }
                    },
                    "required": ["message"]
                }
            }
        ]

        # Build the user message with context
        user_prompt = f"""STOP EVENT CONTEXT:
Reason: {stop_context.get('reason', 'Unknown')}
Conversation Context: {stop_context.get('conversation_context', 'Unknown')}
User Message: {stop_context.get('user_message', 'Unknown')}
Confidence: {stop_context.get('confidence', 'unknown')}
Has Question: {stop_context.get('has_question', False)}
Original Goal: {stop_context.get('original_goal', 'Unknown')}
Session ID: {stop_context.get('session_id', 'unknown')}
Working Directory: {stop_context.get('cwd', 'unknown')}
Timestamp: {stop_context.get('timestamp', 'unknown')}

Conversation Snippet (last 1000 chars):
{stop_context.get('conversation_snippet', '')[-1000:]}

Transcript file: {stop_context.get('transcript_file', 'unknown')}

USER'S RESPONSE: {user_message}

Please handle this response according to your instructions. The user chose one of:
- Option 1 (Continue + teach) - if they said "1" or "continue"
- Option 2 (More info) - if they said "2" or "more info"
- Option 3 (Custom message) - if they said anything else

Remember to send your response via Telegram using the send_telegram tool!"""

        # Run the agent
        messages = [{"role": "user", "content": user_prompt}]

        max_iterations = 10
        for iteration in range(max_iterations):
            log(f"Agent iteration {iteration + 1}/{max_iterations}")

            response = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=4096,
                system=system_prompt,
                tools=tools,
                messages=messages
            )

            log(f"Response stop_reason: {response.stop_reason}")

            # Add assistant response to messages
            messages.append({
                "role": "assistant",
                "content": response.content
            })

            # If no tool use, we're done
            if response.stop_reason != "tool_use":
                log("Agent finished (no more tool use)")
                break

            # Process tool calls
            tool_results = []
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    tool_use_id = content_block.id

                    log(f"Tool call: {tool_name} with input: {tool_input}")

                    try:
                        if tool_name == "read_file":
                            file_path = Path(tool_input["file_path"])
                            if file_path.exists():
                                with open(file_path, 'r') as f:
                                    result = f.read()
                                log(f"Read {len(result)} chars from {file_path}")
                            else:
                                result = f"ERROR: File not found: {file_path}"
                                log(result)

                        elif tool_name == "edit_file":
                            file_path = Path(tool_input["file_path"])
                            old_string = tool_input["old_string"]
                            new_string = tool_input["new_string"]

                            if not file_path.exists():
                                result = f"ERROR: File not found: {file_path}"
                            else:
                                with open(file_path, 'r') as f:
                                    content = f.read()

                                if old_string not in content:
                                    result = f"ERROR: old_string not found in file"
                                else:
                                    new_content = content.replace(old_string, new_string, 1)
                                    with open(file_path, 'w') as f:
                                        f.write(new_content)
                                    result = f"SUCCESS: File edited successfully"
                                    log(f"Edited {file_path}")

                        elif tool_name == "send_telegram":
                            message = tool_input["message"]
                            bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
                            chat_id = env_vars.get('TELEGRAM_CHAT_ID')

                            success = send_telegram_message(bot_token, chat_id, message)
                            if success:
                                result = "SUCCESS: Message sent to Telegram"
                                log("Sent Telegram message")
                            else:
                                result = "ERROR: Failed to send Telegram message"
                                log("Failed to send Telegram message")

                        else:
                            result = f"ERROR: Unknown tool: {tool_name}"
                            log(result)

                    except Exception as e:
                        result = f"ERROR: {str(e)}"
                        log(f"Tool execution error: {e}")
                        import traceback
                        log(traceback.format_exc())

                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": result
                    })

            # Add tool results to messages
            if tool_results:
                messages.append({
                    "role": "user",
                    "content": tool_results
                })
            else:
                # No tool calls but stop_reason was tool_use - shouldn't happen
                log("WARNING: stop_reason was tool_use but no tools found")
                break

        if iteration >= max_iterations - 1:
            log("WARNING: Agent reached max iterations")
            bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
            chat_id = env_vars.get('TELEGRAM_CHAT_ID')
            send_telegram_message(bot_token, chat_id,
                "⚠️ <b>Agent timeout:</b> Reached maximum iterations. Please check logs.")

        return "OK"

    except Exception as e:
        log(f"Error in agent execution: {e}")
        import traceback
        log(traceback.format_exc())

        # Try to send error to Telegram
        try:
            bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
            chat_id = env_vars.get('TELEGRAM_CHAT_ID')
            send_telegram_message(bot_token, chat_id,
                f"❌ <b>Handler error:</b> {str(e)}")
        except:
            pass

        return f"ERROR: {str(e)}"

def main():
    """Main polling loop."""
    log("=== Telegram Response Handler Started ===")
    log(f"Working directory: {PROJECT_ROOT}")

    # Load environment
    env_vars = load_env()
    bot_token = env_vars.get('TELEGRAM_BOT_TOKEN')
    chat_id = env_vars.get('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        log("ERROR: Telegram credentials not configured in .env")
        return 1

    log(f"Bot token: {bot_token[:20]}...")
    log(f"Chat ID: {chat_id}")

    # Get last update ID
    last_update_id = get_last_update_id()
    log(f"Starting from update ID: {last_update_id}")

    # Send startup message
    send_telegram_message(bot_token, chat_id, "🤖 <b>Response Handler Started</b>\n\nListening for your responses to stop notifications...")

    try:
        while True:
            # Get new updates
            updates = get_telegram_updates(bot_token, last_update_id)

            for update in updates:
                update_id = update.get('update_id')
                message = update.get('message', {})
                text = message.get('text', '').strip()
                from_chat_id = str(message.get('chat', {}).get('id', ''))
                reply_to_message_id = message.get('reply_to_message', {}).get('message_id')

                log(f"Received update {update_id}: {text} (reply_to: {reply_to_message_id})")

                # Only process messages from our configured chat
                if from_chat_id != chat_id:
                    log(f"Ignoring message from different chat: {from_chat_id}")
                    last_update_id = update_id + 1
                    save_last_update_id(last_update_id)
                    continue

                # Ignore empty messages
                if not text:
                    last_update_id = update_id + 1
                    save_last_update_id(last_update_id)
                    continue

                # Determine which session to work with
                target_session_id = None
                if reply_to_message_id:
                    # User replied to a specific notification
                    target_session_id = get_session_from_reply(reply_to_message_id)
                    if target_session_id:
                        log(f"Targeting session {target_session_id[:8]} based on reply")
                    else:
                        log(f"No session found for reply_to {reply_to_message_id}, using most recent")

                # Load stop context for the target session
                stop_context = load_stop_context(target_session_id)
                if not stop_context:
                    # List active sessions if any exist
                    active_sessions = list_active_sessions()
                    if active_sessions:
                        sessions_list = "\n".join([
                            f"• {s['session_id'][:8]} ({s['cwd'].split('/')[-1]}) - {s['reason'][:50]}..."
                            for s in active_sessions[:5]
                        ])
                        send_telegram_message(bot_token, chat_id,
                            f"⚠️ No stop context found.\n\n"
                            f"<b>Active sessions:</b>\n{sessions_list}\n\n"
                            f"💡 Reply to a stop notification to target a specific session."
                        )
                    else:
                        send_telegram_message(bot_token, chat_id,
                            "⚠️ No recent stop events found. This handler responds to stop notifications.")

                    last_update_id = update_id + 1
                    save_last_update_id(last_update_id)
                    continue

                # Process the message with the agent
                session_short = stop_context.get('session_id', 'unknown')[:8]
                send_telegram_message(bot_token, chat_id,
                    f"🔄 Processing request for session <code>{session_short}</code>...")

                result = run_agent_with_context(text, stop_context, env_vars)

                # Agent should have sent its response via Telegram directly
                # But send a fallback if something went wrong
                if result and result.startswith("ERROR"):
                    send_telegram_message(bot_token, chat_id, f"❌ {result}")

                # Update last processed ID
                last_update_id = update_id + 1
                save_last_update_id(last_update_id)

            # Brief sleep before next poll
            if not updates:
                time.sleep(1)

    except KeyboardInterrupt:
        log("\n=== Handler stopped by user ===")
        send_telegram_message(bot_token, chat_id, "🛑 <b>Response Handler Stopped</b>")
        return 0
    except Exception as e:
        log(f"FATAL ERROR: {e}")
        import traceback
        log(traceback.format_exc())
        send_telegram_message(bot_token, chat_id, f"💥 <b>Handler crashed:</b> {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
