using Xunit;
using FluentAssertions;
using Microsoft.Agents.Protocol.Xml.Validation;
using System;
using System.Collections.Generic;

namespace Microsoft.Agents.Xml.CodeGen.Tests;

/// <summary>
/// Additional tests for ThreadValidator and ValidationResult to achieve 90%+ coverage.
/// Based on Python and TypeScript test patterns.
/// </summary>
public class ThreadValidatorAdditionalTests
{
    private readonly ThreadValidator _validator = new();

    #region ValidationResult Tests

    [Fact]
    public void ValidationResult_Success_CreatesValidResult()
    {
        // Act
        var result = ValidationResult.Success();

        // Assert
        result.IsValid.Should().BeTrue();
        result.Errors.Should().BeEmpty();
        result.Warnings.Should().BeEmpty();
    }

    [Fact]
    public void ValidationResult_Failure_CreatesInvalidResult()
    {
        // Act
        var result = ValidationResult.Failure("Test error", field: "testField", code: "TEST_001");

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().HaveCount(1);
        result.Errors[0].Message.Should().Be("Test error");
        result.Errors[0].Field.Should().Be("testField");
        result.Errors[0].Code.Should().Be("TEST_001");
    }

    [Fact]
    public void ValidationResult_AddError_MarksInvalid()
    {
        // Arrange
        var result = ValidationResult.Success();

        // Act
        result.AddError("Error message", code: "ERR_001");

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().HaveCount(1);
    }

    [Fact]
    public void ValidationResult_AddWarning_KeepsValid()
    {
        // Arrange
        var result = ValidationResult.Success();

        // Act
        result.AddWarning("Warning message");

        // Assert
        result.IsValid.Should().BeTrue();
        result.Warnings.Should().HaveCount(1);
    }

    [Fact]
    public void ValidationResult_ToString_ShowsStatus()
    {
        // Arrange
        var successResult = ValidationResult.Success();
        var failureResult = ValidationResult.Failure("Test error");

        // Act & Assert
        successResult.ToString().Should().Contain("passed");
        failureResult.ToString().Should().Contain("failed");
        failureResult.ToString().Should().Contain("Test error");
    }

    [Fact]
    public void ValidationError_ToString_WithField()
    {
        // Arrange
        var error = new ValidationError("Invalid value", field: "testField");

        // Act
        var result = error.ToString();

        // Assert
        result.Should().Be("testField: Invalid value");
    }

    [Fact]
    public void ValidationError_ToString_WithoutField()
    {
        // Arrange
        var error = new ValidationError("Test error", field: null);

        // Act
        var result = error.ToString();

        // Assert
        result.Should().Be("Test error");
    }

    #endregion

    #region ThreadValidator Basic Tests

    [Fact]
    public void Validate_ValidThread_ReturnsSuccess()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "user",
                    Contents = new[] { new { Kind = "text", Text = "Hello" } }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_MissingThreadId_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            Messages = new List<object>()
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_001");
    }

    [Fact]
    public void Validate_DuplicateMessageIds_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new { MessageId = "msg-1", Role = "user", Contents = new[] { new { Kind = "text", Text = "First" } } },
                new { MessageId = "msg-1", Role = "agent", Contents = new[] { new { Kind = "text", Text = "Second" } } }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_003");
    }

    [Fact]
    public void Validate_InvalidRole_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new { MessageId = "msg-1", Role = "invalid_role", Contents = new[] { new { Kind = "text", Text = "Test" } } }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_005");
    }

    [Fact]
    public void Validate_OutOfOrderMessages_ReturnsError()
    {
        // Arrange
        var now = DateTime.UtcNow;
        var earlier = now.AddHours(-1);

        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new { MessageId = "msg-1", Role = "user", CreatedAt = now, Contents = new[] { new { Kind = "text", Text = "First" } } },
                new { MessageId = "msg-2", Role = "agent", CreatedAt = earlier, Contents = new[] { new { Kind = "text", Text = "Second" } } }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_004");
    }

    [Fact]
    public void Validate_FunctionCallFlow_Success()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "agent",
                    Contents = new[]
                    {
                        new { Kind = "functionCall", CallId = "call-1", Name = "get_weather", Arguments = "{}" }
                    }
                },
                new
                {
                    MessageId = "msg-2",
                    Role = "tool",
                    Contents = new[]
                    {
                        new { Kind = "functionResult", CallId = "call-1", Name = "get_weather", Result = "Sunny" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_FunctionCallMissingCallId_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "agent",
                    Contents = new[]
                    {
                        new { Kind = "functionCall", Name = "get_weather", Arguments = "{}" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_007");
    }

    [Fact]
    public void Validate_FunctionResultWithoutMatchingCall_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "tool",
                    Contents = new[]
                    {
                        new { Kind = "functionResult", CallId = "call-999", Result = "data" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_011");
    }

    [Fact]
    public void Validate_DuplicateCallIdInMessage_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "agent",
                    Contents = new[]
                    {
                        new { Kind = "functionCall", CallId = "call-1", Name = "func1", Arguments = "{}" },
                        new { Kind = "functionCall", CallId = "call-1", Name = "func2", Arguments = "{}" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_008");
    }

    [Fact]
    public void Validate_FunctionNameMismatch_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "agent",
                    Contents = new[]
                    {
                        new { Kind = "functionCall", CallId = "call-1", Name = "get_weather", Arguments = "{}" }
                    }
                },
                new
                {
                    MessageId = "msg-2",
                    Role = "tool",
                    Contents = new[]
                    {
                        new { Kind = "functionResult", CallId = "call-1", Name = "different_func", Result = "data" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_012");
    }

    [Fact]
    public void Validate_AlreadyFulfilledCallId_ReturnsError()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "agent",
                    Contents = new[]
                    {
                        new { Kind = "functionCall", CallId = "call-1", Name = "test_func", Arguments = "{}" }
                    }
                },
                new
                {
                    MessageId = "msg-2",
                    Role = "tool",
                    Contents = new[]
                    {
                        new { Kind = "functionResult", CallId = "call-1", Name = "test_func", Result = "First" }
                    }
                },
                new
                {
                    MessageId = "msg-3",
                    Role = "tool",
                    Contents = new[]
                    {
                        new { Kind = "functionResult", CallId = "call-1", Name = "test_func", Result = "Second" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == "THREAD_013");
    }

    [Fact]
    public void Validate_EmptyMessages_ReturnsValid()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>()
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_MessageWithoutRole_Succeeds()
    {
        // Arrange - role might be inferred from message type
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new { MessageId = "msg-1", Contents = new[] { new { Kind = "text", Text = "Test" } } }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_UnfulfilledFunctionCall_AddsWarning()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new
                {
                    MessageId = "msg-1",
                    Role = "agent",
                    Contents = new[]
                    {
                        new { Kind = "functionCall", CallId = "call-orphan", Name = "test_func", Arguments = "{}" }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue(); // Valid but has warnings
        result.Warnings.Should().NotBeEmpty();
        result.Warnings.Should().Contain(w => w.Contains("call-orphan"));
    }

    [Fact]
    public void Validate_ChannelRole_IsValid()
    {
        // Arrange
        var thread = new
        {
            ThreadId = "thread-123",
            Messages = new List<object>
            {
                new { MessageId = "msg-1", Role = "channel", Contents = new[] { new { Kind = "text", Text = "Channel message" } } }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    #endregion
}
