// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using Microsoft.Agents.Builder;
using Microsoft.Agents.Builder.App;
using Microsoft.Agents.Builder.State;
using Microsoft.Agents.Core.Models;
using System;
using System.Linq;
using System.Threading.Tasks;
using System.Threading;

namespace EmojiChatBot;

/// <summary>
/// Emoji Chat Bot demonstrating:
/// 1. Message handling with emoji responses
/// 2. Conversation member events (welcome messages)
/// 3. Emoji reaction suggestions
/// </summary>
public class EmojiBotAgent : AgentApplication
{
    public EmojiBotAgent(AgentApplicationOptions options) : base(options)
    {
        // Handle when new members are added to the conversation
        OnConversationUpdate(ConversationUpdateEvents.MembersAdded, WelcomeMessageAsync);

        // Handle regular messages with emoji responses
        OnActivity(ActivityTypes.Message, OnMessageAsync, rank: RouteRank.Last);
    }

    /// <summary>
    /// Send welcome message when user joins
    /// </summary>
    private async Task WelcomeMessageAsync(ITurnContext turnContext, ITurnState turnState, CancellationToken cancellationToken)
    {
        foreach (ChannelAccount member in turnContext.Activity.MembersAdded)
        {
            if (member.Id != turnContext.Activity.Recipient.Id)
            {
                await turnContext.SendActivityAsync(
                    MessageFactory.Text("👋 Welcome! I'm an emoji bot. I'll respond to your messages with fun emoji suggestions!"),
                    cancellationToken);
            }
        }
    }

    /// <summary>
    /// Handle user messages and respond with emoji-enhanced replies
    /// </summary>
    private async Task OnMessageAsync(ITurnContext turnContext, ITurnState turnState, CancellationToken cancellationToken)
    {
        // Extract role from Activity.Properties (default to "user" if not present)
        var role = "user";
        if (turnContext.Activity.Properties != null &&
            turnContext.Activity.Properties.TryGetValue("agentProtocol.role", out var roleValue))
        {
            // Properties stores JsonElement, so get string value
            if (roleValue is System.Text.Json.JsonElement jsonElement &&
                jsonElement.ValueKind == System.Text.Json.JsonValueKind.String)
            {
                role = jsonElement.GetString() ?? "user";
            }
        }

        // Only respond to user messages
        if (role != "user")
        {
            return;
        }

        var userMessage = turnContext.Activity.Text ?? "";
        var lowerMessage = userMessage.ToLower();

        // Analyze message sentiment and suggest emojis
        string emoji;
        string response;

        if (lowerMessage.Contains("happy") || lowerMessage.Contains("great") || lowerMessage.Contains("awesome") || lowerMessage.Contains("wonderful"))
        {
            emoji = "😊🎉";
            response = $"You said: {userMessage}\n\nThat sounds great! {emoji} Here are some happy emojis: 😊 🎉 👍 ✨";
        }
        else if (lowerMessage.Contains("sad") || lowerMessage.Contains("sorry") || lowerMessage.Contains("bad"))
        {
            emoji = "🤗💙";
            response = $"You said: {userMessage}\n\nI hope things get better! {emoji} Some comforting emojis: 🤗 💙 😢 🌟";
        }
        else if (lowerMessage.Contains("love") || lowerMessage.Contains("heart"))
        {
            emoji = "❤️💕";
            response = $"You said: {userMessage}\n\nLove is in the air! {emoji} Some loving emojis: ❤️ 💕 😍 💖";
        }
        else if (lowerMessage.Contains("thank"))
        {
            emoji = "🙏";
            response = $"You said: {userMessage}\n\nYou're welcome! {emoji} Some grateful emojis: 🙏 😊 👍 ✨";
        }
        else if (lowerMessage.Contains("hello") || lowerMessage.Contains("hi"))
        {
            emoji = "👋";
            response = $"{emoji} Hello! You said: {userMessage}\n\nGreeting emojis: 👋 😊 👍 ✨";
        }
        else if (lowerMessage.Contains("emoji"))
        {
            emoji = "😀";
            response = $"You mentioned emojis! {emoji}\n\nHere are some popular ones: 😀 😊 👍 ❤️ 🎉 ✨ 🔥 💯";
        }
        else
        {
            emoji = "✨";
            response = $"You said: {userMessage}\n\n{emoji} Some general emojis: 👍 😊 ✨ 🌟";
        }

        await turnContext.SendActivityAsync(response, cancellationToken: cancellationToken);
    }
}
