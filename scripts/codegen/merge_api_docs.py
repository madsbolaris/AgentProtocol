#!/usr/bin/env python3
"""
Merge auto-generated API documentation with manual overlays.

This script implements the hybrid documentation approach:
- Generated content: Auto-generated from TypeSpec (skeletons, parameters, models)
- Manual content: Human-written examples, use cases, best practices

The merge strategy interleaves manual content with generated content so that
examples and use cases appear right after the corresponding endpoint definition.
"""

import re
from pathlib import Path
from typing import List, Dict, Tuple


class DocMerger:
    """Merge generated and manual documentation with smart interleaving."""

    def __init__(self, generated_dir: str, manual_dir: str, output_dir: str):
        self.generated_dir = Path(generated_dir)
        self.manual_dir = Path(manual_dir)
        self.output_dir = Path(output_dir)

    def merge_all(self):
        """Merge all documentation files."""
        print("🔄 Merging generated and manual documentation...\n")

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find all generated markdown files
        generated_files = list(self.generated_dir.glob("**/*.md"))

        merged_count = 0
        for gen_file in generated_files:
            rel_path = gen_file.relative_to(self.generated_dir)
            manual_file = self.manual_dir / rel_path
            output_file = self.output_dir / rel_path

            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # Merge files
            if manual_file.exists():
                self._merge_file(gen_file, manual_file, output_file)
                print(f"✓ Merged: {rel_path}")
            else:
                # No manual overlay, just copy generated
                output_file.write_text(gen_file.read_text())
                print(f"  Copied: {rel_path} (no manual overlay)")

            merged_count += 1

        print(f"\n✅ Merged {merged_count} files\n")

    def _merge_file(self, gen_file: Path, manual_file: Path, output_file: Path):
        """Merge a single generated file with its manual overlay using smart interleaving."""
        gen_content = gen_file.read_text()
        manual_content = manual_file.read_text()

        # Check if this is an operations file (has ### endpoint sections)
        if self._is_operations_file(gen_content):
            merged = self._merge_operations_file(gen_content, manual_content)
        else:
            # For non-operations files (models, etc.), use simple append strategy
            merged = self._merge_simple(gen_content, manual_content)

        output_file.write_text(merged)

    def _is_operations_file(self, content: str) -> bool:
        """Check if this is an operations file with endpoint sections."""
        # Operations files have patterns like: ## GET /endpoint or ## POST /endpoint
        return bool(re.search(r'^## (GET|POST|PUT|PATCH|DELETE) /', content, re.MULTILINE))

    def _merge_operations_file(self, gen_content: str, manual_content: str) -> str:
        """Merge operations file by interleaving manual content after each endpoint."""
        lines = gen_content.split('\n')

        # Try new structure first (overview + examples)
        overview_sections = self._parse_manual_sections(manual_content, 'overview')
        examples_sections = self._parse_manual_sections(manual_content, 'examples')
        additional_sections = self._parse_manual_sections(manual_content, 'additional')

        # Fall back to old structure (content) if new structure not found
        has_new_structure = bool(overview_sections or examples_sections)
        if not has_new_structure:
            content_sections = self._parse_manual_sections(manual_content, 'content')
            # Treat old "content" sections as examples (after ---)
            examples_sections = content_sections

        merged_lines = []
        i = 0
        in_generated = False
        current_endpoint = None

        while i < len(lines):
            line = lines[i]

            # Detect GENERATED_START
            if '<!-- GENERATED_START -->' in line:
                in_generated = True
                merged_lines.append(line)
                i += 1
                continue

            # Detect GENERATED_END
            if '<!-- GENERATED_END -->' in line:
                in_generated = False
                merged_lines.append(line)
                merged_lines.append('')

                # After GENERATED_END, add any additional manual content
                if 'unmatched' in additional_sections and additional_sections['unmatched']:
                    merged_lines.append('<!-- MANUAL_START: additional -->')
                    merged_lines.append('')
                    merged_lines.extend(additional_sections['unmatched'])
                    merged_lines.append('')
                    merged_lines.append('<!-- MANUAL_END: additional -->')

                i += 1
                continue

            # If in generated section, detect endpoint headers
            if in_generated and re.match(r'^## (GET|POST|PUT|PATCH|DELETE) /', line):
                current_endpoint = line.strip()
                merged_lines.append(line)

                # Look ahead to process endpoint content
                j = i + 1
                inserted_overview = False

                while j < len(lines):
                    next_line = lines[j]

                    # Insert overview before first ### subsection (Request Body, Path Parameters, etc.)
                    if not inserted_overview and re.match(r'^### ', next_line):
                        if current_endpoint in overview_sections:
                            merged_lines.append('')
                            merged_lines.extend(overview_sections[current_endpoint])
                            merged_lines.append('')
                        inserted_overview = True

                    merged_lines.append(next_line)

                    # End of endpoint section - insert examples after ---
                    if next_line.strip() == '---':
                        if current_endpoint in examples_sections:
                            merged_lines.append('')
                            merged_lines.append(f'<!-- MANUAL_START: {self._endpoint_key(current_endpoint)} -->')
                            merged_lines.append('')
                            merged_lines.extend(examples_sections[current_endpoint])
                            merged_lines.append('')
                            merged_lines.append(f'<!-- MANUAL_END: {self._endpoint_key(current_endpoint)} -->')

                        i = j
                        break

                    j += 1

                    if j >= len(lines):
                        i = j - 1
                        break

                i += 1
                continue

            # Regular line
            merged_lines.append(line)
            i += 1

        return '\n'.join(merged_lines)

    def _merge_simple(self, gen_content: str, manual_content: str) -> str:
        """Simple merge strategy: generated first, then all manual content."""
        lines = gen_content.split('\n')

        # Extract manual content (everything between MANUAL_START and MANUAL_END)
        manual_match = re.search(
            r'<!-- MANUAL_START: (\w+) -->(.+?)<!-- MANUAL_END: \1 -->',
            manual_content,
            re.DOTALL
        )

        if not manual_match:
            return gen_content

        section_name = manual_match.group(1)
        manual_text = manual_match.group(2).strip()

        # Find GENERATED_END and insert manual content after it
        merged_lines = []
        found_gen_end = False

        for line in lines:
            merged_lines.append(line)

            if '<!-- GENERATED_END -->' in line and not found_gen_end:
                found_gen_end = True
                merged_lines.append('')
                merged_lines.append(f'<!-- MANUAL_START: {section_name} -->')
                merged_lines.append('')
                merged_lines.extend(manual_text.split('\n'))
                merged_lines.append('')
                merged_lines.append(f'<!-- MANUAL_END: {section_name} -->')

        return '\n'.join(merged_lines)

    def _parse_manual_sections(self, content: str, section_type: str = 'content') -> Dict[str, List[str]]:
        """Parse manual content into sections by endpoint.

        Args:
            content: The manual file content
            section_type: The type of section to parse (overview, examples, additional, or content)
        """
        sections = {}
        unmatched = []

        # Extract content between MANUAL_START and MANUAL_END for the specific section type
        manual_match = re.search(
            rf'<!-- MANUAL_START: {section_type} -->(.+?)<!-- MANUAL_END: {section_type} -->',
            content,
            re.DOTALL
        )

        if not manual_match:
            return sections

        manual_text = manual_match.group(1).strip()
        lines = manual_text.split('\n')

        current_section = []
        current_endpoint = None

        for line in lines:
            # Detect endpoint header in manual content (### POST /endpoint)
            endpoint_match = re.match(r'^### (GET|POST|PUT|PATCH|DELETE) /(.+)$', line)

            if endpoint_match:
                # Save previous section
                if current_endpoint:
                    sections[current_endpoint] = current_section
                elif current_section:
                    unmatched.extend(current_section)

                # Start new section
                # Convert ### to ## to match generated format
                current_endpoint = f'## {endpoint_match.group(1)} /{endpoint_match.group(2)}'
                current_section = []
            else:
                current_section.append(line)

        # Save last section
        if current_endpoint:
            sections[current_endpoint] = current_section
        elif current_section:
            unmatched.extend(current_section)

        if unmatched:
            sections['unmatched'] = unmatched

        return sections

    def _endpoint_key(self, endpoint: str) -> str:
        """Generate a key name for an endpoint."""
        # Convert "## GET /threads/{threadId}" to "get-threads-threadid"
        key = endpoint.lower()
        key = re.sub(r'## ', '', key)
        key = re.sub(r'[{}/]', '-', key)
        key = re.sub(r'-+', '-', key)
        key = key.strip('-')
        return key


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent.parent

    # Paths
    generated_dir = project_root / ".generated" / "api-reference"
    manual_dir = project_root / "docs-content"  # Manual overlays
    output_dir = project_root / "api-reference"  # Final merged output

    print("API Documentation Merger")
    print("=" * 80)
    print(f"Generated: {generated_dir}")
    print(f"Manual:    {manual_dir}")
    print(f"Output:    {output_dir}")
    print("=" * 80)
    print()

    # Merge documentation
    merger = DocMerger(str(generated_dir), str(manual_dir), str(output_dir))
    merger.merge_all()

    print("✅ Documentation merge complete!")
    print()
    print("Next steps:")
    print("docs/api-reference/")
    print("2. Add manual overlays in docs-content/")
    print("3. Re-run this script to merge updates")


if __name__ == "__main__":
    main()
