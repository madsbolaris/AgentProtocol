"""
MkDocs plugin to extract code snippets directly from test files.

This plugin allows you to reference test code directly in documentation without
intermediate snippet files. It extracts code snippets from tests marked with
[DocExample] (C#), @pytest.mark.doc_example (Python), or @docExample (TypeScript).

Usage in docs:
    ```csharp
    --8<-- test::quickstart/client-simple-completion
    ```

The plugin will:
1. Find the test with DocExample ID "client-simple-completion"
   - Requires a file specifier (e.g., "quickstart") to identify which test file to search
   - Only searches test files whose name contains the file specifier
2. Extract the snippet using one of these patterns (in order of preference):
   - C#: #region Snippet / #endregion
   - Python/TypeScript: # <snippet> / # </snippet> or // <snippet> / // </snippet>
   - Legacy: // Act - Exact code from quickstart / // Assert
3. Include it directly in the rendered documentation

Snippet Pattern Examples:

C# with #region (recommended):
    [DocExample("client-simple-completion")]
    public async Task Step1_SimpleCompletion()
    {
        // Arrange
        var client = CreateClient();

        #region Snippet
        string response = await client.CompleteChatAsync("Hello!");
        Console.WriteLine(response);
        #endregion

        // Assert
        Assert.NotNull(response);
    }

Python with structured markers:
    @pytest.mark.doc_example("client-simple-completion")
    async def test_simple_completion():
        # Arrange
        client = create_client()

        # <snippet>
        response = await client.complete_chat_async("Hello!")
        print(response)
        # </snippet>

        # Assert
        assert response is not None

TypeScript with structured markers:
    /**
     * @docExample client-simple-completion
     */
    it('should complete chat', async () => {
        // Arrange
        const client = createClient();

        // <snippet>
        const response = await client.completeChatAsync('Hello!');
        console.log(response);
        // </snippet>

        // Assert
        expect(response).toBeDefined();
    });

Benefits:
- No intermediate snippet files needed
- Direct link to source test (better for doc writers)
- Always in sync (extracts at build time)
- Single source of truth
- Robust extraction patterns that are hard to break
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options


# Language configurations with SDK-specific test directories
LANGUAGES = {
    'csharp': {
        'comment': '//',
        'test_dirs': {
            'client': ['dotnet/tests/Microsoft.Agents.Client.Tests/Docs'],
            'hosting': ['dotnet/tests/Microsoft.Agents.Protocol.Hosting.Tests/Docs'],
        },
        'test_pattern': '**/*Tests.cs',
        'marker_pattern': r'\[DocExample\("([^"]+)"\)\]',
    },
    'python': {
        'comment': '#',
        'test_dirs': {
            'client': ['python/microsoft-agents-protocol-client/tests/docs'],
            'hosting': ['python/microsoft-agents-protocol-hosting/tests/docs'],
        },
        'test_pattern': '**/test_*.py',
        'marker_pattern': r'@pytest\.mark\.doc_example\("([^"]+)"\)',
    },
    'typescript': {
        'comment': '//',
        'test_dirs': {
            'client': ['typescript/packages/agents-protocol-client/tests/docs'],
            'hosting': ['typescript/packages/agents-protocol-hosting/tests/docs'],
        },
        'test_pattern': '**/*.test.ts',
        'marker_pattern': r'\*\s*@docExample\s+([^\s\n]+)',
    }
}

# Map code fence languages to our LANGUAGES config keys
LANGUAGE_MAP = {
    'csharp': 'csharp',
    'cs': 'csharp',
    'c#': 'csharp',
    'python': 'python',
    'py': 'python',
    'typescript': 'typescript',
    'ts': 'typescript',
    'javascript': 'typescript',
    'js': 'typescript',
}


def extract_snippet_from_source(source: str, comment_char: str) -> Optional[str]:
    """
    Extract the snippet from test source code.

    Tries multiple patterns in order of preference:
    1. #region Snippet / #endregion (C# regions)
    2. Structured markers: // <snippet> / // </snippet> or # <snippet> / # </snippet>
    3. Act/Assert comments (legacy fallback)

    Args:
        source: The test source code
        comment_char: Comment character for the language ('//' or '#')

    Returns:
        Extracted snippet or None if not found
    """
    snippet = None

    # Pattern 1: #region Snippet / #endregion (C# regions)
    region_pattern = r'#region\s+Snippet\s*\n(.*?)\n\s*#endregion'
    match = re.search(region_pattern, source, re.DOTALL | re.IGNORECASE)
    if match:
        snippet = match.group(1)

    # Pattern 2: Structured markers (// <snippet> or # <snippet>)
    if not snippet:
        marker_pattern = rf'{re.escape(comment_char)}\s*<snippet>\s*\n(.*?)\n\s*{re.escape(comment_char)}\s*</snippet>'
        match = re.search(marker_pattern, source, re.DOTALL | re.IGNORECASE)
        if match:
            snippet = match.group(1)

    # Pattern 3: Act/Assert comments (legacy fallback)
    if not snippet:
        act_pattern = rf'{re.escape(comment_char)}\s*Act\s*-\s*Exact code from quickstart\s*\n(.*?)\n\s*{re.escape(comment_char)}\s*Assert'
        match = re.search(act_pattern, source, re.DOTALL | re.IGNORECASE)
        if match:
            snippet = match.group(1)

    if not snippet:
        return None

    # Remove common leading whitespace (dedent)
    lines = snippet.split('\n')
    non_empty_lines = [l for l in lines if l.strip()]
    if not non_empty_lines:
        return None

    min_indent = min(len(l) - len(l.lstrip()) for l in non_empty_lines)

    # Dedent all lines
    dedented_lines = []
    for line in lines:
        if line.strip():
            dedented_lines.append(line[min_indent:] if len(line) >= min_indent else line)
        else:
            dedented_lines.append('')

    return '\n'.join(dedented_lines).strip()


def detect_sdk_from_path(page_path: str) -> Optional[str]:
    """
    Detect which SDK (client or hosting) based on the page path.

    Args:
        page_path: Path to the page (e.g., 'products/client-sdk/quickstart.md')

    Returns:
        'client', 'hosting', or None (search all)
    """
    if 'client-sdk' in page_path or '/client/' in page_path:
        return 'client'
    elif 'hosting-sdk' in page_path or '/hosting/' in page_path:
        return 'hosting'
    return None


def find_test_with_id(snippet_id: str, repo_root: Path, language: Optional[str] = None, sdk: Optional[str] = None, test_file_filter: Optional[str] = None) -> Optional[Tuple[str, Path]]:
    """
    Find the test file and extract snippet for the given ID.

    Args:
        snippet_id: The DocExample ID to search for
        repo_root: Root directory of the repository
        language: Optional language to search (e.g., 'csharp', 'python', 'typescript').
                  If provided, only searches that language. If None, searches all languages.
        sdk: Optional SDK to search (e.g., 'client', 'hosting').
             If provided, only searches that SDK's tests. If None, searches all SDKs.
        test_file_filter: Optional test file name or pattern to filter by (e.g., 'quickstart', 'advanced').
                         Only searches test files whose name contains this string.

    Returns:
        (snippet_code, test_file_path) or None
    """
    # Determine which languages to search
    languages_to_search = {language: LANGUAGES[language]}.items() if language and language in LANGUAGES else LANGUAGES.items()

    # Try each language
    for lang_name, config in languages_to_search:
        comment_char = config['comment']
        marker_pattern = config['marker_pattern']

        # Determine which test directories to search based on SDK
        test_dirs_dict = config['test_dirs']
        if sdk and sdk in test_dirs_dict:
            # Search only the specified SDK's test directories
            test_dirs_to_search = test_dirs_dict[sdk]
        else:
            # Search all SDKs' test directories
            test_dirs_to_search = []
            for sdk_name, dirs in test_dirs_dict.items():
                test_dirs_to_search.extend(dirs)

        # Search test directories
        for test_dir in test_dirs_to_search:
            test_path = repo_root / test_dir
            if not test_path.exists():
                continue

            # Find all test files
            for test_file in test_path.glob(config['test_pattern']):
                # Apply test file filter if provided
                if test_file_filter:
                    # Check if the test file name (stem without extension) contains the filter
                    file_stem = test_file.stem.lower()
                    if test_file_filter.lower() not in file_stem:
                        continue

                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Find all doc examples in this file
                    for match in re.finditer(marker_pattern, content, re.MULTILINE):
                        found_id = match.group(1)
                        if found_id == snippet_id:
                            # Found it! Extract the snippet from content starting at marker position
                            # This ensures we get the snippet from THIS test, not the first one in the file
                            content_from_marker = content[match.start():]
                            snippet = extract_snippet_from_source(content_from_marker, comment_char)
                            if snippet:
                                return (snippet, test_file)

                except Exception:
                    continue

    return None


class TestSnippetsPlugin(BasePlugin):
    """
    MkDocs plugin to extract snippets directly from test files.

    Processes markdown before it's rendered, replacing test:: references
    with actual code from tests.
    """

    config_scheme = (
        ('cache_snippets', config_options.Type(bool, default=True)),
    )

    def __init__(self):
        super().__init__()
        self._snippet_cache: Dict[str, str] = {}
        self._repo_root: Optional[Path] = None

    def on_config(self, config, **kwargs):
        """Initialize plugin when config is loaded."""
        # Find repo root (where mkdocs.yml is)
        docs_dir = Path(config['docs_dir'])
        self._repo_root = docs_dir.parent
        return config

    def on_page_markdown(self, markdown, page, config, files):
        """
        Process markdown before rendering.
        Replace test:: references with actual code.
        """
        if not self._repo_root:
            return markdown

        # Detect SDK from page path (client-sdk or hosting-sdk)
        page_path = page.file.src_path if page and page.file else ""
        sdk = detect_sdk_from_path(page_path)

        # Pattern: Match --8<-- test::file/snippet-id or test::file.snippet-id
        # Capture leading whitespace to preserve indentation
        # Requires both file specifier and snippet ID
        # Supports both:
        #   - test::file/snippet-id (slash separator)
        pattern = r'(^[ \t]*)--8<--\s*["\']?test::([a-zA-Z0-9_-]+)/([a-zA-Z0-9_-]+)["\']?'

        def replace_test_reference(match):
            indent = match.group(1)  # Leading whitespace
            test_file_filter = match.group(2)  # Required file/namespace
            snippet_id = match.group(3)        # Required snippet ID
            match_pos = match.start()

            # Find the code fence language by searching backwards
            # Look for ```language before this match
            fence_pattern = r'```([a-zA-Z0-9#+]+)\s*\n'
            fence_language = None

            # Search backwards from match position
            text_before = markdown[:match_pos]
            fence_matches = list(re.finditer(fence_pattern, text_before))
            if fence_matches:
                # Get the most recent code fence before this match
                last_fence = fence_matches[-1]
                fence_language = last_fence.group(1).lower()

            # Map fence language to our LANGUAGES key
            language = LANGUAGE_MAP.get(fence_language) if fence_language else None

            # Create cache key that includes language, SDK, file filter, and snippet ID
            cache_key = f"{sdk or 'all'}:{language or 'all'}:{test_file_filter}:{snippet_id}"

            # Check cache first
            if self.config['cache_snippets'] and cache_key in self._snippet_cache:
                return self._snippet_cache[cache_key]

            # Find and extract the snippet (language-specific, SDK-specific, and file-filtered)
            result = find_test_with_id(snippet_id, self._repo_root, language=language, sdk=sdk, test_file_filter=test_file_filter)

            if result:
                snippet_code, test_file = result
                relative_path = test_file.relative_to(self._repo_root)

                # Add indentation to all lines of the snippet to preserve markdown structure
                if indent:
                    indented_lines = []
                    for line in snippet_code.split('\n'):
                        if line.strip():  # Only indent non-empty lines
                            indented_lines.append(indent + line)
                        else:
                            indented_lines.append(line)
                    snippet_code = '\n'.join(indented_lines)

                # Return just the snippet code (no source comment to avoid visibility in code blocks)
                # Cache it
                if self.config['cache_snippets']:
                    self._snippet_cache[cache_key] = snippet_code

                return snippet_code
            else:
                # Snippet not found - show error in docs
                lang_note = f" in {language} tests" if language else ""
                sdk_note = f" for {sdk} SDK" if sdk else ""
                error_msg = (
                    f"<!-- ERROR: Test snippet '{snippet_id}' not found in '{test_file_filter}' test file{lang_note}{sdk_note} -->\n"
                    f"Error: Could not find test with DocExample ID '{snippet_id}' in '{test_file_filter}' test file{lang_note}{sdk_note}\n"
                    f"Please check:\n"
                    f"1. Test file containing '{test_file_filter}' exists (e.g., QuickstartTests.cs, test_quickstart.py, quickstart.test.ts)\n"
                    f"2. Test has [DocExample(\"{snippet_id}\")] marker (C#), @pytest.mark.doc_example(\"{snippet_id}\") (Python), or @docExample {snippet_id} (TypeScript)\n"
                    f"3. Test has proper snippet markers (#region Snippet / #endregion, <snippet> / </snippet>, or Act/Assert comments)\n"
                    f"4. Snippet ID matches exactly\n"
                    f"5. Code fence language ({fence_language if fence_language else 'unknown'}) maps to correct test directory\n"
                    f"6. Page path ({page_path}) matches correct SDK directory (client-sdk or hosting-sdk)"
                )
                return error_msg

        # Replace all test:: references (MULTILINE flag allows ^ to match start of each line)
        processed_markdown = re.sub(pattern, replace_test_reference, markdown, flags=re.MULTILINE)

        return processed_markdown


def makeExtension(**kwargs):
    """Entry point for MkDocs plugin."""
    return TestSnippetsPlugin(**kwargs)
