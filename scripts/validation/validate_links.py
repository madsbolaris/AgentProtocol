#!/usr/bin/env python3
"""
Markdown Link Validator

Validates all internal cross-references in markdown documentation.
Checks for broken links, missing files, and invalid anchors.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Set
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
class Link:
    source_file: str
    target: str
    line_number: int
    link_type: str  # 'relative', 'absolute', 'anchor'


def find_project_root() -> Path:
    """Find the AgentProtocol project root."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / "typespec").exists() and (current / "docs").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


def extract_markdown_links(md_file: Path, project_root: Path) -> List[Link]:
    """Extract all links from a markdown file."""
    links = []
    content = md_file.read_text()
    lines = content.split('\n')

    # Pattern: [text](link)
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')

    for line_num, line in enumerate(lines, 1):
        for match in link_pattern.finditer(line):
            link_text = match.group(1)
            link_target = match.group(2)

            # Skip external links (http/https)
            if link_target.startswith(('http://', 'https://')):
                continue

            # Determine link type
            if link_target.startswith('#'):
                link_type = 'anchor'
            elif link_target.startswith('/'):
                link_type = 'absolute'
            else:
                link_type = 'relative'

            rel_source = str(md_file.relative_to(project_root))
            links.append(Link(
                source_file=rel_source,
                target=link_target,
                line_number=line_num,
                link_type=link_type
            ))

    return links


def normalize_anchor(text: str) -> str:
    """
    Normalize text to match GitHub's anchor generation rules.
    - Convert to lowercase
    - Replace spaces with hyphens
    - Remove special characters except hyphens
    """
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text.strip('-')


def validate_link(link: Link, project_root: Path) -> Tuple[bool, str]:
    """
    Validate a single link.
    Returns (is_valid, error_message).
    """
    source_path = project_root / link.source_file

    # Handle anchor-only links (within same file)
    if link.link_type == 'anchor':
        anchor = link.target[1:]  # Remove leading #
        # Check if anchor exists in source file
        content = source_path.read_text()
        # Extract all headers and generate their anchors
        header_pattern = re.compile(r'^(#+)\s+(.+)$', re.MULTILINE)
        found = False
        for match in header_pattern.finditer(content):
            header_text = match.group(2).strip()
            # Remove markdown formatting from header
            header_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', header_text)
            header_text = re.sub(r'`([^`]+)`', r'\1', header_text)
            generated_anchor = normalize_anchor(header_text)
            if generated_anchor == anchor.lower():
                found = True
                break
        if not found:
            return False, f"Anchor '{link.target}' not found in {link.source_file}"
        return True, ""

    # Parse target path and anchor
    target_parts = link.target.split('#')
    target_path = target_parts[0]
    target_anchor = target_parts[1] if len(target_parts) > 1 else None

    # Resolve target file path
    if link.link_type == 'absolute':
        # Absolute path from project root
        target_file = project_root / target_path.lstrip('/')
    else:
        # Relative path from source file - use resolve() for proper path handling
        target_file = (source_path.parent / target_path).resolve()

    # Check if target file exists
    if not target_file.exists():
        # Check if it's a directory link
        if target_path.endswith('/'):
            target_dir = target_file
            if target_dir.exists() and target_dir.is_dir():
                return True, ""
        return False, f"Target file not found: {target_path}"

    # If target is a directory, check for README.md or index.md
    if target_file.is_dir():
        readme_file = target_file / "README.md"
        index_file = target_file / "index.md"
        if readme_file.exists():
            target_file = readme_file
        elif index_file.exists():
            target_file = index_file
        else:
            return False, f"Directory link missing README.md or index.md: {target_path}"

    # If there's an anchor, check if it exists in target file
    if target_anchor:
        content = target_file.read_text()
        # Extract all headers and generate their anchors
        header_pattern = re.compile(r'^(#+)\s+(.+)$', re.MULTILINE)
        found = False
        for match in header_pattern.finditer(content):
            header_text = match.group(2).strip()
            # Remove markdown formatting from header
            header_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', header_text)
            header_text = re.sub(r'`([^`]+)`', r'\1', header_text)
            generated_anchor = normalize_anchor(header_text)
            if generated_anchor == target_anchor.lower():
                found = True
                break
        if not found:
            return False, f"Anchor '#{target_anchor}' not found in {target_path}"

    return True, ""


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate internal cross-references in markdown documentation"
    )
    parser.parse_args()

    print(f"{BLUE}╔═══════════════════════════════════════════════════════════╗{RESET}")
    print(f"{BLUE}║     Markdown Link Validator                              ║{RESET}")
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
    for directory in ["specifications", "api-reference", "guides", "typespec"]:
        dir_path = project_root / directory
        if dir_path.exists():
            md_files.extend(dir_path.glob("*.md"))

    # Also check root
    md_files.extend(project_root.glob("*.md"))

    print(f"Found {len(md_files)} markdown files\n")

    # Extract all links
    print(f"{BLUE}[2/3] Extracting links...{RESET}")
    all_links = []
    for md_file in md_files:
        links = extract_markdown_links(md_file, project_root)
        all_links.extend(links)

    print(f"Found {len(all_links)} internal links\n")

    # Validate links
    print(f"{BLUE}[3/3] Validating links...{RESET}")
    broken_links = []

    for link in all_links:
        is_valid, error_msg = validate_link(link, project_root)
        if not is_valid:
            broken_links.append((link, error_msg))

    # Report results
    print("\n" + "=" * 60)

    if not broken_links:
        print(f"{GREEN}✓ All {len(all_links)} links are valid!{RESET}")
        return 0
    else:
        print(f"{RED}✗ Found {len(broken_links)} broken links:{RESET}\n")

        # Group by source file
        by_file = {}
        for link, error in broken_links:
            if link.source_file not in by_file:
                by_file[link.source_file] = []
            by_file[link.source_file].append((link, error))

        for source_file in sorted(by_file.keys()):
            print(f"{YELLOW}{source_file}:{RESET}")
            for link, error in by_file[source_file]:
                print(f"  Line {link.line_number}: {error}")
                print(f"    Target: {link.target}")
            print()

        return 1


if __name__ == "__main__":
    sys.exit(main())
