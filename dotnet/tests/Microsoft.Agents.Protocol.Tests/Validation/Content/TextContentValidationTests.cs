using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Validation;
using Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests.Validation.ContentValidation;

public class TextContentValidationTests
{
    private readonly TextContentValidator _validator = new();

    [Fact]
    public void Validate_ValidTextContent_ReturnsSuccess()
    {
        // Arrange
        var content = new TextContent { Text = "Hello, world!" };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Theory]
    [InlineData(null)]
    [InlineData("")]
    [InlineData("   ")]
    public void Validate_EmptyText_ReturnsError_CNT001(string? text)
    {
        // Arrange
        var content = new TextContent { Text = text! };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().ContainSingle(e => e.Code == ValidationErrorCode.CNT_001);
    }

    [Fact]
    public void Validate_TextExceedsMaxLength_ReturnsError_CNT002()
    {
        // Arrange
        var content = new TextContent { Text = new string('x', 100001) };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().ContainSingle(e => e.Code == ValidationErrorCode.CNT_002);
    }

    [Fact]
    public void Validate_TextAtMaxLength_ReturnsSuccess()
    {
        // Arrange
        var content = new TextContent { Text = new string('x', 100000) };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeTrue();
    }
}
