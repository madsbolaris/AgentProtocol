# EvalXML Preprocessing Test Suite

## Overview

This document defines a canonical test suite for EvalXML preprocessing implementations across all languages (.NET, Python, TypeScript). Each implementation should pass all tests defined here.

## Test Format

Each test case specifies:
- **Name**: Descriptive test name
- **Input**: The XML string before preprocessing
- **Expected**: The XML string after preprocessing
- **Description**: What the test validates

## Test Cases

### Test 1: Basic Assert Block

**Name**: `test_basic_assert_block`

**Input**:
```xml
<assert>x == 5</assert>
```

**Expected**:
```xml
<assert><![CDATA[x == 5]]></assert>
```

**Description**: Verifies basic CDATA wrapping of assertion content.

---

### Test 2: Metric with Comparison Operators

**Name**: `test_metric_comparison`

**Input**:
```xml
<metric>x > 5 && y < 10</metric>
```

**Expected**:
```xml
<metric><![CDATA[x > 5 && y < 10]]></metric>
```

**Description**: Verifies CDATA wrapping protects comparison operators in metrics.

---

### Test 3: Args with XML Special Characters

**Name**: `test_args_xml_special_characters`

**Input**:
```xml
<args>{"name": "test", "value": "x < 5 && y > 3"}</args>
```

**Expected**:
```xml
<args><![CDATA[{"name": "test", "value": "x < 5 && y > 3"}]]></args>
```

**Description**: Verifies that XML special characters (`<`, `>`, `&`, `"`) in args are protected by CDATA.

---

### Test 4: Multiple Raw Blocks

**Name**: `test_multiple_blocks`

**Input**:
```xml
<eval>
  <assert>x == 1</assert>
  <result>true</result>
  <metric>y > 0</metric>
</eval>
```

**Expected**:
```xml
<eval>
  <assert><![CDATA[x == 1]]></assert>
  <result>true</result>
  <metric><![CDATA[y > 0]]></metric>
</eval>
```

**Description**: Verifies that multiple raw blocks are processed independently.

---

### Test 5: Empty Assert Block

**Name**: `test_empty_assert`

**Input**:
```xml
<assert></assert>
```

**Expected**:
```xml
<assert><![CDATA[]]></assert>
```

**Description**: Verifies that empty raw blocks are handled (content wrapped even if empty).

---

### Test 6: All Three Raw Block Types

**Name**: `test_all_raw_block_types`

**Input**:
```xml
<test>
  <assert>x == 1</assert>
  <metric>score > 0.5</metric>
  <args>{"param": "value"}</args>
</test>
```

**Expected**:
```xml
<test>
  <assert><![CDATA[x == 1]]></assert>
  <metric><![CDATA[score > 0.5]]></metric>
  <args><![CDATA[{"param": "value"}]]></args>
</test>
```

**Description**: Verifies that all three raw block types (assert, metric, args) are handled.

---

### Test 7: Assert with Attributes

**Name**: `test_assert_with_attributes`

**Input**:
```xml
<assert type="equality" severity="error">x == 5</assert>
```

**Expected**:
```xml
<assert type="equality" severity="error"><![CDATA[x == 5]]></assert>
```

**Description**: Verifies that attributes are preserved during CDATA wrapping.

---

### Test 8: Multiline Args

**Name**: `test_multiline_args`

**Input**:
```xml
<args>
{
  "name": "test",
  "value": 123
}
</args>
```

**Expected**:
```xml
<args><![CDATA[
{
  "name": "test",
  "value": 123
}
]]></args>
```

**Description**: Verifies that multiline content with indentation is preserved exactly.

---

### Test 9: CDATA End Marker in Content

**Name**: `test_cdata_end_marker`

**Input**:
```xml
<args>data]]>moredata</args>
```

**Expected**:
```xml
<args><![CDATA[data]]]]><![CDATA[>moredata]]></args>
```

**Description**: Verifies special handling of `]]>` sequence which would prematurely end CDATA.

---

### Test 10: Multiple CDATA End Markers

**Name**: `test_multiple_cdata_markers`

**Input**:
```xml
<args>foo]]>bar]]>baz</args>
```

**Expected**:
```xml
<args><![CDATA[foo]]]]><![CDATA[>bar]]]]><![CDATA[>baz]]></args>
```

**Description**: Verifies handling of multiple `]]>` sequences in content.

---

### Test 11: Mixed Content Document

**Name**: `test_mixed_content`

**Input**:
```xml
<eval>
  <description>This is a test</description>
  <assert>x == 5</assert>
  <output>true</output>
  <metric>score > 0.9</metric>
</eval>
```

**Expected**:
```xml
<eval>
  <description>This is a test</description>
  <assert><![CDATA[x == 5]]></assert>
  <output>true</output>
  <metric><![CDATA[score > 0.9]]></metric>
</eval>
```

**Description**: Verifies that only raw block elements are wrapped, while other elements remain unchanged.

---

### Test 12: Nested XML-Like Text

**Name**: `test_nested_xml_like_text`

**Input**:
```xml
<assert><html><body>content</body></html></assert>
```

**Expected**:
```xml
<assert><![CDATA[<html><body>content</body></html>]]></assert>
```

**Description**: Verifies that XML-like text inside raw blocks is treated as literal content and protected.

---

### Test 13: Assert with Ampersands

**Name**: `test_ampersands`

**Input**:
```xml
<assert>x > 1 &amp;&amp; y < 10</assert>
```

**Expected**:
```xml
<assert><![CDATA[x > 1 &amp;&amp; y < 10]]></assert>
```

**Description**: Verifies that HTML entities are preserved as-is inside CDATA.

---

### Test 14: Args with Quotes

**Name**: `test_quotes`

**Input**:
```xml
<args>{"message": "He said \"hello\""}</args>
```

**Expected**:
```xml
<args><![CDATA[{"message": "He said \"hello\""}]]></args>
```

**Description**: Verifies that quotes and escaped quotes are preserved.

---

### Test 15: Self-Closing Raw Block Tag (Error Case)

**Name**: `test_self_closing_tag_error`

**Input**:
```xml
<assert />
```

**Expected**:
Error thrown: `Raw block element <assert/> cannot be self-closing. Use <assert></assert> for empty content.`

**Description**: Verifies that self-closing raw block elements throw an error.

---

### Test 16: Args with Literal CDATA Text

**Name**: `test_literal_cdata_text`

**Input**:
```xml
<args>text = "<![CDATA[data]]>"</args>
```

**Expected**:
```xml
<args><![CDATA[text = "<![CDATA[data]]>"]]></args>
```

**Description**: Verifies that literal CDATA text in args is wrapped (CDATA treats inner CDATA as text).

---

### Test 17: Multiple Attributes

**Name**: `test_multiple_attributes`

**Input**:
```xml
<metric id="m123" type="performance" unit="ms">latency < 100</metric>
```

**Expected**:
```xml
<metric id="m123" type="performance" unit="ms"><![CDATA[latency < 100]]></metric>
```

**Description**: Verifies that multiple attributes are preserved correctly.

---

### Test 18: Case Insensitive Tag Matching

**Name**: `test_case_insensitive`

**Input**:
```xml
<ASSERT>x == 5</ASSERT>
```

**Expected**:
```xml
<ASSERT><![CDATA[x == 5]]></ASSERT>
```

**Description**: Verifies that tag matching is case-insensitive.

---

### Test 19: Mixed Case Tags

**Name**: `test_mixed_case`

**Input**:
```xml
<Assert>x == 1</Assert>
<METRIC>y > 0</METRIC>
<args>{"test": true}</args>
```

**Expected**:
```xml
<Assert><![CDATA[x == 1]]></Assert>
<METRIC><![CDATA[y > 0]]></METRIC>
<args><![CDATA[{"test": true}]]></args>
```

**Description**: Verifies handling of mixed case raw block tags.

---

### Test 20: Complex Real-World Example

**Name**: `test_complex_real_world`

**Input**:
```xml
<evaluation id="eval-001">
  <title>Performance Test</title>
  <description>Check API latency</description>
  <assert type="response-time">latency < 100 &amp;&amp; latency > 0</assert>
  <metric name="p95">percentile(latency, 0.95) < 150</metric>
  <args>
{
  "endpoint": "/api/users",
  "method": "GET",
  "headers": {"Accept": "application/json"}
}
  </args>
  <result>PASS</result>
  <metadata>Test completed successfully</metadata>
</evaluation>
```

**Expected**:
```xml
<evaluation id="eval-001">
  <title>Performance Test</title>
  <description>Check API latency</description>
  <assert type="response-time"><![CDATA[latency < 100 &amp;&amp; latency > 0]]></assert>
  <metric name="p95"><![CDATA[percentile(latency, 0.95) < 150]]></metric>
  <args><![CDATA[
{
  "endpoint": "/api/users",
  "method": "GET",
  "headers": {"Accept": "application/json"}
}
  ]]></args>
  <result>PASS</result>
  <metadata>Test completed successfully</metadata>
</evaluation>
```

**Description**: Verifies handling of a realistic document with all three raw block types, attributes, formatting, and mixed content.

---

## Implementation Checklist

For each language implementation, verify:

- [ ] All 20 test cases pass
- [ ] Input XML is not mutated (if applicable to language)
- [ ] Performance is acceptable (single-pass regex replacement)
- [ ] Edge cases handle gracefully without throwing exceptions
- [ ] Documentation includes examples from this test suite

## Test Execution Guidelines

### .NET (xUnit)
```csharp
[Fact]
public void TestBasicAssertBlock()
{
    var input = "<assert>x == 5</assert>";
    var expected = "<assert><![CDATA[x == 5]]></assert>";
    var result = EvalXmlPreprocessor.Preprocess(input);
    Assert.Equal(expected, result);
}
```

### Python (pytest)
```python
def test_basic_assert_block():
    input_xml = '<assert>x == 5</assert>'
    expected = '<assert><![CDATA[x == 5]]></assert>'
    result = preprocess(input_xml)
    assert result == expected
```

### TypeScript (Jest/Vitest)
```typescript
test('basic assert block', () => {
    const input = '<assert>x == 5</assert>';
    const expected = '<assert><![CDATA[x == 5]]></assert>';
    const result = preprocess(input);
    expect(result).toBe(expected);
});
```

## Validation Criteria

An implementation is considered **compliant** with this specification if:
1. All 20 test cases produce the expected output
2. The implementation follows the algorithm in `eval-xml-preprocessing.md`
3. Performance is reasonable (< 1ms for typical documents < 10KB)

## Revision History

- **v1.0.0** (2026-02-09): Initial test suite with 20 canonical test cases
