#!/usr/bin/env python3
"""
Test claude_agent_sdk outside of pytest to isolate the issue.
"""
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions

async def main():
    print("Testing claude_agent_sdk outside pytest...")

    options = ClaudeAgentOptions(allowed_tools=["Read"])
    prompt = "Say hello in 3 words"

    print("Calling query()...")
    event_count = 0

    async for event in query(prompt=prompt, options=options):
        event_count += 1
        print(f"Got event #{event_count}: {type(event).__name__}")
        if event_count >= 3:
            break

    print(f"Success! Got {event_count} events")

if __name__ == "__main__":
    asyncio.run(main())
