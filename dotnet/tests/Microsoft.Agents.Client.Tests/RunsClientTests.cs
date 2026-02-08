using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol;
using Microsoft.Agents.Protocol.Models.Execution;
using Microsoft.Agents.Protocol.Models.Messages;
using Microsoft.Agents.Client.Tests.TestHelpers;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Tests for RunsClient covering all documentation examples
/// </summary>
public class RunsClientTests
{
    [Fact]
    public async Task CreateAsync_WithBasicRun_ReturnsCreatedRun()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_001",
            AgentId = "agent_001",
            ThreadId = "thread_123",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What's 2+2?" }
                    }
                }
            },
            Output = new List<ChatMessage>(),
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs",
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
            AgentId = "agent_001",
            ThreadId = "thread_123",
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What's 2+2?" }
                    }
                }
            }
        };

        // Act
        var result = await client.Runs.CreateAsync(run);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("run_001", result.RunId);
        Assert.Equal("agent_001", result.AgentId);
        Assert.Equal(RunStatus.InProgress, result.Status);
    }

    [Fact]
    public async Task CreateAndWaitAsync_WithEphemeralRun_ReturnsCompletedRun()
    {
        // Arrange - Example from "Create and Wait for Completion" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedResponse = new RunWaitResponse
        {
            RunId = "run_002",
            Status = RunStatus.Completed,
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "assistant",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Hola" }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow,
            CompletedAt = DateTime.UtcNow.AddSeconds(2)
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs/wait",
            expectedResponse,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var run = new Run
        {
            AgentId = "agent_001",
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Translate 'hello' to Spanish" }
                    }
                }
            },
            ThreadCleanup = ThreadCleanup.Delete
        };

        // Act
        var result = await client.Runs.CreateAndWaitAsync(run);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.Completed, result.Status);
        Assert.Single(result.Output);

        var textContent = result.Output[0].Contents[0] as TextContent;
        Assert.NotNull(textContent);
        Assert.Equal("Hola", textContent.Text);
    }

    [Fact]
    public async Task GetAsync_WithValidRunId_ReturnsRun()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_123",
            AgentId = "agent_001",
            Status = RunStatus.Completed,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>(),
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/runs/run_123",
            expectedRun
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.GetAsync("run_123");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("run_123", result.RunId);
        Assert.Equal(RunStatus.Completed, result.Status);
    }

    [Fact]
    public async Task ListAsync_WithFilters_ReturnsFilteredRuns()
    {
        // Arrange - Example from "List Runs with Filtering" section
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
                CreatedAt = DateTime.UtcNow
            },
            new Run
            {
                RunId = "run_002",
                AgentId = "agent_001",
                ThreadId = "thread_123",
                Status = RunStatus.Completed,
                Input = new List<ChatMessage>(),
                Output = new List<ChatMessage>(),
                CreatedAt = DateTime.UtcNow.AddHours(-1)
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/runs?threadId=thread_123&limit=50",
            expectedRuns
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.ListAsync(threadId: "thread_123", limit: 50);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(2, result.Count);
        Assert.All(result, r => Assert.Equal("thread_123", r.ThreadId));
    }

    [Fact]
    public async Task ListAsync_WithStatusFilter_ReturnsCompletedRuns()
    {
        // Arrange - Example from "Filter by status" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRuns = new List<Run>
        {
            new Run
            {
                RunId = "run_003",
                AgentId = "agent_001",
                Status = RunStatus.Completed,
                Input = new List<ChatMessage>(),
                Output = new List<ChatMessage>(),
                CreatedAt = DateTime.UtcNow
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/runs?status=Completed&limit=100",
            expectedRuns
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.ListAsync(status: RunStatus.Completed, limit: 100);

        // Assert
        Assert.NotNull(result);
        Assert.All(result, r => Assert.Equal(RunStatus.Completed, r.Status));
    }

    [Fact]
    public async Task CancelAsync_WithInterruptAction_StopsRunAndPreservesState()
    {
        // Arrange - Example from "Cancel a Running Execution - Interrupt" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_456",
            AgentId = "agent_001",
            Status = RunStatus.Cancelled,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "assistant",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Partial response..." }
                    }
                }
            },
            CancelledAt = DateTime.UtcNow,
            CancellationReason = "User stopped generation",
            CreatedAt = DateTime.UtcNow.AddMinutes(-1)
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs/run_456/cancel",
            expectedRun,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.CancelAsync("run_456", CancelAction.Interrupt, "User stopped generation");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.Cancelled, result.Status);
        Assert.Equal("User stopped generation", result.CancellationReason);
        Assert.NotNull(result.Output);
        Assert.NotEmpty(result.Output);
    }

    [Fact]
    public async Task CancelAsync_WithRollbackAction_StopsRunAndCleansUp()
    {
        // Arrange - Example from "Cancel a Running Execution - Rollback" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_456",
            AgentId = "agent_001",
            Status = RunStatus.Cancelled,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>(),
            CancelledAt = DateTime.UtcNow,
            CancellationReason = "Failed run cleanup",
            CreatedAt = DateTime.UtcNow.AddMinutes(-1)
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs/run_456/cancel",
            expectedRun,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.CancelAsync("run_456", CancelAction.Rollback, "Failed run cleanup");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.Cancelled, result.Status);
        Assert.Equal("Failed run cleanup", result.CancellationReason);
        Assert.Empty(result.Output); // Rollback cleans up output
    }

    [Fact]
    public async Task SubmitToolOutputsAsync_WithRequiresActionStatus_ContinuesRun()
    {
        // Arrange - Example from "Handle Tool Calls (HITL)" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_789",
            AgentId = "agent_001",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "tool",
                    Contents = new List<Content>
                    {
                        new FunctionResultContent
                        {
                            CallId = "call_abc123",
                            Name = "delete_file",
                            Result = "File deleted successfully"
                        }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs/run_789/submit_tool_outputs",
            expectedRun,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        var toolOutputs = new List<ToolOutput>
        {
            new ToolOutput
            {
                ToolCallId = "call_abc123",
                Output = "File deleted successfully"
            }
        };

        // Act
        var result = await client.Runs.SubmitToolOutputsAsync("run_789", toolOutputs);

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.InProgress, result.Status);
        Assert.NotEmpty(result.Output);
    }

    [Fact]
    public async Task SubmitInputAsync_WithInputRequiredStatus_ContinuesRun()
    {
        // Arrange - Example from "Handle User Input Requests" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_789",
            AgentId = "agent_001",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Option 1" }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs/run_789/submit_input",
            expectedRun,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.SubmitInputAsync("run_789", "Option 1");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.InProgress, result.Status);
    }

    [Fact]
    public async Task SubmitAuthAsync_WithAuthRequiredStatus_ContinuesRun()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_890",
            AgentId = "agent_001",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>(),
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/runs/run_890/submit_auth",
            expectedRun,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.SubmitAuthAsync("run_890", "eyJhbGc...", "Bearer");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.InProgress, result.Status);
    }

    [Fact]
    public async Task WaitAsync_WithExistingRun_WaitsForCompletion()
    {
        // Arrange
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedResponse = new RunWaitResponse
        {
            RunId = "run_999",
            ThreadId = "thread_123",
            Status = RunStatus.Completed,
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "assistant",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Task completed!" }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow.AddMinutes(-5),
            CompletedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/runs/run_999/wait",
            expectedResponse
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.WaitAsync("run_999");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("run_999", result.RunId);
        Assert.Equal(RunStatus.Completed, result.Status);
        Assert.NotNull(result.CompletedAt);
    }
}
