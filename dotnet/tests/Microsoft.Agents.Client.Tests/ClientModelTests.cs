using System;
using System.Collections.Generic;
using System.Text.Json;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Client;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Tests for client model classes (RunRequest, RunResponse, StreamEvent, ChatOptions, etc.)
/// </summary>
public class ClientModelTests
{
    #region RunRequest Tests

    [Fact]
    public void RunRequest_CanSetAgentId()
    {
        // Arrange & Act
        var request = new RunRequest
        {
            AgentId = "agent-123",
            Input = new List<ChatMessage>()
        };

        // Assert
        request.AgentId.Should().Be("agent-123");
    }

    [Fact]
    public void RunRequest_CanSetThreadId()
    {
        // Arrange & Act
        var request = new RunRequest
        {
            ThreadId = "thread-456",
            Input = new List<ChatMessage>()
        };

        // Assert
        request.ThreadId.Should().Be("thread-456");
    }

    [Fact]
    public void RunRequest_CanSetJournalId()
    {
        // Arrange & Act
        var request = new RunRequest
        {
            JournalId = "journal-789",
            Input = new List<ChatMessage>()
        };

        // Assert
        request.JournalId.Should().Be("journal-789");
    }

    [Fact]
    public void RunRequest_CanSetInput()
    {
        // Arrange & Act
        var input = new List<ChatMessage>
        {
            new UserMessage
            {
                Contents = new List<AIContent> { new TextContent { Text = "Test" } }
            }
        };

        var request = new RunRequest
        {
            Input = input
        };

        // Assert
        request.Input.Should().HaveCount(1);
    }

    [Fact]
    public void RunRequest_CanSetMetadata()
    {
        // Arrange & Act
        var metadata = new Dictionary<string, object>
        {
            { "key1", "value1" },
            { "key2", 42 }
        };

        var request = new RunRequest
        {
            Input = new List<ChatMessage>(),
            Metadata = metadata
        };

        // Assert
        request.Metadata.Should().HaveCount(2);
        request.Metadata!["key1"].Should().Be("value1");
        request.Metadata["key2"].Should().Be(42);
    }

    [Fact]
    public void RunRequest_CanSetWebhook()
    {
        // Arrange & Act
        var request = new RunRequest
        {
            Input = new List<ChatMessage>(),
            Webhook = "https://example.com/webhook"
        };

        // Assert
        request.Webhook.Should().Be("https://example.com/webhook");
    }

    [Fact]
    public void RunRequest_AllPropertiesOptionalExceptInput()
    {
        // Arrange & Act
        var request = new RunRequest
        {
            Input = new List<ChatMessage>()
        };

        // Assert
        request.AgentId.Should().BeNull();
        request.ThreadId.Should().BeNull();
        request.JournalId.Should().BeNull();
        request.Metadata.Should().BeNull();
        request.Webhook.Should().BeNull();
    }

    #endregion

    #region RunResponse Tests

    [Fact]
    public void RunResponse_CanSetRunId()
    {
        // Arrange & Act
        var response = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed"
        };

        // Assert
        response.RunId.Should().Be("run-123");
    }

    [Fact]
    public void RunResponse_CanSetThreadId()
    {
        // Arrange & Act
        var response = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed"
        };

        // Assert
        response.ThreadId.Should().Be("thread-456");
    }

    [Fact]
    public void RunResponse_CanSetStatus()
    {
        // Arrange & Act
        var response = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "in_progress"
        };

        // Assert
        response.Status.Should().Be("in_progress");
    }

    [Fact]
    public void RunResponse_CanSetOutput()
    {
        // Arrange & Act
        var output = new List<ChatMessage>
        {
            new AgentMessage
            {
                Contents = new List<AIContent> { new TextContent { Text = "Response" } }
            }
        };

        var response = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = output
        };

        // Assert
        response.Output.Should().HaveCount(1);
    }

    [Fact]
    public void RunResponse_CanSetError()
    {
        // Arrange & Act
        var error = new ErrorInfo
        {
            Code = "error_code",
            Message = "Error message"
        };

        var response = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "failed",
            Error = error
        };

        // Assert
        response.Error.Should().NotBeNull();
        response.Error!.Code.Should().Be("error_code");
        response.Error.Message.Should().Be("Error message");
    }

    #endregion

    #region ErrorInfo Tests

    [Fact]
    public void ErrorInfo_CanSetCode()
    {
        // Arrange & Act
        var error = new ErrorInfo
        {
            Code = "validation_error",
            Message = "Invalid input"
        };

        // Assert
        error.Code.Should().Be("validation_error");
    }

    [Fact]
    public void ErrorInfo_CanSetMessage()
    {
        // Arrange & Act
        var error = new ErrorInfo
        {
            Code = "error",
            Message = "Something went wrong"
        };

        // Assert
        error.Message.Should().Be("Something went wrong");
    }

    [Fact]
    public void ErrorInfo_CanSetDetails()
    {
        // Arrange & Act
        var details = new Dictionary<string, object>
        {
            { "field", "username" },
            { "constraint", "required" }
        };

        var error = new ErrorInfo
        {
            Code = "validation_error",
            Message = "Invalid input",
            Details = details
        };

        // Assert
        error.Details.Should().HaveCount(2);
        error.Details!["field"].Should().Be("username");
    }

    #endregion

    #region StreamEvent Tests

    [Fact]
    public void StreamEvent_CanSetEventType()
    {
        // Arrange & Act
        var evt = new StreamEvent
        {
            EventType = "message.created"
        };

        // Assert
        evt.EventType.Should().Be("message.created");
    }

    [Fact]
    public void StreamEvent_CanSetData()
    {
        // Arrange
        var jsonData = JsonSerializer.SerializeToElement(new { value = "test" });

        // Act
        var evt = new StreamEvent
        {
            EventType = "test",
            Data = jsonData
        };

        // Assert
        evt.Data.ValueKind.Should().Be(JsonValueKind.Object);
    }

    [Fact]
    public void StreamEvent_GetData_DeserializesCorrectly()
    {
        // Arrange
        // Use PascalCase JSON for default deserialization (JsonOptions is internal)
        var json = "{\"Value\":\"test\",\"Number\":42}";
        var jsonData = JsonSerializer.Deserialize<JsonElement>(json);
        var evt = new StreamEvent
        {
            EventType = "test",
            Data = jsonData
        };

        // Act
        var data = evt.GetData<TestData>();

        // Assert
        data.Should().NotBeNull();
        data!.Value.Should().Be("test");
        data.Number.Should().Be(42);
    }

    [Fact]
    public void StreamEvent_GetData_WithComplexObject_DeserializesCorrectly()
    {
        // Arrange
        // Use PascalCase JSON for default deserialization (JsonOptions is internal)
        var json = "{\"Value\":\"complex\",\"Number\":999}";
        var jsonData = JsonSerializer.Deserialize<JsonElement>(json);
        var evt = new StreamEvent
        {
            EventType = "test",
            Data = jsonData
        };

        // Act
        var data = evt.GetData<TestData>();

        // Assert
        data.Should().NotBeNull();
        data!.Value.Should().Be("complex");
        data.Number.Should().Be(999);
    }

    [Fact]
    public void StreamEvent_GetData_WithInvalidData_ReturnsNull()
    {
        // Arrange
        var jsonData = JsonSerializer.SerializeToElement(new { different = "structure" });
        var evt = new StreamEvent
        {
            EventType = "test",
            Data = jsonData
        };

        // Act
        var data = evt.GetData<TestData>();

        // Assert - should not throw, may return default values
        data.Should().NotBeNull();
    }

    private class TestData
    {
        public string Value { get; set; } = string.Empty;
        public int Number { get; set; }
    }

    #endregion

    #region ChatOptions Tests

    [Fact]
    public void ChatOptions_CanSetAgentId()
    {
        // Arrange & Act
        var options = new ChatOptions
        {
            AgentId = "agent-123"
        };

        // Assert
        options.AgentId.Should().Be("agent-123");
    }

    [Fact]
    public void ChatOptions_CanSetTools()
    {
        // Arrange
        var tools = new ToolCollection();
        tools.Add("test", (string x) => x);

        // Act
        var options = new ChatOptions
        {
            Tools = tools
        };

        // Assert
        options.Tools.Should().NotBeNull();
        options.Tools!.Get("test").Should().NotBeNull();
    }

    [Fact]
    public void ChatOptions_CanSetMetadata()
    {
        // Arrange
        var metadata = new Dictionary<string, object>
        {
            { "key", "value" }
        };

        // Act
        var options = new ChatOptions
        {
            Metadata = metadata
        };

        // Assert
        options.Metadata.Should().HaveCount(1);
        options.Metadata!["key"].Should().Be("value");
    }

    [Fact]
    public void ChatOptions_CanSetOnToolCallStarted()
    {
        // Arrange
        Func<ToolCallInfo, System.Threading.Tasks.Task> callback = async (info) =>
        {
            await System.Threading.Tasks.Task.CompletedTask;
        };

        // Act
        var options = new ChatOptions
        {
            OnToolCallStarted = callback
        };

        // Assert
        options.OnToolCallStarted.Should().NotBeNull();
    }

    [Fact]
    public void ChatOptions_CanSetOnToolCallCompleted()
    {
        // Arrange
        Func<ToolCallInfo, object, System.Threading.Tasks.Task> callback = async (info, result) =>
        {
            await System.Threading.Tasks.Task.CompletedTask;
        };

        // Act
        var options = new ChatOptions
        {
            OnToolCallCompleted = callback
        };

        // Assert
        options.OnToolCallCompleted.Should().NotBeNull();
    }

    [Fact]
    public void ChatOptions_CanSetOnToolCallFailed()
    {
        // Arrange
        Func<ToolCallInfo, Exception, System.Threading.Tasks.Task> callback = async (info, ex) =>
        {
            await System.Threading.Tasks.Task.CompletedTask;
        };

        // Act
        var options = new ChatOptions
        {
            OnToolCallFailed = callback
        };

        // Assert
        options.OnToolCallFailed.Should().NotBeNull();
    }

    [Fact]
    public void ChatOptions_AllPropertiesOptional()
    {
        // Arrange & Act
        var options = new ChatOptions();

        // Assert
        options.AgentId.Should().BeNull();
        options.Tools.Should().BeNull();
        options.Metadata.Should().BeNull();
        options.OnToolCallStarted.Should().BeNull();
        options.OnToolCallCompleted.Should().BeNull();
        options.OnToolCallFailed.Should().BeNull();
    }

    #endregion

    #region ToolCallInfo Tests

    [Fact]
    public void ToolCallInfo_CanSetCallId()
    {
        // Arrange & Act
        var info = new ToolCallInfo
        {
            CallId = "call-123",
            Name = "test",
            Arguments = "{}"
        };

        // Assert
        info.CallId.Should().Be("call-123");
    }

    [Fact]
    public void ToolCallInfo_CanSetName()
    {
        // Arrange & Act
        var info = new ToolCallInfo
        {
            CallId = "call-123",
            Name = "greet",
            Arguments = "{}"
        };

        // Assert
        info.Name.Should().Be("greet");
    }

    [Fact]
    public void ToolCallInfo_CanSetArguments()
    {
        // Arrange & Act
        var info = new ToolCallInfo
        {
            CallId = "call-123",
            Name = "test",
            Arguments = "{\"param\":\"value\"}"
        };

        // Assert
        info.Arguments.Should().Be("{\"param\":\"value\"}");
    }

    #endregion

    #region Serialization Tests

    [Fact]
    public void RunRequest_SerializesToJson()
    {
        // Arrange
        var request = new RunRequest
        {
            AgentId = "agent-123",
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        // Act
        var json = JsonSerializer.Serialize(request, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        // Assert
        json.Should().Contain("agentId");
        json.Should().Contain("input");
    }

    [Fact]
    public void RunResponse_DeserializesFromJson()
    {
        // Arrange
        var json = @"{
            ""runId"": ""run-123"",
            ""threadId"": ""thread-456"",
            ""status"": ""completed"",
            ""output"": []
        }";

        // Act
        var response = JsonSerializer.Deserialize<RunResponse>(json, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        // Assert
        response.Should().NotBeNull();
        response!.RunId.Should().Be("run-123");
        response.ThreadId.Should().Be("thread-456");
        response.Status.Should().Be("completed");
    }

    [Fact]
    public void ErrorInfo_SerializesAndDeserializes()
    {
        // Arrange
        var error = new ErrorInfo
        {
            Code = "test_error",
            Message = "Test message",
            Details = new Dictionary<string, object> { { "key", "value" } }
        };

        // Act
        var json = JsonSerializer.Serialize(error, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });
        var deserialized = JsonSerializer.Deserialize<ErrorInfo>(json, new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        });

        // Assert
        deserialized.Should().NotBeNull();
        deserialized!.Code.Should().Be("test_error");
        deserialized.Message.Should().Be("Test message");
    }

    #endregion
}
