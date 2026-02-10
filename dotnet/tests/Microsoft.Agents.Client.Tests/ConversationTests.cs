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
/// Comprehensive tests for Conversation interface and implementation
/// </summary>
public class ConversationTests : IDisposable
{
    private readonly Mock<HttpMessageHandler> _mockHandler;
    private readonly HttpClient _httpClient;
    private readonly AgentProtocolClient _client;

    public ConversationTests()
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

    #region CreateConversation Tests

    [Fact]
    public void CreateConversation_HasNullThreadId()
    {
        // Act
        var conversation = _client.CreateConversation();

        // Assert
        conversation.ThreadId.Should().BeNull();
    }

    [Fact]
    public async Task CreateConversation_FirstMessage_CreatesThread()
    {
        // Arrange
        var conversation = _client.CreateConversation();

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
                        new TextContent { Text = "Hello!" }
                    }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var response = await conversation.SendAsync("Hi");

        // Assert
        conversation.ThreadId.Should().Be("thread-456");
        response.Should().Be("Hello!");
    }

    [Fact]
    public async Task CreateConversation_SecondMessage_UsesExistingThread()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        var firstResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Hello!" } }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, firstResponse);
        await conversation.SendAsync("Hi");

        var secondResponse = new RunResponse
        {
            RunId = "run-124",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "How are you?" } }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, secondResponse);

        // Act
        var response = await conversation.SendAsync("Fine");

        // Assert
        conversation.ThreadId.Should().Be("thread-456");
        response.Should().Be("How are you?");
    }

    #endregion

    #region ResumeConversation Tests

    [Fact]
    public void ResumeConversation_HasProvidedThreadId()
    {
        // Act
        var conversation = _client.ResumeConversation("thread-789");

        // Assert
        conversation.ThreadId.Should().Be("thread-789");
    }

    [Fact]
    public async Task ResumeConversation_SendMessage_UsesExistingThreadId()
    {
        // Arrange
        var conversation = _client.ResumeConversation("thread-789");

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-789",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Welcome back!" } }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var response = await conversation.SendAsync("I'm back");

        // Assert
        conversation.ThreadId.Should().Be("thread-789");
        response.Should().Be("Welcome back!");
    }

    #endregion

    #region SendAsync(string) Tests

    [Fact]
    public async Task SendAsync_String_ReturnsTextResponse()
    {
        // Arrange
        var conversation = _client.CreateConversation();

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
        var result = await conversation.SendAsync("Test message");

        // Assert
        result.Should().Be("Response text");
    }

    [Fact]
    public async Task SendAsync_String_NoOutput_ReturnsEmptyString()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>()
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await conversation.SendAsync("Test");

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public async Task SendAsync_String_NoAgentMessage_ReturnsEmptyString()
    {
        // Arrange
        var conversation = _client.CreateConversation();

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
        var result = await conversation.SendAsync("Test");

        // Assert
        result.Should().BeEmpty();
    }

    [Fact]
    public async Task SendAsync_String_NoTextContent_ReturnsEmptyString()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-456",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent>()
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        var result = await conversation.SendAsync("Test");

        // Assert
        result.Should().BeEmpty();
    }

    #endregion

    #region SendAsync(ChatMessage) Tests

    [Fact]
    public async Task SendAsync_ChatMessage_ReturnsMessage()
    {
        // Arrange
        var conversation = _client.CreateConversation();
        var inputMessage = new UserMessage
        {
            Contents = new List<AIContent> { new TextContent { Text = "Test" } }
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
        var result = await conversation.SendAsync(inputMessage);

        // Assert
        result.Should().NotBeNull();
        result.Role.Should().Be(ChatRole.Agent);
        var textContent = result.Contents?.OfType<TextContent>().FirstOrDefault();
        textContent?.Text.Should().Be("Response");
    }

    [Fact]
    public async Task SendAsync_ChatMessage_NoOutput_ReturnsEmptyMessage()
    {
        // Arrange
        var conversation = _client.CreateConversation();
        var inputMessage = new UserMessage
        {
            Contents = new List<AIContent> { new TextContent { Text = "Test" } }
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
        var result = await conversation.SendAsync(inputMessage);

        // Assert
        result.Should().NotBeNull();
        result.Contents.Should().NotBeNull();
        result.Contents.Should().BeEmpty();
    }

    [Fact]
    public async Task SendAsync_ChatMessage_UpdatesThreadId()
    {
        // Arrange
        var conversation = _client.CreateConversation();
        conversation.ThreadId.Should().BeNull();

        var inputMessage = new UserMessage
        {
            Contents = new List<AIContent> { new TextContent { Text = "Test" } }
        };

        var expectedResponse = new RunResponse
        {
            RunId = "run-123",
            ThreadId = "thread-new",
            Status = "completed",
            Output = new List<ChatMessage>
            {
                new AgentMessage
                {
                    Contents = new List<AIContent> { new TextContent { Text = "Response" } }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedResponse);

        // Act
        await conversation.SendAsync(inputMessage);

        // Assert
        conversation.ThreadId.Should().Be("thread-new");
    }

    #endregion

    #region StreamMessagesAsync Tests

    [Fact]
    public async Task StreamMessagesAsync_YieldsMessages()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-456"",""status"":""in_progress""}

event: message.created
data: {""$type"":""agent"",""messageId"":""msg-1"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Hello""}]}

event: message.updated
data: {""$type"":""agent"",""messageId"":""msg-1"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Hello World""}]}

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
        var messages = new List<ChatMessage>();
        await foreach (var message in conversation.StreamMessagesAsync("Test"))
        {
            messages.Add(message);
        }

        // Assert
        messages.Should().HaveCount(2);
        conversation.ThreadId.Should().Be("thread-456");
    }

    [Fact]
    public async Task StreamMessagesAsync_SkipsNonMessageEvents()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-456"",""status"":""in_progress""}

event: some.other.event
data: {""data"":""value""}

event: message.created
data: {""$type"":""agent"",""messageId"":""msg-1"",""role"":""agent"",""contents"":[{""$type"":""text"",""type"":""text"",""text"":""Hello""}]}

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
        var messages = new List<ChatMessage>();
        await foreach (var message in conversation.StreamMessagesAsync("Test"))
        {
            messages.Add(message);
        }

        // Assert
        messages.Should().HaveCount(1);
    }

    [Fact]
    public async Task StreamMessagesAsync_UpdatesThreadIdFromFirstEvent()
    {
        // Arrange
        var conversation = _client.CreateConversation();
        conversation.ThreadId.Should().BeNull();

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-new"",""status"":""in_progress""}

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
        await foreach (var message in conversation.StreamMessagesAsync("Test"))
        {
            // Just consume
        }

        // Assert
        conversation.ThreadId.Should().Be("thread-new");
    }

    #endregion

    #region StreamEventsAsync Tests

    [Fact]
    public async Task StreamEventsAsync_YieldsAllEvents()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-456"",""status"":""in_progress""}

event: message.created
data: {""messageId"":""msg-1"",""role"":""agent""}

event: message.delta
data: {""messageId"":""msg-1"",""role"":""agent""}

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
        await foreach (var evt in conversation.StreamEventsAsync("Test"))
        {
            events.Add(evt);
        }

        // Assert
        events.Should().HaveCount(3);
        events[0].EventType.Should().Be("run.started");
        events[1].EventType.Should().Be("message.created");
        events[2].EventType.Should().Be("message.delta");
    }

    [Fact]
    public async Task StreamEventsAsync_UpdatesThreadId()
    {
        // Arrange
        var conversation = _client.CreateConversation();
        conversation.ThreadId.Should().BeNull();

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-xyz"",""status"":""in_progress""}

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
        await foreach (var evt in conversation.StreamEventsAsync("Test"))
        {
            // Just consume
        }

        // Assert
        conversation.ThreadId.Should().Be("thread-xyz");
    }

    [Fact]
    public async Task StreamEventsAsync_WithExistingThreadId_DoesNotChangeThreadId()
    {
        // Arrange
        var conversation = _client.ResumeConversation("thread-existing");

        var sseContent = @"event: run.started
data: {""runId"":""run-123"",""threadId"":""thread-existing"",""status"":""in_progress""}

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
        await foreach (var evt in conversation.StreamEventsAsync("Test"))
        {
            // Just consume
        }

        // Assert
        conversation.ThreadId.Should().Be("thread-existing");
    }

    #endregion

    #region GetMessagesAsync Tests

    [Fact]
    public async Task GetMessagesAsync_WithThreadId_ReturnsMessages()
    {
        // Arrange
        var conversation = _client.ResumeConversation("thread-123");

        var expectedMessages = new List<ChatMessage>
        {
            new UserMessage
            {
                MessageId = "msg-1",
                Contents = new List<AIContent>
                {
                    new TextContent { Text = "Hello" }
                }
            },
            new AgentMessage
            {
                MessageId = "msg-2",
                Contents = new List<AIContent>
                {
                    new TextContent { Text = "Hi there!" }
                }
            }
        };

        SetupHttpResponse(HttpStatusCode.OK, expectedMessages);

        // Act
        var actualMessages = await conversation.GetMessagesAsync();

        // Assert
        actualMessages.Should().NotBeNull();
        actualMessages.Should().HaveCount(2);
        actualMessages[0].MessageId.Should().Be("msg-1");
        actualMessages[1].MessageId.Should().Be("msg-2");
    }

    [Fact]
    public async Task GetMessagesAsync_WithoutThreadId_ThrowsInvalidOperationException()
    {
        // Arrange
        var conversation = _client.CreateConversation();

        // Act & Assert
        var exception = await Xunit.Assert.ThrowsAsync<InvalidOperationException>(
            () => conversation.GetMessagesAsync());

        exception.Message.Should().Contain("No thread ID available");
        exception.Message.Should().Contain("Send a message");
    }

    [Fact]
    public async Task GetMessagesAsync_EmptyThread_ReturnsEmptyList()
    {
        // Arrange
        var conversation = _client.ResumeConversation("thread-empty");

        SetupHttpResponse(HttpStatusCode.OK, new List<ChatMessage>());

        // Act
        var messages = await conversation.GetMessagesAsync();

        // Assert
        messages.Should().NotBeNull();
        messages.Should().BeEmpty();
    }

    [Fact]
    public async Task GetMessagesAsync_PropagatesCancellation()
    {
        // Arrange
        var conversation = _client.ResumeConversation("thread-123");
        var cts = new CancellationTokenSource();
        cts.Cancel();

        _mockHandler.Protected()
            .Setup<Task<HttpResponseMessage>>(
                "SendAsync",
                ItExpr.IsAny<HttpRequestMessage>(),
                ItExpr.IsAny<CancellationToken>())
            .ThrowsAsync(new OperationCanceledException());

        // Act & Assert
        await Xunit.Assert.ThrowsAsync<OperationCanceledException>(
            () => conversation.GetMessagesAsync(cts.Token));
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

    #endregion
}
