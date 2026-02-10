using FluentAssertions;
using Microsoft.Agents.Protocol.Validation;
using Microsoft.Agents;
using Microsoft.Agents.Xml.Validation;
using Microsoft.Agents.Protocol.Validation.Validators.MessageValidators;
using Xunit;
using XunitAssert = Xunit.Assert;

namespace Microsoft.Agents.Xml.Validation.Tests.MessageValidation;

public class UserMessageValidationTests
{
    private readonly UserMessageValidator _validator = new();

    [Fact]
    public void Validate_ValidUserMessage_ReturnsSuccess()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "msg_001",
            UserId = "user_123",
            CreatedAt = DateTime.UtcNow.AddMinutes(-1),
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Hello!" }
            }
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_MissingMessageId_ReturnsError_MSG001()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_001);
    }

    [Fact]
    public void Validate_NoContents_ReturnsError_MSG010()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "msg_001",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>()
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_010);
    }

    [Fact]
    public void Validate_ContainsFunctionCall_ReturnsError_ROLE005()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "msg_001",
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Call a function" },
                new FunctionCallContent { CallId = "call_1", Name = "test", Arguments = "{}" }
            }
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.ROLE_005);
    }

    [Fact]
    public void Validate_FutureCreatedAt_ReturnsError_MSG004()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "msg_001",
            CreatedAt = DateTime.UtcNow.AddHours(1),
            Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_004);
    }

    [Fact]
    public void Validate_LongAuthorName_ReturnsError_MSG005()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "msg_001",
            AuthorName = new string('x', 101),
            CreatedAt = DateTime.UtcNow,
            Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
        };

        // Act
        var result = _validator.Validate(message);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_005);
    }
}
