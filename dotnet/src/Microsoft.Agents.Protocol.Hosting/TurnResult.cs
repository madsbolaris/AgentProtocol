namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Represents the result of processing a turn in an agent conversation.
/// Provides explicit control flow for message handling.
/// </summary>
public enum TurnResult
{
    /// <summary>
    /// Continue processing - pass to next handler or LLM.
    /// Use this when you want preprocessing but don't want to consume the message.
    /// </summary>
    Continue,

    /// <summary>
    /// Message has been consumed - stop processing, no response needed.
    /// Use this for reactions, typing indicators, or other events that don't need a response.
    /// </summary>
    Consumed,

    /// <summary>
    /// A response has already been sent - stop processing.
    /// Use this when your handler has sent a response via ctx.RespondAsync().
    /// </summary>
    Replied
}
