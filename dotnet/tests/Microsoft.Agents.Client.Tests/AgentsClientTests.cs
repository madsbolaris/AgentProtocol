using System;
using System.Collections.Generic;
using System.Net;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol;
using Microsoft.Agents.Protocol.Models.Agents;
using Microsoft.Agents.Client.Tests.TestHelpers;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Tests for AgentsClient covering all documentation examples
/// </summary>
public class AgentsClientTests
{
    [Fact]
    public async Task GetCardAsync_WithAgentId_ReturnsAgentCard()
    {
        // Arrange - Example from "Get Agent Card" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var expectedCard = new AgentCard
        {
            AgentId = "agent_001",
            Name = "Support Agent",
            Description = "A helpful customer support agent",
            Capabilities = new AgentCapabilities
            {
                Vision = true,
                Thinking = false,
                Tools = true,
                MaxTokens = 128000,
                ContentTypes = new List<string> { "text", "image" }
            },
            Tools = new List<AITool>
            {
                new AITool
                {
                    Name = "search_orders",
                    Description = "Search customer orders",
                    Parameters = new JSONSchema
                    {
                        SchemaType = "object",
                        Properties = new Dictionary<string, JSONSchema>
                        {
                            ["customerId"] = new JSONSchema
                            {
                                SchemaType = "string",
                                Description = "Customer ID"
                            }
                        },
                        Required = new List<string> { "customerId" }
                    }
                }
            }
        };

        MockHttpClientFactory.SetupGetResponse(
            mockHandler,
            "https://api.example.com/agents/agent_001/card",
            expectedCard
        );

        var options = new AgentProtocolClientOptions
        {
            BaseUrl = new Uri("https://api.example.com"),
            HttpClient = httpClient
        };

        var client = new AgentProtocolClient(options);

        // Act
        var result = await client.Agents.GetCardAsync("agent_001");

        // Assert
        Assert.NotNull(result);
        Assert.Equal("agent_001", result.AgentId);
        Assert.Equal("Support Agent", result.Name);
        Assert.NotNull(result.Capabilities);
        Assert.True(result.Capabilities.Vision);
        Assert.Equal(128000, result.Capabilities.MaxTokens);
        Assert.NotEmpty(result.Tools);
        Assert.Equal("search_orders", result.Tools[0].Name);
    }

    [Fact]
    public async Task InspectAsync_WithAgentDefinition_ReturnsCapabilities()
    {
        // Arrange - Example from "Inspect Agent Before Running" section
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var agent = new PromptAgent
        {
            Model = "gpt-4o",
            Instructions = "You are a helpful assistant",
            Temperature = 0.7,
            Tools = new List<AITool>
            {
                new AITool
                {
                    Name = "get_weather",
                    Description = "Get current weather for a location",
                    Parameters = new JSONSchema
                    {
                        SchemaType = "object",
                        Properties = new Dictionary<string, JSONSchema>
                        {
                            ["location"] = new JSONSchema
                            {
                                SchemaType = "string",
                                Description = "City name"
                            }
                        },
                        Required = new List<string> { "location" }
                    }
                }
            }
        };

        var expectedCard = new AgentCard
        {
            AgentId = null, // Ephemeral inspection - not persisted
            Name = "Ephemeral Agent",
            Capabilities = new AgentCapabilities
            {
                Vision = true,
                Thinking = false,
                Tools = true,
                MaxTokens = 128000
            },
            Tools = agent.Tools
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/agents/inspect",
            expectedCard,
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
        Assert.Null(result.AgentId); // Ephemeral - not persisted
        Assert.NotNull(result.Capabilities);
        Assert.True(result.Capabilities.Vision);
        Assert.True(result.Capabilities.Tools);
        Assert.Equal(128000, result.Capabilities.MaxTokens);
    }

    [Fact]
    public async Task InspectAsync_WithModelCapabilities_ReturnsModelInfo()
    {
        // Arrange - Validate model capabilities before running
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

        var agent = new PromptAgent
        {
            Model = "claude-3-sonnet",
            Instructions = "You are a research analyst"
        };

        var expectedCard = new AgentCard
        {
            Name = "Claude 3 Sonnet",
            Capabilities = new AgentCapabilities
            {
                Vision = true,
                Thinking = true, // Extended thinking support
                Tools = true,
                MaxTokens = 200000,
                ContentTypes = new List<string> { "text", "image" }
            }
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/agents/inspect",
            expectedCard,
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
        Assert.NotNull(result.Capabilities);
        Assert.True(result.Capabilities.Thinking); // Extended thinking capability
        Assert.Equal(200000, result.Capabilities.MaxTokens);
    }

    [Fact]
    public async Task InspectAsync_WithToolDefinitions_ValidatesToolSupport()
    {
        // Arrange - Validate tool configuration
        var mockHandler = MockHttpClientFactory.CreateMockHandler();
        var httpClient = MockHttpClientFactory.CreateMockHttpClient(mockHandler);

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

        var expectedCard = new AgentCard
        {
            Name = "File Manager Agent",
            Capabilities = new AgentCapabilities
            {
                Tools = true,
                MaxTokens = 128000
            },
            Tools = agent.Tools
        };

        MockHttpClientFactory.SetupPostResponse(
            mockHandler,
            "https://api.example.com/agents/inspect",
            expectedCard,
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
        Assert.True(result.Capabilities?.Tools);
        Assert.NotEmpty(result.Tools);
        Assert.Equal("delete_file", result.Tools[0].Name);
        Assert.True(result.Tools[0].RequiresApproval);
    }
}
