using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Storage;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class InMemoryStorageTests
{
    [Fact]
    public async Task GetAsync_ReturnsNull_WhenKeyDoesNotExist()
    {
        // Arrange
        var storage = new InMemoryStorage();

        // Act
        var result = await storage.GetAsync<string>("thread1", "key1");

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task SetAsync_And_GetAsync_StoresAndRetrievesValue()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";
        var key = "key1";
        var value = "test value";

        // Act
        await storage.SetAsync(threadId, key, value);
        var result = await storage.GetAsync<string>(threadId, key);

        // Assert
        result.Should().Be(value);
    }

    [Fact]
    public async Task SetAsync_UpdatesExistingValue()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";
        var key = "key1";

        // Act
        await storage.SetAsync(threadId, key, "value1");
        await storage.SetAsync(threadId, key, "value2");
        var result = await storage.GetAsync<string>(threadId, key);

        // Assert
        result.Should().Be("value2");
    }

    [Fact]
    public async Task GetAsync_SupportsMultipleThreads()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var thread1 = "thread1";
        var thread2 = "thread2";
        var key = "key1";

        // Act
        await storage.SetAsync(thread1, key, "value1");
        await storage.SetAsync(thread2, key, "value2");

        var result1 = await storage.GetAsync<string>(thread1, key);
        var result2 = await storage.GetAsync<string>(thread2, key);

        // Assert
        result1.Should().Be("value1");
        result2.Should().Be("value2");
    }

    [Fact]
    public async Task GetAsync_SupportsMultipleKeys()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";

        // Act
        await storage.SetAsync(threadId, "key1", "value1");
        await storage.SetAsync(threadId, "key2", "value2");

        var result1 = await storage.GetAsync<string>(threadId, "key1");
        var result2 = await storage.GetAsync<string>(threadId, "key2");

        // Assert
        result1.Should().Be("value1");
        result2.Should().Be("value2");
    }

    [Fact]
    public async Task GetAsync_SupportsComplexTypes()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";
        var key = "key1";
        var value = new TestData { Id = 123, Name = "Test" };

        // Act
        await storage.SetAsync(threadId, key, value);
        var result = await storage.GetAsync<TestData>(threadId, key);

        // Assert
        result.Should().NotBeNull();
        result!.Id.Should().Be(123);
        result.Name.Should().Be("Test");
    }

    [Fact]
    public async Task DeleteAsync_RemovesKey()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";
        var key = "key1";

        await storage.SetAsync(threadId, key, "value");

        // Act
        await storage.DeleteAsync(threadId, key);
        var result = await storage.GetAsync<string>(threadId, key);

        // Assert
        result.Should().BeNull();
    }

    [Fact]
    public async Task DeleteAsync_DoesNotThrow_WhenKeyDoesNotExist()
    {
        // Arrange
        var storage = new InMemoryStorage();

        // Act & Assert
        await storage.DeleteAsync("thread1", "nonexistent");
        Assert.True(true);
    }

    [Fact]
    public async Task DeleteAsync_DoesNotThrow_WhenThreadDoesNotExist()
    {
        // Arrange
        var storage = new InMemoryStorage();

        // Act & Assert
        await storage.DeleteAsync("nonexistent", "key1");
        Assert.True(true);
    }

    [Fact]
    public async Task GetKeysAsync_ReturnsEmptyArray_WhenThreadDoesNotExist()
    {
        // Arrange
        var storage = new InMemoryStorage();

        // Act
        var keys = await storage.GetKeysAsync("nonexistent");

        // Assert
        keys.Should().BeEmpty();
    }

    [Fact]
    public async Task GetKeysAsync_ReturnsAllKeys_ForThread()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";

        await storage.SetAsync(threadId, "key1", "value1");
        await storage.SetAsync(threadId, "key2", "value2");
        await storage.SetAsync(threadId, "key3", "value3");

        // Act
        var keys = await storage.GetKeysAsync(threadId);

        // Assert
        keys.Should().HaveCount(3);
        keys.Should().Contain("key1");
        keys.Should().Contain("key2");
        keys.Should().Contain("key3");
    }

    [Fact]
    public async Task GetKeysAsync_OnlyReturnsKeysForSpecificThread()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var thread1 = "thread1";
        var thread2 = "thread2";

        await storage.SetAsync(thread1, "key1", "value1");
        await storage.SetAsync(thread1, "key2", "value2");
        await storage.SetAsync(thread2, "key3", "value3");

        // Act
        var keys = await storage.GetKeysAsync(thread1);

        // Assert
        keys.Should().HaveCount(2);
        keys.Should().Contain("key1");
        keys.Should().Contain("key2");
        keys.Should().NotContain("key3");
    }

    [Fact]
    public async Task CheckHealthAsync_ReturnsTrue()
    {
        // Arrange
        var storage = new InMemoryStorage();

        // Act
        var isHealthy = await storage.CheckHealthAsync();

        // Assert
        isHealthy.Should().BeTrue();
    }

    [Fact]
    public async Task GetAsync_RespectsCancellation()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await storage.GetAsync<string>("thread1", "key1", cts.Token));
    }

    [Fact]
    public async Task SetAsync_RespectsCancellation()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await storage.SetAsync("thread1", "key1", "value", cts.Token));
    }

    [Fact]
    public async Task DeleteAsync_RespectsCancellation()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await storage.DeleteAsync("thread1", "key1", cts.Token));
    }

    [Fact]
    public async Task GetKeysAsync_RespectsCancellation()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var cts = new CancellationTokenSource();
        cts.Cancel();

        // Act & Assert
        await Assert.ThrowsAsync<TaskCanceledException>(async () =>
            await storage.GetKeysAsync("thread1", cts.Token));
    }

    [Fact]
    public async Task Storage_IsThreadSafe()
    {
        // Arrange
        var storage = new InMemoryStorage();
        var threadId = "thread1";
        var taskCount = 100;
        var tasks = new Task[taskCount];

        // Act - Write from multiple threads simultaneously
        for (int i = 0; i < taskCount; i++)
        {
            var index = i;
            tasks[i] = Task.Run(async () =>
            {
                await storage.SetAsync(threadId, $"key{index}", $"value{index}");
            });
        }

        await Task.WhenAll(tasks);

        // Assert - All keys should be stored
        var keys = await storage.GetKeysAsync(threadId);
        keys.Should().HaveCount(taskCount);
    }

    private class TestData
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
    }
}
