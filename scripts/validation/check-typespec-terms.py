#!/usr/bin/env python3
"""
Check if terminology and model names used in documentation exist in TypeSpec.

This script:
1. Extracts all model names, enum names, and interfaces from TypeSpec
2. Searches documentation for potential model/type references
3. Reports terms used in docs that don't exist in TypeSpec
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict


class TypeSpecTermChecker:
    """Check if documentation terms exist in TypeSpec."""

    def __init__(self, typespec_dir: str, docs_dirs: List[str]):
        self.typespec_dir = Path(typespec_dir)
        self.docs_dirs = [Path(d) for d in docs_dirs]

        # TypeSpec vocabulary
        self.models: Set[str] = set()
        self.enums: Set[str] = set()
        self.interfaces: Set[str] = set()
        self.unions: Set[str] = set()
        self.all_types: Set[str] = set()

        # Issues found
        self.issues: List[Dict] = []

    def parse_typespec(self):
        """Parse TypeSpec files to extract all type names."""
        print("📖 Parsing TypeSpec files...\n")

        for tsp_file in self.typespec_dir.glob("**/*.tsp"):
            content = tsp_file.read_text()

            # Extract models: model ModelName
            for match in re.finditer(r'model\s+(\w+)', content):
                self.models.add(match.group(1))
                self.all_types.add(match.group(1))

            # Extract enums: enum EnumName
            for match in re.finditer(r'enum\s+(\w+)', content):
                self.enums.add(match.group(1))
                self.all_types.add(match.group(1))

            # Extract interfaces: interface InterfaceName
            for match in re.finditer(r'interface\s+(\w+)', content):
                self.interfaces.add(match.group(1))
                self.all_types.add(match.group(1))

            # Extract unions: union UnionName
            for match in re.finditer(r'union\s+(\w+)', content):
                self.unions.add(match.group(1))
                self.all_types.add(match.group(1))

        print(f"✓ Found {len(self.models)} models")
        print(f"✓ Found {len(self.enums)} enums")
        print(f"✓ Found {len(self.interfaces)} interfaces")
        print(f"✓ Found {len(self.unions)} unions")
        print(f"✓ Total types: {len(self.all_types)}\n")

    def check_docs(self):
        """Check documentation for undefined terms."""
        print("🔍 Checking documentation for undefined types...\n")

        # Focus on patterns that strongly indicate TypeSpec type names
        patterns = [
            # Compound PascalCase (2+ capital letters): ThreadAutoResponder, AgentCard, RunStatus
            (r'\b([A-Z][a-z]+(?:[A-Z][a-z0-9]+)+)\b', 'COMPOUND_PASCALCASE'),
            # Words with type-indicating suffixes
            (r'\b([A-Z][A-Za-z]*(?:Config|Schema|Request|Response|Event|Hook|Condition|Watch|Choice|Endpoint|State|Update))\b', 'TYPE_SUFFIX'),
        ]

        # Find all markdown files
        md_files = []
        for docs_dir in self.docs_dirs:
            if docs_dir.exists():
                md_files.extend(docs_dir.glob("**/*.md"))

        for md_file in md_files:
            # Skip .workspace directory
            if '.workspace' in str(md_file):
                continue
            self._check_file(md_file, patterns)

        # Remove duplicates
        seen = set()
        unique_issues = []
        for issue in self.issues:
            key = (issue['file'], issue['line'], issue['term'])
            if key not in seen:
                seen.add(key)
                unique_issues.append(issue)
        self.issues = unique_issues

    def _check_file(self, file_path: Path, patterns: List[tuple]):
        """Check a single file for undefined terms."""
        try:
            content = file_path.read_text()
        except Exception as e:
            print(f"⚠️  Could not read {file_path}: {e}")
            return

        for pattern, pattern_type in patterns:
            for match in re.finditer(pattern, content):
                term = match.group(1)

                # Skip if term exists in TypeSpec
                if term in self.all_types:
                    continue

                # Skip common words that aren't type names
                skip_terms = {
                    # Common non-type words (English words)
                    'The', 'This', 'When', 'After', 'Before', 'Each', 'Step',
                    'Example', 'Summary', 'Type', 'Description', 'Value',
                    'Required', 'Optional', 'Default', 'Yes', 'No', 'True', 'False',
                    'Status', 'Error', 'Success', 'Failure', 'Response', 'Request',
                    'Output', 'Result', 'Input', 'Data', 'Config', 'Settings',
                    # Companies/brands
                    'Azure', 'Microsoft', 'OpenAI', 'Anthropic', 'GitHub', 'Google',
                    'Amazon', 'Meta', 'Apple', 'Slack', 'Discord', 'Teams',
                    # Programming languages/frameworks
                    'JavaScript', 'TypeScript', 'Python', 'Java', 'Rust', 'Swift',
                    'React', 'Angular', 'Vue', 'Express', 'Django', 'Flask',
                    'LangChain', 'LlamaIndex', 'Haystack',
                    # Technical terms (not TypeSpec types)
                    'WebSocket', 'TypeSpec', 'Protocol', 'Schema', 'Interface',
                    'Json', 'Xml', 'Yaml', 'Toml', 'Csv', 'Html', 'Css',
                    'Http', 'Https', 'Grpc', 'Rest', 'GraphQL', 'Soap',
                    'Url', 'Uri', 'Uuid', 'Guid', 'Hash', 'Token',
                    'Database', 'Redis', 'Postgres', 'Mongo', 'Sqlite',
                    'Docker', 'Kubernetes', 'Linux', 'Windows', 'Unix',
                    # Libraries/tools
                    'PyAudio', 'NumPy', 'Pandas', 'TensorFlow', 'PyTorch',
                    'Requests', 'FastAPI', 'Pydantic', 'Sqlalchemy',
                    # Services
                    'PagerDuty', 'Datadog', 'Sentry', 'Stripe', 'Twilio',
                    'SharePoint', 'OneDrive', 'Outlook', 'Exchange',
                    # HTTP verbs/methods
                    'Get', 'Post', 'Put', 'Patch', 'Delete', 'Options', 'Head',
                    'Create', 'Update', 'List', 'Fetch', 'Send', 'Receive',
                    # Common programming terms
                    'String', 'Integer', 'Boolean', 'Float', 'Double', 'Byte',
                    'Array', 'List', 'Dict', 'Map', 'Set', 'Queue', 'Stack',
                    'Class', 'Function', 'Method', 'Property', 'Field', 'Variable',
                    'Object', 'Instance', 'Module', 'Package', 'Library',
                    'Async', 'Await', 'Promise', 'Future', 'Callback',
                    'Exception', 'ValueError', 'TypeError', 'KeyError',
                    'IndexError', 'AttributeError', 'RuntimeError',
                    'TimeoutException', 'ConnectionError', 'ValidationError',
                    # DateTime/time related
                    'DateTime', 'Date', 'Time', 'Timestamp', 'Duration',
                    'Calendar', 'Clock', 'Timer', 'Scheduler',
                }
                if term in skip_terms:
                    continue

                # Get line number and context
                line_num = content[:match.start()].count('\n') + 1
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                line_content = content[line_start:line_end if line_end != -1 else len(content)]

                # Skip if in code comment explaining something was removed
                skip_words = ['removed', 'deprecated', 'old', 'was', 'not', 'no longer',
                             'previously', 'formerly', 'instead of', 'example', 'like']
                if any(word in line_content.lower() for word in skip_words):
                    continue

                # Skip if it's in a URL or file path
                if '/' in line_content[max(0, match.start()-line_start-20):match.end()-line_start+20]:
                    continue

                # Report issue
                self.issues.append({
                    'file': str(file_path.relative_to(self.typespec_dir.parent)),
                    'line': line_num,
                    'term': term,
                    'pattern_type': pattern_type,
                    'severity': 'WARNING',
                    'message': f'Term "{term}" not found in TypeSpec',
                    'line_content': line_content[:100]
                })

    def report_issues(self):
        """Report all issues found."""
        if not self.issues:
            print("✅ All terms in documentation exist in TypeSpec!\n")
            return

        # Group by term
        terms_count = defaultdict(list)
        for issue in self.issues:
            terms_count[issue['term']].append(issue)

        print(f"⚠️  Found {len(terms_count)} undefined terms used in documentation:\n")

        # Report by frequency
        print("UNDEFINED TERMS (sorted by frequency):")
        print("=" * 80)

        sorted_terms = sorted(terms_count.items(), key=lambda x: len(x[1]), reverse=True)

        for term, occurrences in sorted_terms[:20]:  # Top 20
            print(f"\n\"{term}\" - {len(occurrences)} occurrences")
            print(f"  Not found in TypeSpec (no model, enum, interface, or union)")

            # Show first few locations
            for issue in occurrences[:3]:
                print(f"  - {issue['file']}:{issue['line']}")

            if len(occurrences) > 3:
                print(f"  ... and {len(occurrences) - 3} more occurrences")

        if len(sorted_terms) > 20:
            print(f"\n  ... and {len(sorted_terms) - 20} more undefined terms")

        # Summary by file
        print("\n\nSUMMARY BY FILE:")
        print("=" * 80)
        files_count = defaultdict(int)
        for issue in self.issues:
            files_count[issue['file']] += 1

        for file_path, count in sorted(files_count.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"{count:3d} undefined terms: {file_path}")


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    typespec_dir = project_root / "typespec"
    docs_dirs = [
        project_root / "api-reference",
        project_root / "guides",
        project_root / "specifications",
    ]

    # Parse TypeSpec
    checker = TypeSpecTermChecker(str(typespec_dir), [str(d) for d in docs_dirs])
    checker.parse_typespec()

    # Check documentation
    checker.check_docs()
    checker.report_issues()

    # Exit with warning (not error) since these are informational
    if checker.issues:
        print(f"\n⚠️  Found {len(set(i['term'] for i in checker.issues))} terms in docs not defined in TypeSpec")
        print("Review these to ensure they're valid or should be removed")
        exit(0)  # Warning, not error
    else:
        print("\n✅ All documentation terms exist in TypeSpec")
        exit(0)


if __name__ == "__main__":
    main()
