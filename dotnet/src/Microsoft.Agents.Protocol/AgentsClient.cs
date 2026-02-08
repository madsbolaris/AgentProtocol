using System;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol.Models.Agents;

namespace Microsoft.Agents.Protocol;

/// <summary>
/// Client for Agents API operations
/// Handles agent discovery, registration, and inspection
/// </summary>
public class AgentsClient
{
    private readonly HttpClient _httpClient;
    private readonly AgentProtocolClientOptions _options;
    private readonly JsonSerializerOptions _jsonOptions;

    internal AgentsClient(HttpClient httpClient, AgentProtocolClientOptions options)
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
    /// Gets agent card (discovery/registration metadata)
    /// </summary>
    /// <param name="agentId">Agent identifier</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>The agent card with capabilities and tools</returns>
    public async Task<AgentCard> GetCardAsync(string agentId, CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrEmpty(agentId)) throw new ArgumentException("Agent ID cannot be null or empty", nameof(agentId));

        var response = await _httpClient.GetAsync($"/agents/{agentId}/card", cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<AgentCard>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize agent card response");
    }

    /// <summary>
    /// Inspects ephemeral agent (capability discovery without persisting)
    /// Useful for validating agent configuration before running
    /// </summary>
    /// <param name="agent">Agent definition to inspect</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Agent card with capabilities (agentId will be null - not persisted)</returns>
    public async Task<AgentCard> InspectAsync(AgentDefinition agent, CancellationToken cancellationToken = default)
    {
        if (agent == null) throw new ArgumentNullException(nameof(agent));

        var request = new { agent };
        var response = await _httpClient.PostAsJsonAsync("/agents/inspect", request, _jsonOptions, cancellationToken);
        response.EnsureSuccessStatusCode();

        return await response.Content.ReadFromJsonAsync<AgentCard>(_jsonOptions, cancellationToken)
            ?? throw new InvalidOperationException("Failed to deserialize agent card response");
    }
}
