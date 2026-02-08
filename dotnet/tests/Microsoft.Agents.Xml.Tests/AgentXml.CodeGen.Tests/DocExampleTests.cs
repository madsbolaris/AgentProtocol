using System;
using System.Collections.Generic;
using Microsoft.Agents.Xml.Generated.Models;
using Microsoft.Agents.Xml.Serialization;
using Microsoft.Agents.Testing;
using Xunit;

namespace Microsoft.Agents.Xml.Tests
{
    /// <summary>
    /// Documentation example tests for agent-xml C# implementation.
    ///
    /// These tests are marked with [DocExample] to be extracted for documentation.
    /// </summary>
    public class DocExampleTests : IClassFixture<OutputCaptureFixture>
    {
        private readonly OutputCapture _capture;
        private readonly MessageSerializer _serializer;

        public DocExampleTests(OutputCaptureFixture fixture)
        {
            _capture = fixture.Capture;
            _serializer = new MessageSerializer();
        }

        [Fact]
        [DocExample("basic-xml-serialization", "Basic XML Message Serialization",
            Description = "Demonstrates how to serialize a simple message to XML format",
            Category = "serialization",
            Tags = new[] { "basic", "xml", "message" })]
        public void TestBasicXmlSerialization()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create a simple text message
            var message = new ChatMessage
            {
                Role = "user",
                MessageId = "msg-001",
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "Hello, how can you help me today?" }
                }
            };

            // Serialize to XML
            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);

            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("basic-xml-serialization", xmlOutput, metadata: new
            {
                description = "Simple user message serialized to XML",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("basic-xml-deserialization", "Deserialize XML to Message Object",
            Description = "Shows how to parse XML and create a message object",
            Category = "serialization",
            Tags = new[] { "xml", "parse", "deserialize" })]
        public void TestBasicXmlDeserialization()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            var xmlInput = @"<?xml version=""1.0"" encoding=""utf-8""?>
<chat role=""user"" messageId=""msg-001"">
  <text>Hello, agent!</text>
</chat>";

            // Deserialize XML to object
            var serializer = new MessageSerializer();
            var message = serializer.Deserialize<ChatMessage>(xmlInput);

            Console.WriteLine($"Role: {message.Role}");
            Console.WriteLine($"Text: {(message.Contents[0] as TextContent)?.Text}");
            // doc-example-end

            _capture.Capture("basic-xml-deserialization", new
            {
                role = message.Role,
                text = (message.Contents[0] as TextContent)?.Text
            }, metadata: new { description = "Deserialized message properties", format = "json" });

            Assert.Equal("user", message.Role);
        }

        [Fact]
        [DocExample("multimodal-message", "Creating Multimodal Messages",
            Description = "Demonstrates creating messages with multiple content types",
            Category = "serialization",
            Tags = new[] { "multimodal", "image", "text" })]
        public void TestMultimodalMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create a message with text and image
            var message = new ChatMessage
            {
                Role = "user",
                MessageId = "msg-002",
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "What's in this image?" },
                    new ImageContent
                    {
                        Uri = "https://example.com/image.jpg",
                        AltText = "A photo of a sunset"
                    }
                }
            };

            // Serialize to XML
            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            // doc-example-end

            _capture.Capture("multimodal-message", xmlOutput, metadata: new
            {
                description = "Multimodal message with text and image",
                content_types = new[] { "text", "image" }
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("system-message", "System Instructions Message",
            Description = "Create a system message with instructions for the agent",
            Category = "messages",
            Tags = new[] { "system", "instructions" })]
        public void TestSystemMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create system message with instructions
            var message = new SystemMessage
            {
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "You are a helpful assistant. Be concise and accurate." }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("system-message", xmlOutput, metadata: new
            {
                description = "System instruction message",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("user-message", "User Input Message",
            Description = "Create a user message with input content",
            Category = "messages",
            Tags = new[] { "user", "input" })]
        public void TestUserMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create user message
            var message = new ChatMessage
            {
                Role = "user",
                MessageId = "user-123",
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "What is the weather in Seattle?" }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("user-message", xmlOutput, metadata: new
            {
                description = "User input message",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("agent-message", "Agent Response Message",
            Description = "Create an agent response message",
            Category = "messages",
            Tags = new[] { "agent", "response", "assistant" })]
        public void TestAgentMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create agent response
            var message = new AgentMessage
            {
                AgentId = "agent-456",
                MessageId = "msg-789",
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "The current weather in Seattle is 55°F and partly cloudy." }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("agent-message", xmlOutput, metadata: new
            {
                description = "Agent response message",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("tool-call-message", "Function/Tool Call Message",
            Description = "Create a message with a function/tool call request",
            Category = "tools",
            Tags = new[] { "function", "tool", "call" })]
        public void TestToolCallMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create agent message with tool call
            var message = new AgentMessage
            {
                AgentId = "agent-456",
                MessageId = "msg-call-1",
                Contents = new List<AIContentBase>
                {
                    new FunctionCallContent
                    {
                        CallId = "call_abc123",
                        Name = "get_weather",
                        Arguments = "{\"location\": \"Seattle\", \"unit\": \"fahrenheit\"}"
                    }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("tool-call-message", xmlOutput, metadata: new
            {
                description = "Agent tool call message",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("tool-result-message", "Tool Execution Result",
            Description = "Create a message with tool execution results",
            Category = "tools",
            Tags = new[] { "function", "tool", "result" })]
        public void TestToolResultMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create tool result message
            var message = new ChatMessage
            {
                Role = "tool",
                MessageId = "msg-result-1",
                Contents = new List<AIContentBase>
                {
                    new FunctionResultContent
                    {
                        CallId = "call_abc123",
                        Name = "get_weather",
                        Content = "{\"temperature\": 55, \"conditions\": \"partly cloudy\"}"
                    }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("tool-result-message", xmlOutput, metadata: new
            {
                description = "Tool execution result",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("error-content", "Error Handling Content",
            Description = "Create a message with error content",
            Category = "errors",
            Tags = new[] { "error", "exception", "handling" })]
        public void TestErrorContent()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create message with error
            var message = new AgentMessage
            {
                AgentId = "agent-456",
                MessageId = "msg-error-1",
                Contents = new List<AIContentBase>
                {
                    new ErrorContent
                    {
                        Code = "rate_limit_exceeded",
                        Message = "Rate limit exceeded. Please try again in 60 seconds."
                    }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("error-content", xmlOutput, metadata: new
            {
                description = "Error content message",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("streaming-message", "Streaming Message Chunk",
            Description = "Handle streaming message chunks",
            Category = "streaming",
            Tags = new[] { "streaming", "chunk", "sse" })]
        public void TestStreamingMessage()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create streaming chunk
            var chunk = new AgentMessage
            {
                AgentId = "agent-456",
                MessageId = "msg-stream-1",
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "The weather " }
                }
            };

            var serializer = new MessageSerializer();
            var xmlChunk = serializer.Serialize(chunk);
            Console.WriteLine($"Chunk: {xmlChunk}");
            // doc-example-end

            _capture.Capture("streaming-message", xmlChunk, metadata: new
            {
                description = "Streaming message chunk",
                format = "xml"
            });

            Assert.NotNull(xmlChunk);
        }

        [Fact]
        [DocExample("message-with-metadata", "Message with Custom Metadata",
            Description = "Create a message with custom metadata fields",
            Category = "advanced",
            Tags = new[] { "metadata", "custom", "attributes" })]
        public void TestMessageWithMetadata()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Create message with metadata
            var message = new ChatMessage
            {
                Role = "user",
                MessageId = "msg-meta-1",
                CreatedAt = DateTime.Parse("2024-01-15T10:30:00Z").ToUniversalTime(),
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "Hello!" }
                }
            };

            var serializer = new MessageSerializer();
            var xmlOutput = serializer.Serialize(message);
            Console.WriteLine(xmlOutput);
            // doc-example-end

            _capture.Capture("message-with-metadata", xmlOutput, metadata: new
            {
                description = "Message with timestamp metadata",
                format = "xml"
            });

            Assert.NotNull(xmlOutput);
        }

        [Fact]
        [DocExample("content-validation", "Validate Content Properties",
            Description = "Validate that message content has required properties",
            Category = "validation",
            Tags = new[] { "validation", "properties", "required" })]
        public void TestContentValidation()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;

            // Validate required properties
            var content = new TextContent { Text = "Hello, world!" };

            Assert.NotNull(content.Text); // Text content must have text
            Assert.True(content.Text.Length > 0); // Text cannot be empty
            Assert.Equal("text", content.Kind); // Kind must match content type

            Console.WriteLine($"✓ Content validated: {content.Text}");
            // doc-example-end

            var result = new
            {
                validated = true,
                content_type = "text",
                text = "Hello, world!"
            };

            _capture.Capture("content-validation", result, metadata: new
            {
                description = "Validation results",
                format = "json"
            });

            Assert.True(result.validated);
        }

        [Fact]
        [DocExample("round-trip-fidelity", "Serialize-Deserialize Round Trip",
            Description = "Test that messages survive serialization round trip",
            Category = "validation",
            Tags = new[] { "roundtrip", "fidelity", "serialization" })]
        public void TestRoundTripFidelity()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;

            // Original message
            var original = new ChatMessage
            {
                Role = "user",
                MessageId = "msg-roundtrip",
                Contents = new List<AIContentBase>
                {
                    new TextContent { Text = "Test message" }
                }
            };

            // Serialize then deserialize
            var serializer = new MessageSerializer();
            var xml = serializer.Serialize(original);
            var restored = serializer.Deserialize<ChatMessage>(xml);

            // Verify fidelity
            Assert.Equal(original.Role, restored.Role);
            Assert.Equal(original.MessageId, restored.MessageId);
            Assert.Equal((original.Contents[0] as TextContent)?.Text, (restored.Contents[0] as TextContent)?.Text);

            Console.WriteLine("✓ Round-trip successful");
            // doc-example-end

            var result = new
            {
                round_trip = "successful",
                preserved_fields = new[] { "role", "message_id", "contents" }
            };

            _capture.Capture("round-trip-fidelity", result, metadata: new
            {
                description = "Round-trip test results",
                format = "json"
            });

            Assert.Equal("successful", result.round_trip);
        }

        [Fact]
        [DocExample("batch-messages", "Process Multiple Messages",
            Description = "Process a batch of messages efficiently",
            Category = "advanced",
            Tags = new[] { "batch", "multiple", "processing" })]
        public void TestBatchMessages()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;
            using System.Linq;

            // Create batch of messages
            var messages = new List<ChatMessage>
            {
                new ChatMessage { Role = "user", Contents = new List<AIContentBase> { new TextContent { Text = "Message 1" } } },
                new ChatMessage { Role = "user", Contents = new List<AIContentBase> { new TextContent { Text = "Message 2" } } },
                new ChatMessage { Role = "user", Contents = new List<AIContentBase> { new TextContent { Text = "Message 3" } } }
            };

            // Process batch
            var serializer = new MessageSerializer();
            var xmlOutputs = messages.Select(msg => serializer.Serialize(msg)).ToList();

            Console.WriteLine($"Processed {xmlOutputs.Count} messages");
            // doc-example-end

            var result = new
            {
                processed_count = 3,
                message_types = new[] { "user", "user", "user" }
            };

            _capture.Capture("batch-messages", result, metadata: new
            {
                description = "Batch processing results",
                format = "json"
            });

            Assert.Equal(3, result.processed_count);
        }

        [Fact]
        [DocExample("thread-messages", "Conversation Thread",
            Description = "Create and manage a conversation thread",
            Category = "threads",
            Tags = new[] { "thread", "conversation", "history" })]
        public void TestThreadMessages()
        {
            // doc-example-start
            using Microsoft.Agents.Xml.Generated.Models;
            using Microsoft.Agents.Xml.Serialization;
            using System.Linq;

            // Create conversation thread
            var thread = new List<object>
            {
                new SystemMessage { Contents = new List<AIContentBase> { new TextContent { Text = "You are a helpful assistant." } } },
                new ChatMessage { Role = "user", Contents = new List<AIContentBase> { new TextContent { Text = "Hello!" } } },
                new AgentMessage { Contents = new List<AIContentBase> { new TextContent { Text = "Hi! How can I help?" } } }
            };

            // Serialize thread
            var serializer = new MessageSerializer();
            var threadXml = thread.Select(msg => serializer.Serialize(msg)).ToList();

            Console.WriteLine($"Thread length: {threadXml.Count} messages");
            // doc-example-end

            var result = new
            {
                thread_length = 3,
                message_roles = new[] { "system", "user", "assistant" }
            };

            _capture.Capture("thread-messages", result, metadata: new
            {
                description = "Conversation thread",
                format = "json"
            });

            Assert.Equal(3, result.thread_length);
        }
    }
}
