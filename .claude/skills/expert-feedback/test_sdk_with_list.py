#!/usr/bin/env python3
"""
Test if list prompts work with the real SDK.
"""
import asyncio
import sys
import os
from pathlib import Path

# Unset Claude Code env vars
os.environ.pop('CLAUDECODE', None)
os.environ.pop('CLAUDE_CODE_ENTRYPOINT', None)

# Add .claude directory for sdk_auth
claude_dir = Path(__file__).parent.parent.parent.parent / ".claude"
sys.path.insert(0, str(claude_dir))
from sdk_auth import setup_claude_auth

async def main():
    print("Setting up Claude auth...")
    if not setup_claude_auth(verbose=True):
        print("Failed to setup auth!")
        return

    print("\nImporting claude_agent_sdk...")
    from claude_agent_sdk import query, ClaudeAgentOptions

    print("Creating options...")
    options = ClaudeAgentOptions(allowed_tools=["Read"])

    # Test 1: String prompt (should work)
    print("\n=== TEST 1: String Prompt ===")
    prompt_str = "Say hello in exactly 3 words."
    print(f"Calling query() with string prompt...")
    event_count = 0
    try:
        async for event in query(prompt=prompt_str, options=options):
            event_count += 1
            print(f"✅ Got event #{event_count}: {type(event).__name__}")
            if event_count >= 3:
                break
        print(f"✅ String prompt test passed: {event_count} events\n")
    except Exception as e:
        print(f"❌ String prompt test failed: {e}\n")

    # Test 2: List prompt (system blocks)
    print("=== TEST 2: List Prompt (System Blocks) ===")
    prompt_list = [
        {
            "type": "text",
            "text": "You are a helpful assistant.",
            "cache_control": {"type": "ephemeral"}
        },
        {
            "type": "text",
            "text": "Say hello in exactly 3 words."
        }
    ]
    print(f"Calling query() with list prompt (2 blocks)...")
    event_count = 0
    try:
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Query timed out after 10 seconds")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(10)  # 10 second timeout

        async for event in query(prompt=prompt_list, options=options):
            event_count += 1
            print(f"✅ Got event #{event_count}: {type(event).__name__}")
            if event_count >= 3:
                break

        signal.alarm(0)  # Cancel timeout
        print(f"✅ List prompt test passed: {event_count} events\n")
    except TimeoutError as e:
        print(f"❌ List prompt test TIMED OUT: {e}")
        print(f"   This means the SDK hung when given a list prompt\n")
    except Exception as e:
        print(f"❌ List prompt test failed: {e}\n")

if __name__ == "__main__":
    asyncio.run(main())
