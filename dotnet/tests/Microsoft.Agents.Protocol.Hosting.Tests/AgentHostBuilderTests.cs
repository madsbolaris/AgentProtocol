using System;
using System.Linq;
using FluentAssertions;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Storage;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class AgentHostBuilderTests
{
    [Fact]
    public void Services_ReturnsServiceCollection()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act
        var result = builder.Services;

        // Assert
        result.Should().BeSameAs(services);
    }

    [Fact]
    public void AddDefaultAgent_ThrowsArgumentNullException_WhenConfigureIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act & Assert
        var act = () => builder.AddDefaultAgent(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("configure");
    }

    [Fact]
    public void AddDefaultAgent_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act
        var result = builder.AddDefaultAgent(b => b.UseLLM("gpt-4", "Test instructions"));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void AddAgent_ThrowsArgumentException_WhenNameIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act & Assert
        var act = () => builder.AddAgent(null!, b => { });
        act.Should().Throw<ArgumentException>().WithParameterName("name");
    }

    [Fact]
    public void AddAgent_ThrowsArgumentException_WhenNameIsEmpty()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act & Assert
        var act = () => builder.AddAgent("", b => { });
        act.Should().Throw<ArgumentException>().WithParameterName("name");
    }

    [Fact]
    public void AddAgent_ThrowsArgumentException_WhenNameIsWhitespace()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act & Assert
        var act = () => builder.AddAgent("   ", b => { });
        act.Should().Throw<ArgumentException>().WithParameterName("name");
    }

    [Fact]
    public void AddAgent_ThrowsArgumentNullException_WhenConfigureIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act & Assert
        var act = () => builder.AddAgent("test-agent", null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("configure");
    }

    [Fact]
    public void AddAgent_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act
        var result = builder.AddAgent("test-agent", b => b.UseLLM("gpt-4", "Test instructions"));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void UseProductionDefaults_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();
        var configuration = new ConfigurationBuilder().Build();

        // Act
        var result = builder.UseProductionDefaults(configuration);

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Build_ThrowsInvalidOperationException_WhenNoAgentsConfigured()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();

        // Act & Assert
        var act = () => builder.Build();
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("At least one agent must be configured.");
    }

    [Fact]
    public void Build_AddsInMemoryStorage_WhenNotAlreadyRegistered()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();
        builder.AddDefaultAgent(b => b.UseLLM("gpt-4", "Test instructions"));

        // Act
        builder.Build();

        // Assert
        services.Should().Contain(s => s.ServiceType == typeof(IStorage) && s.ImplementationType == typeof(InMemoryStorage));
    }

    [Fact]
    public void Build_DoesNotAddStorage_WhenAlreadyRegistered()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        services.AddSingleton<IStorage, InMemoryStorage>();
        var initialCount = services.Count(s => s.ServiceType == typeof(IStorage));
        var builder = services.AddAgentHost();
        builder.AddDefaultAgent(b => b.UseLLM("gpt-4", "Test instructions"));

        // Act
        builder.Build();

        // Assert
        var finalCount = services.Count(s => s.ServiceType == typeof(IStorage));
        finalCount.Should().Be(initialCount);
    }

    [Fact]
    public void Build_AddsOutOfBandPublisher_WhenNotAlreadyRegistered()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();
        builder.AddDefaultAgent(b => b.UseLLM("gpt-4", "Test instructions"));

        // Act
        builder.Build();

        // Assert
        services.Should().Contain(s => s.ServiceType == typeof(IOutOfBandPublisher));
    }

    [Fact]
    public void Build_ReturnsAgentHost()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();
        builder.AddDefaultAgent(b => b.UseLLM("gpt-4", "Test instructions"));

        // Act
        var host = builder.Build();

        // Assert
        host.Should().NotBeNull();
        host.Should().BeAssignableTo<IAgentHost>();
    }

    [Fact]
    public void Build_CanConfigureMultipleAgents()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var builder = services.AddAgentHost();
        builder.AddAgent("agent1", b => b.UseLLM("gpt-4", "Agent 1 instructions"));
        builder.AddAgent("agent2", b => b.UseLLM("claude-3", "Agent 2 instructions"));

        // Act
        var host = builder.Build();

        // Assert
        host.Should().NotBeNull();
    }
}
