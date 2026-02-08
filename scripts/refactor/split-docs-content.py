#!/usr/bin/env python3
"""
Split docs-content files into 1-file-per-endpoint structure.

This script refactors the docs-content directory from:
  - Few files with multiple endpoints grouped together
To:
  - One file per endpoint/model

Example:
  Before: docs-content/operations/thread-subscriptions.md (5 endpoints)
  After:  docs-content/operations/post-threads-threadid-subscriptions.md
          docs-content/operations/get-threads-threadid-subscriptions.md
          (etc.)
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def extract_endpoint_key(endpoint_line: str) -> str:
    """Convert '### POST /threads/{threadId}/subscriptions' to 'post-threads-threadid-subscriptions'."""
    key = endpoint_line.lower()
    key = re.sub(r'###\s+', '', key)
    key = re.sub(r'[{}/\s]', '-', key)
    key = re.sub(r'-+', '-', key)
    key = key.strip('-')
    return key


def parse_manual_file(file_path: Path) -> Dict[str, Tuple[str, str]]:
    """
    Parse a manual content file and extract sections.

    Returns:
        Dict mapping endpoint keys to (title, content) tuples
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    sections = {}

    # Find all MANUAL_START blocks
    pattern = r'<!-- MANUAL_START:\s*(.+?)\s*-->(.+?)<!-- MANUAL_END:\s*\1\s*-->'
    matches = re.finditer(pattern, content, re.DOTALL)

    for match in matches:
        section_name = match.group(1)
        section_content = match.group(2).strip()

        # Check if this is an endpoint-specific section (not overview/examples/additional/content)
        if section_name in ['overview', 'examples', 'additional', 'content']:
            # These are old-style sections that need to be split by endpoint headers
            lines = section_content.split('\n')
            current_endpoint = None
            current_content = []

            for line in lines:
                # Look for endpoint headers: ### GET /path or ### POST /path
                endpoint_match = re.match(r'^###\s+(GET|POST|PUT|PATCH|DELETE)\s+/(.+)$', line)

                if endpoint_match:
                    # Save previous section
                    if current_endpoint and current_content:
                        endpoint_key = extract_endpoint_key(current_endpoint)
                        # Don't include the header line in content
                        sections[endpoint_key] = (current_endpoint, '\n'.join(current_content).strip())

                    # Start new section
                    current_endpoint = line
                    current_content = []
                else:
                    current_content.append(line)

            # Save last section
            if current_endpoint and current_content:
                endpoint_key = extract_endpoint_key(current_endpoint)
                sections[endpoint_key] = (current_endpoint, '\n'.join(current_content).strip())
        else:
            # Already endpoint-specific (e.g., "post /agents")
            # Extract just the endpoint key part
            endpoint_key = extract_endpoint_key(f"### {section_name}")
            sections[endpoint_key] = (section_name, section_content)

    return sections


def write_endpoint_file(output_dir: Path, endpoint_key: str, title: str, content: str):
    """Write a single endpoint's content to its own file."""
    # Create filename: post-threads-threadid-subscriptions.md
    filename = f"{endpoint_key}.md"
    file_path = output_dir / filename

    # Build file content
    lines = []
    lines.append(f"# {title.replace('###', '').strip()}")
    lines.append('')
    lines.append(content)
    lines.append('')

    # Write file
    file_path.write_text('\n'.join(lines))
    print(f"✓ Created: {file_path.relative_to(output_dir.parent.parent)}")


def split_operations_file(input_file: Path, output_dir: Path):
    """Split an operations file into individual endpoint files."""
    print(f"\n📄 Processing: {input_file.name}")

    sections = parse_manual_file(input_file)

    if not sections:
        print(f"   ⚠️  No sections found in {input_file.name}")
        return

    for endpoint_key, (title, content) in sections.items():
        write_endpoint_file(output_dir, endpoint_key, title, content)

    print(f"   ✓ Split into {len(sections)} files")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent

    # Input directory (current docs-content)
    input_dir = project_root / "docs-content" / "operations"

    # Output directory (new structure)
    output_dir = project_root / "docs-content-new" / "operations"
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🔄 Splitting docs-content into 1-file-per-endpoint structure")
    print(f"📂 Input:  {input_dir}")
    print(f"📂 Output: {output_dir}")

    # Process all .md files in operations directory
    for input_file in input_dir.glob("*.md"):
        # Skip README files
        if input_file.name.upper() == 'README.MD':
            continue

        split_operations_file(input_file, output_dir)

    print("\n" + "=" * 70)
    print("✅ Split complete!")
    print(f"\n📁 New structure created in: {output_dir.parent}")
    print("\nNext steps:")
    print("1. Review the new structure")
    print("2. Backup old docs-content: mv docs-content docs-content-old")
    print("3. Use new structure: mv docs-content-new docs-content")
    print("4. Update merge script for 1:1 filename matching")


if __name__ == '__main__':
    main()
