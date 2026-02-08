using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol.Models.Execution;

namespace Microsoft.Agents.Protocol;

/// <summary>
/// Client for Runs API operations
/// Handles creating and managing agent execution instances
/// </summary>
public class RunsClient
{
    private readonly HttpClient _httpClient;
    private readonly AgentProtocolClientOptions _options;
    private readonly JsonSerializerOptions _jsonOptions;

    internal RunsClient(HttpClient httpClient, AgentProtocolClientOptions options)
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
    /// Creates and executes an agent run
    /// </summary>
    /// <param name="run">Run configuration with input messages and agent settings</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The created run with status and output</returns>
    public async Task<Run> CreateAsync(Run run, CancellationToken cancellationToken = default)
    {
        if (run == null) throw new ArgumentNullException(nameof(run));

        var response = await _httpClient.PostAsJsonAsync("/runs", run, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }

    /// <summary>
    /// Creates an ephemeral run and waits for completion (blocking)
    /// </summary>
    /// <param name="run">Run configuration</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The completed run response</returns>
    public async Task<RunWaitResponse> CreateAndWaitAsync(Run run, CancellationToken cancellationToken = default)
    {
        if (run == null) throw new ArgumentNullException(nameof(run));

        var response = await _httpClient.PostAsJsonAsync("/runs/wait", run, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<RunWaitResponse>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run wait response");
    }

    /// <summary>
    /// Gets a specific run by ID
    /// </summary>
    /// <param name="runId">Run identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The run details</returns>
    public async Task<Run> GetAsync(string runId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(runId)) throw new ArgumentException("Run ID cannot be null or empty", nameof(runId));

        var response = await _httpClient.GetAsync($"/runs/{runId}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }

    /// <summary>
    /// Waits for an existing run to complete
    /// </summary>
    /// <param name="runId">Run identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The completed run response</returns>
    public async Task<RunWaitResponse> WaitAsync(string runId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(runId)) throw new ArgumentException("Run ID cannot be null or empty", nameof(runId));

        var response = await _httpClient.GetAsync($"/runs/{runId}/wait", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<RunWaitResponse>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run wait response");
    }

    /// <summary>
    /// Lists runs with optional filtering
    /// </summary>
    /// <param name="threadId">Optional thread ID filter</param>
    /// <param name="agentId">Optional agent ID filter</param>
    /// <param name="status">Optional status filter</param>
    /// <param name="after">Pagination cursor (run ID to start after)</param>
    /// <param name="limit">Maximum number of results (default: 100)</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>List of runs</returns>
    public async Task<List<Run>> ListAsync(
        string? threadId = null,
        string? agentId = null,
        RunStatus? status = null,
        string? after = null,
        int limit = 100,
        CancellationToken cancellationToken = default)
    {
        var queryParams = new List<string>();
        if (!string.IsNullOrEmpty(threadId)) queryParams.Add($"threadId={Uri.EscapeDataString(threadId)}");
        if (!string.IsNullOrEmpty(agentId)) queryParams.Add($"agentId={Uri.EscapeDataString(agentId)}");
        if (status.HasValue) queryParams.Add($"status={status.Value}");
        if (!string.IsNullOrEmpty(after)) queryParams.Add($"after={Uri.EscapeDataString(after)}");
        queryParams.Add($"limit={limit}");

        var query = string.Join("&", queryParams);
        var response = await _httpClient.GetAsync($"/runs?{query}", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<List<Run>>(_jsonOptions, cancellationToken)
            ?? new List<Run>();
    }

    /// <summary>
    /// Cancels a running execution
    /// </summary>
    /// <param name="runId">Run identifier</param>
    /// <param name="action">Cancel action (interrupt or rollback)</param>
    /// <param name="reason">Optional cancellation reason</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated run</returns>
    public async Task<Run> CancelAsync(
        string runId,
        CancelAction action = CancelAction.Interrupt,
        string? reason = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(runId)) throw new ArgumentException("Run ID cannot be null or empty", nameof(runId));

        var request = new { action, reason };
        var response = await _httpClient.PostAsJsonAsync($"/runs/{runId}/cancel", request, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }

    /// <summary>
    /// Submits tool execution results to continue run
    /// </summary>
    /// <param name="runId">Run identifier</param>
    /// <param name="toolOutputs">Tool execution results</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated run</returns>
    public async Task<Run> SubmitToolOutputsAsync(
        string runId,
        List<ToolOutput> toolOutputs,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(runId)) throw new ArgumentException("Run ID cannot be null or empty", nameof(runId));
        if (toolOutputs == null) throw new ArgumentNullException(nameof(toolOutputs));

        var request = new { tool_outputs = toolOutputs };
        var response = await _httpClient.PostAsJsonAsync($"/runs/{runId}/submit_tool_outputs", request, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }

    /// <summary>
    /// Submits user input to continue run
    /// </summary>
    /// <param name="runId">Run identifier</param>
    /// <param name="value">User input value</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated run</returns>
    public async Task<Run> SubmitInputAsync(
        string runId,
        string value,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(runId)) throw new ArgumentException("Run ID cannot be null or empty", nameof(runId));
        if (value == null) throw new ArgumentNullException(nameof(value));

        var request = new { value };
        var response = await _httpClient.PostAsJsonAsync($"/runs/{runId}/submit_input", request, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }

    /// <summary>
    /// Submits authentication credentials to continue run
    /// </summary>
    /// <param name="runId">Run identifier</param>
    /// <param name="token">Authentication token</param>
    /// <param name="tokenType">Token type (e.g., "Bearer")</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The updated run</returns>
    public async Task<Run> SubmitAuthAsync(
        string runId,
        string token,
        string? tokenType = "Bearer",
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(runId)) throw new ArgumentException("Run ID cannot be null or empty", nameof(runId));
        if (token == null) throw new ArgumentNullException(nameof(token));

        var request = new { token, tokenType };
        var response = await _httpClient.PostAsJsonAsync($"/runs/{runId}/submit_auth", request, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<Run>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize run response");
    }
}
