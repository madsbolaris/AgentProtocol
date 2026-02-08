"""
MkDocs plugin for including test examples and results in documentation.

This plugin processes custom tags in markdown files:
- {% include-test "test-id" language="python" %} - Includes code snippet (language-specific)
- {% include-result "test-id" %} - Includes test output (language-agnostic, from shared results)
- {% include-test "test-id" section="setup" language="python" %} - Includes specific section
"""

import json
import re
from pathlib import Path
from typing import Dict, Optional

from mkdocs.config import config_options
from mkdocs.plugins import BasePlugin


class TestExamplesPlugin(BasePlugin):
    """MkDocs plugin for including test examples and results"""

    config_scheme = (
        ("snippets_dir", config_options.Type(str, default="docs/snippets")),
        ("results_dir", config_options.Type(str, default="test-data/results")),
        ("enable_validation", config_options.Type(bool, default=True)),
        ("show_language_tabs", config_options.Type(bool, default=True)),
    )

    def __init__(self):
        super().__init__()
        self.snippets: Dict = {}
        self.results: Dict = {}
        self.repo_root: Optional[Path] = None

    def on_config(self, config):
        """Load snippets and results when config is loaded"""
        self.repo_root = Path(config["docs_dir"]).parent

        # Load snippets metadata
        snippets_dir = self.repo_root / self.config["snippets_dir"]
        metadata_file = snippets_dir / "metadata.json"

        if metadata_file.exists():
            self.snippets = json.loads(metadata_file.read_text())
            print(f"✓ Loaded {len(self.snippets)} test example snippets")
        else:
            print(f"⚠️  No snippets metadata found at {metadata_file}")
            print("   Run: python scripts/extract-doc-examples.py")

        # Load test results from language-specific directories
        results_dir = self.repo_root / self.config["results_dir"]
        for lang in ["python", "dotnet", "typescript"]:
            lang_dir = results_dir / lang
            if not lang_dir.exists():
                continue

            for result_file in lang_dir.glob("*.json"):
                try:
                    result = json.loads(result_file.read_text())
                    test_id = result.get("testId", result_file.stem)
                    key = f"{lang}/{test_id}"
                    self.results[key] = result
                except Exception as e:
                    print(f"⚠️  Failed to load result {result_file}: {e}")

        if self.results:
            print(f"✓ Loaded {len(self.results)} test results")

        return config

    def on_page_markdown(self, markdown, page, config, files):
        """Process custom tags in markdown"""
        # Replace multi-language test includes first (before single-language)
        markdown = self._replace_test_all_includes(markdown)
        # Replace test include tags
        markdown = self._replace_test_includes(markdown)
        # Replace result include tags
        markdown = self._replace_result_includes(markdown)
        return markdown

    def _replace_test_all_includes(self, markdown: str) -> str:
        """
        Replace {%include-test-all %} tags with tabbed code snippets for all available languages.

        Supported formats:
        - {% include-test-all "test-id" %} - Shows all available languages with results
        - {% include-test-all "test-id" section="setup" %} - Specific section, all languages
        """
        pattern = r'{%\s*include-test-all\s+"([^"]+)"(?:\s+section="([^"]+)")?\s*%}'

        def replace(match):
            test_id = match.group(1)
            section = match.group(2) or "main"

            # Find all available languages for this test
            available_languages = []
            for lang in ["python", "csharp", "typescript"]:
                key = f"{lang}/{test_id}/{section}"
                if key in self.snippets:
                    available_languages.append(lang)

            if not available_languages:
                return f"<!-- Error: No examples found for '{test_id}' in any language -->\n\n!!! warning\n    No code examples found for `{test_id}`. Run: `python scripts/extract-doc-examples.py`"

            # Generate Material tabs for each language
            tabs_content = []

            # Language display names
            lang_names = {
                "python": "Python",
                "csharp": "C#",
                "typescript": "TypeScript"
            }

            # Language for syntax highlighting
            lang_syntax = {
                "python": "python",
                "csharp": "csharp",
                "typescript": "typescript"
            }

            for lang in available_languages:
                key = f"{lang}/{test_id}/{section}"
                snippet = self.snippets.get(key)

                if snippet:
                    snippet_file = self.repo_root / self.config["snippets_dir"] / snippet["file"]
                    if snippet_file.exists():
                        code = snippet_file.read_text()

                        # Build tab content
                        tab_label = lang_names.get(lang, lang)
                        syntax = lang_syntax.get(lang, lang)

                        # Find corresponding result
                        result_lang = "dotnet" if lang == "csharp" else lang
                        result_key = f"{result_lang}/{test_id}"
                        result = self.results.get(result_key)

                        tab_content = f'=== "{tab_label}"\n\n'
                        tab_content += f'    ```{syntax}\n'
                        for line in code.splitlines():
                            tab_content += f'    {line}\n'
                        tab_content += '    ```\n'

                        # Add result if available
                        if result:
                            output = result.get("output", {}).get("raw", "")
                            if output:
                                output_format = self._infer_format(output)
                                tab_content += '\n\n    **Output:**\n\n'
                                tab_content += f'    ```{output_format}\n'
                                for line in output.splitlines():
                                    tab_content += f'    {line}\n'
                                tab_content += '    ```\n'

                        tabs_content.append(tab_content)

            # Combine all tabs
            return '\n'.join(tabs_content)

        return re.sub(pattern, replace, markdown)

    def _replace_test_includes(self, markdown: str) -> str:
        """
        Replace {% include-test %} tags with code snippets.

        Supported formats:
        - {% include-test "test-id" %}
        - {% include-test "test-id" language="python" %}
        - {% include-test "test-id" section="setup" language="python" %}
        """
        pattern = r'{%\s*include-test\s+"([^"]+)"(?:\s+section="([^"]+)")?(?:\s+language="([^"]+)")?\s*%}'

        def replace(match):
            test_id = match.group(1)
            section = match.group(2) or "main"
            language = match.group(3) or "python"

            # Build lookup key
            key = f"{language}/{test_id}/{section}"

            snippet = self.snippets.get(key)
            if not snippet:
                # Try without section (in case section wasn't specified)
                for possible_key in self.snippets.keys():
                    if possible_key.startswith(f"{language}/{test_id}/"):
                        snippet = self.snippets[possible_key]
                        break

            if not snippet:
                return f"<!-- Error: Test example '{test_id}' not found for language '{language}' -->\n\n```\nExample not found: {test_id}\nRun: python scripts/extract-doc-examples.py\n```"

            # Load the actual code
            snippet_file = self.repo_root / self.config["snippets_dir"] / snippet["file"]

            if not snippet_file.exists():
                return f"<!-- Error: Snippet file not found: {snippet_file} -->\n\n```\nSnippet file missing\n```"

            code = snippet_file.read_text()

            # Return formatted code block
            return f"```{language}\n{code}\n```"

        return re.sub(pattern, replace, markdown)

    def _replace_result_includes(self, markdown: str) -> str:
        """
        Replace {% include-result %} tags with test outputs.

        Supported formats:
        - {% include-result "test-id" %}
        - {% include-result "test-id" language="python" %}
        - {% include-result "test-id" format="json" %} (default is inferred from output)
        """
        pattern = r'{%\s*include-result\s+"([^"]+)"(?:\s+language="([^"]+)")?(?:\s+format="([^"]+)")?\s*%}'

        def replace(match):
            test_id = match.group(1)
            language = match.group(2) or "python"
            output_format = match.group(3) or None

            # Map language names to result directory names
            lang_map = {"csharp": "dotnet", "python": "python", "typescript": "typescript"}
            result_lang = lang_map.get(language, language)

            # Build lookup key with language
            key = f"{result_lang}/{test_id}"

            result = self.results.get(key)
            if not result:
                return f"<!-- Error: Test result '{test_id}' not found for language '{language}' -->\n\n```\nResult not found: {test_id}\nTests may not have been run with output capture.\n```"

            # Get the output
            output = result.get("output", {}).get("raw", "")

            if not output:
                return f"<!-- Error: No output captured for test '{test_id}' -->"

            # Infer format if not specified
            if not output_format:
                output_format = self._infer_format(output)

            # Return formatted output block
            return f"```{output_format}\n{output}\n```"

        return re.sub(pattern, replace, markdown)

    def _infer_format(self, output: str) -> str:
        """Infer output format from content"""
        output_trimmed = output.strip()

        if output_trimmed.startswith("<?xml") or output_trimmed.startswith("<"):
            return "xml"
        elif output_trimmed.startswith("{") or output_trimmed.startswith("["):
            return "json"
        else:
            return "text"


def makeExtension(**kwargs):
    """Required for MkDocs plugin"""
    return TestExamplesPlugin(**kwargs)
