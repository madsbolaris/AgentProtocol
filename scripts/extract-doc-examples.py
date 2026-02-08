#!/usr/bin/env python3
"""
Extract documentation examples from test files.

This script scans Python, C#, and TypeScript test files for marked documentation
examples and extracts the code snippets for use in documentation.

Usage:
    python scripts/extract-doc-examples.py
    python scripts/extract-doc-examples.py --language python
    python scripts/extract-doc-examples.py --language typescript
    python scripts/extract-doc-examples.py --test-id basic-serialization
    python scripts/extract-doc-examples.py --verbose
"""

import re
import json
import argparse
import textwrap
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class CodeExtractor:
    """Extract code snippets from test files"""

    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.snippets_dir = repo_root / "docs" / "snippets"
        self.verbose = verbose
        self.snippets_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message: str):
        """Log message if verbose mode is enabled"""
        if self.verbose:
            print(message)

    def extract_python_examples(self) -> Dict[str, dict]:
        """Extract examples from Python test files"""
        examples = {}

        test_dirs = [
            self.repo_root / "python" / "microsoft-agents-xml" / "tests",
            self.repo_root / "python" / "microsoft-agents-protocol" / "tests",
        ]

        for test_dir in test_dirs:
            if not test_dir.exists():
                self.log(f"Skipping non-existent directory: {test_dir}")
                continue

            self.log(f"Scanning Python tests in: {test_dir}")
            for test_file in test_dir.rglob("test_*.py"):
                self.log(f"  Reading: {test_file.name}")
                file_examples = self._extract_from_python_file(test_file)
                examples.update(file_examples)
                self.log(f"    Found {len(file_examples)} examples")

        return examples

    def _extract_from_python_file(self, file_path: Path) -> Dict[str, dict]:
        """Extract examples from a single Python file"""
        examples = {}
        content = file_path.read_text()

        # Find functions with @doc_example decorator
        # Pattern: @doc_example("test-id", "title", ...)
        decorator_pattern = r'@doc_example\s*\(\s*["\']([^"\']+)["\']\s*,\s*["\']([^"\']+)["\']\s*(?:,\s*([^)]+))?\s*\)'
        func_pattern = r'def\s+(\w+)\s*\('

        # Find all decorators
        for decorator_match in re.finditer(decorator_pattern, content):
            test_id = decorator_match.group(1)
            title = decorator_match.group(2)
            decorator_pos = decorator_match.end()

            # Find the function that follows this decorator
            func_match = re.search(func_pattern, content[decorator_pos:])
            if not func_match:
                continue

            func_name = func_match.group(1)
            func_start = decorator_match.start()

            # Find all code snippets marked with doc-example-start/end
            snippet_pattern = r'#\s*doc-example-start(?::\s*(\w+))?\s*\n(.*?)\n\s*#\s*doc-example-end(?::\s*\1)?'
            snippets = re.finditer(snippet_pattern, content[func_start:], re.DOTALL)

            for snippet in snippets:
                section_name = snippet.group(1) or "main"
                code = snippet.group(2)

                # Clean up indentation
                code = self._dedent(code)

                # Create unique key
                example_key = f"{test_id}/{section_name}"
                examples[example_key] = {
                    "testId": test_id,
                    "section": section_name,
                    "title": title,
                    "language": "python",
                    "code": code,
                    "sourceFile": str(file_path.relative_to(self.repo_root)),
                    "function": func_name
                }

        return examples

    def extract_csharp_examples(self) -> Dict[str, dict]:
        """Extract examples from C# test files"""
        examples = {}

        test_dirs = [
            self.repo_root / "dotnet" / "tests",
        ]

        for test_dir in test_dirs:
            if not test_dir.exists():
                self.log(f"Skipping non-existent directory: {test_dir}")
                continue

            self.log(f"Scanning C# tests in: {test_dir}")
            for test_file in test_dir.rglob("*Tests.cs"):
                self.log(f"  Reading: {test_file.name}")
                file_examples = self._extract_from_csharp_file(test_file)
                examples.update(file_examples)
                self.log(f"    Found {len(file_examples)} examples")

        return examples

    def _extract_from_csharp_file(self, file_path: Path) -> Dict[str, dict]:
        """Extract examples from a single C# file"""
        examples = {}
        content = file_path.read_text()

        # Find methods with [DocExample] attribute (can span multiple lines)
        # Use a simpler approach: find [DocExample and then find the matching )]
        attr_start_pattern = r'\[DocExample\s*\(\s*"([^"]+)"\s*,\s*"([^"]+)"'
        method_pattern = r'public\s+\w+\s+(\w+)\s*\('

        # Find all attribute starts
        for attr_match in re.finditer(attr_start_pattern, content, re.DOTALL):
            test_id = attr_match.group(1)
            title = attr_match.group(2)
            attr_start = attr_match.start()

            # Find the closing )] for this attribute
            search_pos = attr_match.end()
            bracket_count = 1
            paren_count = 1

            while search_pos < len(content) and (bracket_count > 0 or paren_count > 0):
                if content[search_pos] == '[':
                    bracket_count += 1
                elif content[search_pos] == ']':
                    bracket_count -= 1
                elif content[search_pos] == '(':
                    paren_count += 1
                elif content[search_pos] == ')':
                    paren_count -= 1
                    if paren_count == 0:
                        # Found the closing paren
                        break
                search_pos += 1

            # Now find the closing ]
            while search_pos < len(content):
                if content[search_pos] == ']':
                    attr_pos = search_pos + 1
                    break
                search_pos += 1
            else:
                # Didn't find closing bracket
                continue

            # Find the method that follows this attribute
            method_match = re.search(method_pattern, content[attr_pos:])
            if not method_match:
                continue

            method_name = method_match.group(1)
            method_start = attr_match.start()

            # Find all code snippets marked with doc-example-start/end
            snippet_pattern = r'//\s*doc-example-start(?::\s*(\w+))?\s*\n(.*?)\n\s*//\s*doc-example-end(?::\s*\1)?'
            snippets = re.finditer(snippet_pattern, content[method_start:], re.DOTALL)

            for snippet in snippets:
                section_name = snippet.group(1) or "main"
                code = snippet.group(2)

                # Clean up indentation
                code = self._dedent(code)

                # Create unique key
                example_key = f"{test_id}/{section_name}"
                examples[example_key] = {
                    "testId": test_id,
                    "section": section_name,
                    "title": title,
                    "language": "csharp",
                    "code": code,
                    "sourceFile": str(file_path.relative_to(self.repo_root)),
                    "method": method_name
                }

        return examples

    def extract_typescript_examples(self) -> Dict[str, dict]:
        """Extract examples from TypeScript test files"""
        examples = {}

        test_dirs = [
            self.repo_root / "typescript" / "packages" / "microsoft-agents-xml" / "tests",
        ]

        for test_dir in test_dirs:
            if not test_dir.exists():
                self.log(f"Skipping non-existent directory: {test_dir}")
                continue

            self.log(f"Scanning TypeScript tests in: {test_dir}")
            for test_file in test_dir.rglob("*.test.ts"):
                self.log(f"  Reading: {test_file.name}")
                file_examples = self._extract_from_typescript_file(test_file)
                examples.update(file_examples)
                self.log(f"    Found {len(file_examples)} examples")

        return examples

    def _extract_from_typescript_file(self, file_path: Path) -> Dict[str, dict]:
        """Extract examples from a single TypeScript file"""
        examples = {}
        content = file_path.read_text()

        # Find methods with @docExample decorator
        # Pattern: @docExample({ testId: "...", title: "..." })
        decorator_pattern = r'@docExample\s*\(\s*\{\s*testId:\s*["\']([^"\']+)["\']\s*,\s*title:\s*["\']([^"\']+)["\']\s*(?:,\s*[^}]+)?\s*\}\s*\)'

        # Find all decorators
        for decorator_match in re.finditer(decorator_pattern, content):
            test_id = decorator_match.group(1)
            title = decorator_match.group(2)
            decorator_pos = decorator_match.start()

            # Find code snippets marked with // doc-example-start/end
            # Search within a reasonable range after the decorator
            search_content = content[decorator_pos:decorator_pos + 10000]
            snippet_pattern = r'//\s*doc-example-start(?::\s*(\w+))?\s*\n(.*?)\n\s*//\s*doc-example-end'
            snippets = re.finditer(snippet_pattern, search_content, re.DOTALL)

            for snippet in snippets:
                section_name = snippet.group(1) or "main"
                code = snippet.group(2)

                # Clean up indentation
                code = self._dedent(code)

                # Create unique key
                example_key = f"{test_id}/{section_name}"
                examples[example_key] = {
                    "testId": test_id,
                    "section": section_name,
                    "title": title,
                    "language": "typescript",
                    "code": code,
                    "sourceFile": str(file_path.relative_to(self.repo_root)),
                }

        return examples

    def _dedent(self, code: str) -> str:
        """Remove common leading whitespace"""
        return textwrap.dedent(code).strip()

    def save_snippets(self, examples: Dict[str, dict]):
        """Save extracted snippets to files"""
        metadata = {}

        for key, example in examples.items():
            test_id = example["testId"]
            section = example["section"]
            language = example["language"]
            code = example["code"]

            # Create language-specific directory
            lang_dir = self.snippets_dir / language
            lang_dir.mkdir(exist_ok=True)

            # Save code to file
            filename = f"{test_id}_{section}.{self._get_extension(language)}"
            snippet_file = lang_dir / filename
            snippet_file.write_text(code)

            # Update metadata
            metadata_key = f"{language}/{test_id}/{section}"
            metadata[metadata_key] = {
                "testId": test_id,
                "section": section,
                "title": example["title"],
                "language": language,
                "file": str(snippet_file.relative_to(self.snippets_dir)),
                "sourceFile": example["sourceFile"],
            }

        # Save metadata
        metadata_file = self.snippets_dir / "metadata.json"
        metadata_file.write_text(json.dumps(metadata, indent=2))

        return metadata

    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        return {"python": "py", "csharp": "cs", "typescript": "ts"}.get(language, "txt")


def main():
    parser = argparse.ArgumentParser(
        description="Extract documentation examples from test files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract all examples
  python scripts/extract-doc-examples.py

  # Extract only Python examples
  python scripts/extract-doc-examples.py --language python

  # Extract specific test ID
  python scripts/extract-doc-examples.py --test-id basic-serialization

  # Verbose output
  python scripts/extract-doc-examples.py --verbose
        """
    )
    parser.add_argument(
        "--language",
        choices=["python", "csharp", "typescript"],
        help="Extract only specific language"
    )
    parser.add_argument(
        "--test-id",
        help="Extract only specific test ID"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    extractor = CodeExtractor(repo_root, verbose=args.verbose)

    examples = {}

    if args.language is None or args.language == "python":
        print("Extracting Python examples...")
        python_examples = extractor.extract_python_examples()
        examples.update(python_examples)
        print(f"  Found {len(python_examples)} Python examples")

    if args.language is None or args.language == "csharp":
        print("Extracting C# examples...")
        csharp_examples = extractor.extract_csharp_examples()
        examples.update(csharp_examples)
        print(f"  Found {len(csharp_examples)} C# examples")

    if args.language is None or args.language == "typescript":
        print("Extracting TypeScript examples...")
        typescript_examples = extractor.extract_typescript_examples()
        examples.update(typescript_examples)
        print(f"  Found {len(typescript_examples)} TypeScript examples")

    if args.test_id:
        examples = {k: v for k, v in examples.items() if v["testId"] == args.test_id}
        print(f"Filtered to test ID '{args.test_id}': {len(examples)} examples")

    if not examples:
        print("⚠️  No examples found!")
        return 1

    print("\nSaving snippets...")
    metadata = extractor.save_snippets(examples)

    print("\n" + "=" * 60)
    print("✅ Extraction complete!")
    print("=" * 60)
    print(f"Total examples extracted: {len(examples)}")
    print(f"  Python: {sum(1 for e in examples.values() if e['language'] == 'python')}")
    print(f"  C#: {sum(1 for e in examples.values() if e['language'] == 'csharp')}")
    print(f"  TypeScript: {sum(1 for e in examples.values() if e['language'] == 'typescript')}")
    print(f"\nSnippets saved to: {extractor.snippets_dir}")
    print(f"Metadata saved to: {extractor.snippets_dir / 'metadata.json'}")

    # List extracted test IDs
    test_ids = sorted(set(e["testId"] for e in examples.values()))
    print(f"\nExtracted test IDs:")
    for test_id in test_ids:
        sections = [e["section"] for e in examples.values() if e["testId"] == test_id]
        print(f"  - {test_id} ({', '.join(sections)})")

    return 0


if __name__ == "__main__":
    exit(main())
