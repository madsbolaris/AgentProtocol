using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Client.Tests.Recording;
using Microsoft.Agents.Protocol.Client;
using Xunit;

namespace Microsoft.Agents.Client.Tests.Docs;

/// <summary>
/// Tests for all Client SDK Quickstart Guide samples.
/// Uses HTTP recording/replay for deterministic testing.
///
/// To record new HTTP interactions:
///   RECORD_HTTP=true dotnet test
///
/// To replay recorded interactions (default):
///   dotnet test
///
/// To extract code snippets for docs:
///   python3 scripts/extract-snippets.py csharp
/// </summary>
public class QuickstartTests
{
    #region Step 1: Simple Completion

    [Fact]
    [DocExample("client-simple-completion")]
    public async Task Step1_SimpleCompletion_ReturnsResponse()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("simple-completion");

        #region Snippet
        // Send message and get response
        string response = await client.CompleteChatAsync("What can you help me with?");
        Console.WriteLine(response);
        #endregion

        // Assert
        response.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region Step 2: Multimodal Content

    [Fact]
    [DocExample("client-multimodal")]
    public async Task Step2_MultimodalContent_WithTypedConstructors_Works()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step2_MultimodalContent");

        #region Snippet
        // Send text and image together
        var message = new UserMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "What's in this image?" },
                new ImageContent { Uri = "https://example.com/photo.jpg" }
            }
        };

        var response = await client.CompleteChatAsync(message);
        var responseText = response.Contents?.OfType<TextContent>().FirstOrDefault()?.Text ?? "";
        Console.WriteLine(responseText);
        #endregion

        // Assert
        responseText.Should().NotBeNullOrEmpty();
    }

    #endregion

    #region Step 3: Persistent Conversations

    [Fact]
    [DocExample("client-persistent-conversations")]
    public async Task Step3_PersistentConversations_MaintainsContext()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step3_PersistentConversations");

        #region Snippet
        // Create a conversation that maintains context
        var conversation = client.CreateConversation();

        var msg1 = await conversation.SendAsync("My name is Alice");
        Console.WriteLine($"Agent: {msg1}");

        var msg2 = await conversation.SendAsync("What's my name?");
        Console.WriteLine($"Agent: {msg2}");  // Agent remembers: "Alice"
        #endregion

        // Assert
        msg1.Should().Contain("Alice");
        msg2.Should().Contain("Alice");
    }

    [Fact]
    [DocExample("client-resume-conversation")]
    public async Task Step3_ResumeConversation_UsesExistingThread()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step3_ResumeConversation");

        // Create initial conversation
        var conversation1 = client.CreateConversation();
        await conversation1.SendAsync("My name is Bob");
        var threadId = conversation1.ThreadId!;

        #region Snippet
        // Resume an existing conversation
        var conversation2 = client.ResumeConversation(threadId);
        var response = await conversation2.SendAsync("Do you remember me?");
        Console.WriteLine($"Agent: {response}");
        #endregion

        // Assert
        response.Should().Contain("Bob");
    }

    #endregion

    #region Step 4: Tools/Functions

    [Fact]
    [DocExample("client-tools")]
    public async Task Step4_Tools_AutomaticallyExecuted()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step4_Tools");

        #region Snippet
        // Define tools for the agent to use
        var tools = new ToolCollection();
        tools.Add("get_weather", (string location) =>
            JsonSerializer.Serialize(new { temperature = "72°F", condition = "sunny", location }));

        var options = new ChatOptions { Tools = tools };
        var response = await client.CompleteChatAsync("What's the weather in Seattle?", options);
        Console.WriteLine(response);
        #endregion

        // Assert
        response.Should().Contain("Seattle");
    }

    #endregion

    #region Step 5: Streaming

    [Fact]
    [DocExample("client-simple-streaming")]
    public async Task Step5_SimpleStreaming_ReceivesChunks()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step5_SimpleStreaming");

        #region Snippet
        // Stream text chunks as they arrive
        await client.StreamChatAsync("Tell me a story", chunk =>
        {
            Console.Write(chunk);
        });
        Console.WriteLine();  // New line after streaming
        #endregion

        // Assert
        // (Validation done through recording verification)
    }

    [Fact]
    [DocExample("client-rich-streaming")]
    public async Task Step5_RichContentStreaming_HandlesMultipleContentTypes()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step5_RichContentStreaming");
        var conversation = client.CreateConversation();

        #region Snippet
        // Stream messages with multiple content types
        await foreach (var message in conversation.StreamMessagesAsync("Show me a photo of Paris"))
        {
            foreach (var content in message.Contents)
            {
                if (content is TextContent text)
                    Console.WriteLine($"Text: {text.Text}");
                else if (content is ImageContent image)
                    Console.WriteLine($"Image: {image.Uri}");
            }
        }
        #endregion

        // Assert
        // (Validation done through recording verification)
    }

    [Fact]
    [DocExample("client-thread-messages")]
    public async Task Step5_ThreadMessages_RetrievesHistory()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("Step5_ThreadMessages");
        var conversation = client.CreateConversation();
        await conversation.SendAsync("What's the weather in Paris?");

        #region Snippet
        // Get all messages in the conversation
        var messages = await conversation.GetMessagesAsync();

        foreach (var message in messages)
        {
            Console.WriteLine($"{message.Role}: {string.Join(" ", message.Contents.Select(c => c.ToString()))}");
        }
        #endregion

        // Assert
        messages.Should().NotBeEmpty();
    }

    #endregion

    #region Error Handling

    [Fact]
    [DocExample("client-error-handling")]
    public async Task ErrorHandling_CatchesAgentProtocolException()
    {
        // Arrange
        var client = RecordingTestHelper.CreateRecordingClient("ErrorHandling");

        #region Snippet
        // Handle errors gracefully
        try
        {
            await client.CompleteChatAsync("TRIGGER_ERROR");
        }
        catch (AgentProtocolException ex)
        {
            Console.WriteLine($"Error: {ex.Message}");
        }
        #endregion

        // Assert
        // (Test passes if no unhandled exception)
    }

    #endregion
}
