using Xunit;
using FluentAssertions;
using Microsoft.Agents.Protocol.Xml;

namespace Microsoft.Agents.Xml.CodeGen.Tests;

/// <summary>
/// Tests for EvalXML preprocessing functionality.
/// Based on canonical test suite from Python and TypeScript implementations.
/// </summary>
public class EvalXmlPreprocessorTests
{
    [Fact]
    public void Preprocess_BasicAssertBlock_WrapsCDATA()
    {
        // Arrange
        var input = "<assert>x == 5</assert>";
        var expected = "<assert><![CDATA[x == 5]]></assert>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_MetricComparison_WrapsCDATA()
    {
        // Arrange
        var input = "<metric>x > 5 && y < 10</metric>";
        var expected = "<metric><![CDATA[x > 5 && y < 10]]></metric>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_ArgsWithXmlCharacters_WrapsCDATA()
    {
        // Arrange
        var input = "<args>{\"name\": \"test\", \"value\": \"x < 5 && y > 3\"}</args>";
        var expected = "<args><![CDATA[{\"name\": \"test\", \"value\": \"x < 5 && y > 3\"}]]></args>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_MultipleBlocks_ProcessesIndependently()
    {
        // Arrange
        var input = @"<eval>
  <assert>x == 1</assert>
  <result>true</result>
  <metric>y > 0</metric>
</eval>";
        var expected = @"<eval>
  <assert><![CDATA[x == 1]]></assert>
  <result>true</result>
  <metric><![CDATA[y > 0]]></metric>
</eval>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_EmptyAssert_HandlesCorrectly()
    {
        // Arrange
        var input = "<assert></assert>";
        var expected = "<assert><![CDATA[]]></assert>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_AllRawBlockTypes_HandlesAll()
    {
        // Arrange
        var input = @"<test>
  <assert>x == 1</assert>
  <metric>score > 0.5</metric>
  <args>{""param"": ""value""}</args>
</test>";
        var expected = @"<test>
  <assert><![CDATA[x == 1]]></assert>
  <metric><![CDATA[score > 0.5]]></metric>
  <args><![CDATA[{""param"": ""value""}]]></args>
</test>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_AssertWithAttributes_PreservesAttributes()
    {
        // Arrange
        var input = "<assert type=\"equality\" severity=\"error\">x == 5</assert>";
        var expected = "<assert type=\"equality\" severity=\"error\"><![CDATA[x == 5]]></assert>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_MultilineArgs_PreservesExactly()
    {
        // Arrange
        var input = @"<args>
{
  ""name"": ""test"",
  ""value"": 123
}
</args>";
        var expected = @"<args><![CDATA[
{
  ""name"": ""test"",
  ""value"": 123
}
]]></args>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_CdataEndMarker_HandlesSpecially()
    {
        // Arrange
        var input = "<args>data]]>moredata</args>";
        var expected = "<args><![CDATA[data]]]]><![CDATA[>]]><![CDATA[moredata]]></args>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_MultipleCdataMarkers_HandlesAll()
    {
        // Arrange
        var input = "<args>foo]]>bar]]>baz</args>";
        var expected = "<args><![CDATA[foo]]]]><![CDATA[>]]><![CDATA[bar]]]]><![CDATA[>]]><![CDATA[baz]]></args>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_MixedContent_OnlyWrapsRawBlocks()
    {
        // Arrange
        var input = @"<eval>
  <description>This is a test</description>
  <assert>x == 5</assert>
  <output>true</output>
  <metric>score > 0.9</metric>
</eval>";
        var expected = @"<eval>
  <description>This is a test</description>
  <assert><![CDATA[x == 5]]></assert>
  <output>true</output>
  <metric><![CDATA[score > 0.9]]></metric>
</eval>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_NestedXmlLike_Protects()
    {
        // Arrange
        var input = "<assert><html><body>content</body></html></assert>";
        var expected = "<assert><![CDATA[<html><body>content</body></html>]]></assert>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_CaseInsensitive_HandlesUpperCase()
    {
        // Arrange
        var input = "<ASSERT>x == 5</ASSERT>";
        var expected = "<ASSERT><![CDATA[x == 5]]></ASSERT>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_MixedCase_HandlesAll()
    {
        // Arrange
        var input = @"<Assert>x == 1</Assert>
<METRIC>y > 0</METRIC>
<args>{""test"": true}</args>";
        var expected = @"<Assert><![CDATA[x == 1]]></Assert>
<METRIC><![CDATA[y > 0]]></METRIC>
<args><![CDATA[{""test"": true}]]></args>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(expected);
    }

    [Fact]
    public void Preprocess_SelfClosingTag_ThrowsException()
    {
        // Arrange
        var input = "<assert />";

        // Act & Assert
        var exception = Assert.Throws<InvalidOperationException>(() =>
            EvalXmlPreprocessor.Preprocess(input));

        // Either message is acceptable - implementation may vary
        var hasExpectedMessage = exception.Message.Contains("cannot be self-closing") ||
                                exception.Message.Contains("Missing closing tag");
        hasExpectedMessage.Should().BeTrue();
    }

    [Fact]
    public void Preprocess_SelfClosingWithoutSpace_ThrowsException()
    {
        // Arrange
        var input = "<assert/>";

        // Act & Assert
        var exception = Assert.Throws<InvalidOperationException>(() =>
            EvalXmlPreprocessor.Preprocess(input));

        exception.Message.Should().Contain("cannot be self-closing");
    }

    [Fact]
    public void Preprocess_MissingClosingTag_ThrowsException()
    {
        // Arrange
        var input = "<assert>x == 5";

        // Act & Assert
        var exception = Assert.Throws<InvalidOperationException>(() =>
            EvalXmlPreprocessor.Preprocess(input));

        exception.Message.Should().Contain("Missing closing tag");
    }

    [Fact]
    public void Preprocess_EmptyInput_ReturnsEmpty()
    {
        // Arrange
        var input = "";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be("");
    }

    [Fact]
    public void Preprocess_NoRawBlocks_ReturnsUnchanged()
    {
        // Arrange
        var input = @"<document>
  <title>Test</title>
  <content>Some content</content>
</document>";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Be(input);
    }

    [Fact]
    public void Preprocess_TextAfterLastTag_PreservesText()
    {
        // Arrange
        var input = "<assert>x == 5</assert>Some plain text after the tag.";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Contain("<![CDATA[x == 5]]>");
        result.Should().Contain("Some plain text after the tag.");
    }

    [Fact]
    public void Preprocess_IsolatedLessThan_HandlesCorrectly()
    {
        // Arrange
        var input = "<assert>value</assert> Text with < 5 comparison";

        // Act
        var result = EvalXmlPreprocessor.Preprocess(input);

        // Assert
        result.Should().Contain("<![CDATA[value]]>");
        result.Should().Contain("Text with < 5 comparison");
    }
}
