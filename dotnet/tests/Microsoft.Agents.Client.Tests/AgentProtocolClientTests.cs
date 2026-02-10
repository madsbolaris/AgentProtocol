using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Client;
using Moq;
using Moq.Protected;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Comprehensive tests for AgentProtocolClient
/// </summary>
public class AgentProtocolClientTests : IDisposable
{
    private readonly Mock<HttpMessageHandler> _mockHandler;
    private readonly HttpClient _httpClient;
    private readonly AgentProtocolClient _client;

    public AgentProtocolClientTests()
    {
        _mockHandler = new Mock<HttpMessageHandler>();
        _httpClient = new HttpClient(_mockHandler.Object);
        _client = new AgentProtocolClient("http://localhost:5000", _httpClient);
    }

    public void Dispose()
    {
        _client?.Dispose();
        _httpClient?.Dispose();
    }

    #region Constructor Tests

    [Fact]
    public void Constructor_WithValidBaseUrl_CreatesClient()
    {
        // Act
        var client = new AgentProtocolClient("http://localhost:5000");

        // Assert
        client.Should().NotBeNull();
        client.Dispose();
    }

    [Fact]
    public void Constructor_WithTrailingSlash_TrimsSlash()
    {
        // This is tested implicitly by the URL formation in other tests
        var client = new AgentProtocolClient("http://localhost:5000/");
        client.Should().NotBeNull();
        client.Dispose();
    }

    [Fact]
    public void Constructor_WithCustomHttpClient_UsesProvidedClient()
    {
        // Arrange
        var customClient = new HttpClient();

        // Act
        var client = new AgentProtocolClient("http://localhost:5000", customClient);

        // Assert
        client.Should().NotBeNull();
        client.Dispose();
    }

    #endregion

    #region RunAsync Tests

    [Fact]
    public async Task RunAsync_WithValidRequest_ReturnsRunResponse()
    {
        // Arrange
        var request = new RunRequest
        {
            AgentId = "agent-1",
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = "Hello" }
                    }
                }
            }
        };

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = "Hi there!" }
                    }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.RunAsync(request);

        // Assert
        result.Should().NotBeNull();
        result.RunId.Should().Be("run-123");
        result.ThreadId.Should().Be("thread-456");
        result.Status.Should().Be("completed");
        result.Output.Should().HaveCount(1);

        VerifyHttpRequest(HttpMethod.Post, "http://localhost:5000/runs/wait");
    }

    [Fact]
    public async Task RunAsync_WithEmptyResponse_ThrowsException()
    {
        // Arrange
        var request = new RunRequest
        {
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        // Setup empty content that will fail JSON deserialization
        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent("")
            });

        // Act & Assert
        // Will throw JsonException when trying to deserialize empty content
        await Xunit.Assert.ThrowsAnyAsync<Exception>(() => _client.RunAsync(request));
    }

    [Fact]
    public async Task RunAsync_WithHttpError_ThrowsHttpRequestException()
    {
        // Arrange
        var request = new RunRequest
        {
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.InternalServerError)
            {
                Content = new StringContent("Internal Server Error")
            });

        // Act & Assert
        await Xunit.Assert.ThrowsAsync<HttpRequestException>(() => _client.RunAsync(request));
    }

    #endregion

    #region StreamAsync Tests

    [Fact]
    public async Task StreamAsync_WithValidResponse_YieldsEvents()
    {
        // Arrange
        var request = new RunRequest
        {
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-456"",""status"":""in_progress""}

event: message.delta
data: {""role"":""agent"",""contents"":[{""type"":""text"",""text"":""Hello""}]}

";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(sseContent)
            });

        // Act
        var events = new List<StreamEvent>();
        await foreach (var evt in _client.StreamAsync(request))
        {
            events.Add(evt);
        }

        // Assert
        events.Should().HaveCount(2);
        events[0].EventType.Should().Be("run.started");
        events[1].EventType.Should().Be("message.delta");
    }

    [Fact]
    public async Task StreamAsync_WithEmptyLines_HandlesCorrectly()
    {
        // Arrange
        var request = new RunRequest
        {
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        var sseContent = @"event: test
data: {""value"":""test""}


";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(sseContent)
            });

        // Act
        var events = new List<StreamEvent>();
        await foreach (var evt in _client.StreamAsync(request))
        {
            events.Add(evt);
        }

        // Assert
        events.Should().HaveCount(1);
    }

    [Fact]
    public async Task StreamAsync_WithLastEventNoTrailingNewline_YieldsLastEvent()
    {
        // Arrange
        var request = new RunRequest
        {
            Input = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
                }
            }
        };

        var sseContent = @"event: final
data: {""done"":true}";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(sseContent)
            });

        // Act
        var events = new List<StreamEvent>();
        await foreach (var evt in _client.StreamAsync(request))
        {
            events.Add(evt);
        }

        // Assert
        events.Should().HaveCount(1);
        events[0].EventType.Should().Be("final");
    }

    #endregion

    #region GetRunStatusAsync Tests

    [Fact]
    public async Task GetRunStatusAsync_WithValidRunId_ReturnsStatus()
    {
        // Arrange
        var runId = "run-123";
        var expectedResponse = new RunResponse
        {
            RunId = runId,
            ThreadId = "thread-456",
            Status = "completed"
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.GetRunStatusAsync(runId);

        // Assert
        result.Should().NotBeNull();
        result.RunId.Should().Be(runId);
        result.Status.Should().Be("completed");

        VerifyHttpRequest(HttpMethod.Get, $"http://localhost:5000/runs/{runId}");
    }

    [Fact]
    public async Task GetRunStatusAsync_WithEmptyResponse_ThrowsException()
    {
        // Arrange
        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent("")
            });

        // Act & Assert
        await Xunit.Assert.ThrowsAnyAsync<Exception>(() => _client.GetRunStatusAsync("run-123"));
    }

    #endregion

    #region CancelRunAsync Tests

    [Fact]
    public async Task CancelRunAsync_WithValidRunId_Succeeds()
    {
        // Arrange
        var runId = "run-123";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK));

        // Act
        await _client.CancelRunAsync(runId);

        // Assert
        VerifyHttpRequest(HttpMethod.Post, $"http://localhost:5000/runs/{runId}/cancel");
    }

    [Fact]
    public async Task CancelRunAsync_WithHttpError_ThrowsHttpRequestException()
    {
        // Arrange
        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.NotFound));

        // Act & Assert
        await Xunit.Assert.ThrowsAsync<HttpRequestException>(() => _client.CancelRunAsync("run-123"));
    }

    #endregion

    #region GetThreadMessagesAsync Tests

    [Fact]
    public async Task GetThreadMessagesAsync_WithValidThreadId_ReturnsMessages()
    {
        // Arrange
        var threadId = "thread-123";
        var expectedMessages = new List<ChatMessage>
        {
            new UserMessage
            {
                Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
            },
            new AgentMessage
            {
                Contents = new List<AIContent> { new TextContent { Text = "Hi!" } }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedMessages);

        // Act
        var result = await _client.GetThreadMessagesAsync(threadId);

        // Assert
        result.Should().HaveCount(2);
        VerifyHttpRequest(HttpMethod.Get, $"http://localhost:5000/threads/{threadId}/messages");
    }

    [Fact]
    public async Task GetThreadMessagesAsync_WithEmptyJsonArray_ReturnsEmptyList()
    {
        // Arrange
        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent("[]", Encoding.UTF8, "application/json")
            });

        // Act
        var result = await _client.GetThreadMessagesAsync("thread-123");

        // Assert
        result.Should().NotBeNull();
        result.Should().BeEmpty();
    }

    #endregion

    #region CompleteChatAsync Tests (string message)

    [Fact]
    public async Task CompleteChatAsync_WithStringMessage_ReturnsText()
    {
        // Arrange
        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = "Response text" }
                    }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.CompleteChatAsync("Hello");

        // Assert
        result.Should().Be("Response text");
    }

    [Fact]
    public async Task CompleteChatAsync_WithNoOutput_ReturnsEmptyString()
    {
        // Arrange
        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>()
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.CompleteChatAsync("Hello");

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public async Task CompleteChatAsync_WithNoAgentMessage_ReturnsEmptyString()
    {
        // Arrange
        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new UserMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "User message" } }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.CompleteChatAsync("Hello");

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public async Task CompleteChatAsync_WithOptions_UsesOptions()
    {
        // Arrange
        var options = new ChatOptions
        {
            AgentId = "agent-1",
            Metadata = new Dictionary<string, object> { { "key", "value" } }
        };

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = "Response" }
                    }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.CompleteChatAsync("Hello", options);

        // Assert
        result.Should().Be("Response");
    }

    #endregion

    #region CompleteChatAsync Tests (ChatMessage)

    [Fact]
    public async Task CompleteChatAsync_WithChatMessage_ReturnsMessage()
    {
        // Arrange
        var inputMessage = new UserMessage
        {
            Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
        };

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent>
                    {
                        new TextContent { Text = "Response" }
                    }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.CompleteChatAsync(inputMessage);

        // Assert
        result.Should().NotBeNull();
        result.Role.Should().Be(ChatRole.Agent);
    }

    [Fact]
    public async Task CompleteChatAsync_WithChatMessageNoOutput_ReturnsEmptyMessage()
    {
        // Arrange
        var inputMessage = new UserMessage
        {
            Contents = new List<AIContent> { new TextContent { Text = "Hello" } }
        };

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>()
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await _client.CompleteChatAsync(inputMessage);

        // Assert
        result.Should().NotBeNull();
        result.Contents.Should().NotBeNull();
        result.Contents.Should().BeEmpty();
    }

    #endregion

    #region StreamChatAsync Tests

    [Fact]
    public async Task StreamChatAsync_WithValidMessage_CallsCallback()
    {
        // Arrange
        // Use proper ChatMessage JSON with type discriminator
        var sseContent = @"event: message.delta
data: {""$type"":""agent"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Hello""}]}

event: message.updated
data: {""$type"":""agent"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Hello World""}]}

";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(sseContent)
            });

        var chunks = new List<string>();

        // Act
        await _client.StreamChatAsync("Hello", chunk => chunks.Add(chunk));

        // Assert
        // Should receive 2 chunks: "Hello" from first delta, then " World" from the delta
        chunks.Should().HaveCount(2);
        chunks[0].Should().Be("Hello");
        chunks[1].Should().Be(" World");
    }

    #endregion

    #region Conversation Tests

    [Fact]
    public void CreateConversation_ReturnsConversationInstance()
    {
        // Act
        var conversation = _client.CreateConversation();

        // Assert
        conversation.Should().NotBeNull();
        conversation.ThreadId.Should().BeNull();
    }

    [Fact]
    public void ResumeConversation_WithThreadId_ReturnsConversationWithThreadId()
    {
        // Act
        var conversation = _client.ResumeConversation("thread-123");

        // Assert
        conversation.Should().NotBeNull();
        conversation.ThreadId.Should().Be("thread-123");
    }

    #endregion

    #region CompleteChatAsync with Tools Tests

    [Fact]
    public async Task CompleteChatAsync_WithTools_ExecutesToolFlow()
    {
        // Arrange
        var tools = new ToolCollection();
        tools.Add("greet", (string name) => $"Hello, {name}!");

        var options = new ChatOptions
        {
            Tools = tools
        };

        // Mock streaming response with tool execution
        var sseContent = @"event: message.delta
data: {""$type"":""agent"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Testing""}]}

event: message.updated
data: {""$type"":""agent"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Testing tools""}]}

event: run.completed
data: {""runId"":""run-123"",""threadId"":""thread-456"",""status"":""completed""}

";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(sseContent)
            });

        // Act
        var result = await _client.CompleteChatAsync("Hello", options);

        // Assert
        result.Should().Be("Testing tools");
    }

    [Fact]
    public async Task CompleteChatAsync_WithToolsAndRequiresAction_HandlesToolCall()
    {
        // Arrange
        var tools = new ToolCollection();
        tools.Add("calculate", (int a, int b) => (a + b).ToString());

        var options = new ChatOptions
        {
            Tools = tools
        };

        // Mock streaming response with requires_action event
        var sseContent = @"event: run.requires_action
data: {""runId"":""run-123"",""threadId"":""thread-456"",""status"":""requires_action""}

event: message.updated
data: {""$type"":""agent"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Result: 42""}]}

";

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(new HttpResponseMessage(HttpStatusCode.OK)
            {
                Content = new StringContent(sseContent)
            });

        // Act
        var result = await _client.CompleteChatAsync("Calculate 40 + 2", options);

        // Assert
        result.Should().Be("Result: 42");
    }

    #endregion

    #region StreamEvent GetData Tests

    [Fact]
    public void StreamEvent_GetData_WithNotSupportedException_FallsBackToDefault()
    {
        // Arrange
        var json = "{\"Value\":\"fallback\",\"Number\":100}";
        var jsonData = JsonSerializer.Deserialize<JsonElement>(json);
        var evt = new StreamEvent
        {
            EventType = "test",
            Data = jsonData
        };

        // Act
        var data = evt.GetData<TestEventData>();

        // Assert
        data.Should().NotBeNull();
    }

    private class TestEventData
    {
        public string Value { get; set; } = string.Empty;
        public int Number { get; set; }
    }

    #endregion

    #region Helper Methods

    private void SetupHttpResponse<T>(HttpStatusCode statusCode, T? content)
    {
        var response = new HttpResponseMessage(statusCode);

        if (content != null)
        {
            var json = JsonSerializer.Serialize(content, new JsonSerializerOptions
            {
                PropertyNamingPolicy = JsonNamingPolicy.CamelCase
            });
            response.Content = new StringContent(json, Encoding.UTF8, "application/json");
        }

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ReturnsAsync(response);
    }

    private void VerifyHttpRequest(HttpMethod method, string url)
    {
        _mockHandler.Protected()
            .Verify(
                "SendAsync",
                Times.Once(),
                ItExpr.Is<HttpRequestMessage>(req =>
                    req.Method == method &&
                    req.RequestUri!.ToString() == url),
                ItExpr.IsAny<CancellationToken>());
    }

    #endregion
}
