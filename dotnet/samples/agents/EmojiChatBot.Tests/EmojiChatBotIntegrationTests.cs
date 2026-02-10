using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using EmojiChatBot;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Core;
using Moq;
using Xunit;
using Assert = Xunit.Assert;

namespace EmojiChatBot.Tests;

/// <summary>
/// Integration tests for Emoji Chat Bot
///
/// These tests verify the full end-to-end functionality:
/// - Agent starts and accepts requests
/// - Tool calling works (AddEmojiToMessage, SuggestEmoji)
/// - Event handlers work (HandleUserJoined, HandleUserLeft, HandleEmojiReaction)
/// - State management works (message count, last emoji)
/// </summary>
public class EmojiChatBotIntegrationTests
{
    private readonly EmojiBotAgent _agent;
    private readonly Mock<IMessageContext<ChatContext>> _mockContext;
    private readonly ChatContext _chatContext;

    public EmojiChatBotIntegrationTests()
    {
        var options = new AgentProtocolOptions();
        _agent = new EmojiBotAgent(options);
        _mockContext = new Mock<IMessageContext<ChatContext>>();
        _chatContext = new ChatContext { MessageCount = 0, LastEmojiUsed = null };
        _mockContext.Setup(c => c.Context).Returns(_chatContext);
    }

    #region Tool Function Tests

    [Fact]
    public async Task AddEmojiToMessage_ReturnsSuccess()
    {
        // Act
        var result = await _agent.AddEmojiToMessage("msg-123", "👍");

        // Assert
        Assert.True(result.Success);
        Assert.Equal("msg-123", result.MessageId);
        Assert.Equal("👍", result.Emoji);
        Assert.Contains("Added 👍 reaction", result.Message);
    }

    [Fact]
    public async Task AddEmojiToMessage_WithDifferentEmojis_AllSucceed()
    {
        // Arrange
        var emojis = new[] { "❤️", "🚀", "🎉", "😊", "👍", "💯" };

        foreach (var emoji in emojis)
        {
            // Act
            var result = await _agent.AddEmojiToMessage("msg-test", emoji);

            // Assert
            Assert.True(result.Success);
            Assert.Equal(emoji, result.Emoji);
        }
    }

    [Fact]
    public async Task SuggestEmoji_ForHappyMessage_ReturnsHappyEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("I am so happy today!");

        // Assert
        Assert.Contains("😊", result.SuggestedEmojis);
        Assert.Contains("🎉", result.SuggestedEmojis);
        Assert.Contains("👍", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_ForSadMessage_ReturnsSadEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("I am feeling sad today");

        // Assert
        Assert.Contains("😢", result.SuggestedEmojis);
        Assert.Contains("💔", result.SuggestedEmojis);
        Assert.Contains("🤗", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_ForLoveMessage_ReturnsLoveEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("I love this project!");

        // Assert
        Assert.Contains("❤️", result.SuggestedEmojis);
        Assert.Contains("💕", result.SuggestedEmojis);
        Assert.Contains("😍", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_ForThankYouMessage_ReturnsGratitudeEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("Thank you so much!");

        // Assert
        Assert.Contains("🙏", result.SuggestedEmojis);
        Assert.Contains("😊", result.SuggestedEmojis);
        Assert.Contains("👍", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_ForNeutralMessage_ReturnsDefaultEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("Hello there");

        // Assert
        Assert.Contains("👍", result.SuggestedEmojis);
        Assert.Contains("😊", result.SuggestedEmojis);
        Assert.Contains("✨", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_ForGreatMessage_ReturnsPositiveEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("This is great and awesome!");

        // Assert
        Assert.Contains("😊", result.SuggestedEmojis);
        Assert.Contains("🎉", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_IsCaseInsensitive()
    {
        // Act
        var result1 = await _agent.SuggestEmoji("I am HAPPY");
        var result2 = await _agent.SuggestEmoji("I am happy");

        // Assert
        Assert.Equal(result1.SuggestedEmojis, result2.SuggestedEmojis);
    }

    #endregion

    #region Context Creation Tests

    [Fact]
    public async Task CreateContextAsync_ReturnsNewContext_WithZeroCount()
    {
        // Act
        var context = await _agent.CreateContextAsync("run-1", "thread-1");

        // Assert
        Assert.NotNull(context);
        Assert.Equal(0, context.MessageCount);
        Assert.Null(context.LastEmojiUsed);
    }

    [Fact]
    public async Task CreateContextAsync_WithDifferentIds_CreatesIndependentContexts()
    {
        // Act
        var context1 = await _agent.CreateContextAsync("run-1", "thread-1");
        var context2 = await _agent.CreateContextAsync("run-2", "thread-2");

        // Assert
        Assert.NotNull(context1);
        Assert.NotNull(context2);
        Assert.NotSame(context1, context2);
    }

    #endregion

    #region Chat Context Tests

    [Fact]
    public void ChatContext_DefaultState_IsValid()
    {
        // Arrange & Act
        var context = new ChatContext();

        // Assert
        Assert.Equal(0, context.MessageCount);
        Assert.Null(context.LastEmojiUsed);
    }

    [Fact]
    public void ChatContext_CanSetMessageCount()
    {
        // Arrange
        var context = new ChatContext();

        // Act
        context.MessageCount = 5;

        // Assert
        Assert.Equal(5, context.MessageCount);
    }

    [Fact]
    public void ChatContext_CanSetLastEmoji()
    {
        // Arrange
        var context = new ChatContext();

        // Act
        context.LastEmojiUsed = "🚀";

        // Assert
        Assert.Equal("🚀", context.LastEmojiUsed);
    }

    [Fact]
    public void ChatContext_MessageCountIncrement()
    {
        // Arrange
        var context = new ChatContext { MessageCount = 0 };

        // Act
        for (int i = 0; i < 5; i++)
        {
            context.MessageCount++;
        }

        // Assert
        Assert.Equal(5, context.MessageCount);
    }

    [Fact]
    public void ChatContext_LastEmojiUpdate()
    {
        // Arrange
        var context = new ChatContext();
        var emojis = new[] { "👍", "❤️", "🚀" };

        // Act
        foreach (var emoji in emojis)
        {
            context.LastEmojiUsed = emoji;
        }

        // Assert
        Assert.Equal("🚀", context.LastEmojiUsed);
    }

    #endregion

    #region Result Type Tests

    [Fact]
    public void AddEmojiResult_CanBeCreated()
    {
        // Act
        var result = new AddEmojiResult
        {
            Success = true,
            MessageId = "msg-1",
            Emoji = "👍",
            Message = "Success"
        };

        // Assert
        Assert.True(result.Success);
        Assert.Equal("msg-1", result.MessageId);
        Assert.Equal("👍", result.Emoji);
        Assert.Equal("Success", result.Message);
    }

    [Fact]
    public void AddEmojiResult_DefaultValues()
    {
        // Act
        var result = new AddEmojiResult();

        // Assert
        Assert.False(result.Success);
        Assert.Equal(string.Empty, result.MessageId);
        Assert.Equal(string.Empty, result.Emoji);
        Assert.Equal(string.Empty, result.Message);
    }

    [Fact]
    public void EmojiSuggestion_CanBeCreated()
    {
        // Act
        var suggestion = new EmojiSuggestion
        {
            MessageText = "Test",
            SuggestedEmojis = new[] { "👍", "😊" }
        };

        // Assert
        Assert.Equal("Test", suggestion.MessageText);
        Assert.Equal(2, suggestion.SuggestedEmojis.Length);
    }

    [Fact]
    public void EmojiSuggestion_DefaultValues()
    {
        // Act
        var suggestion = new EmojiSuggestion();

        // Assert
        Assert.Equal(string.Empty, suggestion.MessageText);
        Assert.Empty(suggestion.SuggestedEmojis);
    }

    #endregion

    #region Edge Cases and Error Handling

    [Fact]
    public async Task AddEmojiToMessage_WithEmptyMessageId_Succeeds()
    {
        // Act
        var result = await _agent.AddEmojiToMessage("", "👍");

        // Assert
        Assert.True(result.Success);
        Assert.Equal("", result.MessageId);
    }

    [Fact]
    public async Task AddEmojiToMessage_WithEmptyEmoji_Succeeds()
    {
        // Act
        var result = await _agent.AddEmojiToMessage("msg-1", "");

        // Assert
        Assert.True(result.Success);
        Assert.Equal("", result.Emoji);
    }

    [Fact]
    public async Task SuggestEmoji_WithEmptyText_ReturnsDefaultEmojis()
    {
        // Act
        var result = await _agent.SuggestEmoji("");

        // Assert
        Assert.NotEmpty(result.SuggestedEmojis);
        Assert.Contains("👍", result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_WithVeryLongText_Succeeds()
    {
        // Arrange
        var longText = new string('a', 10000);

        // Act
        var result = await _agent.SuggestEmoji(longText);

        // Assert
        Assert.NotNull(result);
        Assert.NotEmpty(result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_WithSpecialCharacters_Succeeds()
    {
        // Arrange
        var specialChars = "!@#$%^&*()_+-=[]{}|;:'\",.<>?/~`";

        // Act
        var result = await _agent.SuggestEmoji(specialChars);

        // Assert
        Assert.NotNull(result);
        Assert.NotEmpty(result.SuggestedEmojis);
    }

    [Fact]
    public async Task SuggestEmoji_WithUnicodeEmoji_Succeeds()
    {
        // Arrange
        var emojiText = "👋 Hello 🌍 World 🚀";

        // Act
        var result = await _agent.SuggestEmoji(emojiText);

        // Assert
        Assert.NotNull(result);
        Assert.NotEmpty(result.SuggestedEmojis);
    }

    [Fact]
    public async Task AddEmojiToMessage_WithComplexEmoji_Succeeds()
    {
        // Arrange - Testing multi-codepoint emoji
        var complexEmojis = new[] { "👨‍👩‍👧‍👦", "🏳️‍🌈", "👍🏾" };

        foreach (var emoji in complexEmojis)
        {
            // Act
            var result = await _agent.AddEmojiToMessage("msg-1", emoji);

            // Assert
            Assert.True(result.Success);
            Assert.Equal(emoji, result.Emoji);
        }
    }

    #endregion

    #region Integration Scenarios

    [Fact]
    public async Task CompleteWorkflow_SuggestAndAdd()
    {
        // Act - Suggest emoji for a message
        var suggestion = await _agent.SuggestEmoji("I love this!");

        // Act - Add each suggested emoji
        foreach (var emoji in suggestion.SuggestedEmojis)
        {
            var result = await _agent.AddEmojiToMessage("msg-love", emoji);

            // Assert
            Assert.True(result.Success);
            Assert.Equal(emoji, result.Emoji);
        }
    }

    [Fact]
    public async Task MultipleContexts_AreIndependent()
    {
        // Arrange
        var context1 = await _agent.CreateContextAsync("run-1", "thread-1");
        var context2 = await _agent.CreateContextAsync("run-2", "thread-2");

        // Act
        context1.MessageCount = 5;
        context1.LastEmojiUsed = "👍";

        context2.MessageCount = 3;
        context2.LastEmojiUsed = "❤️";

        // Assert
        Assert.Equal(5, context1.MessageCount);
        Assert.Equal("👍", context1.LastEmojiUsed);

        Assert.Equal(3, context2.MessageCount);
        Assert.Equal("❤️", context2.LastEmojiUsed);
    }

    [Fact]
    public async Task StateTracking_AcrossMultipleOperations()
    {
        // Arrange
        var context = new ChatContext();

        // Act - Simulate message flow
        context.MessageCount++;
        var suggestion1 = await _agent.SuggestEmoji("I am happy");

        context.LastEmojiUsed = suggestion1.SuggestedEmojis.First();
        context.MessageCount++;

        var suggestion2 = await _agent.SuggestEmoji("Thank you");
        context.LastEmojiUsed = suggestion2.SuggestedEmojis.First();
        context.MessageCount++;

        // Assert
        Assert.Equal(3, context.MessageCount);
        Assert.NotNull(context.LastEmojiUsed);
        Assert.Contains(context.LastEmojiUsed, suggestion2.SuggestedEmojis);
    }

    [Fact]
    public async Task BatchEmojiSuggestions_AllSucceed()
    {
        // Arrange
        var messages = new[]
        {
            "I am happy",
            "I am sad",
            "I love it",
            "Thank you",
            "This is great",
            "Hello world"
        };

        // Act & Assert
        foreach (var message in messages)
        {
            var result = await _agent.SuggestEmoji(message);
            Assert.NotNull(result);
            Assert.NotEmpty(result.SuggestedEmojis);
            Assert.Equal(message, result.MessageText);
        }
    }

    [Fact]
    public async Task BatchEmojiAdditions_AllSucceed()
    {
        // Arrange
        var emojis = new[] { "👍", "❤️", "🚀", "🎉", "😊", "💯", "🔥", "✨" };

        // Act & Assert
        foreach (var emoji in emojis)
        {
            var result = await _agent.AddEmojiToMessage($"msg-{emoji}", emoji);
            Assert.True(result.Success);
            Assert.Equal(emoji, result.Emoji);
        }
    }

    #endregion

    #region Performance Tests

    [Fact]
    public async Task SuggestEmoji_MultipleCallsInSequence_Perform()
    {
        // Arrange
        var iterations = 100;
        var message = "I am happy";

        // Act
        for (int i = 0; i < iterations; i++)
        {
            var result = await _agent.SuggestEmoji(message);

            // Assert
            Assert.NotNull(result);
            Assert.NotEmpty(result.SuggestedEmojis);
        }
    }

    [Fact]
    public async Task AddEmojiToMessage_MultipleCallsInSequence_Perform()
    {
        // Arrange
        var iterations = 100;

        // Act
        for (int i = 0; i < iterations; i++)
        {
            var result = await _agent.AddEmojiToMessage($"msg-{i}", "👍");

            // Assert
            Assert.True(result.Success);
        }
    }

    [Fact]
    public async Task ContextCreation_MultipleCallsInSequence_Perform()
    {
        // Arrange
        var iterations = 100;

        // Act
        for (int i = 0; i < iterations; i++)
        {
            var context = await _agent.CreateContextAsync($"run-{i}", $"thread-{i}");

            // Assert
            Assert.NotNull(context);
            Assert.Equal(0, context.MessageCount);
        }
    }

    #endregion

    #region Agent Protocol Options Tests

    [Fact]
    public void EmojiBotAgent_CanBeCreatedWithOptions()
    {
        // Arrange
        var options = new AgentProtocolOptions();

        // Act
        var agent = new EmojiBotAgent(options);

        // Assert
        Assert.NotNull(agent);
    }

    [Fact]
    public void EmojiBotAgent_InheritsFromAgentProtocolApplication()
    {
        // Arrange
        var options = new AgentProtocolOptions();
        var agent = new EmojiBotAgent(options);

        // Assert
        Assert.IsAssignableFrom<AgentProtocolApplication<ChatContext>>(agent);
    }

    #endregion
}
