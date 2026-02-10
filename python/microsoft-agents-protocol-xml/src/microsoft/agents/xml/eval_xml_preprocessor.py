"""
EvalXML Preprocessor

Transforms EvalXML (not-valid-XML) into valid XML by wrapping raw block content in CDATA tags.

Raw block elements (assert, metric, args) can contain unescaped XML characters like <, >, &, etc.
This preprocessor transforms them into valid XML by wrapping their content in CDATA sections.
"""

import re
from typing import Set

# Raw block tags that need CDATA wrapping
RAW_BLOCK_TAGS: Set[str] = {"assert", "metric", "args"}

# Regex to match XML tags: <(/?)tagName(attributes)?(/?)>
TAG_REGEX = re.compile(r"^<(\/?)(\w[\w-]*)((?:\s+[^>]*)?)(\/?)\s*>", re.IGNORECASE)


def preprocess(input_xml: str) -> str:
    """
    Preprocesses EvalXML content by wrapping raw block element content in CDATA sections.

    Args:
        input_xml: The raw EvalXML content (potentially invalid XML)

    Returns:
        Valid XML with raw block content wrapped in CDATA

    Raises:
        ValueError: If a raw block element is missing its closing tag or is self-closing
    """
    if not input_xml:
        return input_xml

    output = []
    pos = 0

    while pos < len(input_xml):
        # Find next '<'
        tag_start = input_xml.find("<", pos)
        if tag_start == -1:
            # No more tags, append rest and break
            output.append(input_xml[pos:])
            break

        # Append text before tag
        output.append(input_xml[pos:tag_start])

        # Try to parse tag
        match = TAG_REGEX.match(input_xml[tag_start:])
        if not match:
            # Not a valid tag, append char and continue
            output.append(input_xml[tag_start])
            pos = tag_start + 1
            continue

        full_tag = match.group(0)
        closing_slash = match.group(1)
        tag_name = match.group(2)
        attributes = match.group(3)
        self_closing = match.group(4)

        # Check if this is a raw block opening tag (not closing, not self-closing)
        if not closing_slash and tag_name.lower() in RAW_BLOCK_TAGS and not self_closing:
            # Find closing tag
            closing_tag = f"</{tag_name}>"
            content_start = tag_start + len(full_tag)
            content_end = input_xml.lower().find(closing_tag.lower(), content_start)

            if content_end == -1:
                raise ValueError(f"Missing closing tag for <{tag_name}>")

            # Extract raw content
            raw_content = input_xml[content_start:content_end]

            # Wrap in CDATA
            cdata_content = _wrap_in_cdata(raw_content)

            # Output: opening tag + CDATA + closing tag
            output.append(full_tag)
            output.append(cdata_content)
            output.append(input_xml[content_end:content_end + len(closing_tag)])

            # Move position past closing tag
            pos = content_end + len(closing_tag)

        elif not closing_slash and tag_name.lower() in RAW_BLOCK_TAGS and self_closing:
            # Self-closing raw block tag is invalid
            raise ValueError(
                f"Raw block element <{tag_name}/> cannot be self-closing. "
                f"Use <{tag_name}></{tag_name}> for empty content."
            )
        else:
            # Normal tag, append as-is
            output.append(full_tag)
            pos = tag_start + len(full_tag)

    return "".join(output)


def _wrap_in_cdata(content: str) -> str:
    """
    Wraps content in CDATA section, handling the edge case where content contains "]]>".

    Args:
        content: The raw content to wrap

    Returns:
        Content wrapped in CDATA section(s)
    """
    # Check if content contains the CDATA end marker "]]>"
    if "]]>" not in content:
        # Simple case: no CDATA end marker
        return f"<![CDATA[{content}]]>"
    else:
        # Complex case: split on "]]>" and use standard CDATA splitting technique
        # Each occurrence of "]]>" becomes: ]]]]><![CDATA[>
        parts = content.split("]]>")
        result = []

        for i, part in enumerate(parts):
            if i > 0:
                # Add the "]]>" split across CDATA sections
                result.append("]]]]><![CDATA[>")
            result.append(part)

        # Wrap the entire sequence
        return f"<![CDATA[{''.join(result)}]]>"
