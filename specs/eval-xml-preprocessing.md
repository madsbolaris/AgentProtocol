# EvalXML Preprocessing Specification

## Overview

EvalXML preprocessing is a critical step that prepares XML content containing mixed code blocks for safe XML serialization. The preprocessing algorithm wraps raw content blocks (code, script, style) in CDATA sections to prevent XML parsing errors from special characters like `<`, `>`, and `&`.

## Purpose

When serializing content that contains both XML markup and raw code blocks, standard XML serialization will fail or corrupt the code if it contains XML special characters. The EvalXML preprocessor solves this by:

1. Identifying raw content blocks that need protection
2. Wrapping their content in CDATA sections
3. Preserving all other XML structure unchanged

## Algorithm

### High-Level Flow

```
Input: XML string with mixed content
  ↓
1. Identify raw block elements (code, script, style)
  ↓
2. For each raw block:
   - Extract opening tag
   - Extract content between tags
   - Wrap content in CDATA if not already wrapped
   - Reconstruct block with CDATA-wrapped content
  ↓
Output: XML string safe for serialization
```

### Raw Block Elements

The following XML elements are considered "raw blocks" and their content should be wrapped in CDATA:

- `<assert>` - Test assertions that may contain comparison operators
- `<metric>` - Metric expressions that may contain mathematical operators
- `<args>` - Function arguments that may contain code or special characters

### CDATA Wrapping Rules

#### Rule 1: Identify Raw Blocks
Use regex pattern to find all raw block elements:
```regex
<(assert|metric|args)(\s+[^>]*)?>([\s\S]*?)<\/\1>
```

Pattern breakdown:
- `<(assert|metric|args)` - Opening tag for raw block element (capture group 1)
- `(\s+[^>]*)?` - Optional attributes (capture group 2)
- `>` - End of opening tag
- `([\s\S]*?)` - Content (capture group 3) - non-greedy match of any character including newlines
- `<\/\1>` - Closing tag matching the opening tag

#### Rule 2: Check if Already Wrapped
Content is considered already CDATA-wrapped if it matches:
```regex
^\s*<!\[CDATA\[[\s\S]*\]\]>\s*$
```

Pattern breakdown:
- `^\s*` - Optional leading whitespace
- `<!\[CDATA\[` - CDATA opening marker
- `[\s\S]*` - Any content including newlines
- `\]\]>` - CDATA closing marker
- `\s*$` - Optional trailing whitespace

If content is already wrapped, skip it.

#### Rule 3: Wrap Content
For content that is not already wrapped:
```xml
<![CDATA[{original_content}]]>
```

**Important**: Do not add extra whitespace or newlines. Preserve the exact original content inside the CDATA section.

#### Rule 4: Reconstruct Block
```xml
<{tag}{attributes}><![CDATA[{content}]]></{tag}>
```

### Edge Cases

#### Empty Content
```xml
<!-- Input -->
<assert></assert>

<!-- Output (no CDATA needed for empty content) -->
<assert></assert>
```

Note: Implementations should handle empty raw blocks gracefully. The TypeScript/Python/.NET implementations will process empty blocks but not wrap empty content.

#### Already Wrapped Content
This edge case does not apply to the current implementations, as they use a character-by-character parsing approach rather than regex replacement. The implementations will always wrap raw block content.

#### Multiple Raw Blocks
```xml
<!-- Input -->
<eval>
  <assert>x == 1</assert>
  <result>true</result>
  <metric>y > 0</metric>
</eval>

<!-- Output (each raw block independently wrapped) -->
<eval>
  <assert><![CDATA[x == 1]]></assert>
  <result>true</result>
  <metric><![CDATA[y > 0]]></metric>
</eval>
```

#### Nested XML-Like Characters
```xml
<!-- Input -->
<assert>x < 5 && y > 3</assert>

<!-- Output (< and > protected by CDATA) -->
<assert><![CDATA[x < 5 && y > 3]]></assert>
```

#### Content with "]]>" Sequence
```xml
<!-- Input -->
<args>data]]>moredata</args>

<!-- Output (special CDATA escaping for ]]>) -->
<args><![CDATA[data]]]]><![CDATA[>moredata]]></args>
```

Note: The `]]>` sequence must be split across CDATA sections because it would otherwise terminate the CDATA prematurely.

#### Attributes on Raw Block Elements
```xml
<!-- Input -->
<assert type="equality" severity="error">x == 5</assert>

<!-- Output (preserve attributes exactly) -->
<assert type="equality" severity="error"><![CDATA[x == 5]]></assert>
```

#### Multiline Content
```xml
<!-- Input -->
<args>
{
  "name": "test",
  "value": 123
}
</args>

<!-- Output (preserve exact formatting including newlines) -->
<args><![CDATA[
{
  "name": "test",
  "value": 123
}
]]></args>
```

#### Self-Closing Raw Block Elements
```xml
<!-- Input -->
<assert />

<!-- Output (error - self-closing raw blocks are not allowed) -->
Error: Raw block element <assert/> cannot be self-closing. Use <assert></assert> for empty content.
```

## Reference Implementation (Pseudocode)

```pseudocode
function preprocess_evalxml(xml_string: string) -> string:
    // Pattern to match raw block elements with their content
    pattern = /<(code|script|style)(\s+[^>]*)?>([\s\S]*?)<\/\1>/g

    result = xml_string.replace_all_with_callback(pattern, function(match):
        tag = match.group(1)           // e.g., "code"
        attributes = match.group(2)    // e.g., " lang='python'" or ""
        content = match.group(3)       // the inner content

        // Check if content is empty or already CDATA-wrapped
        if is_empty_or_whitespace(content):
            return match.full_match    // no change needed

        if is_cdata_wrapped(content):
            return match.full_match    // already wrapped, no change

        // Wrap content in CDATA
        cdata_content = "<![CDATA[" + content + "]]>"

        // Reconstruct the element
        if attributes is not null:
            return "<" + tag + attributes + ">" + cdata_content + "</" + tag + ">"
        else:
            return "<" + tag + ">" + cdata_content + "</" + tag + ">"
    )

    return result

function is_cdata_wrapped(content: string) -> bool:
    // Check if content is already wrapped in CDATA
    cdata_pattern = /^\s*<!\[CDATA\[[\s\S]*\]\]>\s*$/
    return content.matches(cdata_pattern)

function is_empty_or_whitespace(content: string) -> bool:
    return content.trim().length == 0
```

## Implementation Notes

### Performance Considerations

1. **Single Pass**: Process the XML string in a single pass using regex replacement with callback
2. **Non-Greedy Matching**: Use `*?` instead of `*` to prevent matching across multiple blocks
3. **Minimal Copying**: Only reconstruct blocks that need CDATA wrapping

### Error Handling

The preprocessing is designed to be **fail-safe**:
- Malformed XML input will still be processed, with CDATA wrapping applied to recognized patterns
- Invalid CDATA in input will be double-wrapped, which is safe (outer CDATA treats inner as text)
- Missing closing tags will not cause the preprocessor to fail, though subsequent XML parsing may

### Testing Strategy

Implementations should include tests for:
1. ✅ Basic CDATA wrapping (simple code block)
2. ✅ Already wrapped content (no double-wrapping)
3. ✅ Multiple raw blocks in same document
4. ✅ XML special characters (`<`, `>`, `&`, `"`, `'`)
5. ✅ Attributes on raw block elements
6. ✅ Empty and whitespace-only content
7. ✅ Multiline content with indentation
8. ✅ Mixed content (raw blocks + regular XML)
9. ✅ Nested XML-like text inside code blocks
10. ✅ Self-closing raw block elements

### Language-Specific Implementation Guidance

#### .NET (C#)
- Use `Regex.Replace()` with callback function
- Consider `RegexOptions.Singleline` for `\s` to match newlines
- Use `string.IsNullOrWhiteSpace()` for empty check

#### Python
- Use `re.sub()` with lambda or function callback
- Use `re.DOTALL` flag for `.` to match newlines
- Use `str.strip()` for whitespace detection

#### TypeScript/JavaScript
- Use `String.replace()` with callback function
- `.` in regex does NOT match newlines by default, use `[\s\S]` instead
- Use `.trim()` for whitespace detection

## Version History

- **v1.0.0** (2026-02-09): Initial specification
  - Defined core CDATA wrapping algorithm
  - Documented edge cases and test scenarios
  - Provided reference pseudocode implementation

## References

- [XML 1.0 Specification - CDATA Sections](https://www.w3.org/TR/xml/#sec-cdata-sect)
- [XML Special Characters](https://www.w3.org/TR/xml/#syntax)
- Microsoft Agents Protocol XML Implementation:
  - .NET: `dotnet/src/Microsoft.Agents.Xml/Preprocessing/EvalXmlPreprocessor.cs`
  - Python: `python/microsoft-agents-xml/microsoft/agents/xml/preprocessing.py`
  - TypeScript: `typescript/packages/agents-xml/src/preprocessing.ts`
