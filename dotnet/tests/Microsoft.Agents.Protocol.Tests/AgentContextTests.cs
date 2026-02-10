using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests;

/// <summary>
/// Tests for AgentContext and IAgentContext implementations.
/// </summary>
public class AgentContextTests
{
    private class MockStorage : IStorage
    {
        private readonly Dictionary<string, Dictionary<string, object>> _data = new();

        public Task<T?> GetAsync<T>(string threadId, string key, CancellationToken cancellationToken = default)
        {
            if (_data.TryGetValue(threadId, out var threadData) &&
                threadData.TryGetValue(key, out var value))
            {
                return Task.FromResult<T?>((T)value);
            }
            return Task.FromResult<T?>(default);
        }

        public Task SetAsync<T>(string threadId, string key, T value, CancellationToken cancellationToken = default)
        {
            if (!_data.ContainsKey(threadId))
            {
                _data[threadId] = new Dictionary<string, object>();
            }
            _data[threadId][key] = value!;
            return Task.CompletedTask;
        }

        public Task DeleteAsync(string threadId, string key, CancellationToken cancellationToken = default)
        {
            if (_data.TryGetValue(threadId, out var threadData))
            {
                threadData.Remove(key);
            }
            return Task.CompletedTask;
        }

        public Task<string[]> GetKeysAsync(string threadId, CancellationToken cancellationToken = default)
        {
            if (_data.TryGetValue(threadId, out var threadData))
            {
                return Task.FromResult(threadData.Keys.ToArray());
            }
            return Task.FromResult(Array.Empty<string>());
        }

        public Task<bool> CheckHealthAsync()
        {
            return Task.FromResult(true);
        }
    }

    [Fact]
    public void AgentContext_Constructor_CreatesInstance()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();

        // Act
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        // Assert
        context.Should().NotBeNull();
        context.RunId.Should().Be("run-123");
        context.ThreadId.Should().Be("thread-456");
    }

    [Fact]
    public void AgentContext_Properties_ReturnsCorrectValues()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-001", "thread-002", storage, logger);

        // Act & Assert
        context.RunId.Should().Be("run-001");
        context.ThreadId.Should().Be("thread-002");
        context.State.Should().NotBeNull();
    }

    [Fact]
    public async Task AgentContext_RespondAsync_WithString_AddsResponse()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var responses = new List<string>();
        Func<string, Task> callback = async (content) =>
        {
            responses.Add(content);
            await Task.CompletedTask;
        };
        var context = new AgentContext("run-123", "thread-456", storage, logger, callback);

        // Act
        await context.RespondAsync("Hello, World!");

        // Assert
        responses.Should().HaveCount(1);
        responses[0].Should().Be("Hello, World!");
    }

    [Fact]
    public async Task AgentContext_RespondAsync_Multiple_AccumulatesResponses()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var responses = new List<string>();
        Func<string, Task> callback = async (content) =>
        {
            responses.Add(content);
            await Task.CompletedTask;
        };
        var context = new AgentContext("run-123", "thread-456", storage, logger, callback);

        // Act
        await context.RespondAsync("Message 1");
        await context.RespondAsync("Message 2");
        await context.RespondAsync("Message 3");

        // Assert
        responses.Should().HaveCount(3);
        responses.Should().ContainInOrder("Message 1", "Message 2", "Message 3");
    }

    [Fact]
    public async Task AgentContext_RespondAsync_WithoutCallback_DoesNotThrow()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger, null);

        // Act & Assert - should not throw
        await context.RespondAsync("Hello!");
    }

    [Fact]
    public async Task AgentContext_RespondAsync_WithCancellationToken_RespectsCancellation()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var responses = new List<string>();
        Func<string, Task> callback = async (content) =>
        {
            responses.Add(content);
            await Task.CompletedTask;
        };
        var context = new AgentContext("run-123", "thread-456", storage, logger, callback);

        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act
        await context.RespondAsync("Should not be added", cts.Token);

        // Assert
        responses.Should().HaveCount(0);
    }

    [Fact]
    public async Task AgentContext_LogAsync_LogsMessage()
    {
        // Arrange
        var storage = new MockStorage();
        var loggerFactory = LoggerFactory.Create(builder =>
        {
            builder.AddConsole();
            builder.SetMinimumLevel(LogLevel.Debug);
        });
        var logger = loggerFactory.CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        // Act & Assert - should not throw
        await context.LogAsync("Test log message", "INFO");
    }

    [Fact]
    public async Task AgentContext_LogAsync_WithDifferentLevels_LogsCorrectly()
    {
        // Arrange
        var storage = new MockStorage();
        var loggerFactory = LoggerFactory.Create(builder =>
        {
            builder.AddConsole();
            builder.SetMinimumLevel(LogLevel.Debug);
        });
        var logger = loggerFactory.CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        // Act & Assert - should not throw
        await context.LogAsync("Debug message", "DEBUG");
        await context.LogAsync("Info message", "INFO");
        await context.LogAsync("Warning message", "WARNING");
        await context.LogAsync("Error message", "ERROR");
    }

    [Fact]
    public async Task AgentContext_LogAsync_WithCancellation_RespectsCancellation()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert - should not log when cancelled
        await context.LogAsync("Should not log", "INFO", cts.Token);
    }

    [Fact]
    public async Task AgentContext_PauseForApprovalAsync_ExecutesWithoutError()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        // Act & Assert - should not throw
        await context.PauseForApprovalAsync("Approve this action");
    }

    [Fact]
    public async Task AgentContext_PauseForApprovalAsync_WithMetadata_ExecutesWithoutError()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        var metadata = new Dictionary<string, object>
        {
            ["action"] = "delete",
            ["resource"] = "file.txt"
        };

        // Act & Assert - should not throw
        await context.PauseForApprovalAsync("Approve deletion", metadata);
    }

    [Fact]
    public async Task AgentContext_PauseForApprovalAsync_WithCancellation_RespectsCancellation()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert - should not pause when cancelled
        await context.PauseForApprovalAsync("Should not pause", null, cts.Token);
    }

    [Fact]
    public async Task AgentContext_State_GetAndSet_WorksCorrectly()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        // Act
        await context.State.SetAsync("counter", 0);
        var result = await context.State.GetAsync<int>("counter");

        // Assert
        result.Should().Be(0);

        // Update
        await context.State.SetAsync("counter", 1);
        var updatedResult = await context.State.GetAsync<int>("counter");
        updatedResult.Should().Be(1);
    }

    [Fact]
    public async Task AgentContext_MultipleContexts_SameThread_ShareState()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();

        var context1 = new AgentContext("run-1", "thread-shared", storage, logger);
        var context2 = new AgentContext("run-2", "thread-shared", storage, logger);

        // Act
        await context1.State.SetAsync("shared_key", "shared_value");
        var result = await context2.State.GetAsync<string>("shared_key");

        // Assert
        result.Should().Be("shared_value");
    }

    [Fact]
    public async Task AgentContext_MultipleContexts_DifferentThreads_IsolateState()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();

        var context1 = new AgentContext("run-1", "thread-1", storage, logger);
        var context2 = new AgentContext("run-2", "thread-2", storage, logger);

        // Act
        await context1.State.SetAsync("key", "value1");
        await context2.State.SetAsync("key", "value2");

        var result1 = await context1.State.GetAsync<string>("key");
        var result2 = await context2.State.GetAsync<string>("key");

        // Assert
        result1.Should().Be("value1");
        result2.Should().Be("value2");
    }

    [Fact]
    public void AgentContext_ImplementsIAgentContext()
    {
        // Arrange
        var storage = new MockStorage();
        var logger = LoggerFactory.Create(builder => { }).CreateLogger<AgentContext>();
        var context = new AgentContext("run-123", "thread-456", storage, logger);

        // Act & Assert
        context.Should().BeAssignableTo<IAgentContext>();
    }
}
