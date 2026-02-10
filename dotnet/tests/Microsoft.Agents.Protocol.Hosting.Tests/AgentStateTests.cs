using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Core;
using Moq;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class AgentStateTests
{
    private readonly Mock<IStorage> _mockStorage;

    public AgentStateTests()
    {
        _mockStorage = new Mock<IStorage>();
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenThreadIdIsNull()
    {
        // Act & Assert
        var act = () => new AgentState(null!, _mockStorage.Object);
        act.Should().Throw<ArgumentNullException>().WithParameterName("threadId");
    }

    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenStorageIsNull()
    {
        // Act & Assert
        var act = () => new AgentState("thread1", null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("storage");
    }

    [Fact]
    public async Task GetAsync_CallsStorageWithThreadId()
    {
        // Arrange
        var threadId = "thread-123";
        var key = "myKey";
        var state = new AgentState(threadId, _mockStorage.Object);

        _mockStorage.Setup(x => x.GetAsync<string>(threadId, key, It.IsAny<CancellationToken>()))
            .ReturnsAsync("test value");

        // Act
        var result = await state.GetAsync<string>(key);

        // Assert
        result.Should().Be("test value");
        _mockStorage.Verify(x => x.GetAsync<string>(threadId, key, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task SetAsync_CallsStorageWithThreadId()
    {
        // Arrange
        var threadId = "thread-123";
        var key = "myKey";
        var value = "test value";
        var state = new AgentState(threadId, _mockStorage.Object);

        // Act
        await state.SetAsync(key, value);

        // Assert
        _mockStorage.Verify(x => x.SetAsync(threadId, key, value, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task DeleteAsync_CallsStorageWithThreadId()
    {
        // Arrange
        var threadId = "thread-123";
        var key = "myKey";
        var state = new AgentState(threadId, _mockStorage.Object);

        // Act
        await state.DeleteAsync(key);

        // Assert
        _mockStorage.Verify(x => x.DeleteAsync(threadId, key, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GetKeysAsync_CallsStorageWithThreadId()
    {
        // Arrange
        var threadId = "thread-123";
        var state = new AgentState(threadId, _mockStorage.Object);
        var expectedKeys = new[] { "key1", "key2" };

        _mockStorage.Setup(x => x.GetKeysAsync(threadId, It.IsAny<CancellationToken>()))
            .ReturnsAsync(expectedKeys);

        // Act
        var result = await state.GetKeysAsync();

        // Assert
        result.Should().BeEquivalentTo(expectedKeys);
        _mockStorage.Verify(x => x.GetKeysAsync(threadId, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GetAsync_ReturnsNull_WhenKeyDoesNotExist()
    {
        // Arrange
        var state = new AgentState("thread1", _mockStorage.Object);
        _mockStorage.Setup(x => x.GetAsync<string>("thread1", "nonexistent", It.IsAny<CancellationToken>()))
            .ReturnsAsync((string?)null);

        // Act
        var result = await state.GetAsync<string>("nonexistent");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task SetAsync_SupportsComplexTypes()
    {
        // Arrange
        var state = new AgentState("thread1", _mockStorage.Object);
        var data = new TestData { Id = 42, Name = "Test" };

        // Act
        await state.SetAsync("myKey", data);

        // Assert
        _mockStorage.Verify(x => x.SetAsync("thread1", "myKey", data, It.IsAny<CancellationToken>()), Times.Once);
    }

    [Fact]
    public async Task GetAsync_RespectsCancellation()
    {
        // Arrange
        var state = new AgentState("thread1", _mockStorage.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        _mockStorage.Setup(x => x.GetAsync<string>(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns<string, string, CancellationToken>((_, _, ct) => Task.FromCanceled<string?>(ct));

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await state.GetAsync<string>("key", cts.Token));
    }

    [Fact]
    public async Task SetAsync_RespectsCancellation()
    {
        // Arrange
        var state = new AgentState("thread1", _mockStorage.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        _mockStorage.Setup(x => x.SetAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns<string, string, string, CancellationToken>((_, _, _, ct) => Task.FromCanceled(ct));

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await state.SetAsync("key", "value", cts.Token));
    }

    [Fact]
    public async Task DeleteAsync_RespectsCancellation()
    {
        // Arrange
        var state = new AgentState("thread1", _mockStorage.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        _mockStorage.Setup(x => x.DeleteAsync(It.IsAny<string>(), It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns<string, string, CancellationToken>((_, _, ct) => Task.FromCanceled(ct));

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await state.DeleteAsync("key", cts.Token));
    }

    [Fact]
    public async Task GetKeysAsync_RespectsCancellation()
    {
        // Arrange
        var state = new AgentState("thread1", _mockStorage.Object);
        var cts = new CancellationTokenSource();
        cts.Cancel();

        _mockStorage.Setup(x => x.GetKeysAsync(It.IsAny<string>(), It.IsAny<CancellationToken>()))
            .Returns<string, CancellationToken>((_, ct) => Task.FromCanceled<string[]>(ct));

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await state.GetKeysAsync(cts.Token));
    }

    private class TestData
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
    }
}
