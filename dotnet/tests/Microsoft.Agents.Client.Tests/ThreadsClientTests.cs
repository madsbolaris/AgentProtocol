using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol;
using Microsoft.Agents.Protocol.Models.Common;
using Microsoft.Agents.Protocol.Models.Execution;
using Microsoft.Agents.Protocol.Models.Messages;
using Microsoft.Agents.Protocol.Models.Threads;
using Microsoft.Agents.Client.Tests.TestHelpers;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Tests for ThreadsClient covering all documentation examples
/// </summary>
public class ThreadsClientTests
{
    [Fact]
    public async Task CreateAsync_WithParticipants_ReturnsCreatedThread()
    {
        // Arrange - Example from "Create a Thread" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedThread = new Thread
        {
            ThreadId = "thread_001",
            Title = "Customer Support Conversation",
            Participants = new List<Participant>
            {
                new Participant
                {
                    Id = "user_001",
                    Kind = "user",
                    Name = "John Doe"
                }
            },
            Status = ThreadStatus.Active,
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads",
            expectedThread,
            HttpStatusCode.Created
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var thread = new Thread
        {
            Title = "Customer Support Conversation",
            Participants = new List<Participant>
            {
                new Participant
                {
                    Id = "user_001",
                    Kind = "user",
                    Name = "John Doe"
                }
            }
        };

        // Act
        var result = await client.Threads.CreateAsync(thread);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("thread_001", result.ThreadId);
        Assert.Equal("Customer Support Conversation", result.Title);
        Assert.Single(result.Participants);
        Assert.Equal("user_001", result.Participants[0].Id);
    }

    [Fact]
    public async Task GetAsync_WithValidThreadId_ReturnsThread()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedThread = new Thread
        {
            ThreadId = "thread_123",
            Title = "Test Thread",
            Status = ThreadStatus.Active,
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123",
            expectedThread
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.GetAsync("thread_123");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("thread_123", result.ThreadId);
        Assert.Equal(ThreadStatus.Active, result.Status);
    }

    [Fact]
    public async Task AddMessageAsync_WithUserMessage_ReturnsCreatedMessage()
    {
        // Arrange - Example from "Add Messages to a Thread" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedMessage = new ChatMessage
        {
            MessageId = "msg_001",
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "I need help with my order" }
            },
            UserId = "user_001",
            ThreadId = "thread_123",
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/messages",
            expectedMessage,
            HttpStatusCode.Created
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var message = new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "I need help with my order" }
            },
            UserId = "user_001"
        };

        // Act
        var result = await client.Threads.AddMessageAsync("thread_123", message);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("msg_001", result.MessageId);
        Assert.Equal("user", result.Role);
        Assert.Equal("user_001", result.UserId);
        Assert.Single(result.Contents);
    }

    [Fact]
    public async Task GetMessagesAsync_WithThreadId_ReturnsMessages()
    {
        // Arrange - Example from "Get Thread Messages" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedMessages = new List<ChatMessage>
        {
            new ChatMessage
            {
                MessageId = "msg_001",
                Role = "user",
                Contents = new List<Content>
                {
                    new TextContent { Text = "Hello" }
                },
                CreatedAt = DateTime.UtcNow.AddMinutes(-5)
            },
            new ChatMessage
            {
                MessageId = "msg_002",
                Role = "assistant",
                Contents = new List<Content>
                {
                    new TextContent { Text = "Hi! How can I help?" }
                },
                CreatedAt = DateTime.UtcNow
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/messages?limit=100",
            expectedMessages
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.GetMessagesAsync("thread_123", limit: 100);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(2, result.Count);
        Assert.Equal("msg_001", result[0].MessageId);
        Assert.Equal("msg_002", result[1].MessageId);
    }

    [Fact]
    public async Task GetMessageAsync_WithMessageId_ReturnsSpecificMessage()
    {
        // Arrange - Example from "Get Thread Messages - specific message" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedMessage = new ChatMessage
        {
            MessageId = "msg_456",
            Role = "assistant",
            Contents = new List<Content>
            {
                new TextContent { Text = "Specific message content" }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/messages/msg_456",
            expectedMessage
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.GetMessageAsync("thread_123", "msg_456");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("msg_456", result.MessageId);
        Assert.Equal("assistant", result.Role);
    }

    [Fact]
    public async Task CreateRunAsync_InThreadContext_ReturnsCreatedRun()
    {
        // Arrange - Example from "Create a Run within a Thread" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_001",
            AgentId = "agent_support",
            ThreadId = "thread_123",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What's my order status?" }
                    }
                }
            },
            Output = new List<ChatMessage>(),
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/runs",
            expectedRun,
            HttpStatusCode.Created
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var run = new Run
        {
            AgentId = "agent_support",
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What's my order status?" }
                    }
                }
            }
        };

        // Act
        var result = await client.Threads.CreateRunAsync("thread_123", run);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("run_001", result.RunId);
        Assert.Equal("thread_123", result.ThreadId);
        Assert.Equal("agent_support", result.AgentId);
    }

    [Fact]
    public async Task ListAsync_WithStatusFilter_ReturnsActiveThreads()
    {
        // Arrange - Example from "List Threads - get active threads" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedThreads = new List<Thread>
        {
            new Thread
            {
                ThreadId = "thread_001",
                Title = "Active Thread 1",
                Status = ThreadStatus.Active,
                CreatedAt = DateTime.UtcNow.AddDays(-1)
            },
            new Thread
            {
                ThreadId = "thread_002",
                Title = "Active Thread 2",
                Status = ThreadStatus.Active,
                CreatedAt = DateTime.UtcNow
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/threads?status=Active&limit=50",
            expectedThreads
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.ListAsync(status: ThreadStatus.Active, limit: 50);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(2, result.Count);
        Assert.All(result, t => Assert.Equal(ThreadStatus.Active, t.Status));
    }

    [Fact]
    public async Task ListAsync_WithUpdatedSinceFilter_ReturnsRecentThreads()
    {
        // Arrange - Example from "List Threads - get recently updated" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var sevenDaysAgo = DateTime.UtcNow.AddDays(-7);
        var expectedThreads = new List<Thread>
        {
            new Thread
            {
                ThreadId = "thread_003",
                Title = "Recent Thread",
                Status = ThreadStatus.Active,
                UpdatedAt = DateTime.UtcNow.AddDays(-2),
                CreatedAt = DateTime.UtcNow.AddDays(-10)
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            $"https://api.example.com/threads?updatedSince={sevenDaysAgo:O}&limit=100",
            expectedThreads
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.ListAsync(updatedSince: sevenDaysAgo);

        // Assert
        Assert.NotNull(result);
        Assert.Single(result);
        Assert.True(result[0].UpdatedAt >= sevenDaysAgo);
    }

    [Fact]
    public async Task UpdateAsync_ArchiveThread_ReturnsUpdatedThread()
    {
        // Arrange - Example from "Update Thread Status - Archive" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedThread = new Thread
        {
            ThreadId = "thread_123",
            Title = "Archived Thread",
            Status = ThreadStatus.Archived,
            UpdatedAt = DateTime.UtcNow,
            CreatedAt = DateTime.UtcNow.AddDays(-30)
        };

        MockHttpClientFactory.SetupPatchResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123",
            expectedThread
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var thread = new Thread
        {
            ThreadId = "thread_123",
            Status = ThreadStatus.Archived
        };

        // Act
        var result = await client.Threads.UpdateAsync("thread_123", thread);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(ThreadStatus.Archived, result.Status);
    }

    [Fact]
    public async Task MarkAsReadAsync_WithThreadId_ResetsUnreadCount()
    {
        // Arrange - Example from "Update Thread Status - Mark as read" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedThread = new Thread
        {
            ThreadId = "thread_123",
            Title = "Test Thread",
            UnreadCount = 0,
            Status = ThreadStatus.Active,
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/read",
            expectedThread,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.MarkAsReadAsync("thread_123");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(0, result.UnreadCount);
    }

    [Fact]
    public async Task CopyAsync_WithOptions_CreatesIndependentCopy()
    {
        // Arrange - Example from "Copy a Thread" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedThread = new Thread
        {
            ThreadId = "thread_456",
            Title = "Copied Thread",
            Status = ThreadStatus.Active,
            Participants = new List<Participant>
            {
                new Participant { Id = "user_001", Kind = "user", Name = "John Doe" }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/copy",
            expectedThread,
            HttpStatusCode.Created
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var copyRequest = new ThreadCopyRequest
        {
            Title = "Copied Thread",
            IncludeMessages = true,
            IncludeParticipants = true
        };

        // Act
        var result = await client.Threads.CopyAsync("thread_123", copyRequest);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("thread_456", result.ThreadId);
        Assert.Equal("Copied Thread", result.Title);
        Assert.NotEmpty(result.Participants);
    }

    [Fact]
    public async Task WatchThreadAsync_WithAgentId_CreatesWatch()
    {
        // Arrange - Example from "Watch Threads (Agent Subscriptions)" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedWatch = new ThreadWatch
        {
            WatchId = "watch_001",
            ThreadId = "thread_123",
            AgentId = "agent_monitor",
            Active = true,
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/watch",
            expectedWatch,
            HttpStatusCode.Created
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.WatchThreadAsync("thread_123", "agent_monitor");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("watch_001", result.WatchId);
        Assert.Equal("thread_123", result.ThreadId);
        Assert.Equal("agent_monitor", result.AgentId);
        Assert.True(result.Active);
    }

    [Fact]
    public async Task ListWatchersAsync_WithThreadId_ReturnsAllWatchers()
    {
        // Arrange - Example from "Watch Threads - list all watchers" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedWatchers = new List<ThreadWatch>
        {
            new ThreadWatch
            {
                WatchId = "watch_001",
                ThreadId = "thread_123",
                AgentId = "agent_monitor",
                Active = true,
                CreatedAt = DateTime.UtcNow.AddHours(-1)
            },
            new ThreadWatch
            {
                WatchId = "watch_002",
                ThreadId = "thread_123",
                AgentId = "agent_support",
                Active = true,
                CreatedAt = DateTime.UtcNow
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/watch",
            expectedWatchers
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.ListWatchersAsync("thread_123");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(2, result.Count);
        Assert.All(result, w => Assert.Equal("thread_123", w.ThreadId));
    }

    [Fact]
    public async Task UnwatchThreadAsync_WithAgentId_RemovesWatch()
    {
        // Arrange - Example from "Watch Threads - unsubscribe agent" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        MockHttpClientFactory.SetupDeleteResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/watch/agent_monitor"
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act & Assert (should not throw)
        await client.Threads.UnwatchThreadAsync("thread_123", "agent_monitor");
    }

    [Fact]
    public async Task DeleteAsync_WithThreadId_DeletesThread()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        MockHttpClientFactory.SetupDeleteResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123"
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act & Assert (should not throw)
        await client.Threads.DeleteAsync("thread_123");
    }

    [Fact]
    public async Task ListRunsAsync_WithThreadContext_ReturnsThreadRuns()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRuns = new List<Run>
        {
            new Run
            {
                RunId = "run_001",
                AgentId = "agent_001",
                ThreadId = "thread_123",
                Status = RunStatus.Completed,
                Input = new List<ChatMessage>(),
                Output = new List<ChatMessage>(),
                CreatedAt = DateTime.UtcNow.AddHours(-2)
            },
            new Run
            {
                RunId = "run_002",
                AgentId = "agent_001",
                ThreadId = "thread_123",
                Status = RunStatus.Completed,
                Input = new List<ChatMessage>(),
                Output = new List<ChatMessage>(),
                CreatedAt = DateTime.UtcNow
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/threads/thread_123/runs?limit=100",
            expectedRuns
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Threads.ListRunsAsync("thread_123");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(2, result.Count);
        Assert.All(result, r => Assert.Equal("thread_123", r.ThreadId));
    }
}
