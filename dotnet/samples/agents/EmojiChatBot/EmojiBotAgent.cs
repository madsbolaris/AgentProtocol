using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Abstractions.Models;
using Microsoft.Agents.Protocol.Sdk;
using Microsoft.Agents.Protocol.Sdk.Attributes;
using Microsoft.Agents.Protocol.Sdk.Core;

namespace EmojiChatBot;

/// <summary>
/// Simple context to track conversation state
/// </summary>
public class ChatContext
{
    public int MessageCount { get; set; }
    public string? LastEmojiUsed { get; set; }
}

/// <summary>
/// Emoji Chat Bot demonstrating:
/// 1. Tool calling with [Tool] attribute
/// 2. System event handling
/// 3. Emoji reaction handling
/// </summary>
public class EmojiBotAgent : AgentProtocolApplication<ChatContext>
{
    public EmojiBotAgent(AgentProtocolOptions options) : base(options)
    {
        // Register event handlers

        // Handle system events (e.g., user joined, user left)
        OnEvent<EventContent>("system.user_joined", HandleUserJoinedAsync);
        OnEvent<EventContent>("system.user_left", HandleUserLeftAsync);

        // Handle emoji reactions
        OnEvent<MessageReactionContent>(HandleEmojiReactionAsync);
    }

    #region Tool Methods (Attribute-Based)

    /// <summary>
    /// Tool that adds an emoji to a message.
    /// The LLM can call this tool when users ask to add reactions or emojis.
    /// </summary>
    [Tool("Add an emoji reaction to a specific message. Use this when the user wants to react to a message with an emoji.")]
    public async Task<AddEmojiResult> AddEmojiToMessage(
        [Description("The ID of the message to add emoji to")] string messageId,
        [Description("The emoji to add (e.g., '👍', '❤️', '😊')")] string emoji)
    {
        // In a real implementation, this would call an API to add the reaction
        // For this demo, we'll just return a success message

        return new AddEmojiResult
        {
            Success = true,
            MessageId = messageId,
            Emoji = emoji,
            Message = $"Added {emoji} reaction to message {messageId}"
        };
    }

    /// <summary>
    /// Tool that suggests emojis based on message sentiment.
    /// </summary>
    [Tool("Suggest appropriate emojis based on the sentiment or content of a message.")]
    public async Task<EmojiSuggestion> SuggestEmoji(
        [Description("The message text to analyze")] string messageText)
    {
        // Simple sentiment-based emoji suggestion
        var lowerText = messageText.ToLower();
        var suggestedEmojis = new System.Collections.Generic.List<string>();

        if (lowerText.Contains("happy") || lowerText.Contains("great") || lowerText.Contains("awesome"))
        {
            suggestedEmojis.AddRange(new[] { "😊", "🎉", "👍" });
        }
        else if (lowerText.Contains("sad") || lowerText.Contains("sorry"))
        {
            suggestedEmojis.AddRange(new[] { "😢", "💔", "🤗" });
        }
        else if (lowerText.Contains("love"))
        {
            suggestedEmojis.AddRange(new[] { "❤️", "💕", "😍" });
        }
        else if (lowerText.Contains("thank"))
        {
            suggestedEmojis.AddRange(new[] { "🙏", "😊", "👍" });
        }
        else
        {
            suggestedEmojis.AddRange(new[] { "👍", "😊", "✨" });
        }

        return new EmojiSuggestion
        {
            MessageText = messageText,
            SuggestedEmojis = suggestedEmojis.ToArray()
        };
    }

    #endregion

    #region Event Handlers

    /// <summary>
    /// Handle system event: user joined the conversation.
    /// This augments the LLM with knowledge about system events it wasn't trained on.
    /// </summary>
    private async Task HandleUserJoinedAsync(
        IMessageContext<ChatContext> context,
        AIContent eventContent,
        CancellationToken cancellationToken)
    {
        // Extract user info from event
        var eventData = (EventContent)eventContent;
        var userName = eventData.Name ?? "Someone";

        // Send welcome message
        await context.SendTextAsync(
            $"👋 Welcome {userName}! I'm an emoji bot. I can help you add emojis to messages and react with emojis!",
            cancellationToken);
    }

    /// <summary>
    /// Handle system event: user left the conversation.
    /// </summary>
    private async Task HandleUserLeftAsync(
        IMessageContext<ChatContext> context,
        AIContent eventContent,
        CancellationToken cancellationToken)
    {
        var eventData = (EventContent)eventContent;
        var userName = eventData.Name ?? "Someone";

        // Log the departure (in real app, might update context or send notification)
        Console.WriteLine($"User {userName} left the conversation");
    }

    /// <summary>
    /// Handle incoming emoji reactions.
    /// This teaches the LLM about emoji reactions, which are domain-specific events.
    /// </summary>
    private async Task HandleEmojiReactionAsync(
        IMessageContext<ChatContext> context,
        AIContent eventContent,
        CancellationToken cancellationToken)
    {
        var reaction = (MessageReactionContent)eventContent;

        // Update context to remember the last emoji
        context.Context.LastEmojiUsed = reaction.Reaction?.Activity ?? "unknown";

        // Count popular reactions and respond
        var emoji = reaction.Reaction?.Activity ?? "?";
        var reactionType = reaction.Reaction?.Type ?? "added";

        if (reactionType == "added")
        {
            await context.SendTextAsync(
                $"I see you reacted with {emoji}! That's a great choice! 😊",
                cancellationToken);
        }
        else if (reactionType == "removed")
        {
            await context.SendTextAsync(
                $"You removed the {emoji} reaction. No problem!",
                cancellationToken);
        }
    }

    #endregion

    #region Custom Context Creation

    /// <summary>
    /// Create custom context for each conversation run.
    /// </summary>
    public override Task<ChatContext> CreateContextAsync(
        string runId,
        string threadId,
        CancellationToken cancellationToken = default)
    {
        return Task.FromResult(new ChatContext
        {
            MessageCount = 0,
            LastEmojiUsed = null
        });
    }

    #endregion
}

#region Result Types

/// <summary>
/// Result returned by AddEmojiToMessage tool.
/// </summary>
public class AddEmojiResult
{
    public bool Success { get; set; }
    public string MessageId { get; set; } = string.Empty;
    public string Emoji { get; set; } = string.Empty;
    public string Message { get; set; } = string.Empty;
}

/// <summary>
/// Result returned by SuggestEmoji tool.
/// </summary>
public class EmojiSuggestion
{
    public string MessageText { get; set; } = string.Empty;
    public string[] SuggestedEmojis { get; set; } = Array.Empty<string>();
}

#endregion
