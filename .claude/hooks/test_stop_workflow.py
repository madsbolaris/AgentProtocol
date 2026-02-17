#!/usr/bin/env python3
"""
Test script to simulate the stop hook workflow.

This script:
1. Creates a mock transcript
2. Calls the stop hook with mock data
3. Verifies the handler auto-starts
4. Checks the Telegram notification was sent
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime

# Create a temporary transcript file
TEST_TRANSCRIPT = Path("/tmp/test_stop_transcript.jsonl")
SESSION_ID = "test-session-" + datetime.now().strftime("%Y%m%d-%H%M%S")

def create_test_transcript():
    """Create a mock transcript with a conversation."""
    messages = [
        {
            "role": "user",
            "content": "Can you create a function to calculate fibonacci numbers?"
        },
        {
            "role": "assistant",
            "content": "I'll create a fibonacci function for you."
        },
        {
            "role": "assistant",
            "content": "Here's a simple fibonacci function:\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```\n\nWould you like me to add memoization to make it more efficient?"
        }
    ]

    with open(TEST_TRANSCRIPT, 'w') as f:
        for msg in messages:
            f.write(json.dumps(msg) + '\n')

    print(f"✅ Created test transcript: {TEST_TRANSCRIPT}")
    return str(TEST_TRANSCRIPT)

def call_stop_hook(transcript_path):
    """Call the stop hook with test data."""
    hook_input = {
        "session_id": SESSION_ID,
        "transcript_path": transcript_path,
        "cwd": "/Users/mabolan/AgentProtocol",
        "stop_hook_active": False
    }

    hook_script = Path(__file__).parent / "stop_continue_analyzer_debug.py"
    print(f"🔄 Calling stop hook: {hook_script}")

    try:
        result = subprocess.run(
            [sys.executable, str(hook_script)],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True,
            timeout=30
        )

        print(f"\n📊 Stop Hook Results:")
        print(f"Return code: {result.returncode}")
        print(f"\nStdout:\n{result.stdout}")
        if result.stderr:
            print(f"\nStderr:\n{result.stderr}")

        # Parse the decision
        try:
            decision = json.loads(result.stdout)
            print(f"\n✅ Decision: {decision}")
            return decision
        except json.JSONDecodeError:
            print(f"❌ Could not parse decision as JSON")
            return None

    except subprocess.TimeoutExpired:
        print("❌ Stop hook timed out")
        return None
    except Exception as e:
        print(f"❌ Error calling stop hook: {e}")
        return None

def check_handler_running():
    """Check if the Telegram handler is running."""
    pid_file = Path("/tmp/telegram_handler.pid")

    if not pid_file.exists():
        print("❌ Handler PID file not found")
        return False

    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read().strip())

        result = subprocess.run(['ps', '-p', str(pid)], capture_output=True)
        if result.returncode == 0:
            print(f"✅ Handler is running (PID: {pid})")
            return True
        else:
            print(f"❌ Handler not running (PID {pid} not found)")
            return False
    except Exception as e:
        print(f"❌ Error checking handler: {e}")
        return False

def check_stop_context():
    """Check if stop context was saved."""
    context_file = Path(f"/tmp/claude_stop_contexts/{SESSION_ID}.json")

    if not context_file.exists():
        print(f"❌ Stop context not found at {context_file}")
        return False

    try:
        with open(context_file, 'r') as f:
            context = json.load(f)

        print(f"✅ Stop context saved:")
        print(f"  - Reason: {context.get('reason', 'N/A')[:80]}...")
        print(f"  - Conversation Context: {context.get('conversation_context', 'N/A')}")
        print(f"  - User Message: {context.get('user_message', 'N/A')}")
        print(f"  - Confidence: {context.get('confidence', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Error reading stop context: {e}")
        return False

def main():
    print("=" * 60)
    print("Testing Stop Hook Workflow")
    print("=" * 60)

    # Step 1: Create test transcript
    print("\n1️⃣ Creating test transcript...")
    transcript_path = create_test_transcript()

    # Step 2: Call stop hook
    print("\n2️⃣ Calling stop hook...")
    decision = call_stop_hook(transcript_path)

    if not decision:
        print("\n❌ Test failed: Could not get decision from stop hook")
        return 1

    # Step 3: Check handler is running
    print("\n3️⃣ Checking if handler auto-started...")
    time.sleep(2)  # Give it a moment to start
    handler_running = check_handler_running()

    # Step 4: Check stop context was saved
    print("\n4️⃣ Checking stop context...")
    context_saved = check_stop_context()

    # Step 5: Check logs
    print("\n5️⃣ Checking logs...")
    print("\nStop Hook Log (last 10 lines):")
    try:
        result = subprocess.run(['tail', '-10', '/tmp/stop_hook_debug.log'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Could not read log: {e}")

    print("\nHandler Log (last 10 lines):")
    try:
        result = subprocess.run(['tail', '-10', '/tmp/telegram_handler.log'], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Could not read log: {e}")

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"✅ Stop hook called: Yes")
    print(f"{'✅' if handler_running else '❌'} Handler auto-started: {handler_running}")
    print(f"{'✅' if context_saved else '❌'} Context saved: {context_saved}")
    print(f"\n📱 Check your Telegram for the notification!")
    print(f"💬 Reply with 1, 2, or 3 to test the handler")

    # Cleanup
    print(f"\n🧹 Cleanup:")
    print(f"  Test transcript: {TEST_TRANSCRIPT}")
    print(f"  Stop context: /tmp/claude_stop_contexts/{SESSION_ID}.json")

    return 0 if (handler_running and context_saved) else 1

if __name__ == '__main__':
    sys.exit(main())
