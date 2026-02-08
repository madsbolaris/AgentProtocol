#!/usr/bin/env python3
"""
Validate the quality of generated API reference documentation.

This script checks for:
- TypeSpec metadata pollution
- Missing manual content
- Structural issues
- Empty or placeholder content
- Formatting problems
- Documentation completeness
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Represents a validation issue found in documentation."""
    severity: str  # 'error', 'warning', 'info'
    file: str
    line: int
    message: str
    context: str = ""


class APIReferenceValidator:
    """Validate generated API reference documentation quality."""

    def __init__(self, api_ref_dir: str):
        self.api_ref_dir = Path(api_ref_dir)
        self.issues: List[ValidationIssue] = []

    def validate_all(self):
        """Run all validation checks."""
        print("🔍 Validating API Reference Documentation...\n")

        # Find all markdown files
        md_files = list(self.api_ref_dir.glob("**/*.md"))

        for md_file in md_files:
            self._validate_file(md_file)

        # Print results
        self._print_results()

        # Return exit code
        error_count = sum(1 for issue in self.issues if issue.severity == 'error')
        return 1 if error_count > 0 else 0

    def _validate_file(self, file_path: Path):
        """Validate a single markdown file."""
        rel_path = file_path.relative_to(self.api_ref_dir)
        content = file_path.read_text()
        lines = content.split('\n')

        # Skip README files from some checks
        is_readme = file_path.name == 'README.md'

        # Run checks
        self._check_metadata_pollution(rel_path, lines)

        if not is_readme:
            self._check_empty_descriptions(rel_path, lines)
            self._check_manual_content_presence(rel_path, content, lines)
            self._check_endpoint_samples(rel_path, content, lines)
            self._check_endpoint_descriptions(rel_path, content, lines)
            self._check_model_descriptions(rel_path, content, lines)
            self._check_duplicate_content(rel_path, lines)
            self._check_broken_structure(rel_path, lines)
            self._check_placeholder_content(rel_path, lines)
            self._check_incomplete_lists(rel_path, lines)

    def _check_metadata_pollution(self, file_path: Path, lines: List[str]):
        """Check for TypeSpec metadata that shouldn't be in user docs."""
        metadata_patterns = [
            'BASE:', 'SOURCE:', 'FROM:', 'RATIONALE:', 'ALIGNED WITH:',
            'MESSAGING APP PATTERN:', 'MESSAGING APP PATTERNS:',
            'MAF PATTERN:', 'M365:', 'A2A', 'EXTENSIBILITY:',
            'SEMANTIC DISTINCTION:', 'BEHAVIORAL IMPACT:',
            'CREATED:', 'DELETED:', 'INSPIRED BY:', 'DESIGN:',
            'WHY:', 'MODIFICATIONS:', 'ADDITION:', 'REPRESENTS:',
            'MODIFICATION:', 'SUPPORTS:', 'STREAMING INPUT PATTERNS:',
            'TRANSPORT LAYER:', 'IMPLEMENTATION NOTE:', 'DESIGN NOTE:'
        ]

        for i, line in enumerate(lines, 1):
            for pattern in metadata_patterns:
                if pattern in line:
                    # Ignore if in code blocks
                    if self._in_code_block(lines, i - 1):
                        continue

                    self.issues.append(ValidationIssue(
                        severity='error',
                        file=str(file_path),
                        line=i,
                        message=f"TypeSpec metadata pollution: '{pattern}' found in user documentation",
                        context=line.strip()[:80]
                    ))

    def _check_empty_descriptions(self, file_path: Path, lines: List[str]):
        """Check for parameter tables with empty descriptions."""
        in_param_table = False
        empty_count = 0
        table_start_line = 0

        for i, line in enumerate(lines, 1):
            # Detect parameter table headers
            if '| Parameter | Type | Required | Description |' in line:
                in_param_table = True
                table_start_line = i
                empty_count = 0
                continue

            if in_param_table:
                # End of table
                if line.strip() and not line.strip().startswith('|'):
                    in_param_table = False
                    # Report if more than 3 empty descriptions in a table
                    if empty_count > 3:
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            file=str(file_path),
                            line=table_start_line,
                            message=f"Parameter table has {empty_count} empty descriptions - consider adding parameter documentation",
                            context=""
                        ))
                    continue

                # Check for empty description (ends with | |)
                if line.strip().endswith('| |'):
                    empty_count += 1

    def _check_manual_content_presence(self, file_path: Path, content: str, lines: List[str]):
        """Check if operations files have manual content (examples, use cases)."""
        # Only check operations files, but exclude operations.md (consolidated reference)
        if not self._is_operations_file(content) or file_path.name == 'operations.md':
            return

        has_manual = 'MANUAL_START' in content
        endpoint_count = len(re.findall(r'^## (GET|POST|PUT|PATCH|DELETE) /', content, re.MULTILINE))

        if endpoint_count > 0 and not has_manual:
            self.issues.append(ValidationIssue(
                severity='error',
                file=str(file_path),
                line=1,
                message=f"Operations file with {endpoint_count} endpoints has NO manual content (examples, use cases)",
                context=""
            ))
        elif has_manual:
            # Check if manual content is sufficient
            manual_sections = len(re.findall(r'<!-- MANUAL_START:', content))
            if manual_sections < endpoint_count * 0.3:  # At least 30% coverage
                self.issues.append(ValidationIssue(
                    severity='warning',
                    file=str(file_path),
                    line=1,
                    message=f"Low manual content coverage: {manual_sections} sections for {endpoint_count} endpoints",
                    context=""
                ))

    def _check_endpoint_samples(self, file_path: Path, content: str, lines: List[str]):
        """Check that endpoints have examples/samples."""
        # Only check operations files, but exclude operations.md (consolidated reference)
        if not self._is_operations_file(content) or file_path.name == 'operations.md':
            return

        # Find all endpoints
        endpoints = []
        for i, line in enumerate(lines, 1):
            match = re.match(r'^## (GET|POST|PUT|PATCH|DELETE) /(.+)$', line)
            if match:
                endpoints.append((i, f"{match.group(1)} /{match.group(2)}"))

        # Check if each endpoint has examples in following lines
        for line_num, endpoint in endpoints:
            # Look for examples in next 200 lines
            has_example = False
            example_keywords = ['Example', 'example', '```http', '```json', 'Sample', 'sample']

            for i in range(line_num, min(line_num + 200, len(lines))):
                # Stop at next endpoint
                if i > line_num and re.match(r'^## (GET|POST|PUT|PATCH|DELETE) /', lines[i]):
                    break

                # Check for example keywords
                if any(keyword in lines[i] for keyword in example_keywords):
                    has_example = True
                    break

            if not has_example:
                self.issues.append(ValidationIssue(
                    severity='error',
                    file=str(file_path),
                    line=line_num,
                    message=f"Endpoint '{endpoint}' has no examples or code samples",
                    context=""
                ))

    def _check_endpoint_descriptions(self, file_path: Path, content: str, lines: List[str]):
        """Check that endpoints have meaningful descriptions."""
        # Only check operations files, but exclude operations.md (consolidated reference)
        if not self._is_operations_file(content) or file_path.name == 'operations.md':
            return

        # Find all endpoints
        for i, line in enumerate(lines, 1):
            match = re.match(r'^## (GET|POST|PUT|PATCH|DELETE) /(.+)$', line)
            if match:
                endpoint = f"{match.group(1)} /{match.group(2)}"

                # Look for description in next few lines (skip blank lines)
                description_found = False
                description_line = None
                description_text = None

                for j in range(i, min(i + 5, len(lines))):
                    check_line = lines[j].strip()

                    # Skip blank lines
                    if not check_line:
                        continue

                    # Stop at next section marker
                    if check_line.startswith('###') or check_line == '---':
                        break

                    # Found description
                    description_found = True
                    description_line = j + 1
                    description_text = check_line
                    break

                if not description_found:
                    self.issues.append(ValidationIssue(
                        severity='error',
                        file=str(file_path),
                        line=i,
                        message=f"Endpoint '{endpoint}' has no description",
                        context=""
                    ))
                elif description_text and len(description_text) < 10:
                    self.issues.append(ValidationIssue(
                        severity='warning',
                        file=str(file_path),
                        line=description_line,
                        message=f"Endpoint '{endpoint}' has very short description: '{description_text}'",
                        context=description_text
                    ))

    def _check_model_descriptions(self, file_path: Path, content: str, lines: List[str]):
        """Check that models and their properties have descriptions."""
        # Only check files that define models (have property tables)
        if 'models.md' not in str(file_path) and 'content-types.md' not in str(file_path):
            return

        # Find model definitions (## ModelName)
        for i, line in enumerate(lines, 1):
            match = re.match(r'^## ([A-Z][a-zA-Z]+)$', line)
            if match:
                model_name = match.group(1)

                # Check if next line has a description
                if i < len(lines):
                    next_line = lines[i].strip()

                    # Empty or immediately starts property table
                    if not next_line or next_line.startswith('|'):
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            file=str(file_path),
                            line=i,
                            message=f"Model '{model_name}' has no description",
                            context=""
                        ))
                    # Very short description
                    elif len(next_line) < 10 and not next_line.startswith('#'):
                        self.issues.append(ValidationIssue(
                            severity='info',
                            file=str(file_path),
                            line=i + 1,
                            message=f"Model '{model_name}' has very short description: '{next_line}'",
                            context=next_line
                        ))

    def _check_duplicate_content(self, file_path: Path, lines: List[str]):
        """Check for duplicate sections or repeated content."""
        seen_headings = {}

        # Standard section names that are expected to repeat
        standard_sections = {
            'Path Parameters', 'Query Parameters', 'Request Body', 'Response',
            'Headers', 'Example', 'Examples', 'Use Cases', 'Description'
        }

        for i, line in enumerate(lines, 1):
            # Check for duplicate h2/h3 headings
            match = re.match(r'^(#{2,3}) (.+)$', line)
            if match:
                heading = match.group(2).strip()

                # Skip standard section names
                if heading in standard_sections:
                    continue

                if heading in seen_headings:
                    # Allow duplicate headings in different MANUAL sections
                    if not (self._in_manual_section(lines, i - 1) and
                           self._in_manual_section(lines, seen_headings[heading] - 1)):
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            file=str(file_path),
                            line=i,
                            message=f"Duplicate heading: '{heading}' (also at line {seen_headings[heading]})",
                            context=line.strip()[:80]
                        ))
                seen_headings[heading] = i

    def _check_broken_structure(self, file_path: Path, lines: List[str]):
        """Check for structural issues in the documentation."""
        in_generated = False
        generated_ended = False
        last_separator_line = 0

        for i, line in enumerate(lines, 1):
            # Check for GENERATED markers
            if '<!-- GENERATED_START -->' in line:
                in_generated = True
            elif '<!-- GENERATED_END -->' in line:
                in_generated = False
                generated_ended = True

            # Track --- separators (endpoints end with these)
            if line.strip() == '---':
                last_separator_line = i

            # Check for manual content NOT after a separator
            # Manual content should only appear after --- separators in operations files
            if in_generated and 'MANUAL_START' in line:
                # Check if this is an operations file
                is_operations = self._is_operations_file('\n'.join(lines))

                if is_operations:
                    # In operations files, MANUAL_START should come after a --- separator
                    # Allow some lines between --- and MANUAL_START for spacing
                    if last_separator_line == 0 or (i - last_separator_line) > 5:
                        self.issues.append(ValidationIssue(
                            severity='error',
                            file=str(file_path),
                            line=i,
                            message="MANUAL_START not after endpoint separator (---) - manual content should follow endpoint definitions",
                            context=line.strip()[:80]
                        ))

            # Check for mismatched MANUAL markers
            if 'MANUAL_START' in line:
                match = re.search(r'MANUAL_START: (\w+)', line)
                if match:
                    section_name = match.group(1)
                    # Look for matching END marker
                    end_found = False
                    for j in range(i, min(i + 500, len(lines))):  # Search next 500 lines
                        if f'MANUAL_END: {section_name}' in lines[j]:
                            end_found = True
                            break
                    if not end_found:
                        self.issues.append(ValidationIssue(
                            severity='error',
                            file=str(file_path),
                            line=i,
                            message=f"MANUAL_START: {section_name} has no matching MANUAL_END",
                            context=line.strip()[:80]
                        ))

    def _check_placeholder_content(self, file_path: Path, lines: List[str]):
        """Check for placeholder or TODO content."""
        placeholder_patterns = [
            (r'\bTODO\b', 'TODO comment found'),
            (r'\bFIXME\b', 'FIXME comment found'),
            (r'\bXXX\b', 'XXX placeholder found'),
            (r'\[Coming soon\]', 'Coming soon placeholder'),
            (r'\[To be documented\]', 'To be documented placeholder'),
        ]

        for i, line in enumerate(lines, 1):
            # Skip code blocks
            if self._in_code_block(lines, i - 1):
                continue

            for pattern, message in placeholder_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.issues.append(ValidationIssue(
                        severity='info',
                        file=str(file_path),
                        line=i,
                        message=message,
                        context=line.strip()[:80]
                    ))

    def _check_incomplete_lists(self, file_path: Path, lines: List[str]):
        """Check for numbered lists that start at 2 or have gaps."""
        for i, line in enumerate(lines, 1):
            # Skip code blocks
            if self._in_code_block(lines, i - 1):
                continue

            # Check for numbered list starting at 2 or higher
            match = re.match(r'^(\s*)(\d+)\.\s+', line)
            if match:
                indent = match.group(1)
                number = int(match.group(2))

                # If starting at 2 or higher, check if item 1 exists
                if number >= 2:
                    # Look back for item 1 at same indent level
                    found_previous = False
                    for j in range(i - 2, max(0, i - 20), -1):  # Look back up to 20 lines
                        prev_match = re.match(r'^(\s*)(\d+)\.\s+', lines[j])
                        if prev_match and prev_match.group(1) == indent:
                            prev_number = int(prev_match.group(2))
                            if prev_number == number - 1:
                                found_previous = True
                                break

                    if not found_previous and number == 2:
                        self.issues.append(ValidationIssue(
                            severity='warning',
                            file=str(file_path),
                            line=i,
                            message=f"Numbered list starts at {number} without preceding item 1",
                            context=line.strip()[:80]
                        ))

    def _is_operations_file(self, content: str) -> bool:
        """Check if file contains endpoint definitions."""
        return bool(re.search(r'^## (GET|POST|PUT|PATCH|DELETE) /', content, re.MULTILINE))

    def _in_code_block(self, lines: List[str], line_index: int) -> bool:
        """Check if a line is inside a code block."""
        code_block_count = 0
        for i in range(line_index):
            if lines[i].strip().startswith('```'):
                code_block_count += 1
        return code_block_count % 2 == 1

    def _in_manual_section(self, lines: List[str], line_index: int) -> bool:
        """Check if a line is inside a MANUAL section."""
        manual_depth = 0
        for i in range(line_index):
            if 'MANUAL_START' in lines[i]:
                manual_depth += 1
            elif 'MANUAL_END' in lines[i]:
                manual_depth -= 1
        return manual_depth > 0

    def _print_results(self):
        """Print validation results."""
        if not self.issues:
            print("✅ All validation checks passed!\n")
            return

        # Group issues by severity
        errors = [i for i in self.issues if i.severity == 'error']
        warnings = [i for i in self.issues if i.severity == 'warning']
        infos = [i for i in self.issues if i.severity == 'info']

        # Print summary
        print(f"📊 Validation Results:")
        print(f"   ❌ Errors:   {len(errors)}")
        print(f"   ⚠️  Warnings: {len(warnings)}")
        print(f"   ℹ️  Info:     {len(infos)}")
        print()

        # Print errors
        if errors:
            print("❌ ERRORS:\n")
            for issue in errors:
                print(f"  {issue.file}:{issue.line}")
                print(f"    {issue.message}")
                if issue.context:
                    print(f"    → {issue.context}")
                print()

        # Print warnings
        if warnings:
            print("⚠️  WARNINGS:\n")
            for issue in warnings:
                print(f"  {issue.file}:{issue.line}")
                print(f"    {issue.message}")
                if issue.context:
                    print(f"    → {issue.context}")
                print()

        # Print info (only first 5)
        if infos:
            print(f"ℹ️  INFO ({len(infos)} items, showing first 5):\n")
            for issue in infos[:5]:
                print(f"  {issue.file}:{issue.line}")
                print(f"    {issue.message}")
                if issue.context:
                    print(f"    → {issue.context}")
                print()


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent
    api_ref_dir = project_root / "api-reference"

    if not api_ref_dir.exists():
        print(f"❌ API reference directory not found: {api_ref_dir}")
        return 1

    validator = APIReferenceValidator(api_ref_dir)
    return validator.validate_all()


if __name__ == "__main__":
    exit(main())
