#!/usr/bin/env python3
"""
Check for deprecated patterns and old terminology in documentation.

This script searches for:
1. Old discriminator patterns ("type": instead of "kind":)
2. Deprecated terminology ("agent participation", "ThreadAutoResponder", etc.)
3. Old API patterns
4. Deprecated model names
5. Old field names
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class OldPatternChecker:
    """Check for deprecated patterns."""

    def __init__(self, repo_root: str, docs_dirs: List[str]):
        self.repo_root = Path(repo_root)
        self.docs_dirs = [Path(d) for d in docs_dirs]
        self.issues: List[Dict] = []

        # Define deprecated patterns
        self.deprecated_patterns = {
            # Old terminology
            'agent participation': {
                'replacement': 'agent auto-response',
                'severity': 'WARNING',
                'message': 'Use "agent auto-response" or "auto-response" instead'
            },
            'ThreadAutoResponder': {
                'replacement': 'ThreadWatch or AutoResponseConfig',
                'severity': 'WARNING',
                'message': 'ThreadAutoResponder is deprecated, use ThreadWatch (agent-scoped) or ThreadAutoResponder (thread-scoped)'
            },
            'agent-participation.md': {
                'replacement': 'agent-auto-response.md',
                'severity': 'ERROR',
                'message': 'Specification renamed to agent-auto-response.md'
            },

            # Old discriminator values
            'celExpression': {
                'replacement': '"kind": "expression"',
                'severity': 'ERROR',
                'message': 'Expression language determined by agent config, not condition type'
            },
            'powerFxExpression': {
                'replacement': '"kind": "expression"',
                'severity': 'ERROR',
                'message': 'Expression language determined by agent config, not condition type'
            },
            'CELExpression': {
                'replacement': '"kind": "expression"',
                'severity': 'ERROR',
                'message': 'Expression language determined by agent config, not condition type'
            },
            'PowerFxExpression': {
                'replacement': '"kind": "expression"',
                'severity': 'ERROR',
                'message': 'Expression language determined by agent config, not condition type'
            },

            # Old model names
            'CELExpressionCondition': {
                'replacement': 'ExpressionCondition',
                'severity': 'ERROR',
                'message': 'Removed in Phase 1, use ExpressionCondition'
            },
            'PowerFxExpressionCondition': {
                'replacement': 'ExpressionCondition',
                'severity': 'ERROR',
                'message': 'Removed in Phase 1, use ExpressionCondition'
            },

            # Old API patterns
            '/agent-participation': {
                'replacement': 'agent auto-response features',
                'severity': 'WARNING',
                'message': 'No dedicated endpoint, use AutoResponseConfig in agent definition'
            },

            # Old field names (ThreadCleanup enum)
            '"preserve"': {
                'replacement': '"keep"',
                'severity': 'ERROR',
                'message': 'ThreadCleanup value "preserve" renamed to "keep"'
            },
            '"destroy"': {
                'replacement': '"delete"',
                'severity': 'ERROR',
                'message': 'ThreadCleanup value "destroy" renamed to "delete"'
            },
        }

        # Patterns that should only be "kind": not "type":
        self.discriminator_values = [
            'text', 'image', 'audio', 'video', 'event', 'toolCall',
            'roles', 'content', 'mention', 'always', 'never', 'expression', 'webhook',
            'time', 'remote', 'functionCall', 'functionResult'
        ]

    def check_all(self):
        """Check all documentation files."""
        print("🔍 Checking for deprecated patterns...\n")

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
        """Check a single file for deprecated patterns."""
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return

        # Check for each deprecated pattern
        for pattern, info in self.deprecated_patterns.items():
            # Case-insensitive search for text patterns
            regex = re.compile(re.escape(pattern), re.IGNORECASE)
            for match in regex.finditer(content):
                line_num = content[:match.start()].count('\n') + 1

                # Get line context
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line_content = content[line_start:line_end if line_end != -1 else len(content)]

                # Skip if it's in a comment explaining removal
                skip_words = ['removed', 'deprecated', 'old', 'was', 'not', 'no longer',
                             'previously', 'formerly', 'replaced', 'instead of']
                if any(word in line_content.lower() for word in skip_words):
                    continue

                self.issues.append({
                    'file': str(file_path.relative_to(self.repo_root)),
                    'line': line_num,
                    'type': 'DEPRECATED_PATTERN',
                    'severity': info['severity'],
                    'pattern': match.group(0),
                    'replacement': info['replacement'],
                    'message': info['message'],
                    'line_content': line_content[:100]  # Limit line length
                })

        # Check for old discriminator field patterns
        for disc_value in self.discriminator_values:
            # Check for "type": "value" pattern (should be "kind": "value")
            old_pattern = f'"type":\\s*"{disc_value}"'
            for match in re.finditer(old_pattern, content):
                line_num = content[:match.start()].count('\n') + 1

                # Get line context
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line_content = content[line_start:line_end if line_end != -1 else len(content)]

                # Skip if it's explaining the old pattern
                if 'old' in line_content.lower() or 'deprecated' in line_content.lower():
                    continue

                self.issues.append({
                    'file': str(file_path.relative_to(self.repo_root)),
                    'line': line_num,
                    'type': 'OLD_DISCRIMINATOR_FIELD',
                    'severity': 'ERROR',
                    'pattern': match.group(0),
                    'replacement': f'"kind": "{disc_value}"',
                    'message': f'Discriminator field should be "kind" not "type"',
                    'line_content': line_content[:100]
                })

    def _report_issues(self):
        """Report all issues found."""
        if not self.issues:
            print("✅ No deprecated patterns found! Documentation is clean.\n")
            return

        # Group by severity
        errors = [i for i in self.issues if i['severity'] == 'ERROR']
        warnings = [i for i in self.issues if i['severity'] == 'WARNING']

        print(f"❌ Found {len(errors)} errors and {len(warnings)} warnings:\n")

        # Report errors
        if errors:
            print("ERRORS (Must fix):")
            print("=" * 80)
            for issue in errors[:20]:  # Limit output
                print(f"\n{issue['file']}:{issue['line']}")
                print(f"  Type: {issue['type']}")
                print(f"  Found: {issue['pattern']}")
                print(f"  Fix: {issue['replacement']}")
                print(f"  Reason: {issue['message']}")
            if len(errors) > 20:
                print(f"\n  ... and {len(errors) - 20} more errors")
            print()

        # Report warnings
        if warnings:
            print("\nWARNINGS (Should fix):")
            print("=" * 80)
            for issue in warnings[:10]:  # Limit output
                print(f"\n{issue['file']}:{issue['line']}")
                print(f"  Type: {issue['type']}")
                print(f"  Found: {issue['pattern']}")
                print(f"  Replacement: {issue['replacement']}")
                print(f"  Reason: {issue['message']}")
            if len(warnings) > 10:
                print(f"\n  ... and {len(warnings) - 10} more warnings")
            print()

        # Summary by file
        print("\nSUMMARY BY FILE:")
        print("=" * 80)
        files_with_issues = defaultdict(lambda: {'ERROR': 0, 'WARNING': 0})
        for issue in self.issues:
            files_with_issues[issue['file']][issue['severity']] += 1

        for file_path, counts in sorted(files_with_issues.items(),
                                       key=lambda x: (x[1]['ERROR'], x[1]['WARNING']),
                                       reverse=True):
            total = sum(counts.values())
            details = f"E:{counts['ERROR']} W:{counts['WARNING']}"
            print(f"{total:3d} issues ({details}): {file_path}")

        # Summary by pattern
        print("\nSUMMARY BY PATTERN:")
        print("=" * 80)
        patterns_count = defaultdict(int)
        for issue in self.issues:
            patterns_count[issue['pattern']] += 1

        for pattern, count in sorted(patterns_count.items(), key=lambda x: x[1], reverse=True):
            print(f"{count:3d} occurrences: {pattern}")


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    docs_dirs = [
        project_root / "api-reference",
        project_root / "guides",
        project_root / "specifications",
    ]

    # Check for old patterns
    print("📖 Checking for deprecated patterns...")
    checker = OldPatternChecker(str(project_root), [str(d) for d in docs_dirs])
    checker.check_all()

    # Exit code
    errors = [i for i in checker.issues if i['severity'] == 'ERROR']
    if errors:
        print(f"\n❌ Found {len(errors)} critical deprecated patterns")
        exit(1)
    else:
        warnings = [i for i in checker.issues if i['severity'] == 'WARNING']
        if warnings:
            print(f"\n⚠️  Found {len(warnings)} warnings (should fix but not critical)")
        else:
            print("\n✅ No deprecated patterns found")
        exit(0)


if __name__ == "__main__":
    main()
