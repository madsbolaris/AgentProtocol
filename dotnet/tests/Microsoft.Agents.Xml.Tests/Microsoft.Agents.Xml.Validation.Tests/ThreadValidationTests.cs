using FluentAssertions;
using Microsoft.Agents.Validation;
using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Xml.Validation;
using Microsoft.Agents.Validation.Validators;
using Xunit;
using AgentThread = Microsoft.Agents.Abstractions.Models.Thread;

namespace Microsoft.Agents.Xml.Validation.Tests;

public class ThreadValidationTests
{
    private readonly ThreadValidator _validator = new();

    [Fact]
    public void Validate_ValidAgentThread_ReturnsSuccess()
    {
        // Arrange
        var thread = new AgentThread
        {
            ThreadId = "thread_001",
            Status = ThreadStatus.Active,
            CreatedAt = DateTime.UtcNow.AddMinutes(-10),
            LastMessageAt = DateTime.UtcNow.AddMinutes(-1),
            Messages = new List<ChatMessage>
            {
                new UserMessage
                {
                    MessageId = "msg_001",
                    UserId = "user_123",
                    CreatedAt = DateTime.UtcNow.AddMinutes(-5),
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                },
                new AgentMessage
                {
                    MessageId = "msg_002",
                    AgentId = "agent_456",
                    CreatedAt = DateTime.UtcNow.AddMinutes(-1),
                    Contents = new List<AIContent> { new TextContent { Text = "Hi there!" } }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }

    [Fact]
    public void Validate_DuplicateMessageIds_ReturnsError_MSG002()
    {
        // Arrange
        var thread = new AgentThread
        {
            ThreadId = "thread_001",
            CreatedAt = DateTime.UtcNow,
            Messages = new List<ChatMessage>
            {
                new UserMessage
                {
                    MessageId = "msg_001",
                    CreatedAt = DateTime.UtcNow,
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                },
                new UserMessage
                {
                    MessageId = "msg_001", // Duplicate!
                    CreatedAt = DateTime.UtcNow,
                    Contents = new List<AIContent> { new TextContent { Text = "Hello again" } }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.MSG_002);
    }

    [Fact]
    public void Validate_InvalidParentMessageId_ReturnsError_THR005()
    {
        // Arrange
        var thread = new AgentThread
        {
            ThreadId = "thread_001",
            CreatedAt = DateTime.UtcNow,
            Messages = new List<ChatMessage>
            {
                new UserMessage
                {
                    MessageId = "msg_001",
                    ParentMessageId = "msg_nonexistent", // Doesn't exist
                    CreatedAt = DateTime.UtcNow,
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.THR_005);
    }

    [Fact]
    public void Validate_CreatedAtAfterLastMessageAt_ReturnsError_THR003()
    {
        // Arrange
        var thread = new AgentThread
        {
            ThreadId = "thread_001",
            CreatedAt = DateTime.UtcNow,
            LastMessageAt = DateTime.UtcNow.AddMinutes(-10), // Before created-at
            Messages = new List<ChatMessage>()
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.THR_003);
    }

    [Fact]
    public void Validate_NegativeUnreadCount_ReturnsError_THR004()
    {
        // Arrange
        var thread = new AgentThread
        {
            ThreadId = "thread_001",
            CreatedAt = DateTime.UtcNow,
            UnreadCount = -1,
            Messages = new List<ChatMessage>()
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeFalse();
        result.Errors.Should().Contain(e => e.Code == ValidationErrorCode.THR_004);
    }

    [Fact]
    public void Validate_CallIdMatching_Success()
    {
        // Arrange
        var thread = new AgentThread
        {
            ThreadId = "thread_001",
            CreatedAt = DateTime.UtcNow,
            Messages = new List<ChatMessage>
            {
                new AgentMessage
                {
                    MessageId = "msg_001",
                    CreatedAt = DateTime.UtcNow,
                    Contents = new List<AIContent>
                    {
                        new FunctionCallContent
                        {
                            CallId = "call_123",
                            Name = "get_weather",
                            Arguments = "{}"
                        }
                    }
                },
                new ToolMessage
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
                            Result = "{}"
                        }
                    }
                }
            }
        };

        // Act
        var result = _validator.Validate(thread);

        // Assert
        result.IsValid.Should().BeTrue();
    }
}
