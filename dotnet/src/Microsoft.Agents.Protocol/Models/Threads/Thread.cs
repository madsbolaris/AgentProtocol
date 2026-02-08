using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;
using Microsoft.Agents.Protocol.Models.Common;

namespace Microsoft.Agents.Protocol.Models.Threads;

/// <summary>
/// Thread - Conversation Thread
/// Represents a conversation with participants and messages
/// </summary>
public class Thread
{
    /// <summary>
    /// Unique thread identifier
    /// </summary>
    [JsonPropertyName("threadId")]
    public string? ThreadId { get; set; }

    /// <summary>
    /// Thread title or subject
    /// </summary>
    [JsonPropertyName("title")]
    public string? Title { get; set; }

    /// <summary>
    /// Thread description
    /// </summary>
    [JsonPropertyName("description")]
    public string? Description { get; set; }

    /// <summary>
    /// Participants in this thread
    /// </summary>
    [JsonPropertyName("participants")]
    public List<Participant>? Participants { get; set; }

    /// <summary>
    /// Thread status
    /// </summary>
    [JsonPropertyName("status")]
    public ThreadStatus? Status { get; set; }

    /// <summary>
    /// Number of unread messages
    /// </summary>
    [JsonPropertyName("unreadCount")]
    public int? UnreadCount { get; set; }

    /// <summary>
    /// Timestamp when thread was created
    /// </summary>
    [JsonPropertyName("createdAt")]
    public DateTime? CreatedAt { get; set; }

    /// <summary>
    /// Timestamp when thread was last updated
    /// </summary>
    [JsonPropertyName("updatedAt")]
    public DateTime? UpdatedAt { get; set; }

    /// <summary>
    /// Timestamp of last activity
    /// </summary>
    [JsonPropertyName("lastActivityAt")]
    public DateTime? LastActivityAt { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// Thread Status Enum
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum ThreadStatus
{
    /// <summary>Thread is active</summary>
    Active,
    /// <summary>Thread is archived</summary>
    Archived,
    /// <summary>Thread is closed</summary>
    Closed,
    /// <summary>Thread is deleted</summary>
    Deleted
}

/// <summary>
/// Thread Copy Request - Request to copy a thread
/// </summary>
public class ThreadCopyRequest
{
    /// <summary>
    /// Optional title for the new thread
    /// </summary>
    [JsonPropertyName("title")]
    public string? Title { get; set; }

    /// <summary>
    /// Whether to include participants
    /// </summary>
    [JsonPropertyName("includeParticipants")]
    public bool? IncludeParticipants { get; set; }

    /// <summary>
    /// Whether to include messages
    /// </summary>
    [JsonPropertyName("includeMessages")]
    public bool? IncludeMessages { get; set; }
}

/// <summary>
/// Thread Watch - Agent subscription to watch thread
/// </summary>
public class ThreadWatch
{
    /// <summary>
    /// Unique watch identifier
    /// </summary>
    [JsonPropertyName("watchId")]
    public string? WatchId { get; set; }

    /// <summary>
    /// Thread being watched
    /// </summary>
    [JsonPropertyName("threadId")]
    public required string ThreadId { get; set; }

    /// <summary>
    /// Agent watching the thread
    /// </summary>
    [JsonPropertyName("agentId")]
    public required string AgentId { get; set; }

    /// <summary>
    /// Whether watch is active
    /// </summary>
    [JsonPropertyName("active")]
    public bool? Active { get; set; }

    /// <summary>
    /// Timestamp when watch was created
    /// </summary>
    [JsonPropertyName("createdAt")]
    public DateTime? CreatedAt { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}
