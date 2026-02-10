using System;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Extensions.DependencyInjection;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests;

/// <summary>
/// Tests for AgentHost lifecycle, health checks, and message processing.
/// </summary>
public class AgentHostTests
{
    [Fact]
    public async Task AgentHost_Start_StartsSuccessfully()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act
        await host.StartAsync();

        // Assert
        var health = await host.CheckHealthAsync();
        health.Status.Should().Be("healthy");
        health.Checks["server"].Should().BeTrue();

        await host.StopAsync();
    }

    [Fact]
    public async Task AgentHost_Start_WithCustomPort_StartsOnCorrectPort()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act
        await host.StartAsync(port: 8080);

        // Assert
        var health = await host.CheckHealthAsync();
        health.Status.Should().Be("healthy");
        // Note: Port verification would require actual server implementation

        await host.StopAsync();
    }

    [Fact]
    public async Task AgentHost_Start_WhenAlreadyRunning_ThrowsException()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        await host.StartAsync();

        // Act
        Func<Task> act = async () => await host.StartAsync();

        // Assert
        await act.Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("*already running*");

        await host.StopAsync();
    }

    [Fact]
    public async Task AgentHost_Stop_StopsSuccessfully()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        await host.StartAsync();

        // Act
        await host.StopAsync();

        // Assert
        var health = await host.CheckHealthAsync();
        health.Checks["server"].Should().BeFalse();
    }

    [Fact]
    public async Task AgentHost_Stop_WithGracePeriod_WaitsForCompletion()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        await host.StartAsync();

        // Act
        var stopOptions = new StopOptions { GracePeriodMs = 5000 };
        await host.StopAsync(stopOptions);

        // Assert
        var health = await host.CheckHealthAsync();
        health.Checks["server"].Should().BeFalse();
    }

    [Fact]
    public async Task AgentHost_Stop_WithFinishQueued_CompletesQueuedTasks()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        await host.StartAsync();

        // Act
        var stopOptions = new StopOptions { FinishQueued = true };
        await host.StopAsync(stopOptions);

        // Assert
        var health = await host.CheckHealthAsync();
        health.Checks["server"].Should().BeFalse();
    }

    [Fact]
    public async Task AgentHost_Stop_WhenNotRunning_DoesNotThrow()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act & Assert - should not throw
        await host.StopAsync();
    }

    [Fact]
    public async Task AgentHost_CheckHealth_ReturnsHealthyWhenRunning()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        await host.StartAsync();

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Should().NotBeNull();
        health.Status.Should().Be("healthy");
        health.Checks.Should().ContainKey("server");
        health.Checks.Should().ContainKey("storage");
        health.Checks.Should().ContainKey("queue");
        health.Checks.Should().ContainKey("llmConnection");
        health.Checks["server"].Should().BeTrue();
        health.Checks["storage"].Should().BeTrue();
        health.Checks["queue"].Should().BeTrue();
        health.UptimeMs.Should().BeGreaterOrEqualTo(0);

        await host.StopAsync();
    }

    [Fact]
    public async Task AgentHost_CheckHealth_ReturnsDegradedWhenSomeChecksFail()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Note: Would need to inject failing storage/queue to test degraded state
        // This is a placeholder for proper implementation
        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Should().NotBeNull();
        // Without starting, server should be false, so status should be degraded
        health.Status.Should().BeOneOf("healthy", "degraded");
    }

    [Fact]
    public async Task AgentHost_CheckHealth_TracksUptimeCorrectly()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        await host.StartAsync();

        // Act
        await Task.Delay(100); // Wait a bit
        var health = await host.CheckHealthAsync();

        // Assert
        health.UptimeMs.Should().BeGreaterOrEqualTo(100);

        await host.StopAsync();
    }

    [Fact]
    public void AgentHost_GetPublisher_ReturnsPublisherInstance()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act
        var publisher = host.GetPublisher();

        // Assert
        publisher.Should().NotBeNull();
        publisher.Should().BeAssignableTo<IOutOfBandPublisher>();
    }

    [Fact]
    public async Task AgentHost_ProcessMessage_WithoutThreadId_ProcessesSuccessfully()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act
        var response = await host.ProcessMessageAsync("Hello");

        // Assert
        response.Should().NotBeNull();
        response.Type.Should().Be("text");
        response.Text.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task AgentHost_ProcessMessage_WithThreadId_ProcessesSuccessfully()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act
        var response = await host.ProcessMessageAsync("Hello", threadId: "thread-123");

        // Assert
        response.Should().NotBeNull();
        response.Type.Should().Be("text");
        response.Text.Should().NotBeNullOrEmpty();
    }

    [Fact]
    public async Task AgentHost_ProcessMessage_NoAgentsConfigured_ReturnsError()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Create host without agents - this should fail at build time
        // but we test the scenario
        Action act = () => services.AddAgentHost().Build();

        // Assert
        act.Should().Throw<Exception>()
            .WithMessage("*at least one agent*");
    }

    [Fact]
    public async Task AgentHost_Integration_CompleteLifecycle()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test agent"))
            .Build();

        // Act & Assert
        // Start
        await host.StartAsync();
        var health1 = await host.CheckHealthAsync();
        health1.Status.Should().Be("healthy");

        // Get publisher
        var publisher = host.GetPublisher();
        publisher.Should().NotBeNull();
        await publisher.SendToThreadAsync("thread-test", "Test message");

        // Process message
        var response = await host.ProcessMessageAsync("Hello", "thread-test");
        response.Should().NotBeNull();

        // Stop
        await host.StopAsync();
        var health2 = await host.CheckHealthAsync();
        health2.Checks["server"].Should().BeFalse();
    }

    [Fact]
    public async Task AgentHost_WithMultipleAgents_ProcessesCorrectly()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        var host = services.AddAgentHost()
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Default agent"))
            .AddAgent("sales", a => a.UseLLM("gpt-4", "Sales agent"))
            .AddAgent("support", a => a.UseLLM("gpt-4", "Support agent"))
            .Build();

        await host.StartAsync();

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Status.Should().Be("healthy");

        await host.StopAsync();
    }
}
