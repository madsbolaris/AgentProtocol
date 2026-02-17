#!/usr/bin/env python3
"""
Find and fix all list prompts in the codebase.

Converts system_blocks (list of dicts) to string prompts to avoid SubprocessCLI transport issues.
"""
import re
from pathlib import Path

def find_system_blocks_usage():
    """Find all files that use system_blocks."""
    results = []
    scripts_dir = Path("scripts")

    for py_file in scripts_dir.rglob("*.py"):
        with open(py_file, 'r') as f:
            content = f.read()
            if 'system_blocks' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines, 1):
                    if 'system_blocks' in line:
                        results.append((str(py_file), i, line.strip()))

    return results

def main():
    print("🔍 Finding all system_blocks usage...\n")

    results = find_system_blocks_usage()

    print(f"Found {len(results)} instances:\n")
    for file, line_num, line in results:
        print(f"  {file}:{line_num}")
        print(f"    {line}")
        print()

    print("\n" + "="*80)
    print("CONVERSION PLAN")
    print("="*80)
    print("""
The fix requires converting system_blocks (list of text dicts) to a single string prompt.

Key changes needed:

1. scripts/agents/spawn.py (line 258):
   BEFORE: query(prompt=config.system_blocks, options=agent_options)
   AFTER:  query(prompt=flatten_system_blocks(config.system_blocks), options=agent_options)

2. Add helper function to spawn.py:
   def flatten_system_blocks(blocks):
       '''Convert list of message blocks to single string.'''
       if isinstance(blocks, str):
           return blocks
       text_parts = []
       for block in blocks:
           if isinstance(block, dict) and block.get('type') == 'text':
               text_parts.append(block['text'])
       return '\\n\\n'.join(text_parts)

This way:
- Cache control markers are ignored (not needed for recording)
- SubprocessCLI transport is avoided (uses simple HTTP transport)
- All existing code continues to work (just flattens the prompt)
""")

if __name__ == '__main__':
    main()
