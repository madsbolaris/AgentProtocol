#!/usr/bin/env python3
"""
Extract AIContent types from messages.tsp.
Outputs: List of all content types in the union.
"""

import re
import sys
from pathlib import Path


def extract_content_types():
    """Extract AIContent types from TypeSpec."""
    script_dir = Path(__file__).parent
    tsp_path = script_dir.parent.parent / "typespec" / "messages.tsp"

    content = tsp_path.read_text()

    # Find the AIContent union definition
    union_regex = r'@discriminator\("kind"\)\s*union\s+AIContent\s*\{([^}]+)\}'
    match = re.search(union_regex, content, re.DOTALL)

    if not match:
        print('Could not find AIContent union in messages.tsp', file=sys.stderr)
        sys.exit(1)

    union_body = match.group(1)

    # Extract content type names (excluding comments)
    lines = union_body.split('\n')
    types = []

    for line in lines:
        trimmed = line.strip()
        # Skip empty lines and comments
        if not trimmed or trimmed.startswith('//'):
            continue

        # Extract type name (before comma)
        type_match = re.match(r'^(\w+),?$', trimmed)
        if type_match:
            types.append(type_match.group(1))

    print(f'AIContent Types Found: {len(types)}')
    print()
    print('\n'.join(types))

    # Write to output file
    output_path = script_dir.parent / ".workspace" / "content-types-current.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text('\n'.join(types))

    print(f'\nOutput written to: {output_path}')


if __name__ == '__main__':
    extract_content_types()
