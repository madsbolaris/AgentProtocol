#!/usr/bin/env python3
"""
Detect Misplaced Content in API Reference Documentation

This script identifies content that appears in the wrong API reference file,
such as ThreadWatch configuration appearing in agents.md instead of threads.md.

Usage:
    python detect-misplaced-content.py [path_to_api_reference]
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class ContentRule:
    """Rule defining what content belongs in which file."""
    pattern: str  # Regex pattern to match
    expected_file: str  # File where this content should appear
    description: str  # Human-readable description
    exception_files: List[str] = None  # Files where this content is OK

    def __post_init__(self):
        if self.exception_files is None:
            self.exception_files = []


# Define rules for content placement
CONTENT_RULES = [
    # ThreadWatch should be in threads.md (or in agents.md if discussing autoResponseConfig)
    ContentRule(
        pattern=r'###\s+ThreadWatch\s+Configuration',
        expected_file='threads.md',
        description='ThreadWatch Configuration section',
        exception_files=['agents.md']  # OK in agents.md if explaining autoResponseConfig
    ),

    # Thread subscription operations should be in thread-subscriptions.md
    ContentRule(
        pattern=r'POST\s+/threads/\{threadId\}/watch',
        expected_file='thread-subscriptions.md',
        description='Thread watch endpoint documentation',
        exception_files=['threads.md', 'README.md']
    ),

    # Agent subscription operations should be in agent-subscriptions.md
    ContentRule(
        pattern=r'POST\s+/agents/\{agentId\}/watch',
        expected_file='agent-subscriptions.md',
        description='Agent watch endpoint documentation',
        exception_files=['agents.md', 'README.md']
    ),

    # Run operations should be in runs.md
    ContentRule(
        pattern=r'POST\s+/threads/\{threadId\}/runs(?!/)',
        expected_file='runs.md',
        description='Run creation endpoint documentation',
        exception_files=['threads.md', 'README.md']
    ),

    # Hook configuration should be in specifications, not API reference
    ContentRule(
        pattern=r'###\s+Hook\s+(Configuration|Evaluation|Types)',
        expected_file='docs/specifications/hooks.md',
        description='Hook system documentation',
        exception_files=['README.md']
    ),

    # AutoResponseConfig details should be in agents.md or specifications
    ContentRule(
        pattern=r'###\s+AutoResponseConfig',
        expected_file='agents.md',
        description='AutoResponseConfig documentation',
        exception_files=['docs/specifications/agent-auto-response.md', 'README.md']
    ),

    # Connection types should be in authentication spec or content-types
    ContentRule(
        pattern=r'###\s+Connection\s+Types',
        expected_file='docs/specifications/authentication.md',
        description='Connection types documentation',
        exception_files=['content-types.md', 'README.md']
    ),
]


# Additional rules for detecting improperly scoped manual content
MANUAL_SCOPE_PATTERNS = [
    # Manual content should be scoped to specific endpoints
    (r'<!-- MANUAL_START: additional -->',
     r'<!-- MANUAL_END: additional -->',
     'Generic "additional" content should be endpoint-specific'),

    # Content between MANUAL_START and MANUAL_END should reference the endpoint
    (r'<!-- MANUAL_START: (\w+) ([\w\-/{}]+) -->',
     r'<!-- MANUAL_END: \1 \2 -->',
     'Manual content should have matching start/end markers'),
]


@dataclass
class Issue:
    """Represents a misplaced content issue."""
    file: str
    line_number: int
    severity: str  # 'error', 'warning', 'info'
    message: str
    matched_pattern: str
    expected_file: str = None

    def __str__(self):
        icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[self.severity]
        location = f"{self.file}:{self.line_number}"
        result = f"{icon} {self.severity.upper()}: {location}\n"
        result += f"   {self.message}\n"
        if self.expected_file:
            result += f"   Expected file: {self.expected_file}\n"
        result += f"   Pattern: {self.matched_pattern}\n"
        return result


def check_content_placement(file_path: Path, rules: List[ContentRule]) -> List[Issue]:
    """Check if content in the file follows placement rules."""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return [Issue(
            file=str(file_path),
            line_number=0,
            severity='error',
            message=f"Failed to read file: {e}",
            matched_pattern='N/A'
        )]

    file_name = file_path.name

    # Check each rule
    for rule in rules:
        pattern_matches = re.finditer(rule.pattern, content, re.MULTILINE | re.IGNORECASE)

        for match in pattern_matches:
            # Find line number
            line_number = content[:match.start()].count('\n') + 1

            # Check if this file is allowed to have this content
            is_expected_file = file_name == Path(rule.expected_file).name
            is_exception = file_name in [Path(f).name for f in rule.exception_files]

            if not is_expected_file and not is_exception:
                # Check context: if it's in a MANUAL_START section, verify it's endpoint-specific
                context_start = max(0, match.start() - 500)
                context = content[context_start:match.start()]

                # Look for MANUAL_START marker
                manual_marker = re.search(r'<!-- MANUAL_START: (\w+) -->', context)

                severity = 'warning'
                message = f"{rule.description} appears in wrong file"

                # If it's in an "additional" section, it's an error
                if manual_marker and manual_marker.group(1) == 'additional':
                    severity = 'error'
                    message = f"{rule.description} in generic 'additional' section (should be endpoint-specific)"

                issues.append(Issue(
                    file=str(file_path.relative_to(file_path.parent.parent)),
                    line_number=line_number,
                    severity=severity,
                    message=message,
                    matched_pattern=match.group(0),
                    expected_file=rule.expected_file
                ))

    return issues


def check_manual_scope(file_path: Path) -> List[Issue]:
    """Check if MANUAL_START/END sections are properly scoped to endpoints."""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return []

    # Find all MANUAL_START: additional sections
    additional_pattern = r'<!-- MANUAL_START: additional -->'
    matches = re.finditer(additional_pattern, content)

    for match in matches:
        line_number = content[:match.start()].count('\n') + 1

        # Get the section content
        end_match = re.search(r'<!-- MANUAL_END: additional -->', content[match.end():])
        if end_match:
            section_content = content[match.end():match.end() + end_match.start()]

            # Check if section has subsections (### headers)
            subsections = re.findall(r'^###\s+(.+)$', section_content, re.MULTILINE)

            if subsections:
                issues.append(Issue(
                    file=str(file_path.relative_to(file_path.parent.parent)),
                    line_number=line_number,
                    severity='error',
                    message=f"Generic 'additional' section contains {len(subsections)} subsections that should be endpoint-specific",
                    matched_pattern='<!-- MANUAL_START: additional -->',
                    expected_file=f"Should use endpoint-specific markers like 'post /agents' or 'get /threads/{{threadId}}'"
                ))

    # Check for mismatched MANUAL_START/END pairs
    start_pattern = r'<!-- MANUAL_START: (.+?) -->'
    end_pattern = r'<!-- MANUAL_END: (.+?) -->'

    starts = [(m.group(1), content[:m.start()].count('\n') + 1)
              for m in re.finditer(start_pattern, content)]
    ends = [(m.group(1), content[:m.start()].count('\n') + 1)
            for m in re.finditer(end_pattern, content)]

    # Verify matching pairs
    for i, (start_label, start_line) in enumerate(starts):
        if i < len(ends):
            end_label, end_line = ends[i]
            if start_label != end_label:
                issues.append(Issue(
                    file=str(file_path.relative_to(file_path.parent.parent)),
                    line_number=start_line,
                    severity='error',
                    message=f"Mismatched MANUAL_START/END: '{start_label}' vs '{end_label}'",
                    matched_pattern=f'<!-- MANUAL_START: {start_label} -->'
                ))
        else:
            issues.append(Issue(
                file=str(file_path.relative_to(file_path.parent.parent)),
                line_number=start_line,
                severity='error',
                message=f"MANUAL_START without matching MANUAL_END: '{start_label}'",
                matched_pattern=f'<!-- MANUAL_START: {start_label} -->'
            ))

    return issues


def check_endpoint_context(file_path: Path) -> List[Issue]:
    """Check if endpoint documentation is properly structured."""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return []

    # Find all endpoint definitions (## POST /path or ## GET /path)
    endpoint_pattern = r'^##\s+(GET|POST|PUT|DELETE|PATCH)\s+([\w\-/{}]+)'
    endpoints = [(m.group(0), content[:m.start()].count('\n') + 1, m.end())
                 for m in re.finditer(endpoint_pattern, content, re.MULTILINE)]

    # For each endpoint, check if subsections (###) are before the next endpoint
    for i, (endpoint, line_num, end_pos) in enumerate(endpoints):
        # Find next endpoint or end of file
        next_start = endpoints[i + 1][2] if i + 1 < len(endpoints) else len(content)
        section = content[end_pos:next_start]

        # Count subsections in this endpoint's section
        subsections = re.findall(r'^###\s+(.+)$', section, re.MULTILINE)

        # Check if subsections are endpoint-specific
        generic_subsections = ['ThreadWatch Configuration', 'Run Conditions',
                              'Loop Prevention', 'Hook Configuration']

        for subsection in subsections:
            if subsection in generic_subsections:
                subsection_line = line_num + section[:section.find(f'### {subsection}')].count('\n')

                # Only flag if this is the wrong endpoint
                if 'ThreadWatch' in subsection and '/agents' in endpoint and '/watch' not in endpoint:
                    issues.append(Issue(
                        file=str(file_path.relative_to(file_path.parent.parent)),
                        line_number=subsection_line,
                        severity='warning',
                        message=f"'{subsection}' section under endpoint '{endpoint.strip()}' may be too generic",
                        matched_pattern=subsection,
                        expected_file="Consider moving to specification or making endpoint-specific"
                    ))

    return issues


def main():
    """Main entry point."""
    # Determine API reference directory
    if len(sys.argv) > 1:
        api_ref_dir = Path(sys.argv[1])
    else:
        api_ref_dir = Path(__file__).parent.parent.parent / 'api-reference'

    if not api_ref_dir.exists():
        print(f"❌ Directory not found: {api_ref_dir}")
        sys.exit(1)

    print("🔍 Detecting Misplaced Content in API Reference Documentation\n")
    print(f"📁 Scanning: {api_ref_dir}\n")

    # Find all markdown files
    md_files = list(api_ref_dir.rglob('*.md'))

    all_issues = []

    for md_file in md_files:
        # Skip README files for content placement checks
        if md_file.name == 'README.md':
            continue

        # Check content placement
        issues = check_content_placement(md_file, CONTENT_RULES)
        all_issues.extend(issues)

        # Check manual scope
        issues = check_manual_scope(md_file)
        all_issues.extend(issues)

        # Check endpoint context
        issues = check_endpoint_context(md_file)
        all_issues.extend(issues)

    # Sort issues by severity
    errors = [i for i in all_issues if i.severity == 'error']
    warnings = [i for i in all_issues if i.severity == 'warning']
    infos = [i for i in all_issues if i.severity == 'info']

    # Print results
    if errors:
        print("❌ ERRORS:\n")
        for issue in errors:
            print(issue)
            print()

    if warnings:
        print("⚠️  WARNINGS:\n")
        for issue in warnings:
            print(issue)
            print()

    if infos:
        print("ℹ️  INFO:\n")
        for issue in infos:
            print(issue)
            print()

    # Summary
    print("=" * 70)
    print("📊 Summary:\n")
    print(f"   ❌ Errors:   {len(errors)}")
    print(f"   ⚠️  Warnings: {len(warnings)}")
    print(f"   ℹ️  Info:     {len(infos)}")
    print(f"   📄 Files:    {len(md_files)}")
    print()

    if errors:
        print("❌ Content placement validation FAILED")
        sys.exit(1)
    elif warnings:
        print("⚠️  Content placement validation passed with warnings")
        sys.exit(0)
    else:
        print("✅ All content properly placed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
