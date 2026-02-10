using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Validation;
using Microsoft.Agents.Protocol.Validation.Validators.ContentValidators;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests.Validation.ContentValidation;

public class FunctionCallContentValidationTests
{
    private readonly FunctionCallContentValidator _validator = new();

    [Fact]
    public void Validate_ValidFunctionCall_ReturnsSuccess()
    {
        // Arrange
        var content = new FunctionCallContent
        {
            CallId = "call_123",
            Name = "get_weather",
            Arguments = "{\"location\": \"Seattle\"}"
        };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_MissingCallId_ReturnsError_REL001()
    {
        // Arrange
        var content = new FunctionCallContent
        {
            CallId = "",
            Name = "get_weather",
            Arguments = "{}"
        };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.REL_001);
    }

    [Theory]
    [InlineData("get-weather")]
    [InlineData("get_weather_123")]
    [InlineData("GetWeather")]
    public void Validate_ValidFunctionName_ReturnsSuccess(string name)
    {
        // Arrange
        var content = new FunctionCallContent
        {
            CallId = "call_123",
            Name = name,
            Arguments = "{}"
        };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Theory]
    [InlineData("get weather")]
    [InlineData("get.weather")]
    [InlineData("get@weather")]
    public void Validate_InvalidFunctionName_ReturnsError_CNT003(string name)
    {
        // Arrange
        var content = new FunctionCallContent
        {
            CallId = "call_123",
            Name = name,
            Arguments = "{}"
        };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.CNT_003);
    }

    [Fact]
    public void Validate_InvalidJson_ReturnsError_CNT004()
    {
        // Arrange
        var content = new FunctionCallContent
        {
            CallId = "call_123",
            Name = "get_weather",
            Arguments = "{invalid json"
        };

        // Act
        var result = _validator.Validate(content);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.CNT_004);
    }

    [Fact]
    public void Validate_DuplicateCallId_ReturnsError_REL003()
    {
        // Arrange
        var context = new ValidationContext();
        var content1 = new FunctionCallContent
        {
            CallId = "call_123",
            Name = "get_weather",
            Arguments = "{}"
        };
        var content2 = new FunctionCallContent
        {
            CallId = "call_123",
            Name = "get_forecast",
            Arguments = "{}"
        };

        // Act
        _validator.Validate(content1, context); // First call registers it
        var result = _validator.Validate(content2, context); // Second call should detect duplicate

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.REL_003);
    }
}
