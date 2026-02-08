#!/usr/bin/env python3
"""
Fix XML indentation in all normalized test files.
Ensures consistent 2-space indentation throughout.
"""

from pathlib import Path
from lxml import etree


def fix_indentation(xml_file_path: Path) -> bool:
    """
    Fix XML indentation in a file.

    Args:
        xml_file_path: Path to the XML file to fix

    Returns:
        True if file was modified, False if no changes needed
    """
    print(f"Processing: {xml_file_path.name}")

    # Parse the XML file
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(str(xml_file_path), parser)

    # Serialize with proper indentation
    xml_bytes = etree.tostring(
        tree,
        encoding='utf-8',
        xml_declaration=True,
        pretty_print=True
    )

    # Write back to file
    xml_file_path.write_bytes(xml_bytes)
    print(f"  ✓ Fixed indentation")
    return True


def main():
    # Get all XML files in results directories
    base_dir = Path(__file__).parent.parent / "test-data" / "results" / "echom365"

    directories = [
        base_dir / "xml",
        base_dir / "wait"
    ]

    total_modified = 0
    total_files = 0

    for directory in directories:
        if not directory.exists():
            print(f"Warning: Directory not found: {directory}")
            continue

        xml_files = sorted(directory.glob("*.xml"))
        print(f"\n{directory.name}/ directory: Found {len(xml_files)} XML files")

        modified_count = 0
        for xml_file in xml_files:
            total_files += 1
            try:
                if fix_indentation(xml_file):
                    modified_count += 1
                    total_modified += 1
            except Exception as e:
                print(f"  ✗ Error: {e}")

        print(f"✓ Fixed {modified_count}/{len(xml_files)} files in {directory.name}/")

    print(f"\n✅ Total: Fixed indentation in {total_modified}/{total_files} files")


if __name__ == "__main__":
    main()
