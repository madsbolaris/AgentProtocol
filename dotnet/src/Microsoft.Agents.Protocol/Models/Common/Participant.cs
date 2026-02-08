using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Protocol.Models.Common;

/// <summary>
/// Participant - User or Agent in a Conversation
/// Unified model for conversation participants
/// </summary>
public class Participant
{
    /// <summary>
    /// Participant identifier
    /// For users: Entra User ID (Object ID)
    /// For agents: Agent ID (Service Principal Object ID)
    /// For system: "system"
    /// </summary>
    [JsonPropertyName("id")]
    public required string Id { get; set; }

    /// <summary>
    /// Participant type
    /// </summary>
    [JsonPropertyName("kind")]
    public required string Kind { get; set; } // "user", "agent", "system"

    /// <summary>
    /// Display name
    /// </summary>
    [JsonPropertyName("name")]
    public string? Name { get; set; }

    /// <summary>
    /// Role in the conversation (e.g., "user", "assistant", "system")
    /// </summary>
    [JsonPropertyName("role")]
    public string? Role { get; set; }

    /// <summary>
    /// Participant metadata (avatar URL, status, preferences, etc.)
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}
