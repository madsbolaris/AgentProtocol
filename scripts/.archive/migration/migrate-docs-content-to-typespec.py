#!/usr/bin/env python3
"""
Migrate docs-content to TypeSpec

Extracts documentation from docs-content/operations/*.md files and adds it
to the corresponding TypeSpec endpoints as @usage, @example, and @response tags.

Usage:
    python migrate-docs-content-to-typespec.py [--dry-run]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


def parse_docs_content_file(file_path: Path) -> Dict[str, any]:
    """
    Parse a docs-content markdown file and extract structured information.

    Returns dict with:
    - endpoint: method and path
    - purpose: purpose description
    - use_cases: list of use cases
    - responses: dict of status code -> description
    - examples: list of example blocks
    """
    content = file_path.read_text()

    result = {
        'endpoint': '',
        'purpose': '',
        'use_cases': [],
        'responses': {},
        'examples': [],
        'full_content': content
    }

    # Extract endpoint from title (# GET /path or # POST /path)
    title_match = re.search(r'^#\s+(GET|POST|PUT|PATCH|DELETE)\s+(/[^\n]+)', content, re.MULTILINE)
    if title_match:
        result['endpoint'] = f"{title_match.group(1)} {title_match.group(2)}"

    # Extract Purpose
    purpose_match = re.search(r'\*\*Purpose\*\*:\s*(.+?)(?=\n\n|\*\*)', content, re.DOTALL | re.IGNORECASE)
    if purpose_match:
        result['purpose'] = purpose_match.group(1).strip()

    # Extract Use Cases
    use_cases_match = re.search(r'\*\*Use Cases\*\*:\s*\n((?:^-\s+.+$\n?)+)', content, re.MULTILINE | re.IGNORECASE)
    if use_cases_match:
        use_cases_text = use_cases_match.group(1)
        result['use_cases'] = [line.strip('- ').strip() for line in use_cases_text.split('\n') if line.strip().startswith('-')]

    # Extract Responses
    response_pattern = r'-\s+\*\*(\d{3})\s+([^:]+)\*\*:\s*(.+?)(?=\n-|\n\n|\*\*|$)'
    for match in re.finditer(response_pattern, content, re.DOTALL):
        code = match.group(1)
        status = match.group(2).strip()
        description = match.group(3).strip()
        result['responses'][code] = f"{status}\n{description}"

    # Extract Examples
    # Look for code blocks with optional titles
    example_pattern = r'(?:^|\n)(?:\*\*Example[^*]*\*\*[:\-\s]*|Step \d+:[^\n]*\n)?```(\w+)\n(.*?)```'
    examples = []
    for i, match in enumerate(re.finditer(example_pattern, content, re.DOTALL), 1):
        language = match.group(1) or 'http'
        code = match.group(2).strip()

        # Try to find a title before the code block
        block_start = match.start()
        text_before = content[max(0, block_start-200):block_start]
        title_match = re.search(r'(?:\*\*Example[^*]*\*\*[:\-\s]*|Step \d+:)\s*([^\n]+)', text_before)
        title = title_match.group(1).strip() if title_match else f"Example {i}"

        examples.append({'title': title, 'language': language, 'code': code})

    result['examples'] = examples

    return result


def filename_to_endpoint(filename: str) -> str:
    """Convert filename to endpoint string: get-runs-runid.md -> GET /runs/{runId}"""
    # Remove .md extension
    name = filename.replace('.md', '')

    # Split by hyphens
    parts = name.split('-')

    # First part is the method
    method = parts[0].upper()

    # Rest is the path
    path_parts = parts[1:]

    # Convert path segments, replacing 'id' suffixes with {paramName}
    path_segments = []
    for i, part in enumerate(path_parts):
        if part.endswith('id'):
            # Convert threadid -> {threadId}, runid -> {runId}
            param_name = part[:-2] + 'Id'
            path_segments.append(f"{{{param_name}}}")
        else:
            path_segments.append(part)

    path = '/' + '/'.join(path_segments)

    return f"{method} {path}"


def find_endpoint_in_typespec(typespec_content: str, endpoint: str) -> Tuple[int, int]:
    """
    Find the location of an endpoint's doc comment in TypeSpec content.

    Returns (start_pos, end_pos) of the /** ... */ comment, or (-1, -1) if not found.
    """
    method, path = endpoint.split(' ', 1)
    method_lower = method.lower()

    # Pattern to find the operation
    # Look for @doc comment followed by @method decorator
    pattern = rf'/\*\*(.*?)\*/\s*(?:@doc[^)]*\)\s*)?@{method_lower}\s+(?:@segment[^)]*\)\s*)?(\w+)\s*\('

    matches = list(re.finditer(pattern, typespec_content, re.DOTALL))

    # Try to match by path or operation name
    for match in matches:
        comment_start = match.start()
        comment_end = match.start() + len(match.group(0))
        doc_comment = match.group(1)
        operation_name = match.group(2)

        # Check if path matches in the doc comment or nearby
        context = typespec_content[max(0, comment_start-500):min(len(typespec_content), comment_end+500)]
        if path in context or path.replace('{', '').replace('}', '') in context:
            # Found it - return the position of the /** comment
            return (comment_start, comment_start + len(match.group(0).split('*/')[0]) + 2)

    return (-1, -1)


def generate_structured_doc(data: Dict) -> str:
    """Generate structured TypeSpec documentation from extracted data."""
    lines = ["/**"]

    # Summary (from title or purpose)
    summary = data.get('purpose', '').split('.')[0] if data.get('purpose') else ''
    if summary:
        lines.append(f" * {summary}")
        lines.append(" *")

    # @usage section
    if data.get('purpose') or data.get('use_cases'):
        lines.append(" * @usage")
        if data.get('purpose'):
            lines.append(f" * {data['purpose']}")
            lines.append(" *")

        if data.get('use_cases'):
            lines.append(" * Use Cases:")
            for use_case in data['use_cases']:
                lines.append(f" * - {use_case}")
            lines.append(" *")

    # @example blocks
    if data.get('examples'):
        for example in data['examples']:
            lines.append(f" * @example {example['title']}")
            lines.append(f" * ```{example['language']}")
            for code_line in example['code'].split('\n'):
                lines.append(f" * {code_line}")
            lines.append(" * ```")
            lines.append(" *")

    # @response tags
    if data.get('responses'):
        for code in sorted(data['responses'].keys(), key=int):
            desc_lines = data['responses'][code].split('\n')
            lines.append(f" * @response {code} {desc_lines[0]}")
            for desc_line in desc_lines[1:]:
                if desc_line.strip():
                    lines.append(f" * {desc_line.strip()}")
            lines.append(" *")

    lines.append(" */")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='Migrate docs-content to TypeSpec')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done')
    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    docs_content_dir = project_root / 'docs-content' / 'operations'
    typespec_dir = project_root / 'typespec'

    if not docs_content_dir.exists():
        print(f"❌ docs-content directory not found: {docs_content_dir}")
        sys.exit(1)

    print("📝 Migrating docs-content to TypeSpec\n")
    if args.dry_run:
        print("🔍 DRY RUN - No files will be modified\n")

    # Get all docs-content files
    doc_files = list(docs_content_dir.glob('*.md'))
    print(f"📁 Found {len(doc_files)} documentation files\n")

    migrated = 0
    skipped = 0
    errors = []

    for doc_file in doc_files:
        print(f"Processing {doc_file.name}...", end=" ")

        try:
            # Parse docs-content file
            data = parse_docs_content_file(doc_file)

            if not data['endpoint']:
                print("⚠️  Could not extract endpoint")
                skipped += 1
                continue

            # Find corresponding TypeSpec file and endpoint
            # Most endpoints are in routes.tsp
            typespec_file = typespec_dir / 'routes.tsp'

            if not typespec_file.exists():
                print(f"✗ TypeSpec file not found")
                errors.append(f"{doc_file.name}: routes.tsp not found")
                skipped += 1
                continue

            typespec_content = typespec_file.read_text()

            # Find endpoint in TypeSpec
            start_pos, end_pos = find_endpoint_in_typespec(typespec_content, data['endpoint'])

            if start_pos == -1:
                print(f"⚠️  Endpoint not found in TypeSpec")
                skipped += 1
                continue

            # Generate new structured doc
            new_doc = generate_structured_doc(data)

            # Replace old doc with new doc
            if not args.dry_run:
                new_content = typespec_content[:start_pos] + new_doc + typespec_content[end_pos:]
                typespec_file.write_text(new_content)

            print(f"✓ Migrated")
            migrated += 1

        except Exception as e:
            print(f"✗ Error: {e}")
            errors.append(f"{doc_file.name}: {e}")
            skipped += 1

    # Summary
    print("\n" + "=" * 70)
    print("📊 Migration Summary:\n")
    print(f"✅ Migrated: {migrated}")
    print(f"⚠️  Skipped:  {skipped}")
    print(f"❌ Errors:   {len(errors)}")

    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")

    print()
    if args.dry_run:
        print("💡 Run without --dry-run to apply changes")
    else:
        print("💡 Next steps:")
        print("1. Review migrated TypeSpec files")
        print("2. Run validation: python scripts/validation/validate-typespec-docs.py")
        print("3. Delete docs-content: rm -rf docs-content/")

    sys.exit(0 if migrated > 0 else 1)


if __name__ == '__main__':
    main()
