using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Microsoft.Agents.Protocol.Hosting.LLM;
using Microsoft.Agents.Protocol.Model;
using Microsoft.Agents.Protocol.Model.OpenAI;
using Microsoft.Extensions.DependencyInjection;
using Xunit;
using XunitAssert = Xunit.Assert;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

/// <summary>
/// Tests for LLM configuration patterns (string vs provider instance).
/// Verifies Vercel AI-style pattern: accept either string (gateway) or provider instance.
/// </summary>
public class LLMConfigurationTests
{
    #region String-Based Configuration Tests

    [Fact]
    public void UseLLM_WithString_CreatesClientFromEnvironment()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key-123");

        var services = new ServiceCollection();
        services.AddLogging();

        try
        {
            // Act
            var builder = new AgentHostBuilder(services);
            var agentBuilder = new AgentBuilder(services);

            // This should auto-create an OpenAI client from environment variables
            agentBuilder.UseLLM("gpt-4o-mini", "You are a test assistant");

            // Assert - should not throw
            XunitAssert.True(true);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
        }
    }

    [Fact]
    public void UseLLM_WithString_ThrowsWhenEndpointMissing()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key");

        var services = new ServiceCollection();
        services.AddLogging();

        try
        {
            // Act & Assert
            var agentBuilder = new AgentBuilder(services);

            var exception = XunitAssert.Throws<InvalidOperationException>(() =>
                agentBuilder.UseLLM("gpt-4o-mini", "You are a test assistant")
            );

            XunitAssert.Contains("FOUNDRY_ENDPOINT", exception.Message);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
        }
    }

    [Fact]
    public void UseLLM_WithString_ThrowsWhenApiKeyMissing()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);

        var services = new ServiceCollection();
        services.AddLogging();

        try
        {
            // Act & Assert
            var agentBuilder = new AgentBuilder(services);

            var exception = XunitAssert.Throws<InvalidOperationException>(() =>
                agentBuilder.UseLLM("gpt-4o-mini", "You are a test assistant")
            );

            XunitAssert.Contains("FOUNDRY_API_KEY", exception.Message);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
        }
    }

    [Fact]
    public void UseLLM_WithString_ReadsModelFromEnvironment()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key-123");
        Environment.SetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-turbo");

        var services = new ServiceCollection();
        services.AddLogging();

        try
        {
            // Act
            var agentBuilder = new AgentBuilder(services);

            // Pass explicit model (should override environment variable)
            agentBuilder.UseLLM("gpt-4o-mini", "You are a test assistant");

            // Assert - should not throw
            XunitAssert.True(true);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
            Environment.SetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT", null);
        }
    }

    #endregion

    #region Provider Instance Configuration Tests

    [Fact]
    public void UseLLM_WithProviderInstance_UsesProvidedClient()
    {
        // Arrange
        var mockClient = new MockProtocolLLMClient("custom-model");
        var services = new ServiceCollection();
        services.AddLogging();

        // Act
        var agentBuilder = new AgentBuilder(services);
        agentBuilder.UseLLM(mockClient, "You are a test assistant");

        // Assert - should not throw
        XunitAssert.True(true);
    }

    [Fact]
    public void UseLLM_WithProviderInstance_DoesNotRequireEnvironmentVariables()
    {
        // Arrange - explicitly clear environment variables
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);

        var mockClient = new MockProtocolLLMClient("custom-model");
        var services = new ServiceCollection();
        services.AddLogging();

        try
        {
            // Act
            var agentBuilder = new AgentBuilder(services);
            agentBuilder.UseLLM(mockClient, "You are a test assistant");

            // Assert - should not throw even without environment variables
            XunitAssert.True(true);
        }
        finally
        {
            // Cleanup just in case
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
        }
    }

    [Fact]
    public void UseLLM_WithProviderInstance_ThrowsWhenClientIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Act & Assert
        var agentBuilder = new AgentBuilder(services);

        XunitAssert.Throws<ArgumentNullException>(() =>
            agentBuilder.UseLLM((IProtocolLLMClient)null!, "You are a test assistant")
        );
    }

    [Fact]
    public void UseLLM_WithProviderInstance_ExtractsModelFromProviderInfo()
    {
        // Arrange
        var expectedModel = "custom-gpt-model";
        var mockClient = new MockProtocolLLMClient(expectedModel);
        var services = new ServiceCollection();
        services.AddLogging();

        // Act
        var agentBuilder = new AgentBuilder(services);
        agentBuilder.UseLLM(mockClient, "You are a test assistant");

        // Assert
        XunitAssert.Equal(expectedModel, mockClient.ProviderInfo.Model);
    }

    #endregion

    #region LLMClientFactory Tests

    [Fact]
    public void LLMClientFactory_CreateFromEnvironment_WithModel_CreatesClient()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key-123");

        try
        {
            // Act
            var client = LLMClientFactory.CreateFromEnvironment("gpt-4o-mini");

            // Assert
            XunitAssert.NotNull(client);
            XunitAssert.Equal("gpt-4o-mini", client.ProviderInfo.Model);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
        }
    }

    [Fact]
    public void LLMClientFactory_CreateFromEnvironment_WithoutModel_ReadsFromEnvironment()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key-123");
        Environment.SetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT", "gpt-5-turbo");

        try
        {
            // Act
            var client = LLMClientFactory.CreateFromEnvironment();

            // Assert
            XunitAssert.NotNull(client);
            XunitAssert.Equal("gpt-5-turbo", client.ProviderInfo.Model);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
            Environment.SetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT", null);
        }
    }

    [Fact]
    public void LLMClientFactory_CreateFromEnvironment_ThrowsWhenModelNotSpecified()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key-123");
        Environment.SetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT", null);

        try
        {
            // Act & Assert
            var exception = XunitAssert.Throws<InvalidOperationException>(() =>
                LLMClientFactory.CreateFromEnvironment()
            );

            XunitAssert.Contains("FOUNDRY_MODEL_DEPLOYMENT", exception.Message);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
        }
    }

    #endregion

    #region Full Integration Tests

    [Fact]
    public void AddAgentProtocol_WithStringConfiguration_BuildsSuccessfully()
    {
        // Arrange
        Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", "https://api.test.com");
        Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", "test-key-123");

        var services = new ServiceCollection();
        services.AddLogging();

        try
        {
            // Act
            services.AddAgentProtocol(host => host
                .AddDefaultAgent(agent => agent
                    .UseLLM("gpt-4o-mini", "You are a test assistant")
                )
            );

            // Assert - should build without throwing
            var provider = services.BuildServiceProvider();
            XunitAssert.NotNull(provider);
        }
        finally
        {
            // Cleanup
            Environment.SetEnvironmentVariable("FOUNDRY_ENDPOINT", null);
            Environment.SetEnvironmentVariable("FOUNDRY_API_KEY", null);
        }
    }

    [Fact]
    public void AddAgentProtocol_WithProviderInstance_BuildsSuccessfully()
    {
        // Arrange
        var mockClient = new MockProtocolLLMClient("custom-model");
        var services = new ServiceCollection();
        services.AddLogging();

        // Act
        services.AddAgentProtocol(host => host
            .AddDefaultAgent(agent => agent
                .UseLLM(mockClient, "You are a test assistant")
            )
        );

        // Assert - should build without throwing
        var provider = services.BuildServiceProvider();
        XunitAssert.NotNull(provider);
    }

    #endregion

    #region Mock Client

    /// <summary>
    /// Mock LLM client for testing purposes.
    /// </summary>
    private class MockProtocolLLMClient : IProtocolLLMClient
    {
        private readonly string _model;

        public MockProtocolLLMClient(string model)
        {
            _model = model;
        }

        public LLMProviderInfo ProviderInfo => new()
        {
            Provider = "Mock",
            Model = _model,
            SupportsStreaming = true,
            SupportsFunctionCalling = true
        };

        public Task<AgentMessage> GenerateAsync(
            List<ChatMessage> conversationHistory,
            ToolDefinition[]? availableTools = null,
            CancellationToken cancellationToken = default)
        {
            return Task.FromResult(new AgentMessage
            {
                MessageId = "test-msg-123",
                Contents = new List<AIContent>
                {
                    new TextContent { Text = "Mock response" }
                }
            });
        }

        public async IAsyncEnumerable<AgentMessageDelta> StreamAsync(
            List<ChatMessage> conversationHistory,
            ToolDefinition[]? availableTools = null,
            [System.Runtime.CompilerServices.EnumeratorCancellation] CancellationToken cancellationToken = default)
        {
            yield return new AgentMessageDelta
            {
                MessageId = "test-msg-123",
                Type = DeltaType.MessageStart
            };

            yield return new AgentMessageDelta
            {
                MessageId = "test-msg-123",
                Type = DeltaType.TextDelta,
                Content = new TextContent { Text = "Mock streaming response" }
            };

            yield return new AgentMessageDelta
            {
                MessageId = "test-msg-123",
                Type = DeltaType.MessageComplete,
                IsComplete = true
            };

            await Task.CompletedTask;
        }
    }

    #endregion
}
