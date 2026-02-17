#!/usr/bin/env python3
"""
Shared codebase analysis for all experts.

Analyzes codebase structure, complexity, and metrics.

Usage:
    python3 scripts/shared/analyze_codebase.py --path /path/to/codebase
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


def count_lines(file_path: Path) -> Dict[str, int]:
    """Count lines in a file.

    Args:
        file_path: Path to file

    Returns:
        Dict with line counts:
        - total: Total lines
        - code: Non-blank, non-comment lines
        - blank: Blank lines
        - comment: Comment lines
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except (UnicodeDecodeError, PermissionError):
        return {"total": 0, "code": 0, "blank": 0, "comment": 0}

    total = len(lines)
    blank = 0
    comment = 0
    code = 0

    in_multiline_comment = False
    for line in lines:
        stripped = line.strip()

        if not stripped:
            blank += 1
            continue

        # Check for multiline comments (Python)
        if file_path.suffix == '.py':
            if stripped.startswith('"""') or stripped.startswith("'''"):
                in_multiline_comment = not in_multiline_comment
                comment += 1
                continue
            if in_multiline_comment:
                comment += 1
                continue

        # Single line comments
        if stripped.startswith('#') or stripped.startswith('//'):
            comment += 1
        else:
            code += 1

    return {
        "total": total,
        "code": code,
        "blank": blank,
        "comment": comment
    }


def analyze_codebase(path: Path, extensions: Set[str] = None) -> Dict:
    """Analyze codebase structure and metrics.

    Args:
        path: Directory to analyze
        extensions: File extensions to include (default: common code extensions)

    Returns:
        Dict with codebase analysis:
        - total_files: Total number of files
        - by_extension: Breakdown by file extension
        - total_lines: Total lines of code
        - directory_structure: Directory breakdown
    """
    if extensions is None:
        extensions = {
            '.py', '.js', '.ts', '.tsx', '.jsx',
            '.java', '.go', '.rs', '.c', '.cpp', '.h',
            '.cs', '.rb', '.php', '.swift', '.kt'
        }

    if not path.is_dir():
        return {"error": f"Path is not a directory: {path}"}

    # Collect all files
    files_by_ext = defaultdict(list)
    all_files = []

    for file_path in path.rglob("*"):
        if file_path.is_file() and file_path.suffix in extensions:
            # Skip hidden directories and common excludes
            if any(part.startswith('.') for part in file_path.parts):
                continue
            if any(exclude in file_path.parts for exclude in ['node_modules', '__pycache__', 'venv', '.venv', 'dist', 'build']):
                continue

            files_by_ext[file_path.suffix].append(file_path)
            all_files.append(file_path)

    # Analyze each extension
    by_extension = {}
    total_lines = {"total": 0, "code": 0, "blank": 0, "comment": 0}

    for ext, files in files_by_ext.items():
        ext_stats = {
            "files": len(files),
            "total_lines": 0,
            "code_lines": 0,
            "blank_lines": 0,
            "comment_lines": 0,
            "avg_file_size": 0
        }

        for file_path in files:
            counts = count_lines(file_path)
            ext_stats["total_lines"] += counts["total"]
            ext_stats["code_lines"] += counts["code"]
            ext_stats["blank_lines"] += counts["blank"]
            ext_stats["comment_lines"] += counts["comment"]

        if ext_stats["files"] > 0:
            ext_stats["avg_file_size"] = ext_stats["total_lines"] / ext_stats["files"]

        by_extension[ext] = ext_stats

        # Add to totals
        total_lines["total"] += ext_stats["total_lines"]
        total_lines["code"] += ext_stats["code_lines"]
        total_lines["blank"] += ext_stats["blank_lines"]
        total_lines["comment"] += ext_stats["comment_lines"]

    # Directory structure breakdown
    directories = defaultdict(int)
    for file_path in all_files:
        # Count files in each directory
        for parent in file_path.parents:
            if parent == path:
                break
            rel_path = str(parent.relative_to(path))
            directories[rel_path] += 1

    # Sort directories by file count
    top_directories = sorted(
        [{"path": k, "files": v} for k, v in directories.items()],
        key=lambda x: x["files"],
        reverse=True
    )[:20]  # Top 20 directories

    return {
        "total_files": len(all_files),
        "total_lines": total_lines,
        "by_extension": {
            ext: stats for ext, stats in sorted(
                by_extension.items(),
                key=lambda x: x[1]["total_lines"],
                reverse=True
            )
        },
        "top_directories": top_directories,
        "analyzed_path": str(path)
    }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze codebase structure and metrics"
    )
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="Path to codebase directory"
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

    result = analyze_codebase(args.path)

    if "error" in result:
        print(json.dumps(result))
        return 1

    if args.format == "summary":
        # Human-readable summary
        print(f"\n📦 Codebase Analysis: {args.path.name}\n")
        print(f"Total Files: {result['total_files']:,}")
        print(f"Total Lines: {result['total_lines']['total']:,}")
        print(f"  Code: {result['total_lines']['code']:,}")
        print(f"  Blank: {result['total_lines']['blank']:,}")
        print(f"  Comments: {result['total_lines']['comment']:,}")

        print("\n📊 By Extension:")
        for ext, stats in list(result['by_extension'].items())[:10]:
            print(f"  {ext}: {stats['files']} files, {stats['code_lines']:,} LOC")

        if result['top_directories']:
            print("\n📁 Top Directories:")
            for dir_info in result['top_directories'][:10]:
                print(f"  {dir_info['path']}: {dir_info['files']} files")
        print()
    else:
        # JSON output
        print(json.dumps(result, indent=2))

    return 0


if __name__ == "__main__":
    exit(main())
