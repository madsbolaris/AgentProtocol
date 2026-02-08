using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol;
using Microsoft.Agents.Protocol.Models.Agents;
using Microsoft.Agents.Protocol.Models.Execution;
using Microsoft.Agents.Protocol.Models.Messages;
using Microsoft.Agents.Client.Tests.TestHelpers;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Tests for advanced scenarios and complex examples from documentation
/// </summary>
public class AdvancedScenariosTests
{
    [Fact]
    public async Task InlineAgentDefinition_WithEphemeralExecution_ReturnsResult()
    {
        // Arrange - Example from "Using Inline Agent Definitions" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedResponse = new RunWaitResponse
        {
            RunId = "run_ephemeral_001",
            Status = RunStatus.Completed,
            Output = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "assistant",
                    Contents = new List<Content>
                    {
                        new TextContent
                        {
                            Text = "Calculus is the mathematical study of continuous change..."
                        }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow,
            CompletedAt = DateTime.UtcNow.AddSeconds(5)
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
            AgentId = "ephemeral",
            Agent = new PromptAgent
            {
                Model = "gpt-4o",
                Instructions = "You are a math tutor",
                Temperature = 0.3
            },
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Explain calculus" }
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
        Assert.NotEmpty(result.Output);
    }

    [Fact]
    public async Task WorkingWithImages_VisionModel_ProcessesImageContent()
    {
        // Arrange - Example from "Working with Images" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedRun = new Run
        {
            RunId = "run_vision_001",
            AgentId = "agent_vision",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What's in this image?" },
                        new ImageContent
                        {
                            Url = "https://example.com/image.jpg",
                            Detail = "high"
                        }
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

        var message = new ChatMessage
        {
            Role = "user",
            Contents = new List<Content>
            {
                new TextContent { Text = "What's in this image?" },
                new ImageContent
                {
                    Url = "https://example.com/image.jpg",
                    Detail = "high"
                }
            }
        };

        var run = new Run
        {
            AgentId = "agent_vision",
            Input = new List<ChatMessage> { message }
        };

        // Act
        var result = await client.Runs.CreateAsync(run);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("agent_vision", result.AgentId);
        Assert.Equal(2, result.Input[0].Contents.Count);
        Assert.IsType<TextContent>(result.Input[0].Contents[0]);
        Assert.IsType<ImageContent>(result.Input[0].Contents[1]);
    }

    [Fact]
    public async Task ToolExecutionWithApproval_RequiresHumanInTheLoop()
    {
        // Arrange - Example from "Tool Execution with Approval" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        // First, inspect the agent to see tool configuration
        var agent = new PromptAgent
        {
            Model = "gpt-4o",
            Instructions = "You help manage files",
            Tools = new List<AITool>
            {
                new AITool
                {
                    Name = "delete_file",
                    Description = "Delete a file from the system",
                    RequiresApproval = true,
                    Parameters = new JSONSchema
                    {
                        SchemaType = "object",
                        Properties = new Dictionary<string, JSONSchema>
                        {
                            ["path"] = new JSONSchema
                            {
                                SchemaType = "string",
                                Description = "File path to delete"
                            }
                        },
                        Required = new List<string> { "path" }
                    }
                }
            }
        };

        var agentCard = new AgentCard
        {
            Name = "File Manager",
            Capabilities = new AgentCapabilities { Tools = true },
            Tools = agent.Tools
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/agents/inspect",
            agentCard,
            HttpStatusCode.OK
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Agents.InspectAsync(agent);

        // Assert
        Assert.NotNull(result);
        Assert.NotEmpty(result.Tools);
        Assert.True(result.Tools[0].RequiresApproval);
        Assert.Equal("delete_file", result.Tools[0].Name);
    }

    [Fact]
    public async Task CustomHttpClientConfiguration_UsesProvidedClient()
    {
        // Arrange - Example from "Custom HTTP Client Configuration" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var customHttpClient = new System.Net.Http.HttpClient(mockHandler)
        {
            Timeout = TimeSpan.FromMinutes(5),
            BaseAddress = new Uri("https://api.example.com")
        };

        var expectedRun = new Run
        {
            RunId = "run_custom_001",
            AgentId = "agent_001",
            Status = RunStatus.InProgress,
            Input = new List<ChatMessage>(),
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
            ApiKey = "test-key",
            HttpClient = customHttpClient,
            MaxRetries = 5
        };

        // Act
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
                        new TextContent { Text = "Test message" }
                    }
                }
            }
        };

        var result = await client.Runs.CreateAsync(run);

        // Assert
        Assert.NotNull(result);
        Assert.Equal("run_custom_001", result.RunId);
    }

    [Fact]
    public async Task ErrorHandling_FailedRun_ContainsErrorDetails()
    {
        // Arrange - Example from "Error Handling" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var failedRun = new Run
        {
            RunId = "run_failed_001",
            AgentId = "agent_001",
            Status = RunStatus.Failed,
            Input = new List<ChatMessage>(),
            Output = new List<ChatMessage>(),
            Error = new RunError
            {
                Code = "context_length_exceeded",
                Message = "The conversation exceeded the maximum token limit of 128000 tokens",
                Details = new Dictionary<string, object>
                {
                    ["maxTokens"] = 128000,
                    ["actualTokens"] = 150000
                }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/runs/run_failed_001",
            failedRun
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Runs.GetAsync("run_failed_001");

        // Assert
        Assert.NotNull(result);
        Assert.Equal(RunStatus.Failed, result.Status);
        Assert.NotNull(result.Error);
        Assert.Equal("context_length_exceeded", result.Error.Code);
        Assert.Contains("maximum token limit", result.Error.Message);
        Assert.NotNull(result.Error.Details);
    }

    [Fact]
    public async Task MultiTurnConversation_WithThreadContext_MaintainsState()
    {
        // Arrange - Multi-turn conversation pattern
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        // Turn 1: Create thread
        var expectedThread = new Microsoft.Agents.Protocol.Models.Threads.Thread
        {
            ThreadId = "thread_multi_001",
            Title = "Math Help",
            Status = Microsoft.Agents.Protocol.Models.Threads.ThreadStatus.Active,
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads",
            expectedThread,
            HttpStatusCode.Created
        );

        // Turn 2: First run
        var firstRun = new Run
        {
            RunId = "run_turn_001",
            AgentId = "agent_math",
            ThreadId = "thread_multi_001",
            Status = RunStatus.Completed,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What is 5 + 3?" }
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
                        new TextContent { Text = "5 + 3 equals 8" }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_multi_001/runs",
            firstRun,
            HttpStatusCode.Created
        );

        // Turn 3: Second run (references previous context)
        var secondRun = new Run
        {
            RunId = "run_turn_002",
            AgentId = "agent_math",
            ThreadId = "thread_multi_001",
            Status = RunStatus.Completed,
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Now multiply that by 2" }
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
                        new TextContent { Text = "8 multiplied by 2 equals 16" }
                    }
                }
            },
            CreatedAt = DateTime.UtcNow
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/threads/thread_multi_001/runs",
            secondRun,
            HttpStatusCode.Created
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act - Simulate multi-turn conversation
        // Turn 1: Create thread
        var thread = await client.Threads.CreateAsync(new Microsoft.Agents.Protocol.Models.Threads.Thread
        {
            Title = "Math Help"
        });

        // Turn 2: First question
        var turn1 = await client.Threads.CreateRunAsync(thread.ThreadId!, new Run
        {
            AgentId = "agent_math",
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "What is 5 + 3?" }
                    }
                }
            }
        });

        // Turn 3: Follow-up question (references previous answer)
        var turn2 = await client.Threads.CreateRunAsync(thread.ThreadId!, new Run
        {
            AgentId = "agent_math",
            Input = new List<ChatMessage>
            {
                new ChatMessage
                {
                    Role = "user",
                    Contents = new List<Content>
                    {
                        new TextContent { Text = "Now multiply that by 2" }
                    }
                }
            }
        });

        // Assert
        Assert.NotNull(thread);
        Assert.Equal("thread_multi_001", thread.ThreadId);

        Assert.NotNull(turn1);
        Assert.Equal("thread_multi_001", turn1.ThreadId);
        Assert.Equal(RunStatus.Completed, turn1.Status);
        Assert.NotNull(turn1.Output);

        Assert.NotNull(turn2);
        Assert.Equal("thread_multi_001", turn2.ThreadId);
        Assert.Equal(RunStatus.Completed, turn2.Status);
        Assert.NotNull(turn2.Output);
        // Verify multi-turn conversation maintains thread context
        Assert.Equal(turn1.ThreadId, turn2.ThreadId);
    }

    [Fact]
    public void ClientInitialization_WithMultipleConstructors_CreatesClient()
    {
        // Arrange & Act - Example from Quick Start and constructor variations

        // Constructor 1: Just URL
        var client1 = new AgentProtocolClient("https://api.example.com");
        Assert.NotNull(client1);
        Assert.NotNull(client1.Runs);
        Assert.NotNull(client1.Threads);
        Assert.NotNull(client1.Agents);

        // Constructor 2: URL and API key
        var client2 = new AgentProtocolClient("https://api.example.com", "test-api-key");
        Assert.NotNull(client2);

        // Constructor 3: Full options
        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            ApiKey = "test-api-key",
            TimeoutSeconds = 60,
            MaxRetries = 5
        };
        var client3 = new AgentProtocolClient(options);
        Assert.NotNull(client3);

        // Cleanup
        client1.Dispose();
        client2.Dispose();
        client3.Dispose();
    }
}
