#!/usr/bin/env python3
"""
Shared code duplication analysis for all experts.

Detects duplicate code blocks across files using simple hash-based detection.

Usage:
    python3 scripts/shared/analyze_duplication.py --path /path/to/analyze [--min-lines 5]
"""

import argparse
import hashlib
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


def hash_lines(lines: List[str]) -> str:
    """Hash a list of lines for duplication detection.

    Args:
        lines: List of code lines

    Returns:
        SHA256 hash of the normalized lines
    """
    # Normalize: strip whitespace, ignore empty lines
    normalized = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):  # Ignore empty and comment-only lines
            normalized.append(stripped)

    if not normalized:
        return ""

    content = "\n".join(normalized)
    return hashlib.sha256(content.encode()).hexdigest()


def find_duplicates(
    path: Path,
    min_lines: int = 5,
    extensions: Set[str] = {'.py', '.js', '.ts', '.tsx', '.jsx'}
) -> Dict:
    """Find duplicate code blocks in files.

    Args:
        path: Directory or file to analyze
        min_lines: Minimum number of lines for a block to be considered
        extensions: File extensions to analyze

    Returns:
        Dict with duplication analysis:
        - duplicate_blocks: List of duplicate blocks with locations
        - total_duplicated_lines: Total lines of duplicated code
        - duplication_ratio: Ratio of duplicated to total lines
    """
    if path.is_file():
        files = [path]
    else:
        files = []
        for ext in extensions:
            files.extend(path.rglob(f"*{ext}"))

    # Map from block hash to list of (file, start_line, end_line, lines)
    block_locations: Dict[str, List[Tuple[Path, int, int, List[str]]]] = defaultdict(list)

    # Process each file
    for file_path in files:
        if file_path.suffix not in extensions:
            continue

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except (UnicodeDecodeError, PermissionError):
            continue

        # Sliding window to find blocks
        for start in range(len(lines) - min_lines + 1):
            end = start + min_lines
            block = lines[start:end]
            block_hash = hash_lines(block)

            if block_hash:  # Non-empty block
                block_locations[block_hash].append(
                    (file_path, start + 1, end, block)  # Line numbers are 1-indexed
                )

    # Find duplicates (blocks that appear more than once)
    duplicates = []
    total_duplicated_lines = 0

    for block_hash, locations in block_locations.items():
        if len(locations) > 1:
            # This block appears multiple times
            block_lines = len(locations[0][3])
            duplicate_entry = {
                "block_hash": block_hash[:8],  # Short hash for readability
                "block_size": block_lines,
                "occurrences": len(locations),
                "total_lines": block_lines * len(locations),
                "locations": [
                    {
                        "file": str(loc[0].relative_to(path) if path.is_dir() else loc[0].name),
                        "start_line": loc[1],
                        "end_line": loc[2],
                        "preview": "".join(loc[3][:3]).strip()[:100]  # First 3 lines, max 100 chars
                    }
                    for loc in locations
                ]
            }
            duplicates.append(duplicate_entry)
            total_duplicated_lines += block_lines * (len(locations) - 1)  # Subtract original

    # Sort by total lines (most duplicated first)
    duplicates.sort(key=lambda x: x["total_lines"], reverse=True)

    # Calculate total lines
    total_lines = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                total_lines += len(f.readlines())
        except (UnicodeDecodeError, PermissionError):
            continue

    duplication_ratio = (
        total_duplicated_lines / total_lines if total_lines > 0 else 0
    )

    return {
        "total_files_analyzed": len(files),
        "total_lines": total_lines,
        "total_duplicated_lines": total_duplicated_lines,
        "duplication_ratio": round(duplication_ratio, 4),
        "duplicate_blocks_count": len(duplicates),
        "duplicate_blocks": duplicates
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze code duplication in directory or file"
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to directory or file to analyze"
    )
    parser.add_argument(
        "--min-lines",
        type=int,
        default=5,
        help="Minimum lines for a block to be considered (default: 5)"
    )
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format (json or summary)"
    )

    args = parser.parse_args()

    if not args.path.exists():
        print(json.dumps({"error": f"Path not found: {args.path}"}))
        return 1

    result = find_duplicates(args.path, min_lines=args.min_lines)

    if args.format == "summary":
        # Human-readable summary
        print(f"\n🔍 Code Duplication Analysis: {args.path.name}\n")
        print(f"Files Analyzed: {result['total_files_analyzed']}")
        print(f"Total Lines: {result['total_lines']:,}")
        print(f"Duplicated Lines: {result['total_duplicated_lines']:,}")
        print(f"Duplication Ratio: {result['duplication_ratio'] * 100:.2f}%")
        print(f"Duplicate Blocks: {result['duplicate_blocks_count']}")

        if result['duplicate_blocks']:
            print("\n📋 Top Duplicate Blocks:")
            for i, block in enumerate(result['duplicate_blocks'][:10], 1):
                print(f"\n{i}. Block {block['block_hash']} ({block['block_size']} lines)")
                print(f"   Occurrences: {block['occurrences']}")
                print(f"   Total Lines: {block['total_lines']}")
                print("   Locations:")
                for loc in block['locations'][:5]:  # Show first 5 locations
                    print(f"     - {loc['file']}:{loc['start_line']}")
                if len(block['locations']) > 5:
                    print(f"     ... and {len(block['locations']) - 5} more")
        print()
    else:
        # JSON output
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
