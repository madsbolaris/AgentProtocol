using System.Collections.Concurrent;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol.Hosting.Core;

namespace Microsoft.Agents.Protocol.Hosting.Storage;

/// <summary>
/// In-memory implementation of IStorage for development and testing.
/// </summary>
public class InMemoryStorage : IStorage
{
    private readonly ConcurrentDictionary<string, ConcurrentDictionary<string, object>> _storage = new();

    /// <inheritdoc/>
    public Task<T?> GetAsync<T>(string threadId, string key, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.FromCanceled<T?>(cancellationToken);
        }

        if (_storage.TryGetValue(threadId, out var threadData) &&
            threadData.TryGetValue(key, out var value))
        {
            return Task.FromResult<T?>((T)value);
        }

        return Task.FromResult<T?>(default);
    }

    /// <inheritdoc/>
    public Task SetAsync<T>(string threadId, string key, T value, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.FromCanceled(cancellationToken);
        }

        var threadData = _storage.GetOrAdd(threadId, _ => new ConcurrentDictionary<string, object>());
        threadData[key] = value!;
        return Task.CompletedTask;
    }

    /// <inheritdoc/>
    public Task DeleteAsync(string threadId, string key, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.FromCanceled(cancellationToken);
        }

        if (_storage.TryGetValue(threadId, out var threadData))
        {
            threadData.TryRemove(key, out _);
        }

        return Task.CompletedTask;
    }

    /// <inheritdoc/>
    public Task<string[]> GetKeysAsync(string threadId, CancellationToken cancellationToken = default)
    {
        if (cancellationToken.IsCancellationRequested)
        {
            return Task.FromCanceled<string[]>(cancellationToken);
        }

        if (_storage.TryGetValue(threadId, out var threadData))
        {
            return Task.FromResult(threadData.Keys.ToArray());
        }

        return Task.FromResult(Array.Empty<string>());
    }

    /// <inheritdoc/>
    public Task<bool> CheckHealthAsync()
    {
        return Task.FromResult(true);
    }
}
