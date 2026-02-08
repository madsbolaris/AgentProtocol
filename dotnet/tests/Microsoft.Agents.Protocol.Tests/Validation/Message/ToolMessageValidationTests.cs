using FluentAssertions;
using Microsoft.Agents.Xml.Generated.Models;
using Microsoft.Agents.Xml.Validation;
using Microsoft.Agents.Xml.Validation.Validators.MessageValidators;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests.Validation.MessageValidation;

public class ToolMessageValidationTests
{
    private readonly ToolMessageValidator _validator = new();

    [Fact]
    public void Validate_ValidToolMessage_ReturnsSuccess()
    {
        // Arrange
        var context = new ValidationContext();

        // Register a function call first
        var functionCall = new FunctionCallContent
        {
            CallId = "call_123",
            Name = "get_weather",
            Arguments = "{}"
        };
        context.RegisterFunctionCall(functionCall);

        var message = new ToolMessage
        {
            MessageId = "msg_002",
            CallId = "call_123",
            Name = "get_weather",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>
            {
                new FunctionResultContent
                {
                    CallId = "call_123",
                    Name = "get_weather",
                    Result = "{\"temp\": 72}"
                }
            }
        };

        // Act
        var result = _validator.Validate(message, context);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_MissingCallId_ReturnsError_MSG012()
    {
        // Arrange
        var message = new ToolMessage
        {
            MessageId = "msg_002",
            CallId = "",
            Name = "get_weather",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>()
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_012);
    }

    [Fact]
    public void Validate_MissingName_ReturnsError_MSG012()
    {
        // Arrange
        var message = new ToolMessage
        {
            MessageId = "msg_002",
            CallId = "call_123",
            Name = "",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>()
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_012);
    }

    [Fact]
    public void Validate_CallIdMismatch_ReturnsError_REL005()
    {
        // Arrange
        var context = new ValidationContext();

        var message = new ToolMessage
        {
            MessageId = "msg_002",
            CallId = "call_nonexistent",
            Name = "get_weather",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>
            {
                new FunctionResultContent { CallId = "call_nonexistent", Result = "{}" }
            }
        };

        // Act
        var result = _validator.Validate(message, context);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.REL_005);
    }

    [Fact]
    public void Validate_NameMismatch_ReturnsError_REL008()
    {
        // Arrange
        var context = new ValidationContext();

        // Register a function call
        var functionCall = new FunctionCallContent
        {
            CallId = "call_123",
            Name = "get_weather",
            Arguments = "{}"
        };
        context.RegisterFunctionCall(functionCall);

        var message = new ToolMessage
        {
            MessageId = "msg_002",
            CallId = "call_123",
            Name = "get_forecast", // Different name
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>()
        };

        // Act
        var result = _validator.Validate(message, context);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.REL_008);
    }

    [Fact]
    public void Validate_InvalidContentType_ReturnsError_ROLE004()
    {
        // Arrange
        var message = new ToolMessage
        {
            MessageId = "msg_002",
            CallId = "call_123",
            Name = "get_weather",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>
            {
                new TextContent { Text = "This shouldn't be here" }
            }
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.ROLE_004);
    }
}
