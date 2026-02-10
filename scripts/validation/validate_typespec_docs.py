#!/usr/bin/env python3
import argparse
"""
Validate TypeSpec Documentation Completeness

Checks that TypeSpec files have required structured documentation:
- @usage sections for all endpoints/models
- @example blocks for all endpoints
- @response tags for all response codes

Usage:
    python validate-typespec-docs.py [path_to_typespec]
"""

import re
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Set


@dataclass
class DocIssue:
    """Represents a documentation issue."""
    file: str
    line: int
    severity: str  # 'error', 'warning', 'info'
    category: str  # 'missing_usage', 'missing_example', etc.
    message: str
    endpoint: str = ""

    def __str__(self):
        icon = {'error': '❌', 'warning': '⚠️', 'info': 'ℹ️'}[self.severity]
        location = f"{self.file}:{self.line}"
        if self.endpoint:
            location += f" ({self.endpoint})"
        result = f"{icon} {self.severity.upper()}: {location}\n"
        result += f"   {self.message}\n"
        result += f"   Category: {self.category}\n"
        return result


def find_endpoints(content: str, file_path: Path) -> List[Dict]:
    """
    Find all endpoint definitions in TypeSpec file.

    Returns list of dicts with:
    - line: line number
    - method: HTTP method
    - path: endpoint path
    - operation: operation name
    - doc_comment: documentation comment
    """
    endpoints = []

    # Pattern to match operation definitions with their doc comments
    # Matches: @doc(...) @get/@post/etc operation(...): Response
    operation_pattern = r'/\*\*(.*?)\*/\s*(?:@doc\([^)]+\)\s*)?@(get|post|put|patch|delete)\s+(?:@segment\([^)]+\)\s*)?(\w+)\s*\([^)]*\)'

    for match in re.finditer(operation_pattern, content, re.DOTALL | re.IGNORECASE):
        doc_comment = match.group(1)
        method = match.group(2).upper()
        operation = match.group(3)

        # Find line number
        line_num = content[:match.start()].count('\n') + 1

        # Extract path from doc comment or decorators
        path_match = re.search(r'@segment\s*\(["\']([^"\']+)["\']\)', content[match.start():match.end()])
        path = path_match.group(1) if path_match else f"/{operation}"

        endpoints.append({
            'line': line_num,
            'method': method,
            'path': path,
            'operation': operation,
            'doc_comment': doc_comment,
            'endpoint_str': f"{method} {path}"
        })

    return endpoints


def check_structured_docs(doc_comment: str) -> Dict[str, bool]:
    """
    Check if documentation has required structured sections.

    Returns dict with:
    - has_usage: bool
    - has_example: bool
    - has_responses: bool
    - example_count: int
    - response_codes: List[str]
    """
    result = {
        'has_usage': False,
        'has_example': False,
        'has_responses': False,
        'example_count': 0,
        'response_codes': []
    }

    # Check for @usage tag
    if re.search(r'@usage', doc_comment):
        result['has_usage'] = True

    # Check for free-form USAGE: section (backward compatibility)
    if not result['has_usage'] and re.search(r'USAGE:', doc_comment, re.IGNORECASE):
        result['has_usage'] = True

    # Check for @example tags
    example_matches = re.findall(r'@example\s+[^\n]+', doc_comment)
    result['example_count'] = len(example_matches)
    result['has_example'] = result['example_count'] > 0

    # Check for free-form EXAMPLES: section (backward compatibility)
    if not result['has_example'] and re.search(r'EXAMPLES?:', doc_comment, re.IGNORECASE):
        result['has_example'] = True
        result['example_count'] = 1

    # Check for @response tags
    response_matches = re.findall(r'@response\s+(\d+)', doc_comment)
    result['response_codes'] = response_matches
    result['has_responses'] = len(response_matches) > 0

    # Check for free-form RESPONSE: section (backward compatibility)
    if not result['has_responses'] and re.search(r'RESPONSE:', doc_comment, re.IGNORECASE):
        result['has_responses'] = True

    return result


def validate_endpoint(endpoint: Dict, file_path: Path) -> List[DocIssue]:
    """Validate documentation for a single endpoint."""
    issues = []
    doc_check = check_structured_docs(endpoint['doc_comment'])

    # Check for @usage or free-form usage
    if not doc_check['has_usage']:
        issues.append(DocIssue(
            file=file_path.name,
            line=endpoint['line'],
            severity='error',
            category='missing_usage',
            message='Missing @usage section or USAGE: description',
            endpoint=endpoint['endpoint_str']
        ))

    # Check for @example or free-form examples
    if not doc_check['has_example']:
        issues.append(DocIssue(
            file=file_path.name,
            line=endpoint['line'],
            severity='error',
            category='missing_example',
            message='Missing @example block or EXAMPLES: section',
            endpoint=endpoint['endpoint_str']
        ))
    elif doc_check['example_count'] == 0:
        issues.append(DocIssue(
            file=file_path.name,
            line=endpoint['line'],
            severity='warning',
            category='insufficient_examples',
            message='Only has free-form EXAMPLES:, recommend adding @example blocks',
            endpoint=endpoint['endpoint_str']
        ))

    # Check for @response or free-form response docs
    if not doc_check['has_responses']:
        issues.append(DocIssue(
            file=file_path.name,
            line=endpoint['line'],
            severity='error',
            category='missing_responses',
            message='Missing @response tags or RESPONSE: documentation',
            endpoint=endpoint['endpoint_str']
        ))

    return issues


def check_migration_needed(content: str) -> Dict[str, int]:
    """
    Check if file uses free-form sections that need migration.

    Returns count of each free-form section type.
    """
    free_form_sections = {
        'PURPOSE:': 0,
        'USE CASES:': 0,
        'EXAMPLES:': 0,
        'RESPONSE:': 0,
        'REQUEST:': 0,
        'RATIONALE:': 0
    }

    for section in free_form_sections.keys():
        count = len(re.findall(rf'{re.escape(section)}', content, re.IGNORECASE))
        free_form_sections[section] = count

    return free_form_sections


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate TypeSpec documentation"
    )
    parser.add_argument(
        "typespec_dir",
        nargs="?",
        type=Path,
        default=Path(__file__).parent.parent.parent / 'typespec',
        help="Path to TypeSpec directory (default: typespec/)"
    )
    args = parser.parse_args()

    typespec_dir = args.typespec_dir

    if not typespec_dir.exists():
        print(f"❌ Directory not found: {typespec_dir}")
        sys.exit(1)

    print("📋 Validating TypeSpec Documentation\n")
    print(f"📁 Scanning: {typespec_dir}\n")

    # Find all TypeSpec files
    tsp_files = list(typespec_dir.glob('*.tsp'))

    all_issues = []
    migration_stats = {}

    for tsp_file in tsp_files:
        content = tsp_file.read_text()

        # Find endpoints
        endpoints = find_endpoints(content, tsp_file)

        # Validate each endpoint
        for endpoint in endpoints:
            issues = validate_endpoint(endpoint, tsp_file)
            all_issues.extend(issues)

        # Check if migration needed
        migration_stats[tsp_file.name] = check_migration_needed(content)

    # Sort issues by severity
    errors = [i for i in all_issues if i.severity == 'error']
    warnings = [i for i in all_issues if i.severity == 'warning']
    infos = [i for i in all_issues if i.severity == 'info']

    # Print results
    if errors:
        print("❌ ERRORS:\n")
        for issue in errors:
            print(issue)

    if warnings:
        print("⚠️  WARNINGS:\n")
        for issue in warnings:
            print(issue)

    if infos:
        print("ℹ️  INFO:\n")
        for issue in infos:
            print(issue)

    # Migration recommendations
    print("\n" + "=" * 70)
    print("📊 Migration Recommendations:\n")

    needs_migration = []
    for file_name, sections in migration_stats.items():
        total_free_form = sum(sections.values())
        if total_free_form > 0:
            needs_migration.append((file_name, total_free_form, sections))

    if needs_migration:
        print("Files with free-form sections that should be migrated:\n")
        for file_name, count, sections in sorted(needs_migration, key=lambda x: x[1], reverse=True):
            print(f"  {file_name}: {count} free-form sections")
            for section, section_count in sections.items():
                if section_count > 0:
                    print(f"    - {section} ({section_count})")
            print()

    # Summary
    print("=" * 70)
    print("📊 Summary:\n")
    print(f"   ❌ Errors:   {len(errors)}")
    print(f"   ⚠️  Warnings: {len(warnings)}")
    print(f"   ℹ️  Info:     {len(infos)}")
    print(f"   📄 Files:    {len(tsp_files)}")
    print(f"   🔍 Endpoints checked: {len([i for i in all_issues if i.endpoint])}")
    print()

    # Recommendations
    print("💡 Next Steps:\n")
    if errors or warnings:
        print("1. Run migration tool to convert free-form sections:")
        print("   python scripts/migration/migrate-typespec-docs.py")
        print()
        print("2. Review and validate migrated documentation")
        print()
        print("3. Re-run this validation script")
    else:
        print("✅ All TypeSpec files have structured documentation!")
    print()

    # Exit code
    if errors:
        print("❌ TypeSpec documentation validation FAILED")
        sys.exit(1)
    elif warnings:
        print("⚠️  TypeSpec documentation validation passed with warnings")
        sys.exit(0)
    else:
        print("✅ TypeSpec documentation validation PASSED")
        sys.exit(0)


if __name__ == '__main__':
    main()
