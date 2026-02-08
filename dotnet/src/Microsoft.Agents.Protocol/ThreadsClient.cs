using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol.Models.Messages;
using Microsoft.Agents.Protocol.Models.Execution;
using ConversationThread = Microsoft.Agents.Protocol.Models.Threads.Thread;
using ThreadStatus = Microsoft.Agents.Protocol.Models.Threads.ThreadStatus;
using ThreadCopyRequest = Microsoft.Agents.Protocol.Models.Threads.ThreadCopyRequest;
using ThreadWatch = Microsoft.Agents.Protocol.Models.Threads.ThreadWatch;

namespace Microsoft.Agents.Protocol;

/// <summary>
/// Client for Threads API operations
/// Handles creating and managing conversation threads
/// </summary>
public class ThreadsClient
{
    private readonly HttpClient _httpClient;
    private readonly AgentProtocolClientOptions _options;
    private readonly JsonSerializerOptions _jsonOptions;

    internal ThreadsClient(HttpClient httpClient, AgentProtocolClientOptions options)
    {
        _httpClient = httpClient ?? throw new ArgumentNullException(nameof(httpClient));
        _options = options ?? throw new ArgumentNullException(nameof(options));

        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };
    }

    /// <summary>
    /// Creates a new conversation thread
    /// </summary>
    /// <param name="thread">Thread configuration</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created thread</returns>
    public async Task<ConversationThread> CreateAsync(ConversationThread thread, CancellationToken cancellationToken = default)
    {
        if (thread == null) throw new ArgumentNullException(nameof(thread));

        var response = await _httpClient.PostAsJsonAsync("/threads", thread, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ConversationThread>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize thread response");
    }

    /// <summary>
    /// Gets a specific thread by ID
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The thread details</returns>
    public async Task<ConversationThread> GetAsync(string threadId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var response = await _httpClient.GetAsync($"/threads/{threadId}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ConversationThread>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize thread response");
    }

    /// <summary>
    /// Lists threads with optional filtering
    /// </summary>
    /// <param name="updatedSince">Filter by threads updated after this timestamp</param>
    /// <param name="status">Optional status filter</param>
    /// <param name="after">Pagination cursor (thread ID to start after)</param>
    /// <param name="limit">Maximum number of results (default: 100)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of threads</returns>
    public async Task<List<ConversationThread>> ListAsync(
        DateTime? updatedSince = null,
        ThreadStatus? status = null,
        string? after = null,
        int limit = 100,
        CancellationToken cancellationToken = default)
    {
        var queryParams = new List<string>();
        if (updatedSince.HasValue) queryParams.Add($"updatedSince={updatedSince.Value:O}");
        if (status.HasValue) queryParams.Add($"status={status.Value}");
        if (!string.IsNullOrEmpty(after)) queryParams.Add($"after={Uri.EscapeDataString(after)}");
        queryParams.Add($"limit={limit}");

        var query = string.Join("&", queryParams);
        var response = await _httpClient.GetAsync($"/threads?{query}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<List<ConversationThread>>(_jsonOptions, cancellationToken)
            ?? new List<ConversationThread>();
    }

    /// <summary>
    /// Updates thread metadata or status
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="thread">Updated thread data</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated thread</returns>
    public async Task<ConversationThread> UpdateAsync(string threadId, ConversationThread thread, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (thread == null) throw new ArgumentNullException(nameof(thread));

        var response = await _httpClient.PatchAsJsonAsync($"/threads/{threadId}", thread, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ConversationThread>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize thread response");
    }

    /// <summary>
    /// Deletes a thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    public async Task DeleteAsync(string threadId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var response = await _httpClient.DeleteAsync($"/threads/{threadId}", cancellationToken);
        response.EnsureSuccessStatusCode();
    }

    /// <summary>
    /// Marks thread as read
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated thread</returns>
    public async Task<ConversationThread> MarkAsReadAsync(string threadId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var response = await _httpClient.PostAsync($"/threads/{threadId}/read", null, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ConversationThread>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize thread response");
    }

    /// <summary>
    /// Adds a message to a thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="message">Message to add</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created message</returns>
    public async Task<ChatMessage> AddMessageAsync(string threadId, ChatMessage message, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (message == null) throw new ArgumentNullException(nameof(message));

        var response = await _httpClient.PostAsJsonAsync($"/threads/{threadId}/messages", message, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ChatMessage>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize message response");
    }

    /// <summary>
    /// Gets messages from a thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="branch">Optional branch message ID</param>
    /// <param name="after">Pagination cursor (message ID to start after)</param>
    /// <param name="limit">Maximum number of results (default: 100)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of messages</returns>
    public async Task<List<ChatMessage>> GetMessagesAsync(
        string threadId,
        string? branch = null,
        string? after = null,
        int limit = 100,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var queryParams = new List<string>();
        if (!string.IsNullOrEmpty(branch)) queryParams.Add($"branch={Uri.EscapeDataString(branch)}");
        if (!string.IsNullOrEmpty(after)) queryParams.Add($"after={Uri.EscapeDataString(after)}");
        queryParams.Add($"limit={limit}");

        var query = string.Join("&", queryParams);
        var response = await _httpClient.GetAsync($"/threads/{threadId}/messages?{query}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<List<ChatMessage>>(_jsonOptions, cancellationToken)
            ?? new List<ChatMessage>();
    }

    /// <summary>
    /// Gets a specific message by ID
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="messageId">Message identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The message</returns>
    public async Task<ChatMessage> GetMessageAsync(string threadId, string messageId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (string.IsNullOrEmpty(messageId)) throw new ArgumentException("Message ID cannot be null or empty", nameof(messageId));

        var response = await _httpClient.GetAsync($"/threads/{threadId}/messages/{messageId}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ChatMessage>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize message response");
    }

    /// <summary>
    /// Copies a thread to create an independent copy
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="request">Copy request options</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The new thread</returns>
    public async Task<ConversationThread> CopyAsync(string threadId, ThreadCopyRequest? request = null, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var response = await _httpClient.PostAsJsonAsync($"/threads/{threadId}/copy", request ?? new ThreadCopyRequest(), _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ConversationThread>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize thread response");
    }

    /// <summary>
    /// Creates a run within the thread context
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="run">Run configuration</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created run</returns>
    public async Task<Run> CreateRunAsync(string threadId, Run run, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (run == null) throw new ArgumentNullException(nameof(run));

        var response = await _httpClient.PostAsJsonAsync($"/threads/{threadId}/runs", run, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }

    /// <summary>
    /// Lists runs within the thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="status">Optional status filter</param>
    /// <param name="after">Pagination cursor (run ID to start after)</param>
    /// <param name="limit">Maximum number of results (default: 100)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of runs</returns>
    public async Task<List<Run>> ListRunsAsync(
        string threadId,
        RunStatus? status = null,
        string? after = null,
        int limit = 100,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var queryParams = new List<string>();
        if (status.HasValue) queryParams.Add($"status={status.Value}");
        if (!string.IsNullOrEmpty(after)) queryParams.Add($"after={Uri.EscapeDataString(after)}");
        queryParams.Add($"limit={limit}");

        var query = string.Join("&", queryParams);
        var response = await _httpClient.GetAsync($"/threads/{threadId}/runs?{query}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<List<Run>>(_jsonOptions, cancellationToken)
            ?? new List<Run>();
    }

    /// <summary>
    /// Subscribes agent to watch thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="agentId">Agent identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created watch</returns>
    public async Task<ThreadWatch> WatchThreadAsync(string threadId, string agentId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (string.IsNullOrEmpty(agentId)) throw new ArgumentException("Agent ID cannot be null or empty", nameof(agentId));

        var request = new { agentId };
        var response = await _httpClient.PostAsJsonAsync($"/threads/{threadId}/watch", request, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<ThreadWatch>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize watch response");
    }

    /// <summary>
    /// Unsubscribes agent from watching thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="agentId">Agent identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    public async Task UnwatchThreadAsync(string threadId, string agentId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));
        if (string.IsNullOrEmpty(agentId)) throw new ArgumentException("Agent ID cannot be null or empty", nameof(agentId));

        var response = await _httpClient.DeleteAsync($"/threads/{threadId}/watch/{agentId}", cancellationToken);
        response.EnsureSuccessStatusCode();
    }

    /// <summary>
    /// Lists agents watching thread
    /// </summary>
    /// <param name="threadId">Thread identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of thread watches</returns>
    public async Task<List<ThreadWatch>> ListWatchersAsync(string threadId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(threadId)) throw new ArgumentException("Thread ID cannot be null or empty", nameof(threadId));

        var response = await _httpClient.GetAsync($"/threads/{threadId}/watch", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<List<ThreadWatch>>(_jsonOptions, cancellationToken)
            ?? new List<ThreadWatch>();
    }
}
