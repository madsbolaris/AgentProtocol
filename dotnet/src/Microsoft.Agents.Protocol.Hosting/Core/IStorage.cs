using System.Threading;
using System.Threading.Tasks;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Interface for thread-scoped state storage.
/// </summary>
public interface IStorage
{
    /// <summary>
    /// Gets a value from storage for a specific thread and key.
    /// </summary>
    /// <typeparam name="T">The type of value to retrieve.</typeparam>
    /// <param name="threadId">The thread ID.</param>
    /// <param name="key">The key.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The value, or default if not found.</returns>
    Task<T?> GetAsync<T>(string threadId, string key, CancellationToken cancellationToken = default);

    /// <summary>
    /// Sets a value in storage for a specific thread and key.
    /// </summary>
    /// <typeparam name="T">The type of value to store.</typeparam>
    /// <param name="threadId">The thread ID.</param>
    /// <param name="key">The key.</param>
    /// <param name="value">The value to store.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task SetAsync<T>(string threadId, string key, T value, CancellationToken cancellationToken = default);

    /// <summary>
    /// Deletes a value from storage.
    /// </summary>
    /// <param name="threadId">The thread ID.</param>
    /// <param name="key">The key.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    Task DeleteAsync(string threadId, string key, CancellationToken cancellationToken = default);

    /// <summary>
    /// Gets all keys for a specific thread.
    /// </summary>
    /// <param name="threadId">The thread ID.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Array of keys.</returns>
    Task<string[]> GetKeysAsync(string threadId, CancellationToken cancellationToken = default);

    /// <summary>
    /// Checks if the storage is healthy and accessible.
    /// </summary>
    /// <returns>True if healthy, false otherwise.</returns>
    Task<bool> CheckHealthAsync();
}
