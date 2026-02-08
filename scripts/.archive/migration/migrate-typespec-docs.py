#!/usr/bin/env python3
"""
Migrate TypeSpec Documentation to Structured Format

Converts free-form documentation sections to structured @tag format:
- PURPOSE: → @usage
- USE CASES: → @usage (appended)
- EXAMPLES: → @example blocks
- RESPONSE: → @response tags
- REQUEST: → @param tags
- RATIONALE: → @usage (appended)

Usage:
    python migrate-typespec-docs.py [--file FILE] [--dry-run]

Options:
    --file FILE    Migrate specific file (default: all files in typespec/)
    --dry-run      Show what would be changed without modifying files
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import shutil


@dataclass
class MigrationResult:
    """Result of migrating a single comment."""
    original: str
    migrated: str
    sections_migrated: Dict[str, int]
    warnings: List[str]


@dataclass
class FileMigrationResult:
    """Result of migrating a file."""
    file_path: Path
    comments_migrated: int
    sections_migrated: Dict[str, int]
    warnings: List[str]
    success: bool
    error: str = ""


def extract_doc_comments(content: str) -> List[Tuple[int, int, str]]:
    """
    Extract all documentation comments from TypeSpec content.

    Returns list of (start_pos, end_pos, comment_text) tuples.
    """
    comments = []

    # Pattern to match /** ... */ style comments
    pattern = r'/\*\*(.*?)\*/'

    for match in re.finditer(pattern, content, re.DOTALL):
        start_pos = match.start()
        end_pos = match.end()
        comment_text = match.group(0)
        comments.append((start_pos, end_pos, comment_text))

    return comments


def parse_free_form_sections(comment: str) -> Dict[str, str]:
    """
    Parse free-form sections from documentation comment.

    Extracts sections like:
    - PURPOSE:
    - USE CASES:
    - EXAMPLES:
    - RESPONSE:
    - REQUEST:
    - RATIONALE:
    """
    sections = {}

    # Remove comment markers for easier parsing
    lines = []
    for line in comment.split('\n'):
        line = line.strip()
        if line.startswith('/**'):
            line = line[3:].strip()
        elif line.startswith('*/'):
            line = line[2:].strip()
        elif line.startswith('*'):
            line = line[1:].strip()
        if line.endswith('*/'):
            line = line[:-2].strip()
        lines.append(line)

    content = '\n'.join(lines)

    # Pattern to match section headers (all caps followed by colon)
    # Common sections: PURPOSE:, USE CASES:, EXAMPLES:, RESPONSE:, REQUEST:, RATIONALE:
    section_pattern = r'(?:^|\n)([A-Z][A-Z\s]+?):\s*\n((?:(?![A-Z][A-Z\s]+:).*\n?)*)'

    for match in re.finditer(section_pattern, content, re.MULTILINE):
        section_name = match.group(1).strip()
        section_content = match.group(2).strip()

        # Only capture known sections
        known_sections = [
            'PURPOSE', 'USE CASES', 'EXAMPLES', 'RESPONSE', 'REQUEST',
            'RATIONALE', 'EXAMPLE', 'USAGE', 'WHY', 'DESIGN',
            'INSPIRED BY', 'ALIGNMENT WITH', 'DIFFERENCES FROM',
            'COMPATIBILITY NOTES', 'A2A', 'MODIFICATIONS', 'EXTENSIBILITY'
        ]

        if any(section_name.startswith(known) for known in known_sections):
            sections[section_name] = section_content

    return sections


def extract_examples_from_section(examples_text: str) -> List[Tuple[str, str, str]]:
    """
    Extract individual examples from EXAMPLES: section.

    Returns list of (title, language, code) tuples.
    """
    examples = []

    # Pattern to match "Example N: Title" followed by code block
    example_pattern = r'Example\s+\d+:\s*([^\n]+)\n```(\w*)\n(.*?)```'

    for match in re.finditer(example_pattern, examples_text, re.DOTALL):
        title = match.group(1).strip()
        language = match.group(2) or 'http'
        code = match.group(3).strip()
        examples.append((title, language, code))

    # If no structured examples found, try to extract code blocks without titles
    if not examples:
        code_block_pattern = r'```(\w*)\n(.*?)```'
        for i, match in enumerate(re.finditer(code_block_pattern, examples_text, re.DOTALL), 1):
            language = match.group(1) or 'http'
            code = match.group(2).strip()
            title = f"Example {i}"
            examples.append((title, language, code))

    return examples


def extract_responses_from_section(response_text: str) -> List[Tuple[str, str]]:
    """
    Extract response codes and descriptions from RESPONSE: section.

    Returns list of (code, description) tuples.
    """
    responses = []

    # Pattern to match "- 200 OK: Description" or "200 OK: Description"
    response_pattern = r'(?:^|\n)\s*-?\s*(\d{3})\s+([A-Z][A-Za-z\s]+):\s*([^\n]+)'

    for match in re.finditer(response_pattern, response_text, re.MULTILINE):
        code = match.group(1)
        status_text = match.group(2).strip()
        description = match.group(3).strip()
        full_desc = f"{status_text}\n{description}"
        responses.append((code, full_desc))

    return responses


def migrate_comment(comment: str) -> MigrationResult:
    """
    Migrate a single documentation comment to structured format.

    Converts free-form sections to @tags.
    """
    original = comment
    sections = parse_free_form_sections(comment)
    warnings = []
    sections_migrated = {}

    # If no free-form sections found, return unchanged
    if not sections:
        return MigrationResult(
            original=original,
            migrated=original,
            sections_migrated={},
            warnings=[]
        )

    # Extract the first line (summary) before any sections
    lines = []
    for line in comment.split('\n'):
        line_stripped = line.strip()
        if line_stripped.startswith('/**'):
            line_stripped = line_stripped[3:].strip()
        elif line_stripped.startswith('*/'):
            break
        elif line_stripped.startswith('*'):
            line_stripped = line_stripped[1:].strip()

        # Stop at first section header
        if line_stripped and any(line_stripped.startswith(f"{s}:") for s in ['PURPOSE', 'USE CASES', 'EXAMPLES', 'RESPONSE', 'REQUEST']):
            break

        if line_stripped:
            lines.append(line_stripped)

    summary = lines[0] if lines else "TODO: Add summary"

    # Build new structured comment
    new_lines = ["/**", f" * {summary}", " *"]

    # Build @usage section from PURPOSE, USE CASES, RATIONALE
    usage_parts = []

    if 'PURPOSE' in sections:
        usage_parts.append(sections['PURPOSE'])
        sections_migrated['PURPOSE'] = 1

    if 'USE CASES' in sections:
        use_cases = sections['USE CASES']
        usage_parts.append(f"\nUse Cases:\n{use_cases}")
        sections_migrated['USE CASES'] = 1

    if 'RATIONALE' in sections:
        rationale = sections['RATIONALE']
        usage_parts.append(f"\nRationale:\n{rationale}")
        sections_migrated['RATIONALE'] = 1

    # Add other contextual sections to usage
    for section_name in ['INSPIRED BY', 'ALIGNMENT WITH', 'DIFFERENCES FROM', 'WHY', 'DESIGN']:
        if section_name in sections:
            content = sections[section_name]
            usage_parts.append(f"\n{section_name}:\n{content}")
            sections_migrated[section_name] = 1

    if usage_parts:
        new_lines.append(" * @usage")
        usage_text = '\n\n'.join(usage_parts)
        for line in usage_text.split('\n'):
            new_lines.append(f" * {line}" if line else " *")
        new_lines.append(" *")

    # Convert EXAMPLES section to @example blocks
    if 'EXAMPLES' in sections or 'EXAMPLE' in sections:
        examples_text = sections.get('EXAMPLES') or sections.get('EXAMPLE')
        examples = extract_examples_from_section(examples_text)

        if examples:
            for title, language, code in examples:
                new_lines.append(f" * @example {title}")
                new_lines.append(f" * ```{language}")
                for code_line in code.split('\n'):
                    new_lines.append(f" * {code_line}")
                new_lines.append(" * ```")
                new_lines.append(" *")
            sections_migrated['EXAMPLES'] = len(examples)
        else:
            # Couldn't parse structured examples, keep original
            warnings.append("Could not parse EXAMPLES section into structured @example blocks")
            new_lines.append(" * EXAMPLES:")
            for line in examples_text.split('\n'):
                new_lines.append(f" * {line}" if line else " *")
            new_lines.append(" *")

    # Convert RESPONSE section to @response tags
    if 'RESPONSE' in sections:
        response_text = sections['RESPONSE']
        responses = extract_responses_from_section(response_text)

        if responses:
            for code, description in responses:
                new_lines.append(f" * @response {code} {description.split(chr(10))[0]}")
                # Add continuation lines if description has multiple lines
                desc_lines = description.split('\n')[1:]
                for desc_line in desc_lines:
                    if desc_line.strip():
                        new_lines.append(f" * {desc_line.strip()}")
                new_lines.append(" *")
            sections_migrated['RESPONSE'] = len(responses)
        else:
            # Couldn't parse responses, keep original
            warnings.append("Could not parse RESPONSE section into @response tags")
            new_lines.append(" * RESPONSE:")
            for line in response_text.split('\n'):
                new_lines.append(f" * {line}" if line else " *")
            new_lines.append(" *")

    # Keep other sections that don't have clear mappings
    preserve_sections = ['REQUEST', 'BASE', 'SOURCE', 'FROM', 'MODIFICATIONS',
                        'EXTENSIBILITY', 'COMPATIBILITY NOTES', 'A2A']
    for section_name, content in sections.items():
        if any(section_name.startswith(preserve) for preserve in preserve_sections):
            new_lines.append(f" * {section_name}:")
            for line in content.split('\n'):
                new_lines.append(f" * {line}" if line else " *")
            new_lines.append(" *")

    new_lines.append(" */")

    migrated = '\n'.join(new_lines)

    return MigrationResult(
        original=original,
        migrated=migrated,
        sections_migrated=sections_migrated,
        warnings=warnings
    )


def migrate_file(file_path: Path, dry_run: bool = False) -> FileMigrationResult:
    """
    Migrate all documentation comments in a TypeSpec file.

    Returns FileMigrationResult with statistics and any errors.
    """
    try:
        content = file_path.read_text()
        original_content = content

        # Extract all doc comments
        comments = extract_doc_comments(content)

        if not comments:
            return FileMigrationResult(
                file_path=file_path,
                comments_migrated=0,
                sections_migrated={},
                warnings=[],
                success=True
            )

        # Migrate each comment (in reverse order to preserve positions)
        all_sections = {}
        all_warnings = []
        migrated_count = 0

        for start_pos, end_pos, comment_text in reversed(comments):
            result = migrate_comment(comment_text)

            # Only replace if sections were migrated
            if result.sections_migrated:
                content = content[:start_pos] + result.migrated + content[end_pos:]
                migrated_count += 1

                # Aggregate statistics
                for section, count in result.sections_migrated.items():
                    all_sections[section] = all_sections.get(section, 0) + count

                all_warnings.extend(result.warnings)

        # Write back to file if not dry run
        if not dry_run and migrated_count > 0:
            # Create backup
            backup_path = file_path.with_suffix(file_path.suffix + '.backup')
            shutil.copy2(file_path, backup_path)

            # Write migrated content
            file_path.write_text(content)

        return FileMigrationResult(
            file_path=file_path,
            comments_migrated=migrated_count,
            sections_migrated=all_sections,
            warnings=all_warnings,
            success=True
        )

    except Exception as e:
        return FileMigrationResult(
            file_path=file_path,
            comments_migrated=0,
            sections_migrated={},
            warnings=[],
            success=False,
            error=str(e)
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate TypeSpec documentation to structured format')
    parser.add_argument('--file', type=str, help='Specific file to migrate')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without modifying files')
    args = parser.parse_args()

    # Determine files to migrate
    if args.file:
        files = [Path(args.file)]
    else:
        typespec_dir = Path(__file__).parent.parent.parent / 'typespec'
        files = list(typespec_dir.glob('*.tsp'))

    print("📝 TypeSpec Documentation Migration\n")
    if args.dry_run:
        print("🔍 DRY RUN - No files will be modified\n")
    print(f"📁 Files to migrate: {len(files)}\n")

    # Migrate each file
    results = []
    for file_path in files:
        print(f"Processing {file_path.name}...", end=" ")
        result = migrate_file(file_path, dry_run=args.dry_run)
        results.append(result)

        if result.success:
            if result.comments_migrated > 0:
                print(f"✓ {result.comments_migrated} comments migrated")
            else:
                print("○ No changes needed")
        else:
            print(f"✗ Error: {result.error}")

    # Print summary
    print("\n" + "=" * 70)
    print("📊 Migration Summary:\n")

    total_comments = sum(r.comments_migrated for r in results)
    total_sections = {}
    total_warnings = []

    for result in results:
        for section, count in result.sections_migrated.items():
            total_sections[section] = total_sections.get(section, 0) + count
        total_warnings.extend(result.warnings)

    print(f"Comments migrated: {total_comments}")
    print(f"Sections migrated: {sum(total_sections.values())}")
    print()

    if total_sections:
        print("Sections converted:")
        for section, count in sorted(total_sections.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {section}: {count}")
        print()

    if total_warnings:
        print(f"⚠️  Warnings: {len(total_warnings)}")
        for warning in set(total_warnings):  # Deduplicate
            print(f"  - {warning}")
        print()

    # Files modified
    files_modified = [r for r in results if r.comments_migrated > 0]
    if files_modified and not args.dry_run:
        print("Files modified:")
        for result in files_modified:
            backup = result.file_path.with_suffix(result.file_path.suffix + '.backup')
            print(f"  ✓ {result.file_path.name} (backup: {backup.name})")
        print()

    # Next steps
    print("=" * 70)
    print("💡 Next Steps:\n")

    if args.dry_run:
        print("1. Review the changes above")
        print("2. Run without --dry-run to apply changes")
        print("3. Review migrated files")
        print("4. Run validation: python scripts/validation/validate-typespec-docs.py")
    else:
        print("1. Review migrated files")
        print("2. Run validation: python scripts/validation/validate-typespec-docs.py")
        print("3. Test generation: python scripts/generation/generate-api-reference.py")
        print("4. If satisfied, delete .backup files")
        print("5. Commit changes to version control")
    print()

    if total_comments > 0:
        print(f"✅ Migration {'would modify' if args.dry_run else 'completed'}: {total_comments} comments, {sum(total_sections.values())} sections")
    else:
        print("ℹ️  No comments needed migration")

    sys.exit(0)


if __name__ == '__main__':
    main()
