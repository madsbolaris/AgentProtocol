using System.Threading;
using System.Threading.Tasks;

namespace Microsoft.Agents.Protocol.Hosting.Core;

/// <summary>
/// Provides access to thread-scoped state storage for an agent.
/// </summary>
public class AgentState
{
    private readonly string _threadId;
    private readonly IStorage _storage;

    /// <summary>
    /// Creates a new AgentState instance.
    /// </summary>
    /// <param name="threadId">The thread ID.</param>
    /// <param name="storage">The storage implementation.</param>
    public AgentState(string threadId, IStorage storage)
    {
        _threadId = threadId ?? throw new ArgumentNullException(nameof(threadId));
        _storage = storage ?? throw new ArgumentNullException(nameof(storage));
    }

    /// <summary>
    /// Gets a value from state.
    /// </summary>
    /// <typeparam name="T">The type of value to retrieve.</typeparam>
    /// <param name="key">The key.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>The value, or default if not found.</returns>
    public Task<T?> GetAsync<T>(string key, CancellationToken cancellationToken = default)
    {
        return _storage.GetAsync<T>(_threadId, key, cancellationToken);
    }

    /// <summary>
    /// Sets a value in state.
    /// </summary>
    /// <typeparam name="T">The type of value to store.</typeparam>
    /// <param name="key">The key.</param>
    /// <param name="value">The value to store.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public Task SetAsync<T>(string key, T value, CancellationToken cancellationToken = default)
    {
        return _storage.SetAsync(_threadId, key, value, cancellationToken);
    }

    /// <summary>
    /// Deletes a value from state.
    /// </summary>
    /// <param name="key">The key.</param>
    /// <param name="cancellationToken">Cancellation token.</param>
    public Task DeleteAsync(string key, CancellationToken cancellationToken = default)
    {
        return _storage.DeleteAsync(_threadId, key, cancellationToken);
    }

    /// <summary>
    /// Gets all keys in state.
    /// </summary>
    /// <param name="cancellationToken">Cancellation token.</param>
    /// <returns>Array of keys.</returns>
    public Task<string[]> GetKeysAsync(CancellationToken cancellationToken = default)
    {
        return _storage.GetKeysAsync(_threadId, cancellationToken);
    }
}
