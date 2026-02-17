/**
 * Tests for EvalXML preprocessing functionality.
 *
 * Based on canonical test suite: specs/eval-xml-preprocessing-tests.md
 */

import { describe, test, expect } from '@jest/globals';
import { preprocess } from '../src/evalXmlPreprocessor';

describe('EvalXmlPreprocessor', () => {
  test('basic assert block', () => {
    // Test 1: Basic CDATA wrapping of assertion content
    const input = '<assert>x == 5</assert>';
    const expected = '<assert><![CDATA[x == 5]]></assert>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('metric comparison', () => {
    // Test 2: CDATA wrapping protects comparison operators in metrics
    const input = '<metric>x > 5 && y < 10</metric>';
    const expected = '<metric><![CDATA[x > 5 && y < 10]]></metric>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('args with XML special characters', () => {
    // Test 3: XML special characters in args are protected by CDATA
    const input = '<args>{"name": "test", "value": "x < 5 && y > 3"}</args>';
    const expected = '<args><![CDATA[{"name": "test", "value": "x < 5 && y > 3"}]]></args>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('multiple blocks', () => {
    // Test 4: Multiple raw blocks are processed independently
    const input = `<eval>
  <assert>x == 1</assert>
  <result>true</result>
  <metric>y > 0</metric>
</eval>`;
    const expected = `<eval>
  <assert><![CDATA[x == 1]]></assert>
  <result>true</result>
  <metric><![CDATA[y > 0]]></metric>
</eval>`;
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('empty assert', () => {
    // Test 5: Empty raw blocks are handled
    const input = '<assert></assert>';
    const expected = '<assert><![CDATA[]]></assert>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('all raw block types', () => {
    // Test 6: All three raw block types are handled
    const input = `<test>
  <assert>x == 1</assert>
  <metric>score > 0.5</metric>
  <args>{"param": "value"}</args>
</test>`;
    const expected = `<test>
  <assert><![CDATA[x == 1]]></assert>
  <metric><![CDATA[score > 0.5]]></metric>
  <args><![CDATA[{"param": "value"}]]></args>
</test>`;
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('assert with attributes', () => {
    // Test 7: Attributes are preserved during CDATA wrapping
    const input = '<assert type="equality" severity="error">x == 5</assert>';
    const expected = '<assert type="equality" severity="error"><![CDATA[x == 5]]></assert>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('multiline args', () => {
    // Test 8: Multiline content with indentation is preserved exactly
    const input = `<args>
{
  "name": "test",
  "value": 123
}
</args>`;
    const expected = `<args><![CDATA[
{
  "name": "test",
  "value": 123
}
]]></args>`;
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('CDATA end marker', () => {
    // Test 9: Special handling of ]]> sequence
    const input = '<args>data]]>moredata</args>';
    const expected = '<args><![CDATA[data]]]]><![CDATA[>moredata]]></args>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('multiple CDATA markers', () => {
    // Test 10: Handling of multiple ]]> sequences
    const input = '<args>foo]]>bar]]>baz</args>';
    const expected = '<args><![CDATA[foo]]]]><![CDATA[>bar]]]]><![CDATA[>baz]]></args>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('mixed content', () => {
    // Test 11: Only raw block elements are wrapped
    const input = `<eval>
  <description>This is a test</description>
  <assert>x == 5</assert>
  <output>true</output>
  <metric>score > 0.9</metric>
</eval>`;
    const expected = `<eval>
  <description>This is a test</description>
  <assert><![CDATA[x == 5]]></assert>
  <output>true</output>
  <metric><![CDATA[score > 0.9]]></metric>
</eval>`;
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('nested XML-like text', () => {
    // Test 12: XML-like text inside raw blocks is protected
    const input = '<assert><html><body>content</body></html></assert>';
    const expected = '<assert><![CDATA[<html><body>content</body></html>]]></assert>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('ampersands', () => {
    // Test 13: HTML entities are preserved as-is inside CDATA
    const input = '<assert>x > 1 &amp;&amp; y < 10</assert>';
    const expected = '<assert><![CDATA[x > 1 &amp;&amp; y < 10]]></assert>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('quotes', () => {
    // Test 14: Quotes and escaped quotes are preserved
    const input = '<args>{"message": "He said \\"hello\\""}</args>';
    const expected = '<args><![CDATA[{"message": "He said \\"hello\\""}]]></args>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('self-closing tag error', () => {
    // Test 15: Self-closing raw block elements throw an error
    const input = '<assert />';
    expect(() => preprocess(input)).toThrow(/cannot be self-closing|Missing closing tag/);
  });

  test('self-closing without space', () => {
    // Test: Self-closing without space before slash
    const input = '<assert/>';
    expect(() => preprocess(input)).toThrow('cannot be self-closing');
  });

  test('literal CDATA text', () => {
    // Test 16: Literal CDATA text in args is wrapped (with ]]> escaping)
    const input = '<args>text = "<![CDATA[data]]>"</args>';
    const expected = '<args><![CDATA[text = "<![CDATA[data]]]]><![CDATA[>"]]></args>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('multiple attributes', () => {
    // Test 17: Multiple attributes are preserved correctly
    const input = '<metric id="m123" type="performance" unit="ms">latency < 100</metric>';
    const expected = '<metric id="m123" type="performance" unit="ms"><![CDATA[latency < 100]]></metric>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('case insensitive', () => {
    // Test 18: Tag matching is case-insensitive
    const input = '<ASSERT>x == 5</ASSERT>';
    const expected = '<ASSERT><![CDATA[x == 5]]></ASSERT>';
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('mixed case', () => {
    // Test 19: Handling of mixed case raw block tags
    const input = `<Assert>x == 1</Assert>
<METRIC>y > 0</METRIC>
<args>{"test": true}</args>`;
    const expected = `<Assert><![CDATA[x == 1]]></Assert>
<METRIC><![CDATA[y > 0]]></METRIC>
<args><![CDATA[{"test": true}]]></args>`;
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('complex real world', () => {
    // Test 20: Realistic document with all three raw block types
    const input = `<evaluation id="eval-001">
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
</evaluation>`;
    const expected = `<evaluation id="eval-001">
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
</evaluation>`;
    const result = preprocess(input);
    expect(result).toBe(expected);
  });

  test('empty input', () => {
    // Edge case: Empty input returns empty output
    expect(preprocess('')).toBe('');
  });

  test('no raw blocks', () => {
    // Content without raw blocks is unchanged
    const input = `<document>
  <title>Test</title>
  <content>Some content</content>
</document>`;
    const result = preprocess(input);
    expect(result).toBe(input);
  });

  test('missing closing tag error', () => {
    // Missing closing tag raises error
    const input = '<assert>x == 5';
    expect(() => preprocess(input)).toThrow('Missing closing tag');
  });
});
