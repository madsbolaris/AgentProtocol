#!/usr/bin/env python3
"""
Check all markdown cross-references (internal links) are valid.

This script:
1. Finds all markdown files in the repository
2. Extracts all internal links ([text](path) and [text](path#anchor))
3. Validates that target files exist
4. Validates that anchors exist in target files
5. Reports broken links
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
from urllib.parse import urlparse, unquote


class MarkdownLinkChecker:
    """Check all markdown cross-references."""

    def __init__(self, repo_root: str, docs_dirs: List[str]):
        self.repo_root = Path(repo_root)
        self.docs_dirs = [Path(d) for d in docs_dirs]
        self.issues: List[Dict] = []
        self.file_anchors: Dict[Path, Set[str]] = {}

    def check_all(self):
        """Check all markdown files."""
        print("🔍 Checking markdown cross-references...\n")

        # Find all markdown files
        md_files = []
        for docs_dir in self.docs_dirs:
            if docs_dir.exists():
                md_files.extend(docs_dir.glob("**/*.md"))

        print(f"✓ Found {len(md_files)} markdown files to check\n")

        # Check each file
        for md_file in md_files:
            # Skip .workspace directory
            if '.workspace' in str(md_file):
                continue
            self._check_file(md_file)

        # Report issues
        self._report_issues()

    def _check_file(self, file_path: Path):
        """Check all links in a markdown file."""
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return

        # Find all markdown links: [text](url)
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        for match in re.finditer(link_pattern, content):
            link_text = match.group(1)
            link_url = match.group(2)
            line_num = content[:match.start()].count('\n') + 1

            # Skip external links (http://, https://, mailto:)
            if link_url.startswith(('http://', 'https://', 'mailto:')):
                continue

            # Skip fragment-only links (#anchor)
            if link_url.startswith('#'):
                # Check anchor exists in current file
                self._check_anchor_in_file(file_path, file_path, link_url[1:], line_num, link_text)
                continue

            # Parse internal link
            self._check_internal_link(file_path, link_url, line_num, link_text)

    def _check_internal_link(self, source_file: Path, link_url: str, line_num: int, link_text: str):
        """Check an internal link."""
        # Split into path and anchor
        if '#' in link_url:
            link_path, anchor = link_url.split('#', 1)
            anchor = unquote(anchor)  # Decode URL encoding
        else:
            link_path = link_url
            anchor = None

        # Skip empty paths
        if not link_path:
            return

        # Resolve relative path
        target_path = (source_file.parent / link_path).resolve()

        # Check if target exists
        if not target_path.exists():
            self.issues.append({
                'file': str(source_file.relative_to(self.repo_root)),
                'line': line_num,
                'type': 'BROKEN_LINK',
                'severity': 'ERROR',
                'link_text': link_text,
                'link_url': link_url,
                'target': str(target_path.relative_to(self.repo_root)) if target_path.is_relative_to(self.repo_root) else str(target_path),
                'message': f'Link target does not exist: {link_url}'
            })
            return

        # If anchor specified, check it exists
        if anchor:
            self._check_anchor_in_file(source_file, target_path, anchor, line_num, link_text)

    def _check_anchor_in_file(self, source_file: Path, target_file: Path, anchor: str, line_num: int, link_text: str):
        """Check if anchor exists in target file."""
        # Get or build anchor cache for this file
        if target_file not in self.file_anchors:
            self.file_anchors[target_file] = self._extract_anchors(target_file)

        anchors = self.file_anchors[target_file]

        # Check if anchor exists
        if anchor not in anchors:
            self.issues.append({
                'file': str(source_file.relative_to(self.repo_root)),
                'line': line_num,
                'type': 'BROKEN_ANCHOR',
                'severity': 'ERROR',
                'link_text': link_text,
                'anchor': anchor,
                'target': str(target_file.relative_to(self.repo_root)),
                'message': f'Anchor "#{anchor}" does not exist in {target_file.name}'
            })

    def _extract_anchors(self, file_path: Path) -> Set[str]:
        """Extract all valid anchor IDs from a markdown file."""
        anchors = set()
        try:
            content = file_path.read_text()

            # Find all headers: # Header, ## Header, etc.
            header_pattern = r'^#+\s+(.+)$'
            for match in re.finditer(header_pattern, content, re.MULTILINE):
                header_text = match.group(1)
                # Convert header to anchor ID (GitHub style)
                anchor = self._header_to_anchor(header_text)
                anchors.add(anchor)

            # Find explicit anchor IDs: <a id="anchor"></a> or <a name="anchor"></a>
            explicit_anchor_pattern = r'<a\s+(?:id|name)="([^"]+)"'
            for match in re.finditer(explicit_anchor_pattern, content):
                anchors.add(match.group(1))

        except Exception as e:
            print(f"⚠️  Could not extract anchors from {file_path}: {e}")

        return anchors

    def _header_to_anchor(self, header_text: str) -> str:
        """Convert markdown header to GitHub-style anchor ID."""
        # Remove markdown formatting (bold, italic, code, links)
        header_text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', header_text)  # **bold**
        header_text = re.sub(r'\*([^\*]+)\*', r'\1', header_text)      # *italic*
        header_text = re.sub(r'`([^`]+)`', r'\1', header_text)         # `code`
        header_text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', header_text)  # [link](url)

        # Convert to lowercase
        anchor = header_text.lower()

        # Replace spaces and special chars with hyphens
        anchor = re.sub(r'[^\w\s-]', '', anchor)
        anchor = re.sub(r'[\s_]+', '-', anchor)
        anchor = anchor.strip('-')

        return anchor

    def _report_issues(self):
        """Report all issues found."""
        if not self.issues:
            print("✅ No broken links found! All cross-references are valid.\n")
            return

        # Group by type
        errors = [i for i in self.issues if i['severity'] == 'ERROR']

        print(f"❌ Found {len(errors)} broken links:\n")

        # Group by type
        broken_links = [i for i in errors if i['type'] == 'BROKEN_LINK']
        broken_anchors = [i for i in errors if i['type'] == 'BROKEN_ANCHOR']

        # Report broken links
        if broken_links:
            print("BROKEN LINKS (Target file does not exist):")
            print("=" * 80)
            for issue in broken_links[:20]:  # Limit output
                print(f"\n{issue['file']}:{issue['line']}")
                print(f"  Link text: {issue['link_text']}")
                print(f"  Link URL: {issue['link_url']}")
                print(f"  Target: {issue['target']}")
            if len(broken_links) > 20:
                print(f"\n  ... and {len(broken_links) - 20} more broken links")
            print()

        # Report broken anchors
        if broken_anchors:
            print("\nBROKEN ANCHORS (Anchor does not exist in target):")
            print("=" * 80)
            for issue in broken_anchors[:20]:  # Limit output
                print(f"\n{issue['file']}:{issue['line']}")
                print(f"  Link text: {issue['link_text']}")
                print(f"  Target: {issue['target']}")
                print(f"  Missing anchor: #{issue['anchor']}")
            if len(broken_anchors) > 20:
                print(f"\n  ... and {len(broken_anchors) - 20} more broken anchors")
            print()

        # Summary by file
        print("\nSUMMARY BY FILE:")
        print("=" * 80)
        files_with_issues = defaultdict(lambda: {'BROKEN_LINK': 0, 'BROKEN_ANCHOR': 0})
        for issue in self.issues:
            files_with_issues[issue['file']][issue['type']] += 1

        for file_path, counts in sorted(files_with_issues.items(),
                                       key=lambda x: sum(x[1].values()),
                                       reverse=True):
            total = sum(counts.values())
            details = f"Links:{counts['BROKEN_LINK']} Anchors:{counts['BROKEN_ANCHOR']}"
            print(f"{total:3d} issues ({details}): {file_path}")


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    docs_dirs = [
        project_root / "api-reference",
        project_root / "guides",
        project_root / "specifications",
    ]

    # Check links
    print("📖 Checking markdown cross-references...")
    checker = MarkdownLinkChecker(str(project_root), [str(d) for d in docs_dirs])
    checker.check_all()

    # Exit code
    errors = [i for i in checker.issues if i['severity'] == 'ERROR']
    if errors:
        print(f"\n❌ Cross-reference check failed with {len(errors)} broken links")
        exit(1)
    else:
        print("\n✅ All cross-references are valid")
        exit(0)


if __name__ == "__main__":
    main()
