"""
Minimal test to diagnose SDK hanging issue.

This test strips away all complexity to test just the SDK call.
"""
import pytest
import sys
from pathlib import Path

# Add scripts directory to path
_scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(_scripts_dir))


@pytest.mark.asyncio
async def test_sdk_simple_call(mock_claude_sdk, test_workspace):
    """
    Minimal test: just call the SDK with a simple prompt.

    This should either:
    - In replay mode: fail with "no recording found" (expected)
    - In record mode: make real API call and save recording
    """
    # Import AFTER mock is set up
    from claude_agent_sdk import query, ClaudeAgentOptions

    print(f"\n🔍 Test mode: {mock_claude_sdk.mode if mock_claude_sdk else 'record'}")
    print(f"🔍 Mock SDK: {type(mock_claude_sdk)}")

    # Create simple options
    options = ClaudeAgentOptions(allowed_tools=["Read"])

    # Create simple prompt (must be string, not array!)
    prompt = "Say hello in exactly 3 words."

    print(f"🚀 About to call query()...")

    # Call SDK
    event_count = 0
    try:
        async for event in query(prompt=prompt, options=options):
            event_count += 1
            print(f"📥 Got event #{event_count}: {type(event).__name__ if hasattr(event, '__name__') else type(event)}")

            # Just get first 3 events to keep it simple
            if event_count >= 3:
                print(f"✅ Got {event_count} events, stopping")
                break
    except FileNotFoundError as e:
        # Expected in replay mode if no recording exists
        print(f"⚠️  FileNotFoundError (expected in replay mode): {str(e)[:100]}...")
        if mock_claude_sdk and mock_claude_sdk.mode == "replay":
            pytest.skip("No recording found - expected in replay mode")
        raise
    except Exception as e:
        print(f"❌ Unexpected error: {type(e).__name__}: {e}")
        raise

    print(f"✅ Test completed successfully, got {event_count} events")
    assert event_count > 0, "Should have received at least one event"
