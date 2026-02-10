using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Represents a reaction (emoji, like, etc.) from a user.
/// </summary>
public class ReactionContent : AIContent
{
    /// <summary>
    /// Gets or sets the emoji or reaction identifier.
    /// </summary>
    public string? Emoji { get; set; }

    /// <summary>
    /// Gets or sets the message ID this reaction is for.
    /// </summary>
    public string? MessageId { get; set; }

    public override string Kind => "reaction";
}
