using System;
using System.Collections.Generic;
using System.Text.Json;
using Microsoft.Agents.Protocol.Models.Agents;
using Microsoft.Agents.Protocol.Models.Common;
using Microsoft.Agents.Protocol.Models.Execution;
using Microsoft.Agents.Protocol.Models.Messages;
using Microsoft.Agents.Protocol.Models.Threads;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Tests for JSON serialization/deserialization of model classes
/// Validates that the models serialize correctly for the Agent Protocol API
/// </summary>
public class ModelSerializationTests
{
    private readonly JsonSerializerOptions _jsonOptions;

    public ModelSerializationTests()
    {
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };
    }

    [Fact]
    public void Run_SerializesAndDeserializes_Correctly()
    {
        // Arrange
        var run = new Run
        {
            RunId = "run_123",
            AgentId = "agent_001",
            ThreadId = "thread_456",
            Status = RunStatus.Completed,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Hello" }
                    }
                }
            },
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "assistant",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Hi there!" }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow,
            ThreadCleanup = ThreadCleanup.Keep
        };

        // Act
        var json = JsonSerializer.Serialize(run, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<Run>(json, _jsonOptions);

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal(run.RunId, deserialized.RunId);
        Assert.Equal(run.AgentId, deserialized.AgentId);
        Assert.Equal(run.ThreadId, deserialized.ThreadId);
        Assert.Equal(run.Status, deserialized.Status);
        Assert.Equal(run.ThreadCleanup, deserialized.ThreadCleanup);
    }

    [Fact]
    public void ChatMessage_WithMultipleContentTypes_SerializesCorrectly()
    {
        // Arrange - Test polymorphic content types
        var message = new ChatMessage
        {
            MessageId = "msg_001",
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "What's in this image?" },
                new ImageContent { Url = "https://example.com/image.jpg", Detail = "high" },
                new FunctionCallContent
                {
                    CallId = "call_123",
                    Name = "analyze_image",
                    Arguments = "{\"url\":\"https://example.com/image.jpg\"}"
                }
            }
        };

        // Act
        var json = JsonSerializer.Serialize(message, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<ChatMessage>(json, _jsonOptions);

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal(3, deserialized.Contents.Count);
        Assert.IsType<TextContent>(deserialized.Contents[0]);
        Assert.IsType<ImageContent>(deserialized.Contents[1]);
        Assert.IsType<FunctionCallContent>(deserialized.Contents[2]);

        var textContent = (TextContent)deserialized.Contents[0];
        Assert.Equal("What's in this image?", textContent.Text);

        var imageContent = (ImageContent)deserialized.Contents[1];
        Assert.Equal("https://example.com/image.jpg", imageContent.Url);
        Assert.Equal("high", imageContent.Detail);

        var functionCall = (FunctionCallContent)deserialized.Contents[2];
        Assert.Equal("call_123", functionCall.CallId);
        Assert.Equal("analyze_image", functionCall.Name);
    }

    [Fact]
    public void Connection_PolymorphicTypes_SerializeCorrectly()
    {
        // Arrange - Test all connection types
        Connection[] connections = new Connection[]
        {
            new ReferenceConnection { Name = "myConnection" },
            new ApiKeyConnection { Key = "sk-test-123", HeaderName = "Authorization" },
            new RemoteConnection
            {
                Endpoint = "https://api.example.com",
                Credentials = new Dictionary<string, object>
                {
                    ["token"] = "Bearer xyz"
                }
            },
            new AnonymousConnection()
        };

        // Act & Assert
        foreach (var connection in connections)
        {
            var json = JsonSerializer.Serialize(connection, _jsonOptions);
            var deserialized = JsonSerializer.Deserialize<Connection>(json, _jsonOptions);

            Assert.NotNull(deserialized);

            if (connection is ReferenceConnection refConn)
            {
                var deserializedRef = Assert.IsType<ReferenceConnection>(deserialized);
                Assert.Equal(refConn.Name, deserializedRef.Name);
            }
            else if (connection is ApiKeyConnection apiKeyConn)
            {
                var deserializedApiKey = Assert.IsType<ApiKeyConnection>(deserialized);
                Assert.Equal(apiKeyConn.Key, deserializedApiKey.Key);
                Assert.Equal(apiKeyConn.HeaderName, deserializedApiKey.HeaderName);
            }
            else if (connection is RemoteConnection remoteConn)
            {
                var deserializedRemote = Assert.IsType<RemoteConnection>(deserialized);
                Assert.Equal(remoteConn.Endpoint, deserializedRemote.Endpoint);
            }
            else if (connection is AnonymousConnection)
            {
                Assert.IsType<AnonymousConnection>(deserialized);
            }
        }
    }

    [Fact]
    public void PromptAgent_WithTools_SerializesCorrectly()
    {
        // Arrange
        var agent = new PromptAgent
        {
            Model = "gpt-4o",
            Instructions = "You are a helpful assistant",
            Temperature = 0.7,
            MaxTokens = 2000,
            Tools = new List<AITool>
            {
                new AITool
                {
                    Name = "get_weather",
                    Description = "Get weather information",
                    Parameters = new JSONSchema
                    {
                        SchemaType = "object",
                        Properties = new Dictionary<string, JSONSchema>
                        {
                            ["location"] = new JSONSchema
                            {
                                SchemaType = "string",
                                Description = "City name",
                                Format = "city"
                            },
                            ["units"] = new JSONSchema
                            {
                                SchemaType = "string",
                                Enum = new List<object> { "celsius", "fahrenheit" }
                            }
                        },
                        Required = new List<string> { "location" }
                    },
                    RequiresApproval = false
                }
            }
        };

        // Act
        var json = JsonSerializer.Serialize<AgentDefinition>(agent, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<AgentDefinition>(json, _jsonOptions) as PromptAgent;

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal(agent.Model, deserialized.Model);
        Assert.Equal(agent.Instructions, deserialized.Instructions);
        Assert.Equal(agent.Temperature, deserialized.Temperature);
        Assert.Equal(agent.MaxTokens, deserialized.MaxTokens);
        Assert.Single(deserialized.Tools);
        Assert.Equal("get_weather", deserialized.Tools[0].Name);
        Assert.NotNull(deserialized.Tools[0].Parameters);
        Assert.Equal(2, deserialized.Tools[0].Parameters.Properties?.Count);
    }

    [Fact]
    public void Thread_WithParticipants_SerializesCorrectly()
    {
        // Arrange
        var thread = new Thread
        {
            ThreadId = "thread_123",
            Title = "Support Conversation",
            Status = ThreadStatus.Active,
            Participants = new List<Participant>
            {
                new Participant
                {
                    Id = "user_001",
                    Kind = "user",
                    Name = "John Doe",
                    Role = "user"
                },
                new Participant
                {
                    Id = "agent_001",
                    Kind = "agent",
                    Name = "Support Bot",
                    Role = "assistant"
                }
            },
            UnreadCount = 5,
            Metadata = new Dictionary<string, object>
            {
                ["priority"] = "high",
                ["department"] = "support"
            }
        };

        // Act
        var json = JsonSerializer.Serialize(thread, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<Thread>(json, _jsonOptions);

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal(thread.ThreadId, deserialized.ThreadId);
        Assert.Equal(thread.Title, deserialized.Title);
        Assert.Equal(thread.Status, deserialized.Status);
        Assert.Equal(2, deserialized.Participants?.Count);
        Assert.Equal("user_001", deserialized.Participants[0].Id);
        Assert.Equal("agent_001", deserialized.Participants[1].Id);
        Assert.Equal(5, deserialized.UnreadCount);
    }

    [Fact]
    public void RunError_WithDetails_SerializesCorrectly()
    {
        // Arrange
        var error = new RunError
        {
            Code = "context_length_exceeded",
            Message = "The conversation exceeded the maximum token limit",
            Details = new Dictionary<string, object>
            {
                ["maxTokens"] = 128000,
                ["actualTokens"] = 150000,
                ["exceeded"] = true
            }
        };

        // Act
        var json = JsonSerializer.Serialize(error, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<RunError>(json, _jsonOptions);

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal(error.Code, deserialized.Code);
        Assert.Equal(error.Message, deserialized.Message);
        Assert.NotNull(deserialized.Details);
        Assert.Equal(3, deserialized.Details.Count);
    }

    [Fact]
    public void CompletionUsage_SerializesCorrectly()
    {
        // Arrange
        var usage = new CompletionUsage
        {
            InputTokens = 1000,
            OutputTokens = 500,
            TotalTokens = 1500
        };

        // Act
        var json = JsonSerializer.Serialize(usage, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<CompletionUsage>(json, _jsonOptions);

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal(1000, deserialized.InputTokens);
        Assert.Equal(500, deserialized.OutputTokens);
        Assert.Equal(1500, deserialized.TotalTokens);
    }

    [Fact]
    public void AgentCard_WithCapabilities_SerializesCorrectly()
    {
        // Arrange
        var card = new AgentCard
        {
            AgentId = "agent_001",
            Name = "GPT-4o Agent",
            Description = "Advanced AI assistant",
            Capabilities = new AgentCapabilities
            {
                Vision = true,
                Thinking = false,
                Tools = true,
                MaxTokens = 128000,
                ContentTypes = new List<string> { "text", "image", "audio" }
            },
            Tools = new List<AITool>
            {
                new AITool
                {
                    Name = "web_search",
                    Description = "Search the web",
                    Parameters = new JSONSchema { SchemaType = "object" }
                }
            }
        };

        // Act
        var json = JsonSerializer.Serialize(card, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<AgentCard>(json, _jsonOptions);

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal("agent_001", deserialized.AgentId);
        Assert.NotNull(deserialized.Capabilities);
        Assert.True(deserialized.Capabilities.Vision);
        Assert.False(deserialized.Capabilities.Thinking);
        Assert.Equal(128000, deserialized.Capabilities.MaxTokens);
        Assert.Equal(3, deserialized.Capabilities.ContentTypes?.Count);
    }

    [Fact]
    public void RunStatus_EnumValues_SerializeAsStrings()
    {
        // Arrange - Test all run status values
        var statuses = new[]
        {
            RunStatus.Queued,
            RunStatus.InProgress,
            RunStatus.RequiresAction,
            RunStatus.InputRequired,
            RunStatus.AuthRequired,
            RunStatus.Cancelling,
            RunStatus.Cancelled,
            RunStatus.Failed,
            RunStatus.Completed,
            RunStatus.Incomplete,
            RunStatus.Timeout
        };

        // Act & Assert
        foreach (var status in statuses)
        {
            var json = JsonSerializer.Serialize(status, _jsonOptions);
            var deserialized = JsonSerializer.Deserialize<RunStatus>(json, _jsonOptions);
            Assert.Equal(status, deserialized);
        }
    }

    [Fact]
    public void NullableFields_OmittedInSerialization()
    {
        // Arrange - Test that null fields are not included in JSON
        var run = new Run
        {
            AgentId = "agent_001",
            Input = new List<ChatMessage>(),
            ThreadId = null, // Should be omitted
            JournalId = null, // Should be omitted
            Metadata = null // Should be omitted
        };

        // Act
        var json = JsonSerializer.Serialize(run, _jsonOptions);

        // Assert
        Assert.DoesNotContain("threadId", json);
        Assert.DoesNotContain("journalId", json);
        Assert.DoesNotContain("metadata", json);
        Assert.Contains("agentId", json);
        Assert.Contains("input", json);
    }

    [Fact]
    public void FunctionResultContent_WithError_SerializesCorrectly()
    {
        // Arrange
        var content = new FunctionResultContent
        {
            CallId = "call_123",
            Name = "delete_file",
            Result = "Error: Permission denied",
            IsError = true
        };

        // Act
        var json = JsonSerializer.Serialize<Content>(content, _jsonOptions);
        var deserialized = JsonSerializer.Deserialize<Content>(json, _jsonOptions) as FunctionResultContent;

        // Assert
        Assert.NotNull(deserialized);
        Assert.Equal("call_123", deserialized.CallId);
        Assert.Equal("delete_file", deserialized.Name);
        Assert.Contains("Permission denied", deserialized.Result);
        Assert.True(deserialized.IsError);
    }

    [Fact]
    public void ToolOutput_SerializesWithSnakeCase()
    {
        // Arrange - Tool output uses snake_case for tool_call_id
        var toolOutput = new ToolOutput
        {
            ToolCallId = "call_abc123",
            Output = "File deleted successfully"
        };

        // Act
        var json = JsonSerializer.Serialize(toolOutput, _jsonOptions);

        // Assert
        Assert.Contains("tool_call_id", json); // Should use snake_case
        Assert.Contains("call_abc123", json);
        Assert.Contains("output", json);
    }
}
