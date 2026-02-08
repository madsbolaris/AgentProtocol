using System;
using System.Collections.Generic;
using Xunit;
using FluentAssertions;
using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Xml.Serialization;

namespace Microsoft.Agents.Xml.CodeGen.Tests;

/// <summary>
/// Tests for XML serialization/deserialization of messages and content.
/// </summary>
public class SerializationTests
{
    private readonly MessageSerializer _serializer = new();

    [Fact]
    public void SerializeSystemMessage_ProducesCorrectXml()
    {
        // Arrange
        var message = new SystemMessage
        {
            MessageId = "msg_000",
            ThreadId = "thread_abc123", // ThreadId is set but won't be serialized (marked [XmlIgnore])
            CreatedAt = new DateTime(2026, 2, 7, 10, 0, 0, DateTimeKind.Utc),
            Content = "You are a helpful AI assistant with access to weather tools."
        };

        // Act
        var xml = _serializer.Serialize(message);

        // Assert
        xml.Should().Contain("<system");
        xml.Should().Contain("message-id=\"msg_000\"");
        xml.Should().NotContain("thread-id"); // ThreadId should NOT be serialized (marked [XmlIgnore])
        xml.Should().Contain("You are a helpful AI assistant");
        xml.Should().NotContain("<content>"); // Should use XmlText, not element
    }

    [Fact]
    public void SerializeUserMessage_WithMultiModalContent()
    {
        // Arrange
        var message = new UserMessage
        {
            MessageId = "msg_002",
            ThreadId = "thread_abc123",
            UserId = "user_alice_123",
            AuthorName = "Alice",
            CreatedAt = new DateTime(2026, 2, 7, 10, 30, 0, DateTimeKind.Utc),
            Contents = new List<AIContent>
            {
                new TextContent { Text = "What's in this image?" },
                new ImageContent
                {
                    Uri = "https://example.com/photos/seattle-skyline.jpg",
                    Alt = "Seattle skyline",
                    MimeType = "image/jpeg",
                    Width = 1920,
                    Height = 1080,
                    Audience = "user,agent"
                }
            }
        };

        // Act
        var xml = _serializer.Serialize(message);

        // Assert
        xml.Should().Contain("<user");
        xml.Should().Contain("message-id=\"msg_002\"");
        xml.Should().Contain("user-id=\"user_alice_123\"");
        xml.Should().Contain("<text>What's in this image?</text>");
        xml.Should().Contain("<image");
        xml.Should().Contain("uri=\"https://example.com/photos/seattle-skyline.jpg\"");
        xml.Should().Contain("audience=\"user assistant\"");
    }

    [Fact]
    public void SerializeAgentMessage_WithThinkingAndFunctionCall()
    {
        // Arrange
        var message = new AgentMessage
        {
            MessageId = "msg_003",
            ThreadId = "thread_abc123",
            AgentId = "agent_claude_001",
            AuthorName = "Claude",
            CompletionId = "run_xyz789",
            CreatedAt = new DateTime(2026, 2, 7, 10, 30, 2, DateTimeKind.Utc),
            Contents = new List<AIContent>
            {
                new TextReasoningContent
                {
                    Exposed = false,
                    Audience = "agent",
                    Text = "User has uploaded an image. Need to analyze it first."
                },
                new FunctionCallContent
                {
                    CallId = "call_001",
                    Name = "analyze_image",
                    Audience = "agent",
                    Arguments = "{\"image_url\": \"https://example.com/photos/seattle-skyline.jpg\"}"
                }
            }
        };

        // Act
        var xml = _serializer.Serialize(message);

        // Assert
        xml.Should().Contain("<agent");
        xml.Should().Contain("agent-id=\"agent_claude_001\"");
        xml.Should().NotContain("model="); // model is not in the schema
        xml.Should().Contain("<thinking");
        xml.Should().Contain("exposed=\"false\"");
        xml.Should().Contain("User has uploaded an image");
        xml.Should().Contain("<function-call");
        xml.Should().Contain("call-id=\"call_001\"");
        xml.Should().Contain("name=\"analyze_image\"");
        xml.Should().Contain("{\"image_url\":");
    }

    [Fact]
    public void SerializeToolMessage_WithFunctionResult()
    {
        // Arrange
        var message = new ToolMessage
        {
            MessageId = "msg_004",
            ThreadId = "thread_abc123",
            CallId = "call_001",
            Name = "analyze_image",
            CreatedAt = new DateTime(2026, 2, 7, 10, 30, 5, DateTimeKind.Utc),
            Contents = new List<AIContent>
            {
                new FunctionResultContent
                {
                    CallId = "call_001",
                    Name = "analyze_image",
                    Result = "{\"location\": \"Seattle, WA\", \"confidence\": 0.95}"
                }
            }
        };

        // Act
        var xml = _serializer.Serialize(message);

        // Assert
        xml.Should().Contain("<tool");
        xml.Should().Contain("call-id=\"call_001\"");
        xml.Should().Contain("name=\"analyze_image\"");
        xml.Should().Contain("<function-result>");
        xml.Should().Contain("{\"location\": \"Seattle, WA\"");
    }

    [Fact]
    public void DeserializeSystemMessage_FromXml()
    {
        // Arrange
        var xml = @"<?xml version=""1.0"" encoding=""utf-8""?>
<system message-id=""msg_000"" created-at=""2026-02-07T10:00:00Z"">
  You are a helpful AI assistant.
</system>";

        // Act
        var message = (SystemMessage)_serializer.Deserialize(xml);

        // Assert
        message.MessageId.Should().Be("msg_000");
        message.ThreadId.Should().BeNullOrEmpty(); // ThreadId is NOT deserialized (marked [XmlIgnore])
        message.Content.Should().Contain("helpful AI assistant");
        message.Role.Should().Be(ChatRole.System);
    }

    [Fact]
    public void DeserializeUserMessage_WithContent()
    {
        // Arrange
        var xml = @"<?xml version=""1.0"" encoding=""utf-8""?>
<user message-id=""msg_002"" user-id=""user_alice_123"">
  <text>Hello world</text>
  <image uri=""https://example.com/photo.jpg"" mime-type=""image/jpeg"" />
</user>";

        // Act
        var message = (UserMessage)_serializer.Deserialize(xml);

        // Assert
        message.MessageId.Should().Be("msg_002");
        message.UserId.Should().Be("user_alice_123");
        message.Contents.Should().HaveCount(2);
        message.Contents[0].Should().BeOfType<TextContent>();
        message.Contents[1].Should().BeOfType<ImageContent>();

        var textContent = (TextContent)message.Contents[0];
        textContent.Text.Should().Be("Hello world");

        var imageContent = (ImageContent)message.Contents[1];
        imageContent.Uri.Should().Be("https://example.com/photo.jpg");
    }

    [Fact]
    public void RoundTrip_PreservesAllData()
    {
        // Arrange
        var original = new UserMessage
        {
            MessageId = "msg_123",
            ThreadId = "thread_456", // ThreadId is set but won't round-trip (marked [XmlIgnore])
            UserId = "user_789",
            AuthorName = "Alice",
            CreatedAt = new DateTime(2026, 2, 7, 10, 0, 0, DateTimeKind.Utc),
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Test message" },
                new ImageContent
                {
                    Uri = "https://example.com/test.jpg",
                    MimeType = "image/jpeg",
                    Width = 800,
                    Height = 600
                }
            }
        };

        // Act
        var xml = _serializer.Serialize(original);
        var deserialized = (UserMessage)_serializer.Deserialize(xml);

        // Assert
        deserialized.MessageId.Should().Be(original.MessageId);
        deserialized.ThreadId.Should().BeNullOrEmpty(); // ThreadId does NOT round-trip (marked [XmlIgnore])
        deserialized.UserId.Should().Be(original.UserId);
        deserialized.Contents.Should().HaveCount(2);

        var textContent = (TextContent)deserialized.Contents[0];
        textContent.Text.Should().Be("Test message");

        var imageContent = (ImageContent)deserialized.Contents[1];
        imageContent.Uri.Should().Be("https://example.com/test.jpg");
        imageContent.Width.Should().Be(800);
    }

    [Fact]
    public void SerializeMultipleMessages_WithRootElement()
    {
        // Arrange
        var messages = new List<ChatMessage>
        {
            new SystemMessage
            {
                MessageId = "msg_000",
                Content = "You are helpful."
            },
            new UserMessage
            {
                MessageId = "msg_001",
                UserId = "user_123",
                Contents = new List<AIContent>
                {
                    new TextContent { Text = "Hello!" }
                }
            }
        };

        // Act
        var xml = _serializer.SerializeMany(messages, "conversation");

        // Assert
        xml.Should().Contain("<conversation>");
        xml.Should().Contain("<system");
        xml.Should().Contain("<user");
        xml.Should().Contain("</conversation>");
    }

    [Fact]
    public void DeserializeMultipleMessages_WithRootElement()
    {
        // Arrange
        var xml = @"<?xml version=""1.0"" encoding=""utf-8""?>
<conversation>
  <system message-id=""msg_000"">You are helpful.</system>
  <user message-id=""msg_001"" user-id=""user_123"">
    <text>Hello!</text>
  </user>
</conversation>";

        // Act
        var messages = _serializer.DeserializeMany(xml, "conversation");

        // Assert
        messages.Should().HaveCount(2);
        messages[0].Should().BeOfType<SystemMessage>();
        messages[1].Should().BeOfType<UserMessage>();
    }
}
