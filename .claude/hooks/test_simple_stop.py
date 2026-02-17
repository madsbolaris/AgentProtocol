#!/usr/bin/env python3
"""
Simple test hook to verify Stop hooks work at all.
This hook ALWAYS blocks with a test message.
"""
import json
import sys

def main():
    # Read input
    hook_input = json.loads(sys.stdin.read())

    # Log to stderr for debugging
    print(f"[STOP HOOK TEST] Hook fired! stop_hook_active={hook_input.get('stop_hook_active')}", file=sys.stderr)

    # Always block with a test message
    if hook_input.get('stop_hook_active', False):
        print(json.dumps({"decision": "allow"}), file=sys.stdout)
        print("[STOP HOOK TEST] Allowing due to stop_hook_active", file=sys.stderr)
    else:
        print(json.dumps({"decision": "block", "reason": "TEST: This is a test hook that always blocks"}), file=sys.stdout)
        print("[STOP HOOK TEST] Blocking with test message", file=sys.stderr)

    return 0

if __name__ == '__main__':
    sys.exit(main())
