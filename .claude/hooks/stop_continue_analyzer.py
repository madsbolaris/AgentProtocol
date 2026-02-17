#!/usr/bin/env python3
"""
Stop Hook: Continue Analyzer

This hook runs when Claude stops responding and uses an LLM to analyze
whether Claude stopped prematurely and just needs to be told "continue".

Plays a beep sound ONLY when human intervention is needed (not on auto-continue).
"""

import json
import os
import subprocess
import sys
import warnings
from pathlib import Path

# Suppress deprecation warnings
warnings.filterwarnings('ignore')

# Add .claude directory to path to import sdk_auth
claude_dir = Path(__file__).parent.parent
sys.path.insert(0, str(claude_dir))

from sdk_auth import get_api_key_from_keychain

COUNTER_FILE = "/tmp/stop_hook_counter.json"
MAX_CONSECUTIVE_BLOCKS = 100  # Maximum auto-continues before forcing stop

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
    except Exception:
        pass
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

        # Keep last 10 reasons
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

        # Check for low confidence streak (3 low or 10 medium in a row)
        low_confidence_streak = False
        confidences = state["recent_confidences"]

        if len(confidences) >= 3 and confidences[-3:] == ["low", "low", "low"]:
            low_confidence_streak = True

        if len(confidences) >= 10 and confidences[-10:] == ["medium"] * 10:
            low_confidence_streak = True

        states[session_id] = state

        with open(COUNTER_FILE, 'w') as f:
            json.dump(states, f)

        return state["count"], is_spinning, low_confidence_streak
    except Exception:
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
    except Exception:
        pass

def analyze_conversation(transcript_path: str, api_key: str, original_goal: str = None) -> dict:
    """Use Anthropic SDK to analyze if Claude stopped prematurely."""
    try:
        import anthropic

        # Read the transcript (JSONL format - one JSON object per line)
        messages = []
        with open(transcript_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        obj = json.loads(line)
                        if 'message' in obj:
                            messages.append(obj['message'])
                    except json.JSONDecodeError:
                        continue

        # Extract recent conversation - more context for better analysis
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

        # Use Anthropic SDK to analyze
        client = anthropic.Anthropic(api_key=api_key)

        # Build original goal context
        goal_context = ""
        if original_goal:
            goal_context = f"""
ORIGINAL USER REQUEST (the initial goal for this session):
"{original_goal}"
"""

        analysis_prompt = f"""Analyze this conversation between a user and Claude Code (an AI coding assistant).
{goal_context}
Recent conversation history (last {len(conversation_summary)} messages, showing {len(conversation_summary[-10:])} exchanges):
{conversation_text}

Determine if Claude stopped prematurely and needs "continue" vs if human intervention is required.

Key decision factors:
1. Compare current state to the ORIGINAL USER REQUEST - is the goal complete?
2. Check if Claude asked a REAL question needing human input (if yes, stop immediately)

Continue if Claude has unfinished work:
- Mentioned next steps not yet taken ("I'll do X next", "then I'll...")
- Started but incomplete implementation
- Tests to run or code to verify
- Clear remaining tasks

Stop if work appears done or blocked:
- Original request is satisfied
- All tasks mentioned are complete
- Claude asked a REAL question requiring design decision or clarification
- Stuck or confused about how to proceed

Question classification:
REAL questions (stop - needs user input):
- "Which library should I use?" "Do you want OAuth or JWT?"
- "What should the error message say?" "How should this be structured?"
- "Should I use approach A or B?" (when A and B are significantly different)

FILLER questions (continue - just asking permission):
- "Would you like me to continue?" "Should I proceed?" "May I continue?"
- "Shall I keep going?" "Would you like me to finish?" "Continue to X?"
- "Should I do the next step?" "Proceed to phase 2?"
- "Continue phase 1.4 or jump to 2?" (always continue current phase, don't skip)
- "Can you test this?" "Please run this and let me know" "Try it out"
- "Could you verify this works?" "Let me know if this works"

Rules:
- If Claude asks permission to continue incomplete work → continue
- If Claude asks whether to continue current work or skip ahead → continue current work
- If Claude asks user to test/verify something → continue and Claude should test it programmatically:
  * Python: Run scripts, check logs, analyze output
  * UI: Use headless browsers, automation, screenshots
  * Never ask user to manually test - always automate testing

Return JSON:
{{
    "should_continue": true/false,
    "reason": "Brief reason (5-10 words)",
    "confidence": "high/medium/low",
    "has_question": true/false
}}

Guidelines:
- Keep reason brief: "Tests not run" not "Need to verify the tests pass"
- Set has_question=true only for REAL questions requiring user input
- Be conservative - only continue if clearly mid-task
- Don't continue if stuck/spinning on same problem"""

        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",  # Sonnet 4.5 for smarter analysis
            max_tokens=300,
            messages=[{"role": "user", "content": analysis_prompt}]
        )

        # Parse the response
        response_text = response.content[0].text

        # Try to extract JSON from the response
        try:
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                result = json.loads(json_str)
                return result
            else:
                return {
                    "should_continue": False,
                    "reason": "Could not parse LLM response",
                    "confidence": "low"
                }
        except json.JSONDecodeError:
            return {
                "should_continue": False,
                "reason": "Invalid JSON in LLM response",
                "confidence": "low"
            }

    except Exception as e:
        return {
            "should_continue": False,
            "reason": f"Analysis error: {str(e)}",
            "confidence": "low"
        }


def main():
    """Main hook entry point."""
    try:
        # Read hook input from stdin
        hook_input = json.loads(sys.stdin.read())

        session_id = hook_input.get('session_id', 'unknown')

        # Check our own counter to prevent truly infinite loops
        state = get_session_state(session_id)
        current_count = state["count"]

        # If we've hit our limit, allow stop
        if current_count >= MAX_CONSECUTIVE_BLOCKS:
            reset_session_counter(session_id)
            print(json.dumps({"decision": "allow"}))
            return 0

        # Claude Code's safety flag - we'll ignore it unless we hit our own limit
        # (stop_hook_active is just informational now)

        # Get API key
        api_key = get_api_key_from_keychain()
        if not api_key:
            print(json.dumps({"decision": "allow"}))
            return 0

        # Get transcript path
        transcript_path = hook_input.get('transcript_path')
        if not transcript_path or not os.path.exists(transcript_path):
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
                # Save state with updated goal
                states = {}
                if os.path.exists(COUNTER_FILE):
                    with open(COUNTER_FILE, 'r') as cf:
                        states = json.load(cf)
                states[session_id] = state
                with open(COUNTER_FILE, 'w') as cf:
                    json.dump(states, cf)
        except Exception:
            pass

        # Analyze the conversation
        analysis = analyze_conversation(transcript_path, api_key, state.get("original_goal"))

        # Make decision based on analysis
        has_question = analysis.get('has_question', False)
        should_continue = analysis.get('should_continue', False)
        confidence = analysis.get('confidence', 'low')

        # Never continue if Claude has a REAL question for the user
        if has_question:
            decision = {"decision": "allow"}
            reset_session_counter(session_id)
        elif should_continue and confidence in ['high', 'medium']:
            reason = analysis.get('reason', 'Continue working on the task')

            # Increment our counter and check if spinning or low confidence streak
            new_count, is_spinning, low_conf_streak = increment_session_counter(session_id, reason, confidence)

            # If spinning on same problem or low confidence streak, stop and let user intervene
            if is_spinning:
                decision = {"decision": "allow"}
                reset_session_counter(session_id)
            elif low_conf_streak:
                decision = {"decision": "allow"}
                reset_session_counter(session_id)
            else:
                decision = {
                    "decision": "block",
                    "reason": f"Continue: {reason}"
                }
        else:
            decision = {"decision": "allow"}
            reset_session_counter(session_id)

        # Play beep ONLY if allowing stop (human intervention needed)
        if decision.get("decision") == "allow":
            try:
                # Use Popen to avoid blocking/timeout issues
                subprocess.Popen(
                    ["afplay", "/System/Library/Sounds/Ping.aiff"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception:
                pass  # Beep failed, not critical

        # Output decision
        print(json.dumps(decision))
        return 0

    except Exception as e:
        # On error, allow the stop (fail open)
        print(json.dumps({"decision": "allow"}))
        return 1


if __name__ == '__main__':
    sys.exit(main())
