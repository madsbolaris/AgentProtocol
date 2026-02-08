using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Protocol.Models.Messages;

/// <summary>
/// Chat Message - Represents a single message in a conversation
/// </summary>
public class ChatMessage
{
    /// <summary>
    /// Unique message identifier
    /// </summary>
    [JsonPropertyName("messageId")]
    public string? MessageId { get; set; }

    /// <summary>
    /// Message role (user, assistant, tool, channel, system)
    /// </summary>
    [JsonPropertyName("role")]
    public required string Role { get; set; }

    /// <summary>
    /// Message contents (text, images, tool calls, etc.)
    /// </summary>
    [JsonPropertyName("contents")]
    public required List<Content> Contents { get; set; }

    /// <summary>
    /// User ID who sent this message (for role=user)
    /// </summary>
    [JsonPropertyName("userId")]
    public string? UserId { get; set; }

    /// <summary>
    /// Agent ID that generated this message (for role=assistant)
    /// </summary>
    [JsonPropertyName("agentId")]
    public string? AgentId { get; set; }

    /// <summary>
    /// Author's display name
    /// </summary>
    [JsonPropertyName("authorName")]
    public string? AuthorName { get; set; }

    /// <summary>
    /// Thread ID this message belongs to
    /// </summary>
    [JsonPropertyName("threadId")]
    public string? ThreadId { get; set; }

    /// <summary>
    /// Run ID that created this message
    /// </summary>
    [JsonPropertyName("runId")]
    public string? RunId { get; set; }

    /// <summary>
    /// Parent message ID (for branching conversations)
    /// </summary>
    [JsonPropertyName("parentId")]
    public string? ParentId { get; set; }

    /// <summary>
    /// Timestamp when message was created
    /// </summary>
    [JsonPropertyName("createdAt")]
    public DateTime? CreatedAt { get; set; }

    /// <summary>
    /// Timestamp when message was last updated
    /// </summary>
    [JsonPropertyName("updatedAt")]
    public DateTime? UpdatedAt { get; set; }

    /// <summary>
    /// Message status (pending, streaming, completed, error)
    /// </summary>
    [JsonPropertyName("status")]
    public string? Status { get; set; }

    /// <summary>
    /// Custom metadata
    /// </summary>
    [JsonPropertyName("metadata")]
    public Dictionary<string, object>? Metadata { get; set; }
}

/// <summary>
/// Content - Base class for message content types
/// </summary>
[JsonPolymorphic(TypeDiscriminatorPropertyName = "kind")]
[JsonDerivedType(typeof(TextContent), "text")]
[JsonDerivedType(typeof(ImageContent), "image")]
[JsonDerivedType(typeof(FunctionCallContent), "functionCall")]
[JsonDerivedType(typeof(FunctionResultContent), "functionResult")]
public abstract class Content
{
    /// <summary>
    /// Audience annotation (who can see this content: "user", "assistant")
    /// </summary>
    [JsonPropertyName("audience")]
    public string? Audience { get; set; }
}

/// <summary>
/// Text Content - Plain text or markdown content
/// </summary>
public class TextContent : Content
{
    /// <summary>
    /// The text content
    /// </summary>
    [JsonPropertyName("text")]
    public required string Text { get; set; }
}

/// <summary>
/// Image Content - Image data or URL
/// </summary>
public class ImageContent : Content
{
    /// <summary>
    /// Image URL or data URI
    /// </summary>
    [JsonPropertyName("url")]
    public required string Url { get; set; }

    /// <summary>
    /// Image detail level (low, high, auto)
    /// </summary>
    [JsonPropertyName("detail")]
    public string? Detail { get; set; }
}

/// <summary>
/// Function Call Content - AI-generated tool call
/// </summary>
public class FunctionCallContent : Content
{
    /// <summary>
    /// Unique call identifier
    /// </summary>
    [JsonPropertyName("callId")]
    public required string CallId { get; set; }

    /// <summary>
    /// Function name
    /// </summary>
    [JsonPropertyName("name")]
    public required string Name { get; set; }

    /// <summary>
    /// Function arguments (JSON string)
    /// </summary>
    [JsonPropertyName("arguments")]
    public required string Arguments { get; set; }
}

/// <summary>
/// Function Result Content - Tool execution result
/// </summary>
public class FunctionResultContent : Content
{
    /// <summary>
    /// Call ID this result corresponds to
    /// </summary>
    [JsonPropertyName("callId")]
    public required string CallId { get; set; }

    /// <summary>
    /// Function name
    /// </summary>
    [JsonPropertyName("name")]
    public required string Name { get; set; }

    /// <summary>
    /// Execution result (string or JSON)
    /// </summary>
    [JsonPropertyName("result")]
    public required string Result { get; set; }

    /// <summary>
    /// Whether the call failed
    /// </summary>
    [JsonPropertyName("isError")]
    public bool? IsError { get; set; }
}
