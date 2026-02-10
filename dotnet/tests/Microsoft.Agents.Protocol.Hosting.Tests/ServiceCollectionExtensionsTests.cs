using System;
using System.Linq;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class ServiceCollectionExtensionsTests
{
    [Fact]
    public void AddAgentHost_ThrowsArgumentNullException_WhenServicesIsNull()
    {
        // Arrange
        IServiceCollection? services = null;

        // Act & Assert
        var act = () => services!.AddAgentHost();
        act.Should().Throw<ArgumentNullException>().WithParameterName("services");
    }

    [Fact]
    public void AddAgentHost_ReturnsAgentHostBuilder()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        var result = services.AddAgentHost();

        // Assert
        result.Should().NotBeNull();
        result.Should().BeOfType<AgentHostBuilder>();
    }

    [Fact]
    public void AddAgentHost_AddsLogging_WhenNotAlreadyPresent()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost();

        // Assert
        services.Should().Contain(s => s.ServiceType == typeof(ILoggerFactory));
    }

    [Fact]
    public void AddAgentHost_DoesNotAddLogging_WhenAlreadyPresent()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();
        var initialCount = services.Count(s => s.ServiceType == typeof(ILoggerFactory));

        // Act
        services.AddAgentHost();

        // Assert
        var finalCount = services.Count(s => s.ServiceType == typeof(ILoggerFactory));
        finalCount.Should().Be(initialCount);
    }

    [Fact]
    public void AddAgentHost_ReturnsBuilderWithServices()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        var builder = services.AddAgentHost();

        // Assert
        builder.Services.Should().BeSameAs(services);
    }
}
