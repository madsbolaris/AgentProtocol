namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Response from processing a message.
/// </summary>
public class MessageResponse
{
    /// <summary>
    /// The type of response (text, image, etc.).
    /// </summary>
    public string Type { get; set; } = "text";

    /// <summary>
    /// The text content of the response.
    /// </summary>
    public string? Text { get; set; }

    /// <summary>
    /// The thread ID for the conversation.
    /// </summary>
    public string? ThreadId { get; set; }

    /// <summary>
    /// The run ID for this execution.
    /// </summary>
    public string? RunId { get; set; }
}
