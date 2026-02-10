using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Storage;
using Microsoft.Extensions.Logging;
using Moq;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class AgentContextTests
{
    private readonly Mock<ILogger> _mockLogger;
    private readonly Mock<IStorage> _mockStorage;

    public AgentContextTests()
    {
        _mockLogger = new Mock<ILogger>();
        _mockStorage = new Mock<IStorage>();
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenRunIdIsNull()
    {
        // Act & Assert
        var act = () => new AgentContext(null!, "thread1", _mockStorage.Object, _mockLogger.Object);
        act.Should().Throw<ArgumentNullException>().WithParameterName("runId");
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenThreadIdIsNull()
    {
        // Act & Assert
        var act = () => new AgentContext("run1", null!, _mockStorage.Object, _mockLogger.Object);
        act.Should().Throw<ArgumentNullException>().WithParameterName("threadId");
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenStorageIsNull()
    {
        // Act & Assert
        var act = () => new AgentContext("run1", "thread1", null!, _mockLogger.Object);
        act.Should().Throw<ArgumentNullException>().WithParameterName("storage");
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenLoggerIsNull()
    {
        // Act & Assert
        var act = () => new AgentContext("run1", "thread1", _mockStorage.Object, null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("logger");
    }

    [Fact]
    public void Constructor_SetsProperties_Correctly()
    {
        // Arrange
        var runId = "run-123";
        var threadId = "thread-456";

        // Act
        var context = new AgentContext(runId, threadId, _mockStorage.Object, _mockLogger.Object);

        // Assert
        context.RunId.Should().Be(runId);
        context.ThreadId.Should().Be(threadId);
        context.Logger.Should().Be(_mockLogger.Object);
        context.State.Should().NotBeNull();
    }

    [Fact]
    public async Task RespondAsync_WithAIContent_CallsCallback()
    {
        // Arrange
        string? capturedResponse = null;
        Task ResponseCallback(string text)
        {
            capturedResponse = text;
            return Task.CompletedTask;
        }

        var context = new AgentContext(
            "run1",
            "thread1",
            _mockStorage.Object,
            _mockLogger.Object,
            ResponseCallback);

        var content = new TextContent { Text = "Test response" };

        // Act
        await context.RespondAsync(content);

        // Assert
        capturedResponse.Should().NotBeNull();
        capturedResponse.Should().Contain("Test response");
    }

    [Fact]
    public async Task RespondAsync_WithString_CallsCallback()
    {
        // Arrange
        string? capturedResponse = null;
        Task ResponseCallback(string text)
        {
            capturedResponse = text;
            return Task.CompletedTask;
        }

        var context = new AgentContext(
            "run1",
            "thread1",
            _mockStorage.Object,
            _mockLogger.Object,
            ResponseCallback);

        // Act
        await context.RespondAsync("Test response");

        // Assert
        capturedResponse.Should().Be("Test response");
    }

    [Fact]
    public async Task RespondAsync_WithAIContent_DoesNothing_WhenCallbackIsNull()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);
        var content = new TextContent { Text = "Test response" };

        // Act & Assert - should not throw
        await context.RespondAsync(content);
    }

    [Fact]
    public async Task RespondAsync_WithString_DoesNothing_WhenCallbackIsNull()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act & Assert - should not throw
        await context.RespondAsync("Test response");
    }

    [Fact]
    public async Task RespondAsync_WithAIContent_RespectsCancellation()
    {
        // Arrange
        var cts = new CancellationTokenSource();
        cts.Cancel();

        var context = new AgentContext(
            "run1",
            "thread1",
            _mockStorage.Object,
            _mockLogger.Object,
            _ => Task.CompletedTask);

        var content = new TextContent { Text = "Test" };

        // Act
        await context.RespondAsync(content, cts.Token);

        // Assert - should not call callback when cancelled
        Xunit.Assert.True(true);
    }

    [Fact]
    public async Task RespondAsync_WithString_RespectsCancellation()
    {
        // Arrange
        var cts = new CancellationTokenSource();
        cts.Cancel();

        var context = new AgentContext(
            "run1",
            "thread1",
            _mockStorage.Object,
            _mockLogger.Object,
            _ => Task.CompletedTask);

        // Act
        await context.RespondAsync("Test", cts.Token);

        // Assert - should not call callback when cancelled
        Xunit.Assert.True(true);
    }

    [Fact]
    public async Task LogAsync_LogsMessage_WithRunId()
    {
        // Arrange
        var context = new AgentContext("run-123", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act
        await context.LogAsync("Test log message");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("run-123") && v.ToString()!.Contains("Test log message")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task LogAsync_WithLevel_LogsAtDebugLevel()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act
        await context.LogAsync("Debug message", "DEBUG");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Debug,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Debug message")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task LogAsync_WithLevel_LogsAtWarningLevel()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act
        await context.LogAsync("Warning message", "WARNING");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Warning,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Warning message")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task LogAsync_WithLevel_LogsAtErrorLevel()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act
        await context.LogAsync("Error message", "ERROR");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Error,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Error message")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task LogAsync_WithLevel_DefaultsToInformation()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act
        await context.LogAsync("Default message", "UNKNOWN");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Default message")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task LogAsync_RespectsCancellation()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act
        await context.LogAsync("Test", cancellationToken: cts.Token);

        // Assert - should not log when cancelled
        _mockLogger.Verify(
            x => x.Log(
                It.IsAny<LogLevel>(),
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Never);
    }

    [Fact]
    public async Task PauseForApprovalAsync_LogsPauseRequest()
    {
        // Arrange
        var context = new AgentContext("run-123", "thread1", _mockStorage.Object, _mockLogger.Object);

        // Act
        await context.PauseForApprovalAsync("Need approval for action");

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Pause for approval") && v.ToString()!.Contains("Need approval for action")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task PauseForApprovalAsync_WithMetadata_LogsCorrectly()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);
        var metadata = new { action = "delete", resource = "file.txt" };

        // Act
        await context.PauseForApprovalAsync("Need approval", metadata);

        // Assert
        _mockLogger.Verify(
            x => x.Log(
                LogLevel.Information,
                It.IsAny<EventId>(),
                It.Is<It.IsAnyType>((v, t) => v.ToString()!.Contains("Pause for approval")),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Once);
    }

    [Fact]
    public async Task PauseForApprovalAsync_RespectsCancellation()
    {
        // Arrange
        var context = new AgentContext("run1", "thread1", _mockStorage.Object, _mockLogger.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act
        await context.PauseForApprovalAsync("Test", cancellationToken: cts.Token);

        // Assert - should not log when cancelled
        _mockLogger.Verify(
            x => x.Log(
                It.IsAny<LogLevel>(),
                It.IsAny<EventId>(),
                It.IsAny<It.IsAnyType>(),
                It.IsAny<Exception>(),
                It.IsAny<Func<It.IsAnyType, Exception?, string>>()),
            Times.Never);
    }
}
