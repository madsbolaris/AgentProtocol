#!/usr/bin/env python3
"""
Test the stop_continue_analyzer hook with mock data.
"""

import json
import subprocess
import tempfile
from pathlib import Path

def test_continue_scenario():
    """Test a scenario where Claude should continue."""

    # Create mock transcript where Claude has more work to do
    mock_transcript = {
        "messages": [
            {
                "role": "user",
                "content": "Please implement a new authentication system with OAuth2 and add tests"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I'll help implement an OAuth2 authentication system. Let me start by creating the auth module."
                    }
                ]
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I've created the authentication module with OAuth2 support. Now I need to add comprehensive tests and update the documentation."
                    }
                ]
            }
        ]
    }

    # Write mock transcript to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_transcript, f)
        transcript_path = f.name

    try:
        # Create hook input
        hook_input = {
            "transcript_path": transcript_path,
            "stop_hook_active": False,
            "session_id": "test-session",
            "cwd": "/tmp"
        }

        # Run the hook
        result = subprocess.run(
            ['.claude/hooks/stop_continue_analyzer.py'],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        print("=== Test: Continue Scenario ===")
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        # Parse decision
        if result.stdout:
            decision = json.loads(result.stdout)
            print(f"Decision: {decision.get('decision')}")
            if decision.get('decision') == 'block':
                print(f"Reason: {decision.get('reason')}")
                print("✅ Hook correctly identified work remaining")
            else:
                print("⚠️  Hook did not identify work remaining")

        return result.returncode == 0

    finally:
        Path(transcript_path).unlink(missing_ok=True)


def test_stop_scenario():
    """Test a scenario where Claude should stop (task complete)."""

    mock_transcript = {
        "messages": [
            {
                "role": "user",
                "content": "What's the weather like today?"
            },
            {
                "role": "assistant",
                "content": [
                    {
                        "type": "text",
                        "text": "I don't have access to real-time weather data. You can check weather.com or use a weather app for current conditions."
                    }
                ]
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_transcript, f)
        transcript_path = f.name

    try:
        hook_input = {
            "transcript_path": transcript_path,
            "stop_hook_active": False,
            "session_id": "test-session",
            "cwd": "/tmp"
        }

        result = subprocess.run(
            ['.claude/hooks/stop_continue_analyzer.py'],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        print("\n=== Test: Stop Scenario ===")
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")

        if result.stdout:
            decision = json.loads(result.stdout)
            print(f"Decision: {decision.get('decision')}")
            if decision.get('decision') == 'allow':
                print("✅ Hook correctly identified task is complete")
            else:
                print("⚠️  Hook thinks more work is needed")

        return result.returncode == 0

    finally:
        Path(transcript_path).unlink(missing_ok=True)


def test_recursive_stop():
    """Test that recursive stops are prevented."""

    mock_transcript = {
        "messages": [
            {
                "role": "user",
                "content": "Do something"
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(mock_transcript, f)
        transcript_path = f.name

    try:
        hook_input = {
            "transcript_path": transcript_path,
            "stop_hook_active": True,  # Simulating recursive call
            "session_id": "test-session",
            "cwd": "/tmp"
        }

        result = subprocess.run(
            ['.claude/hooks/stop_continue_analyzer.py'],
            input=json.dumps(hook_input),
            capture_output=True,
            text=True
        )

        print("\n=== Test: Recursive Stop Prevention ===")
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")

        if result.stdout:
            decision = json.loads(result.stdout)
            if decision.get('decision') == 'allow':
                print("✅ Hook correctly prevented infinite loop")
            else:
                print("❌ Hook did not prevent infinite loop")

        return result.returncode == 0

    finally:
        Path(transcript_path).unlink(missing_ok=True)


if __name__ == '__main__':
    print("Testing Stop Hook Continue Analyzer\n")

    success = True
    success &= test_continue_scenario()
    success &= test_stop_scenario()
    success &= test_recursive_stop()

    print("\n" + "="*50)
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
