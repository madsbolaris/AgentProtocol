#!/usr/bin/env python3
"""
Script to wrap individual message XML files with <thread> wrapper.
Processes files in test-data/normalized directory.
"""
import os
import re
from pathlib import Path
from lxml import etree

def wrap_with_thread(xml_file_path: Path):
    """Wrap an XML file's content with a <thread> element."""

    # Read the original file
    with open(xml_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Parse the XML
    try:
        parser = etree.XMLParser(remove_blank_text=False)
        tree = etree.fromstring(content.encode('utf-8'), parser)
    except Exception as e:
        print(f"Error parsing {xml_file_path}: {e}")
        return False

    # Check if already wrapped in <thread>
    if tree.tag == 'thread':
        print(f"Skipping {xml_file_path.name} - already has <thread> wrapper")
        return False

    # Extract file number for thread-id
    file_num = xml_file_path.stem.split('-')[0]
    thread_id = f"thread_example_{file_num.zfill(3)}"

    # Create thread wrapper
    thread = etree.Element('thread')
    thread.set('thread-id', thread_id)
    thread.set('status', 'active')
    thread.set('created-at', '2026-02-07T10:00:00Z')

    # Preserve the message as-is by adding it to thread
    thread.append(tree)

    # Create new XML with proper formatting
    xml_str = etree.tostring(
        thread,
        pretty_print=True,
        xml_declaration=True,
        encoding='utf-8'
    ).decode('utf-8')

    # Write back to file
    with open(xml_file_path, 'w', encoding='utf-8') as f:
        f.write(xml_str)

    print(f"✓ Wrapped {xml_file_path.name}")
    return True

def main():
    """Main function to process all result XML files."""
    base_dir = Path(__file__).parent.parent / "test-data" / "results" / "echobot"

    # Process both xml and wait directories
    directories = [
        base_dir / "xml",
        base_dir / "wait"
    ]

    total_updated = 0
    total_files = 0

    for directory in directories:
        if not directory.exists():
            print(f"Warning: Directory not found: {directory}")
            continue

        xml_files = sorted(directory.glob("*.xml"))
        print(f"\n{directory.name}/ directory: Found {len(xml_files)} XML files")

        updated_count = 0
        for xml_file in xml_files:
            total_files += 1
            if wrap_with_thread(xml_file):
                updated_count += 1
                total_updated += 1

        print(f"✓ Updated {updated_count}/{len(xml_files)} files in {directory.name}/")

    print(f"\n✅ Total: Updated {total_updated}/{total_files} files")

if __name__ == "__main__":
    main()
