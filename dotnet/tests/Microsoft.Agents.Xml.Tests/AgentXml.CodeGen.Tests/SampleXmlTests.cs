using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml;
using System.Xml.Linq;
using Xunit;
using FluentAssertions;
using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Xml.Serialization;

namespace Microsoft.Agents.Xml.CodeGen.Tests;

/// <summary>
/// Tests deserialization of actual sample.xml file.
/// </summary>
public class SampleXmlTests
{
    private readonly MessageSerializer _serializer = new();

    [Fact]
    public void DeserializeSampleXml_Messages()
    {
        // sample.xml has <tools> section first, then messages
        // We need to skip the tools section and parse just the messages

        var samplePath = Path.Combine("..", "..", "..", "..", "..", "sample.xml");
        if (!File.Exists(samplePath))
        {
            // Try alternative path
            samplePath = "sample.xml";
        }

        if (!File.Exists(samplePath))
        {
            // Skip test if sample.xml not found
            return;
        }

        // Read and parse the XML
        var doc = XDocument.Load(samplePath);
        var messages = new List<ChatMessage>();

        // Extract message elements (skip tools)
        var messageElements = doc.Root?.Elements()
            .Where(e => e.Name.LocalName != "tools")
            .ToList() ?? new List<XElement>();

        // Deserialize each message element
        foreach (var element in messageElements)
        {
            var xml = element.ToString();

            try
            {
                var message = _serializer.Deserialize(xml);
                messages.Add(message);
            }
            catch (Exception ex)
            {
                // Log which element failed
                Console.WriteLine($"Failed to deserialize {element.Name}: {ex.Message}");
                throw;
            }
        }

        // Assert we got messages
        messages.Should().NotBeEmpty();
        Console.WriteLine($"✅ Successfully deserialized {messages.Count} messages from sample.xml");

        // Verify message types
        messages.Should().Contain(m => m is SystemMessage);
        messages.Should().Contain(m => m is UserMessage);
        messages.Should().Contain(m => m is AgentMessage);
        messages.Should().Contain(m => m is ToolMessage);

        // Verify first system message
        var systemMsg = messages.OfType<SystemMessage>().FirstOrDefault();
        systemMsg.Should().NotBeNull();
        systemMsg!.MessageId.Should().Be("msg_000");
        systemMsg.Content.Should().Contain("helpful AI assistant");

        // Verify user message with content
        var userMsg = messages.OfType<UserMessage>().FirstOrDefault();
        userMsg.Should().NotBeNull();
        userMsg!.Contents.Should().NotBeEmpty();

        // Verify agent message with thinking
        var agentMsg = messages.OfType<AgentMessage>()
            .FirstOrDefault(m => m.Contents.OfType<TextReasoningContent>().Any());
        agentMsg.Should().NotBeNull();

        var thinking = agentMsg!.Contents.OfType<TextReasoningContent>().FirstOrDefault();
        thinking.Should().NotBeNull();
        thinking!.Exposed.Should().BeFalse();

        // Verify function call
        var agentWithCall = messages.OfType<AgentMessage>()
            .FirstOrDefault(m => m.Contents.OfType<FunctionCallContent>().Any());
        agentWithCall.Should().NotBeNull();

        var functionCall = agentWithCall!.Contents.OfType<FunctionCallContent>().FirstOrDefault();
        functionCall.Should().NotBeNull();
        functionCall!.Name.Should().NotBeEmpty();
        functionCall.Arguments.Should().Contain("{");

        // Verify tool result
        var toolMsg = messages.OfType<ToolMessage>().FirstOrDefault();
        toolMsg.Should().NotBeNull();
        toolMsg!.CallId.Should().NotBeEmpty();

        var result = toolMsg.Contents.OfType<FunctionResultContent>().FirstOrDefault();
        result.Should().NotBeNull();
        result!.Result.Should().Contain("{");
    }

    [Fact]
    public void RoundTrip_SampleXmlMessages()
    {
        // Create messages similar to sample.xml
        var messages = new List<ChatMessage>
        {
            new SystemMessage
            {
                MessageId = "msg_000",
                ThreadId = "thread_abc123",
                CreatedAt = new DateTime(2026, 2, 7, 10, 0, 0, DateTimeKind.Utc),
                Content = "You are a helpful AI assistant."
            },
            new UserMessage
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
            },
            new AgentMessage
            {
                MessageId = "msg_003",
                ParentMessageId = "msg_002",
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
                        Text = "User has uploaded an image and is asking two questions:\n1. What's in the image?\n2. What's the weather there?\n\nStrategy: First analyze the image to identify the location."
                    },
                    new FunctionCallContent
                    {
                        CallId = "call_001",
                        Name = "analyze_image",
                        Audience = "agent",
                        Arguments = "{\"image_url\": \"https://example.com/photos/seattle-skyline.jpg\", \"analysis_type\": \"location_identification\"}"
                    }
                }
            },
            new ToolMessage
            {
                MessageId = "msg_004",
                ParentMessageId = "msg_003",
                ThreadId = "thread_abc123",
                CallId = "call_001",
                Name = "analyze_image",
                CreatedAt = new DateTime(2026, 2, 7, 10, 30, 5, DateTimeKind.Utc),
                Contents = new List<AIContent>
                {
                    new FunctionResultContent
                    {
                        Result = "{\"location\": \"Seattle, WA\", \"confidence\": 0.95, \"landmarks\": [\"Space Needle\", \"Elliott Bay\"], \"description\": \"Urban skyline with distinctive architecture\"}"
                    }
                }
            }
        };

        // Serialize all messages
        var xml = _serializer.SerializeMany(messages);
        Console.WriteLine("Generated XML:");
        Console.WriteLine(xml);

        // Deserialize back
        var deserialized = _serializer.DeserializeMany(xml);

        // Verify count
        deserialized.Should().HaveCount(messages.Count);

        // Verify each message type and key properties
        deserialized[0].Should().BeOfType<SystemMessage>();
        ((SystemMessage)deserialized[0]).Content.Should().Contain("helpful AI assistant");

        deserialized[1].Should().BeOfType<UserMessage>();
        var userMsg = (UserMessage)deserialized[1];
        userMsg.UserId.Should().Be("user_alice_123");
        userMsg.Contents.Should().HaveCount(2);
        userMsg.Contents[0].Should().BeOfType<TextContent>();
        userMsg.Contents[1].Should().BeOfType<ImageContent>();

        deserialized[2].Should().BeOfType<AgentMessage>();
        var agentMsg = (AgentMessage)deserialized[2];
        agentMsg.AgentId.Should().Be("agent_claude_001");
        agentMsg.Contents.Should().HaveCount(2);
        agentMsg.Contents[0].Should().BeOfType<TextReasoningContent>();
        agentMsg.Contents[1].Should().BeOfType<FunctionCallContent>();

        deserialized[3].Should().BeOfType<ToolMessage>();
        var toolMsg = (ToolMessage)deserialized[3];
        toolMsg.CallId.Should().Be("call_001");
        toolMsg.Contents[0].Should().BeOfType<FunctionResultContent>();

        Console.WriteLine($"✅ Successfully round-tripped {messages.Count} messages");
    }

    [Fact]
    public void DeserializeIndividualMessage_SystemMessage()
    {
        var xml = @"<system
  message-id=""msg_000""
  created-at=""2026-02-07T10:00:00Z"">
  You are a helpful AI assistant with access to weather, documentation search, and image analysis tools.
</system>";

        var message = _serializer.Deserialize(xml);

        message.Should().BeOfType<SystemMessage>();
        var systemMsg = (SystemMessage)message;
        systemMsg.MessageId.Should().Be("msg_000");
        systemMsg.ThreadId.Should().BeNullOrEmpty(); // ThreadId is NOT deserialized (marked [XmlIgnore])
        systemMsg.Content.Should().Contain("helpful AI assistant");
    }

    [Fact]
    public void DeserializeIndividualMessage_UserWithMultiModal()
    {
        var xml = @"<user
  message-id=""msg_002""
  user-id=""user_alice_123""
  author-name=""Alice""
  created-at=""2026-02-07T10:30:00Z"">
  <text>What's in this image, and what's the weather like there?</text>
  <image
    uri=""https://example.com/photos/seattle-skyline.jpg""
    alt=""Seattle skyline""
    mime-type=""image/jpeg""
    width=""1920""
    height=""1080""
    audience=""user,agent"" />
</user>";

        var message = _serializer.Deserialize(xml);

        message.Should().BeOfType<UserMessage>();
        var userMsg = (UserMessage)message;
        userMsg.MessageId.Should().Be("msg_002");
        userMsg.UserId.Should().Be("user_alice_123");
        userMsg.Contents.Should().HaveCount(2);

        userMsg.Contents[0].Should().BeOfType<TextContent>();
        var text = (TextContent)userMsg.Contents[0];
        text.Text.Should().Contain("What's in this image");

        userMsg.Contents[1].Should().BeOfType<ImageContent>();
        var image = (ImageContent)userMsg.Contents[1];
        image.Uri.Should().Contain("seattle-skyline.jpg");
        image.Audience.Should().Be("user,agent");
    }

    [Fact]
    public void DeserializeIndividualMessage_AgentWithThinkingAndCall()
    {
        var xml = @"<agent
  message-id=""msg_003""
  parent-message-id=""msg_002""
  agent-id=""agent_claude_001""
  author-name=""Claude""
  completion-id=""run_xyz789""
  created-at=""2026-02-07T10:30:02Z"">
  <thinking exposed=""false"" audience=""agent"">
    User has uploaded an image and is asking two questions:
    1. What's in the image? (requires analyze_image tool)
    2. What's the weather there? (requires get_weather tool, but need to identify location first)

    Strategy: First analyze the image to identify the location, then get weather for that location.
  </thinking>
  <function-call call-id=""call_001"" name=""analyze_image"" audience=""agent"">
    {""image_url"": ""https://example.com/photos/seattle-skyline.jpg"", ""analysis_type"": ""location_identification""}
  </function-call>
</agent>";

        var message = _serializer.Deserialize(xml);

        message.Should().BeOfType<AgentMessage>();
        var agentMsg = (AgentMessage)message;
        agentMsg.MessageId.Should().Be("msg_003");
        agentMsg.AgentId.Should().Be("agent_claude_001");
        agentMsg.Contents.Should().HaveCount(2);

        agentMsg.Contents[0].Should().BeOfType<TextReasoningContent>();
        var thinking = (TextReasoningContent)agentMsg.Contents[0];
        thinking.Exposed.Should().BeFalse();
        thinking.Audience.Should().Be("agent");
        thinking.Text.Should().Contain("User has uploaded an image");

        agentMsg.Contents[1].Should().BeOfType<FunctionCallContent>();
        var call = (FunctionCallContent)agentMsg.Contents[1];
        call.CallId.Should().Be("call_001");
        call.Name.Should().Be("analyze_image");
        call.Arguments.Should().Contain("image_url");
    }

    [Fact]
    public void DeserializeIndividualMessage_ToolResult()
    {
        var xml = @"<tool
  message-id=""msg_004""
  parent-message-id=""msg_003""
  call-id=""call_001""
  name=""analyze_image""
  created-at=""2026-02-07T10:30:05Z"">
  <function-result>
    {""location"": ""Seattle, WA"", ""confidence"": 0.95, ""landmarks"": [""Space Needle"", ""Elliott Bay""], ""description"": ""Urban skyline with distinctive architecture""}
  </function-result>
</tool>";

        var message = _serializer.Deserialize(xml);

        message.Should().BeOfType<ToolMessage>();
        var toolMsg = (ToolMessage)message;
        toolMsg.MessageId.Should().Be("msg_004");
        toolMsg.CallId.Should().Be("call_001");
        toolMsg.Name.Should().Be("analyze_image");
        toolMsg.Contents.Should().HaveCount(1);

        toolMsg.Contents[0].Should().BeOfType<FunctionResultContent>();
        var result = (FunctionResultContent)toolMsg.Contents[0];
        result.Result.Should().Contain("Seattle, WA");
        result.Result.Should().Contain("0.95");
    }
}
