/**
 * EvalXML Preprocessor
 *
 * Transforms EvalXML (not-valid-XML) into valid XML by wrapping raw block content in CDATA tags.
 *
 * Raw block elements (assert, metric, args) can contain unescaped XML characters like <, >, &, etc.
 * This preprocessor transforms them into valid XML by wrapping their content in CDATA sections.
 */

const RAW_BLOCK_TAGS = new Set(['assert', 'metric', 'args']);

// Regex to match XML tags: <(/?)tagName(attributes)?(/?)>
const TAG_REGEX = /^<(\/?)(\w[\w-]*)((?:\s+[^>]*)?)(\/?)\s*>/i;

/**
 * Preprocesses EvalXML content by wrapping raw block element content in CDATA sections.
 *
 * @param input The raw EvalXML content (potentially invalid XML)
 * @returns Valid XML with raw block content wrapped in CDATA
 * @throws Error if a raw block element is missing its closing tag or is self-closing
 */
export function preprocess(input: string): string {
  if (!input) {
    return input;
  }

  let output = '';
  let pos = 0;

  while (pos < input.length) {
    // Find next '<'
    const tagStart = input.indexOf('<', pos);
    if (tagStart === -1) {
      // No more tags, append rest and break
      output += input.slice(pos);
      break;
    }

    // Append text before tag
    output += input.slice(pos, tagStart);

    // Try to parse tag
    const tagMatch = input.slice(tagStart).match(TAG_REGEX);
    if (!tagMatch) {
      // Not a valid tag, append char and continue
      output += input[tagStart];
      pos = tagStart + 1;
      continue;
    }

    const [fullTag, closingSlash, tagName, , selfClosing] = tagMatch;

    // Check if this is a raw block opening tag (not closing, not self-closing)
    if (!closingSlash && RAW_BLOCK_TAGS.has(tagName.toLowerCase()) && !selfClosing) {
      // Find closing tag
      const closingTag = `</${tagName}>`;
      const contentStart = tagStart + fullTag.length;
      const contentEnd = input.toLowerCase().indexOf(closingTag.toLowerCase(), contentStart);

      if (contentEnd === -1) {
        throw new Error(`Missing closing tag for <${tagName}>`);
      }

      // Extract raw content
      const rawContent = input.slice(contentStart, contentEnd);

      // Wrap in CDATA
      const cdataContent = wrapInCDATA(rawContent);

      // Output: opening tag + CDATA + closing tag
      output += fullTag + cdataContent + input.slice(contentEnd, contentEnd + closingTag.length);

      // Move position past closing tag
      pos = contentEnd + closingTag.length;
    } else if (!closingSlash && RAW_BLOCK_TAGS.has(tagName.toLowerCase()) && selfClosing) {
      // Self-closing raw block tag is invalid
      throw new Error(
        `Raw block element <${tagName}/> cannot be self-closing. ` +
        `Use <${tagName}></${tagName}> for empty content.`
      );
    } else {
      // Normal tag, append as-is
      output += fullTag;
      pos = tagStart + fullTag.length;
    }
  }

  return output;
}

/**
 * Wraps content in CDATA section, handling the edge case where content contains "]]>".
 *
 * @param content The raw content to wrap
 * @returns Content wrapped in CDATA section(s)
 */
function wrapInCDATA(content: string): string {
  // Check if content contains the CDATA end marker "]]>"
  if (!content.includes(']]>')) {
    // Simple case: no CDATA end marker
    return `<![CDATA[${content}]]>`;
  } else {
    // Complex case: split on "]]>" and use standard CDATA splitting technique
    // Each occurrence of "]]>" becomes: ]]]]><![CDATA[>
    const parts = content.split(']]>');
    const result = parts.map((part, i) => {
      if (i > 0) {
        return ']]]]><![CDATA[>' + part;
      }
      return part;
    }).join('');

    // Wrap the entire sequence
    return `<![CDATA[${result}]]>`;
  }
}
