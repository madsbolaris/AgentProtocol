using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Storage;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class AgentHostTests
{
    private readonly Mock<ILogger<AgentHost>> _mockLogger;
    private readonly Mock<IStorage> _mockStorage;
    private readonly Mock<ILoggerFactory> _mockLoggerFactory;
    private readonly Mock<IOutOfBandPublisher> _mockPublisher;

    public AgentHostTests()
    {
        _mockLogger = new Mock<ILogger<AgentHost>>();
        _mockStorage = new Mock<IStorage>();
        _mockLoggerFactory = new Mock<ILoggerFactory>();
        _mockPublisher = new Mock<IOutOfBandPublisher>();

        _mockLoggerFactory.Setup(x => x.CreateLogger(It.IsAny<string>()))
            .Returns(Mock.Of<ILogger>());
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenLoggerIsNull()
    {
        // Act & Assert
        var act = () => new AgentHost(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("logger");
    }

    [Fact]
    public void Constructor_WithPublisher_UsesProvidedPublisher()
    {
        // Act
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, _mockPublisher.Object, null);

        // Assert
        host.Should().NotBeNull();
        var publisher = host.GetPublisher();
        publisher.Should().Be(_mockPublisher.Object);
    }

    [Fact]
    public void Constructor_UsesInMemoryStorage_WhenStorageIsNull()
    {
        // Act
        var host = new AgentHost(_mockLogger.Object, null, null, _mockLoggerFactory.Object);

        // Assert
        host.Should().NotBeNull();
    }

    [Fact]
    public void Constructor_CreatesPublisher_WhenLoggerFactoryProvided()
    {
        // Act
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Assert
        host.Should().NotBeNull();
        var publisher = host.GetPublisher();
        publisher.Should().NotBeNull();
    }

    [Fact]
    public async Task StartAsync_StartsHost_Successfully()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Act
        await host.StartAsync(3000);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Agent host started on port 3000")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task StartAsync_ThrowsInvalidOperationException_WhenAlreadyRunning()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);

        // Act & Assert
        var act = async () => await host.StartAsync(3000);
        await act.Should().ThrowAsync<InvalidOperationException>()
            .WithMessage("Agent host is already running.");
    }

    [Fact]
    public async Task StopAsync_StopsHost_Successfully()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);

        // Act
        await host.StopAsync();

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Agent host stopped")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task StopAsync_DoesNothing_WhenNotRunning()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Act
        await host.StopAsync();

        // Assert - should not throw
        Assert.True(true);
    }

    [Fact]
    public async Task StopAsync_WaitsForGracePeriod_WhenSpecified()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);
        var stopOptions = new StopOptions { GracePeriodMs = 100 };

        // Act
        var stopwatch = System.Diagnostics.Stopwatch.StartNew();
        await host.StopAsync(stopOptions);
        stopwatch.Stop();

        // Assert
        stopwatch.ElapsedMilliseconds.Should().BeGreaterOrEqualTo(100);
    }

    [Fact]
    public async Task StopAsync_LogsFinishQueued_WhenFinishQueuedIsTrue()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);
        var stopOptions = new StopOptions { FinishQueued = true };

        // Act
        await host.StopAsync(stopOptions);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Finishing queued tasks")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task CheckHealthAsync_ReturnsHealthy_WhenAllChecksPass()
    {
        // Arrange
        _mockStorage.Setup(x => x.CheckHealthAsync()).ReturnsAsync(true);
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Should().NotBeNull();
        health.Status.Should().Be("healthy");
        health.Checks["server"].Should().BeTrue();
        health.Checks["storage"].Should().BeTrue();
        health.Checks["queue"].Should().BeTrue();
        health.Checks["llmConnection"].Should().BeTrue();
        health.UptimeMs.Should().BeGreaterOrEqualTo(0);
    }

    [Fact]
    public async Task CheckHealthAsync_ReturnsDegraded_WhenServerNotRunning()
    {
        // Arrange
        _mockStorage.Setup(x => x.CheckHealthAsync()).ReturnsAsync(true);
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Should().NotBeNull();
        health.Status.Should().Be("degraded");
        health.Checks["server"].Should().BeFalse();
    }

    [Fact]
    public async Task CheckHealthAsync_ReturnsDegraded_WhenStorageUnhealthy()
    {
        // Arrange
        _mockStorage.Setup(x => x.CheckHealthAsync()).ReturnsAsync(false);
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Should().NotBeNull();
        health.Status.Should().Be("degraded");
        health.Checks["storage"].Should().BeFalse();
    }

    [Fact]
    public async Task CheckHealthAsync_HandleStorageException_Gracefully()
    {
        // Arrange
        _mockStorage.Setup(x => x.CheckHealthAsync()).ThrowsAsync(new Exception("Storage error"));
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        await host.StartAsync(3000);

        // Act
        var health = await host.CheckHealthAsync();

        // Assert
        health.Should().NotBeNull();
        health.Status.Should().Be("degraded");
        health.Checks["storage"].Should().BeFalse();
    }

    [Fact]
    public void GetPublisher_ReturnsPublisher()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Act
        var publisher = host.GetPublisher();

        // Assert
        publisher.Should().NotBeNull();
        publisher.Should().BeAssignableTo<IOutOfBandPublisher>();
    }

    [Fact]
    public async Task ProcessMessageAsync_ReturnsResponse_WithGeneratedIds()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Act
        var response = await host.ProcessMessageAsync("Hello, World!");

        // Assert
        response.Should().NotBeNull();
        response.Text.Should().Be("Echo: Hello, World!");
        response.ThreadId.Should().NotBeNullOrEmpty();
        response.ThreadId.Should().StartWith("thread-");
        response.RunId.Should().NotBeNullOrEmpty();
        response.RunId.Should().StartWith("run-");
        response.Type.Should().Be("text");
    }

    [Fact]
    public async Task ProcessMessageAsync_UsesProvidedThreadId()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        var threadId = "custom-thread-id";

        // Act
        var response = await host.ProcessMessageAsync("Hello", threadId);

        // Assert
        response.Should().NotBeNull();
        response.ThreadId.Should().Be(threadId);
    }

    [Fact]
    public async Task ProcessMessageAsync_LogsProcessing()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);

        // Act
        await host.ProcessMessageAsync("Test message");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Processing message")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task ProcessMessageAsync_RespectsCancellationToken()
    {
        // Arrange
        var host = new AgentHost(_mockLogger.Object, _mockStorage.Object, null, _mockLoggerFactory.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await host.ProcessMessageAsync("Test", cancellationToken: cts.Token));
    }
}
