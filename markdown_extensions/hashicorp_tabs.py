"""
HashiCorp Tabs Extension for MkDocs
Transforms Material tabs into HashiCorp tab structure
"""

from markdown import Extension
from markdown.postprocessors import Postprocessor
import re
import uuid


class HashiCorpTabsPostprocessor(Postprocessor):
    """Postprocessor that transforms Material tabs into HashiCorp tabs"""

    def run(self, text):
        """Transform all tabbed-set elements into HashiCorp tab structure"""
        # Process each tabbed-set individually
        offset = 0
        while True:
            match = re.search(r'<div class="tabbed-set[^>]*>', text[offset:])
            if not match:
                break

            start = offset + match.start()
            # Find the matching closing div
            depth = 1
            pos = start + len(match.group(0))
            while depth > 0 and pos < len(text):
                if text[pos:pos+5] == '<div ':
                    depth += 1
                    pos += 5
                elif text[pos:pos+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        end = pos + 6
                        break
                    pos += 6
                else:
                    pos += 1

            if depth == 0:
                original = text[start:end]
                replacement = self.convert_to_hashicorp_tabs(original)
                text = text[:start] + replacement + text[end:]
                offset = start + len(replacement)
            else:
                break

        return text

    def convert_to_hashicorp_tabs(self, html):
        """Convert a single tabbed-set to HashiCorp structure"""
        # Extract tab labels
        label_pattern = r'<label[^>]*>([^<]+)</label>'
        labels = re.findall(label_pattern, html)

        if not labels:
            return html  # No tabs found, return original

        # Extract tab content blocks - match each tabbed-block
        contents = []
        pattern = r'<div class="tabbed-block">'
        pos = 0
        while True:
            match = re.search(pattern, html[pos:])
            if not match:
                break

            start = pos + match.start() + len(match.group(0))
            # Find matching closing div for this tabbed-block
            depth = 1
            pos_inner = start
            while depth > 0 and pos_inner < len(html):
                if html[pos_inner:pos_inner+5] == '<div ':
                    depth += 1
                    pos_inner += 5
                elif html[pos_inner:pos_inner+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        contents.append(html[start:pos_inner])
                        break
                    pos_inner += 6
                else:
                    pos_inner += 1

            pos = pos_inner + 6

        if len(contents) != len(labels):
            return html  # Mismatch, return original

        # Generate unique IDs for this tab group
        group_id = str(uuid.uuid4())[:8]

        # Build HashiCorp tab structure
        result = ['<div class="mdx-tabs_tabsWrapper__eBd6p"><div>']
        result.append('<div class="tabs_tabControls__T_UOv tabs_showAnchorLine__oSYFX tabs_allowNestedStyles__gpKFS">')
        result.append('<div class="tab-button-controls_tabList__ueYEe" role="tablist">')

        # Add tab buttons
        for i, label in enumerate(labels):
            is_selected = 'true' if i == 0 else 'false'
            tabindex = '0' if i == 0 else '-1'
            panel_id = f'panel-{i}-{group_id}'
            tab_id = f'tab-{i}-{group_id}'

            result.append(f'''<button class="tab-button-controls_tabButton__l1jN9 g-focus-ring-from-box-shadow" aria-controls="{panel_id}" aria-selected="{is_selected}" id="{tab_id}" role="tab" tabindex="{tabindex}" type="button"><span class="tab-button-controls_label__GDzfu hds-typography-body-200">{label}</span></button>''')

        result.append('</div></div>')  # Close tab controls

        # Add tab panels
        for i, content in enumerate(contents):
            is_hidden = 'true' if i > 0 else 'false'
            panel_id = f'panel-{i}-{group_id}'
            tab_id = f'tab-{i}-{group_id}'

            result.append(f'''<div aria-hidden="{is_hidden}" aria-labelledby="{tab_id}" class="tabs_tabPanel__lKCo_ tabs_allowNestedStyles__gpKFS" id="{panel_id}" role="tabpanel">{content}</div>''')

        result.append('</div></div>')  # Close wrapper divs

        return ''.join(result)


class HashiCorpCodeBlocksPostprocessor(Postprocessor):
    """Postprocessor that transforms Material code blocks into HashiCorp code blocks"""

    # Map Pygments token classes to HashiCorp CSS variable colors
    TOKEN_COLOR_MAP = {
        'c1': '--code-block-color-comment',      # Comments
        'c': '--code-block-color-comment',
        'cm': '--code-block-color-comment',
        'cp': '--code-block-color-preprocessor',
        'k': '--code-block-color-keyword',       # Keywords
        'kc': '--code-block-color-keyword',
        'kd': '--code-block-color-keyword',
        'kn': '--code-block-color-keyword',
        'kp': '--code-block-color-keyword',
        'kr': '--code-block-color-keyword',
        'kt': '--code-block-color-keyword',
        's': '--code-block-color-string',        # Strings
        's1': '--code-block-color-string',
        's2': '--code-block-color-string',
        'nb': '--code-block-color-function',     # Built-ins
        'n': '--code-block-color-token',         # Names
        'nc': '--code-block-color-function',
        'nf': '--code-block-color-function',
        'w': '--code-block-color-token',         # Whitespace
        'o': '--code-block-color-punctuation',   # Operators
        'p': '--code-block-color-punctuation',   # Punctuation
        'err': '--code-block-color-error',       # Errors
    }

    def run(self, text):
        """Transform all code blocks"""
        offset = 0
        while True:
            # Find highlight divs (Material's code block wrapper)
            match = re.search(r'<div class="(?:language-[^\s]+\s+)?highlight">', text[offset:])
            if not match:
                break

            start = offset + match.start()
            # Find the matching closing div
            depth = 1
            pos = start + len(match.group(0))
            while depth > 0 and pos < len(text):
                if text[pos:pos+5] == '<div ':
                    depth += 1
                    pos += 5
                elif text[pos:pos+6] == '</div>':
                    depth -= 1
                    if depth == 0:
                        end = pos + 6
                        break
                    pos += 6
                else:
                    pos += 1

            if depth == 0:
                original = text[start:end]
                # Extract language from parent div if exists
                lang_match = re.search(r'<div class="language-([^\s"]+)', text[max(0, start-100):start])
                language = lang_match.group(1) if lang_match else 'text'

                replacement = self.convert_to_hashicorp_codeblock(original, language)
                text = text[:start] + replacement + text[end:]
                offset = start + len(replacement)
            else:
                break

        return text

    def convert_to_hashicorp_codeblock(self, html, language):
        """Convert a single code block to HashiCorp structure"""
        # Extract the code content
        code_match = re.search(r'<code>(.*?)</code>', html, re.DOTALL)
        if not code_match:
            return html

        code_content = code_match.group(1)

        # Extract the line content from Material's structure
        # Material wraps all code in: <span class="line">...</span>
        line_match = re.search(r'<span class="line">(.*?)</span>', code_content, re.DOTALL)

        if line_match:
            full_content = line_match.group(1)
        else:
            # Fallback: no line span found, work with raw content
            full_content = code_content

        # Remove Material's line number anchors
        full_content = re.sub(r'<a[^>]*id="__codelineno-[^"]*"[^>]*></a>', '', full_content)

        # Remove Material's __span wrapper: <span id="__span-X-Y">CONTENT</span>
        # Use a loop to unwrap nested spans
        while True:
            new_content = re.sub(r'<span id="__span-[^"]+">(.+?)</span>', r'\1', full_content, count=1, flags=re.DOTALL)
            if new_content == full_content:
                break
            full_content = new_content

        # First, unwrap all <span class="w"> tags by matching and removing them
        # Use depth tracking to handle nested spans within class="w" spans
        max_iterations = 20
        for _ in range(max_iterations):
            # Find the first <span class="w">
            match = re.search(r'<span class="w">', full_content)
            if not match:
                break

            start = match.start()
            pos = match.end()

            # Find the matching closing </span> using depth tracking
            depth = 1
            while depth > 0 and pos < len(full_content):
                if full_content[pos:pos+6] == '<span ':
                    depth += 1
                    pos += 6
                elif full_content[pos:pos+7] == '</span>':
                    depth -= 1
                    if depth == 0:
                        # Remove the opening and closing tags but keep content
                        content = full_content[match.end():pos]
                        full_content = full_content[:start] + content + full_content[pos+7:]
                        break
                    pos += 7
                else:
                    pos += 1

            if depth != 0:
                # Couldn't find matching close tag
                break

        # Transform Pygments spans to inline styles
        def replace_span(match):
            classes = match.group(1)
            content = match.group(2)

            # Move trailing newlines outside the span
            trailing_newlines = ''
            while content.endswith('\n'):
                content = content[:-1]
                trailing_newlines += '\n'

            # Find color variable for this token type
            color_var = None
            for token_class, var in self.TOKEN_COLOR_MAP.items():
                if token_class in classes.split():
                    color_var = var
                    break

            if color_var:
                return f'<span style="color: var({color_var});">{content}</span>{trailing_newlines}'
            else:
                # If no color mapping, just return the content without a span
                return f'{content}{trailing_newlines}'

        # Replace all Pygments token spans (iterate to handle nested spans)
        # Start from innermost spans (those with no nested tags) and work outward
        for _ in range(max_iterations):
            # Match spans that don't contain other spans (innermost first)
            new_content = re.sub(r'<span class="([^"]+)">([^<]*)</span>', replace_span, full_content)
            if new_content == full_content:
                break
            full_content = new_content

        # Final cleanup: unwrap ALL remaining class-based spans using depth tracking
        # This handles spans with nested content that the regex couldn't match
        for _ in range(max_iterations):
            match = re.search(r'<span class="[^"]+">', full_content)
            if not match:
                break

            start = match.start()
            pos = match.end()

            # Find the matching closing </span> using depth tracking
            depth = 1
            while depth > 0 and pos < len(full_content):
                if full_content[pos:pos+6] == '<span ':
                    depth += 1
                    pos += 6
                elif full_content[pos:pos+7] == '</span>':
                    depth -= 1
                    if depth == 0:
                        # Keep content but remove the span wrapper
                        content = full_content[match.end():pos]
                        full_content = full_content[:start] + content + full_content[pos+7:]
                        break
                    pos += 7
                else:
                    pos += 1

            if depth != 0:
                # Couldn't find matching close tag
                break

        # Now split by literal newlines to get individual lines
        lines_raw = full_content.split('\n')

        processed_lines = []
        for line in lines_raw:
            # Strip HTML-only whitespace but preserve code indentation
            stripped = line.strip()
            if stripped:
                processed_lines.append(line)
            elif not processed_lines:  # Skip leading empty lines
                continue
            else:  # Keep empty lines in the middle for spacing
                processed_lines.append('')

        # Remove trailing empty lines more aggressively
        while processed_lines:
            # Check if last line is empty or only contains HTML whitespace
            last = processed_lines[-1]
            if not last or not last.strip():
                processed_lines.pop()
            else:
                break

        # Wrap each line in HashiCorp structure
        wrapped_lines = []
        for line_content in processed_lines:
            wrapped_lines.append(f'<span class="line-of-code__mDztA line-highlight-first__OMDUP line-highlight-last__qC6nm"><span class="line">{line_content}</span>\n</span>')

        formatted_code = ''.join(wrapped_lines)

        # Generate unique ID
        block_id = str(uuid.uuid4())[:6]

        # Build HashiCorp code block structure
        result = f'''<div class="code-block__dOm6M dark__aBMo7 undefined is-standalone__WLWxy language-{language} mdx-code-blocks_codeBlockMargin__xk4yr">
<div class="header__42Fek"></div>
<div class="body__pLFmP">
<pre style="display: none;">{formatted_code}</pre>
<pre class="code__J06se" id=":r{block_id}:"><code><span>{formatted_code}</span></code></pre>
<button type="button" class="button__gOWvd size-small__kT0Jp icon-only__5c-is color-secondary-white__AseI0 copy-button__uXOTd idle__1ofXr copy-button__nMsTD" aria-label="Copy" aria-describedby=":r{block_id}:">
<svg class="flight-icon__f6lPO flight-icon-clipboard-copy display-inline__ItStG" aria-hidden="true" fill="currentColor" width="12" height="12" viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg">
<path fill="currentColor" fill-rule="evenodd" d="M2 4.75C2 3.784 2.784 3 3.75 3h5.586c.464 0 .909.184 1.237.513l2.914 2.914c.329.328.513.773.513 1.237v6.586A1.75 1.75 0 0112.25 16h-8.5A1.75 1.75 0 012 14.25V4.75zm1.75-.25a.25.25 0 00-.25.25v9.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25V7.664a.25.25 0 00-.073-.177l-2.914-2.914a.25.25 0 00-.177-.073H3.75z" clip-rule="evenodd"/>
<path fill="currentColor" d="M4.5 6.5a.75.75 0 01.75-.75h4.5a.75.75 0 010 1.5h-4.5A.75.75 0 014.5 6.5zm0 3a.75.75 0 01.75-.75h4.5a.75.75 0 010 1.5h-4.5A.75.75 0 014.5 9.5zm.75 2.25a.75.75 0 000 1.5h2.5a.75.75 0 000-1.5h-2.5z"/>
</svg>
</button>
</div>
</div>'''

        return result


class HashiCorpTabsExtension(Extension):
    """Extension class for HashiCorp Tabs and Code Blocks"""

    def extendMarkdown(self, md):
        """Register the postprocessors"""
        md.postprocessors.register(
            HashiCorpTabsPostprocessor(md),
            'hashicorp_tabs',
            0  # Run after other postprocessors
        )
        md.postprocessors.register(
            HashiCorpCodeBlocksPostprocessor(md),
            'hashicorp_codeblocks',
            -1  # Run after tabs
        )


def makeExtension(**kwargs):
    """Factory function for creating the extension"""
    return HashiCorpTabsExtension(**kwargs)
