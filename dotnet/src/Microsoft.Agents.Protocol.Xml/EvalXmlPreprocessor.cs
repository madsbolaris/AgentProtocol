using System;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

namespace Microsoft.Agents.Protocol.Xml;

/// <summary>
/// Preprocesses EvalXML (not-valid-XML) into valid XML by wrapping raw block content in CDATA tags.
///
/// Raw block elements (assert, metric, args) can contain unescaped XML characters like &lt;, &gt;, &amp;, etc.
/// This preprocessor transforms them into valid XML by wrapping their content in CDATA sections.
/// </summary>
public static class EvalXmlPreprocessor
{
    private static readonly HashSet<string> RawBlockTags = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
    {
        "assert",
        "metric",
        "args"
    };

    // Regex to match XML tags: <(/?)tagName(attributes)?(/?)>
    private static readonly Regex TagRegex = new Regex(
        @"^<(\/?)(\w[\w-]*)((?:\s+[^>]*)?)(\/?)\s*>",
        RegexOptions.Compiled
    );

    /// <summary>
    /// Preprocesses EvalXML content by wrapping raw block element content in CDATA sections.
    /// </summary>
    /// <param name="input">The raw EvalXML content (potentially invalid XML)</param>
    /// <returns>Valid XML with raw block content wrapped in CDATA</returns>
    public static string Preprocess(string input)
    {
        if (string.IsNullOrEmpty(input))
        {
            return input;
        }

        var output = new StringBuilder();
        int pos = 0;

        while (pos < input.Length)
        {
            // Find next '<'
            int tagStart = input.IndexOf('<', pos);
            if (tagStart == -1)
            {
                // No more tags, append rest and break
                output.Append(input.Substring(pos));
                break;
            }

            // Append text before tag
            output.Append(input.Substring(pos, tagStart - pos));

            // Try to parse tag
            var match = TagRegex.Match(input.Substring(tagStart));
            if (!match.Success)
            {
                // Not a valid tag, append char and continue
                output.Append(input[tagStart]);
                pos = tagStart + 1;
                continue;
            }

            string fullTag = match.Value;
            string closingSlash = match.Groups[1].Value;
            string tagName = match.Groups[2].Value;
            string attributes = match.Groups[3].Value;
            string selfClosing = match.Groups[4].Value;

            // Check if this is a raw block opening tag (not closing, not self-closing)
            if (string.IsNullOrEmpty(closingSlash) &&
                RawBlockTags.Contains(tagName) &&
                string.IsNullOrEmpty(selfClosing))
            {
                // Find closing tag
                string closingTag = $"</{tagName}>";
                int contentStart = tagStart + fullTag.Length;
                int contentEnd = input.IndexOf(closingTag, contentStart, StringComparison.OrdinalIgnoreCase);

                if (contentEnd == -1)
                {
                    throw new InvalidOperationException($"Missing closing tag for <{tagName}>");
                }

                // Extract raw content
                string rawContent = input.Substring(contentStart, contentEnd - contentStart);

                // Wrap in CDATA
                string cdataContent = WrapInCDATA(rawContent);

                // Output: opening tag + CDATA + closing tag
                output.Append(fullTag);
                output.Append(cdataContent);
                output.Append(closingTag);

                // Move position past closing tag
                pos = contentEnd + closingTag.Length;
            }
            else if (string.IsNullOrEmpty(closingSlash) &&
                     RawBlockTags.Contains(tagName) &&
                     !string.IsNullOrEmpty(selfClosing))
            {
                // Self-closing raw block tag is invalid
                throw new InvalidOperationException(
                    $"Raw block element <{tagName}/> cannot be self-closing. " +
                    $"Use <{tagName}></{tagName}> for empty content."
                );
            }
            else
            {
                // Normal tag, append as-is
                output.Append(fullTag);
                pos = tagStart + fullTag.Length;
            }
        }

        return output.ToString();
    }

    /// <summary>
    /// Wraps content in CDATA section, handling the edge case where content contains "]]>".
    /// </summary>
    /// <param name="content">The raw content to wrap</param>
    /// <returns>Content wrapped in CDATA section(s)</returns>
    private static string WrapInCDATA(string content)
    {
        // Check if content contains the CDATA end marker "]]>"
        if (!content.Contains("]]>"))
        {
            // Simple case: no CDATA end marker
            return $"<![CDATA[{content}]]>";
        }
        else
        {
            // Complex case: split on "]]>" and use standard CDATA splitting technique
            // Each part becomes: <![CDATA[part]]]]><![CDATA[>]]>
            var parts = content.Split(new[] { "]]>" }, StringSplitOptions.None);
            var result = new StringBuilder();

            for (int i = 0; i < parts.Length; i++)
            {
                if (i > 0)
                {
                    // Add the "]]>" split across CDATA sections
                    result.Append("]]]]><![CDATA[>]]><![CDATA[");
                }
                result.Append(parts[i]);
            }

            // Wrap the entire sequence
            return $"<![CDATA[{result}]]>";
        }
    }
}
