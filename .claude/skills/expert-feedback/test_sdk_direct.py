#!/usr/bin/env python3
"""
Test claude_agent_sdk with proper auth setup, outside pytest.
"""
print("STEP 1: Starting imports...")
import asyncio
import sys
import os
from pathlib import Path

print("STEP 2: Setting up path...")
# Add .claude directory for sdk_auth
claude_dir = Path(__file__).parent.parent.parent.parent / ".claude"
sys.path.insert(0, str(claude_dir))
print(f"STEP 3: Importing sdk_auth from {claude_dir}...")
from sdk_auth import setup_claude_auth
print("STEP 4: sdk_auth imported successfully")

async def main():
    print("Setting up Claude auth...")
    if not setup_claude_auth(verbose=True):
        print("Failed to setup auth!")
        return

    print("\nImporting claude_agent_sdk...")
    from claude_agent_sdk import query, ClaudeAgentOptions

    print("Creating options...")
    options = ClaudeAgentOptions(allowed_tools=["Read"])

    print("Creating prompt...")
    prompt = "Say hello in exactly 3 words."

    print("\nCalling claude_agent_sdk.query()...")
    event_count = 0

    try:
        async for event in query(prompt=prompt, options=options):
            event_count += 1
            print(f"✅ Got event #{event_count}: {type(event).__name__}")
            if event_count >= 3:
                print("Got 3 events, breaking...")
                break
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return

    print(f"\n🎉 Success! Got {event_count} events")

if __name__ == "__main__":
    asyncio.run(main())
