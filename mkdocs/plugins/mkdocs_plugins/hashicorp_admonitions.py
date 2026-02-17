"""
Custom MkDocs plugin to render HashiCorp-style alerts from MkDocs admonition syntax.

Converts:
    !!! note "Title"
        Content here

To HashiCorp HDS alert HTML matching the schema:
    <div class="alert alert-info g-type-body">
      <p><strong>Note:</strong> Content here</p>
    </div>
"""

import re
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor


class HashiCorpAdmonitionPreprocessor(Preprocessor):
    """Preprocessor to convert !!! admonitions to HashiCorp alert HTML."""

    # Pattern to match MkDocs admonitions
    ADMONITION_PATTERN = re.compile(
        r'^!!!\s+(note|info|warning|danger|success|tip)\s*(?:"([^"]*)")?\s*$',
        re.MULTILINE
    )

    # Mapping of admonition types to HashiCorp alert classes
    TYPE_MAP = {
        'note': 'alert-info',
        'info': 'alert-info',
        'tip': 'alert-info',
        'warning': 'alert-warning',
        'danger': 'alert-danger',
        'success': 'alert-success',
    }

    # Mapping of types to label text
    LABEL_MAP = {
        'note': 'Note',
        'info': 'Info',
        'tip': 'Tip',
        'warning': 'Warning',
        'danger': 'Danger',
        'success': 'Success',
    }

    def run(self, lines):
        """Process the markdown lines and replace admonition blocks."""
        new_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            match = self.ADMONITION_PATTERN.match(line)

            if match:
                admonition_type = match.group(1).lower()
                custom_title = match.group(2)

                # Collect the indented content lines
                i += 1
                content_lines = []
                while i < len(lines) and (lines[i].startswith('    ') or lines[i].strip() == ''):
                    if lines[i].strip():
                        content_lines.append(lines[i][4:])  # Remove 4-space indent
                    else:
                        content_lines.append('')  # Preserve empty lines for markdown structure
                    i += 1

                # Generate HashiCorp alert HTML
                html = self._generate_alert_html(
                    admonition_type,
                    custom_title,
                    content_lines
                )
                new_lines.append(html)
                continue

            new_lines.append(line)
            i += 1

        return new_lines

    def _generate_alert_html(self, admonition_type, custom_title, content_lines):
        """Generate HashiCorp-style alert HTML with markdown content preserved."""
        alert_class = self.TYPE_MAP.get(admonition_type, 'alert-info')
        label = custom_title or self.LABEL_MAP.get(admonition_type, 'Note')

        # Join content lines and preserve markdown (will be processed by markdown parser)
        content = '\n'.join(content_lines).strip()

        # Check if content starts with a list or code block - needs separator
        needs_separator = content.startswith(('-', '*', '+', '```', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.'))

        # Use md_in_html format to allow markdown processing within the HTML block
        # The markdown parser will process the content after this preprocessor runs
        if needs_separator:
            # Lists and code blocks need to be on separate lines from the label
            html = f'''<div class="alert {alert_class} g-type-body" markdown="1">

**{label}:**

{content}

</div>'''
        else:
            # Regular text can flow after the label
            html = f'''<div class="alert {alert_class} g-type-body" markdown="1">

**{label}:** {content}

</div>'''

        return html


class HashiCorpAdmonitionExtension(Extension):
    """Markdown extension for HashiCorp admonitions."""

    def extendMarkdown(self, md):
        """Register the preprocessor with markdown."""
        md.preprocessors.register(
            HashiCorpAdmonitionPreprocessor(md),
            'hashicorp_admonitions',
            200  # High priority - before admonition extension
        )


def makeExtension(**kwargs):
    """Required function for markdown extensions."""
    return HashiCorpAdmonitionExtension(**kwargs)
