#!/usr/bin/env python3
"""
Simplified API Documentation Merger (1:1 filename matching).

With the new 1-file-per-endpoint structure, merging is simple:
1. For each generated file, look for a matching manual file with the same name
2. Append the manual content after the generated content
3. Done!

No complex parsing of MANUAL_START/END blocks needed.
"""

import shutil
from pathlib import Path


def merge_simple_file(gen_file: Path, manual_file: Path, output_file: Path) -> bool:
    """
    Merge a generated file with its manual content file.

    Args:
        gen_file: Generated file from TypeSpec
        manual_file: Manual content file (same filename)
        output_file: Output merged file

    Returns:
        True if merged, False if only generated content copied
    """
    # Read generated content
    gen_content = gen_file.read_text()

    # Check if manual file exists
    if not manual_file.exists():
        # No manual content - just copy generated
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(gen_content)
        return False

    # Read manual content
    manual_content = manual_file.read_text()

    # Simple merge: generated content + manual content
    # The manual content is just the examples/notes for that specific endpoint
    merged_lines = []

    # Add generated content
    merged_lines.append(gen_content.rstrip())
    merged_lines.append('')
    merged_lines.append('<!-- MANUAL_START -->')
    merged_lines.append('')

    # Add manual content (already has title/header)
    merged_lines.append(manual_content.strip())

    merged_lines.append('')
    merged_lines.append('<!-- MANUAL_END -->')

    # Write merged content
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text('\n'.join(merged_lines))

    return True


def merge_directory(gen_dir: Path, manual_dir: Path, output_dir: Path):
    """Merge all files in a directory."""
    # Get all generated files
    gen_files = list(gen_dir.glob('*.md'))

    merged_count = 0
    copied_count = 0

    for gen_file in gen_files:
        # Look for matching manual file
        manual_file = manual_dir / gen_file.name
        output_file = output_dir / gen_file.name

        # Merge or copy
        if merge_simple_file(gen_file, manual_file, output_file):
            print(f"✓ Merged: {gen_file.name}")
            merged_count += 1
        else:
            print(f"  Copied: {gen_file.name} (no manual overlay)")
            copied_count += 1

    return merged_count, copied_count


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent

    # Paths
    generated_dir = project_root / ".generated" / "api-reference"
    manual_dir = project_root / "docs-content"
    output_dir = project_root / "api-reference"

    print("API Documentation Merger (Simplified 1:1 Matching)")
    print("=" * 80)
    print(f"Generated: {generated_dir}")
    print(f"Manual:    {manual_dir}")
    print(f"Output:    {output_dir}")
    print("=" * 80)
    print()

    total_merged = 0
    total_copied = 0

    # Merge top-level files
    merged, copied = merge_directory(generated_dir, manual_dir, output_dir)
    total_merged += merged
    total_copied += copied

    # Merge operations subdirectory
    if (generated_dir / "operations").exists():
        print()
        merged, copied = merge_directory(
            generated_dir / "operations",
            manual_dir / "operations",
            output_dir / "operations"
        )
        total_merged += merged
        total_copied += copied

    # Merge models subdirectory
    if (generated_dir / "models").exists():
        print()
        merged, copied = merge_directory(
            generated_dir / "models",
            manual_dir / "models",
            output_dir / "models"
        )
        total_merged += merged
        total_copied += copied

    print()
    print(f"✅ Merged {total_merged} files, copied {total_copied} files")
    print()
    print("✅ Documentation merge complete!")
    print()
    print("Next steps:")
    print("docs/api-reference/")
    print("2. Add manual overlays in docs-content/")
    print("3. Re-run this script to merge updates")


if __name__ == '__main__':
    main()
