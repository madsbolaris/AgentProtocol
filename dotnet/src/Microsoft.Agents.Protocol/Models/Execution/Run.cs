using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;
using Microsoft.Agents.Protocol.Models.Agents;
using Microsoft.Agents.Protocol.Models.Messages;

namespace Microsoft.Agents.Protocol.Models.Execution;

/// <summary>
/// Run - Execution Instance
/// Represents a single agent invocation within a conversation
/// </summary>
public class Run
{
    /// <summary>
    /// Unique identifier for this run
    /// </summary>
    [JsonPropertyName("runId")]
    public string? RunId { get; set; }

    /// <summary>
    /// Agent identifier
    /// </summary>
    [JsonPropertyName("agentId")]
    public required string AgentId { get; set; }

    /// <summary>
    /// Optional thread identifier for stateful execution
    /// </summary>
    [JsonPropertyName("threadId")]
    public string? ThreadId { get; set; }

    /// <summary>
    /// Optional journal identifier for cross-conversation memory
    /// </summary>
    [JsonPropertyName("journalId")]
    public string? JournalId { get; set; }

    /// <summary>
    /// Current lifecycle status
    /// </summary>
    [JsonPropertyName("status")]
    public RunStatus? Status { get; set; }

    /// <summary>
    /// Input messages that started this run
    /// </summary>
    [JsonPropertyName("input")]
    public required List<ChatMessage> Input { get; set; }

    /// <summary>
    /// Optional inline agent definition (for ephemeral/stateless execution)
    /// </summary>
    [JsonPropertyName("agent")]
    public AgentDefinition? Agent { get; set; }

    /// <summary>
    /// Messages generated during this run
    /// </summary>
    [JsonPropertyName("output")]
    public List<ChatMessage>? Output { get; set; }

    /// <summary>
    /// Token usage statistics
    /// </summary>
    [JsonPropertyName("usage")]
    public CompletionUsage? Usage { get; set; }

    /// <summary>
    /// Timestamp when run was created
    /// </summary>
    [JsonPropertyName("createdAt")]
    public DateTime? CreatedAt { get; set; }

    /// <summary>
    /// Timestamp of last status update
    /// </summary>
    [JsonPropertyName("updatedAt")]
    public DateTime? UpdatedAt { get; set; }

    /// <summary>
    /// Timestamp when run finished
    /// </summary>
    [JsonPropertyName("completedAt")]
    public DateTime? CompletedAt { get; set; }

    /// <summary>
    /// Timestamp when run was cancelled
    /// </summary>
    [JsonPropertyName("cancelledAt")]
    public DateTime? CancelledAt { get; set; }

    /// <summary>
    /// Reason for cancellation
    /// </summary>
    [JsonPropertyName("cancellationReason")]
    public string? CancellationReason { get; set; }

    /// <summary>
    /// Error details if run failed
    /// </summary>
    [JsonPropertyName("error")]
    public RunError? Error { get; set; }

    /// <summary>
    /// User who initiated this run
    /// </summary>
    [JsonPropertyName("userId")]
    public string? UserId { get; set; }

    /// <summary>
    /// Thread cleanup strategy
    /// </summary>
    [JsonPropertyName("threadCleanup")]
    public ThreadCleanup? ThreadCleanup { get; set; }

    /// <summary>
    /// Webhook URL for completion notification
    /// </summary>
    [JsonPropertyName("webhook")]
    public string? Webhook { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// Run Status Enum
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum RunStatus
{
    /// <summary>Run is queued and waiting to start</summary>
    Queued,
    /// <summary>Run is currently executing</summary>
    InProgress,
    /// <summary>Run is waiting for tool execution results</summary>
    RequiresAction,
    /// <summary>Run is waiting for human input</summary>
    InputRequired,
    /// <summary>Run is waiting for authentication</summary>
    AuthRequired,
    /// <summary>User requested cancellation, run is stopping</summary>
    Cancelling,
    /// <summary>Run was cancelled by user</summary>
    Cancelled,
    /// <summary>Run encountered an error</summary>
    Failed,
    /// <summary>Run finished successfully</summary>
    Completed,
    /// <summary>Run stopped before completion</summary>
    Incomplete,
    /// <summary>Run exceeded time limit</summary>
    Timeout
}

/// <summary>
/// Thread Cleanup Strategy
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum ThreadCleanup
{
    /// <summary>Keep thread after run completes</summary>
    Keep,
    /// <summary>Delete thread after run completes</summary>
    Delete
}

/// <summary>
/// Cancel Action
/// </summary>
[JsonConverter(typeof(JsonStringEnumConverter))]
public enum CancelAction
{
    /// <summary>Stop run but preserve state and history</summary>
    Interrupt,
    /// <summary>Stop run and delete run record + messages</summary>
    Rollback
}

/// <summary>
/// Run Error - Error details for failed runs
/// </summary>
public class RunError
{
    /// <summary>
    /// Machine-readable error code
    /// </summary>
    [JsonPropertyName("code")]
    public required string Code { get; set; }

    /// <summary>
    /// Human-readable error message
    /// </summary>
    [JsonPropertyName("message")]
    public required string Message { get; set; }

    /// <summary>
    /// Optional additional error details
    /// </summary>
    [JsonPropertyName("details")]
    public Dictionary<string, object>? Details { get; set; }
}

/// <summary>
/// Completion Usage - Token usage statistics
/// </summary>
public class CompletionUsage
{
    /// <summary>
    /// Input tokens consumed
    /// </summary>
    [JsonPropertyName("inputTokens")]
    public int? InputTokens { get; set; }

    /// <summary>
    /// Output tokens generated
    /// </summary>
    [JsonPropertyName("outputTokens")]
    public int? OutputTokens { get; set; }

    /// <summary>
    /// Total tokens used
    /// </summary>
    [JsonPropertyName("totalTokens")]
    public int? TotalTokens { get; set; }
}

/// <summary>
/// Run Wait Response - Response from wait endpoints
/// </summary>
public class RunWaitResponse
{
    /// <summary>
    /// Run identifier
    /// </summary>
    [JsonPropertyName("runId")]
    public required string RunId { get; set; }

    /// <summary>
    /// Agent identifier (if provided)
    /// </summary>
    [JsonPropertyName("agentId")]
    public string? AgentId { get; set; }

    /// <summary>
    /// Thread ID if run was stateful
    /// </summary>
    [JsonPropertyName("threadId")]
    public string? ThreadId { get; set; }

    /// <summary>
    /// Final run status
    /// </summary>
    [JsonPropertyName("status")]
    public required RunStatus Status { get; set; }

    /// <summary>
    /// Input messages (if provided)
    /// </summary>
    [JsonPropertyName("input")]
    public List<ChatMessage>? Input { get; set; }

    /// <summary>
    /// Messages generated during the run
    /// </summary>
    [JsonPropertyName("output")]
    public required List<ChatMessage> Output { get; set; }

    /// <summary>
    /// Token usage statistics
    /// </summary>
    [JsonPropertyName("usage")]
    public CompletionUsage? Usage { get; set; }

    /// <summary>
    /// Error details if run failed
    /// </summary>
    [JsonPropertyName("error")]
    public RunError? Error { get; set; }

    /// <summary>
    /// Timestamp when run was created
    /// </summary>
    [JsonPropertyName("createdAt")]
    public required DateTime CreatedAt { get; set; }

    /// <summary>
    /// Timestamp when run finished
    /// </summary>
    [JsonPropertyName("completedAt")]
    public DateTime? CompletedAt { get; set; }
}

/// <summary>
/// Tool Output - Result from tool execution
/// </summary>
public class ToolOutput
{
    /// <summary>
    /// Tool call ID this output corresponds to
    /// </summary>
    [JsonPropertyName("tool_call_id")]
    public required string ToolCallId { get; set; }

    /// <summary>
    /// Tool execution result
    /// </summary>
    [JsonPropertyName("output")]
    public required string Output { get; set; }
}
