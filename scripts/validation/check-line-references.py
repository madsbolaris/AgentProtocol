#!/usr/bin/env python3
"""
Line Number Reference Checker

Identifies line number references in documentation that point to TypeSpec files.
These are fragile and should be replaced with symbolic references.
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple
from dataclasses import dataclass

# Colors for output
try:
    from colorama import init, Fore, Style
    init()
    RED = Fore.RED
    GREEN = Fore.GREEN
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL
except ImportError:
    RED = GREEN = YELLOW = BLUE = RESET = ""


@dataclass
class LineReference:
    file: str
    line_number: int
    reference_text: str
    target_file: str
    target_lines: str


def find_project_root() -> Path:
    """Find the AgentProtocol project root."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "typespec").exists() and (current / "docs").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def find_line_references(md_file: Path, project_root: Path) -> List[LineReference]:
    """Find all line number references to TypeSpec files."""
    references = []
    content = md_file.read_text()
    lines = content.split('\n')

    # Patterns to detect line references
    # Pattern 1: `typespec/file.tsp:123-456`
    # Pattern 2: `typespec/file.tsp:123`
    # Pattern 3: (typespec/file.tsp:123-456)
    # Pattern 4: lines 123-456

    patterns = [
        re.compile(r'`(typespec/[\w./-]+\.tsp):(\d+(?:-\d+)?)`'),
        re.compile(r'\((typespec/[\w./-]+\.tsp):(\d+(?:-\d+)?)\)'),
        re.compile(r'(typespec/[\w./-]+\.tsp):(\d+(?:-\d+)?)'),
        re.compile(r'lines?\s+(\d+(?:-\d+)?)', re.IGNORECASE),
    ]

    rel_file = str(md_file.relative_to(project_root))

    for line_num, line in enumerate(lines, 1):
        for pattern in patterns:
            for match in pattern.finditer(line):
                if len(match.groups()) == 2:
                    target_file = match.group(1)
                    target_lines = match.group(2)
                else:
                    # Pattern 4 doesn't capture file, skip it for now
                    continue

                references.append(LineReference(
                    file=rel_file,
                    line_number=line_num,
                    reference_text=match.group(0),
                    target_file=target_file,
                    target_lines=target_lines
                ))

    return references


def validate_line_reference(ref: LineReference, project_root: Path) -> Tuple[bool, str]:
    """
    Check if line reference points to valid content.
    Returns (is_valid, context_info).
    """
    target_path = project_root / ref.target_file

    if not target_path.exists():
        return False, "File not found"

    try:
        content = target_path.read_text()
        lines = content.split('\n')

        # Parse line range
        if '-' in ref.target_lines:
            start, end = map(int, ref.target_lines.split('-'))
        else:
            start = end = int(ref.target_lines)

        # Check if line numbers are valid
        if start < 1 or end > len(lines):
            return False, f"Line range {ref.target_lines} is out of bounds (file has {len(lines)} lines)"

        # Extract context (first few lines of referenced range)
        context_lines = lines[start-1:min(start+2, end)]
        context = '\n    '.join(context_lines)

        return True, context
    except Exception as e:
        return False, str(e)


def suggest_replacement(ref: LineReference, context: str) -> str:
    """Suggest a symbolic replacement for line reference."""
    # Try to detect what's being referenced
    lower_context = context.lower()

    if 'enum' in lower_context:
        # Extract enum name
        match = re.search(r'enum\s+(\w+)', context)
        if match:
            enum_name = match.group(1)
            return f"See `{enum_name}` enum in `{ref.target_file}`"

    if 'model' in lower_context or 'interface' in lower_context:
        match = re.search(r'(?:model|interface)\s+(\w+)', context)
        if match:
            model_name = match.group(1)
            return f"See `{model_name}` model in `{ref.target_file}`"

    # Generic suggestion
    return f"See relevant section in `{ref.target_file}`"


def main():
    """Main validation function."""
    print(f"{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     Line Number Reference Checker                        ║{RESET}")
    print(f"{BLUE}╚═══════════════════════════════════════════════════════════╝{RESET}\n")

    try:
        project_root = find_project_root()
        print(f"Project root: {project_root}\n")
    except RuntimeError as e:
        print(f"{RED}Error: {e}{RESET}")
        return 1

    # Find all markdown files
    print(f"{BLUE}[1/3] Scanning for markdown files...{RESET}")
    md_files = []
    for directory in ["specifications", "api-reference", "guides"]:
        dir_path = project_root / directory
        if dir_path.exists():
            md_files.extend(dir_path.glob("*.md"))

    print(f"Found {len(md_files)} markdown files\n")

    # Find line references
    print(f"{BLUE}[2/3] Searching for line number references...{RESET}")
    all_references = []
    for md_file in md_files:
        refs = find_line_references(md_file, project_root)
        all_references.extend(refs)

    print(f"Found {len(all_references)} line number references\n")

    if not all_references:
        print(f"{GREEN}✓ No line number references found!{RESET}")
        return 0

    # Validate and suggest replacements
    print(f"{BLUE}[3/3] Analyzing references...{RESET}\n")
    print("=" * 60)

    # Group by file
    by_file = {}
    for ref in all_references:
        if ref.file not in by_file:
            by_file[ref.file] = []
        by_file[ref.file].append(ref)

    for source_file in sorted(by_file.keys()):
        print(f"\n{YELLOW}{source_file}:{RESET}")

        for ref in by_file[source_file]:
            is_valid, info = validate_line_reference(ref, project_root)

            if is_valid:
                suggestion = suggest_replacement(ref, info)
                print(f"  Line {ref.line_number}: {RED}{ref.reference_text}{RESET}")
                print(f"    Current context: {info[:100]}...")
                print(f"    {GREEN}Suggested: {suggestion}{RESET}")
            else:
                print(f"  Line {ref.line_number}: {RED}{ref.reference_text}{RESET}")
                print(f"    {RED}ERROR: {info}{RESET}")
        print()

    # Summary
    print("=" * 60)
    print(f"{YELLOW}⚠ Found {len(all_references)} line number references that should be updated{RESET}")
    print(f"{YELLOW}These references are fragile and break when code changes.{RESET}")
    print(f"\nRecommendation: Replace with symbolic references as suggested above.")

    return 1 if all_references else 0


if __name__ == "__main__":
    sys.exit(main())
