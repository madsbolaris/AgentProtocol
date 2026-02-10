// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

// ============================================================================
// MODERN SAMPLE - New Hosting Package Only
// ============================================================================
// This sample demonstrates the NEW way to build agents using ONLY the
// Microsoft.Agents.Protocol.Hosting package. This is the recommended approach
// for new applications.
//
// For examples of adapting LEGACY M365 Agents SDK apps to speak Agent Protocol,
// see the EchoM365 and BasicM365Agent samples.
// ============================================================================

using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Core;
using OpenAI;
using OpenAI.Chat;
using System;
using System.ClientModel;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

#pragma warning disable OPENAI001

namespace EmojiChatBot;

/// <summary>
/// Emoji Chat Bot demonstrating:
/// 1. LLM-powered emoji suggestions
/// 2. LLM recording/playback for deterministic testing
/// 3. Modern Agent Protocol hosting (NO M365 SDK)
/// </summary>
public class EmojiBotAgent : AgentProtocolApplication<EmojiContext>
{
    private readonly ChatClient? _chatClient;
    private readonly LLMRecorder? _recorder;
    private readonly LLMPlayer? _player;
    private readonly string _model = "gpt-5-nano";
    private readonly bool _useRecordings;

    public EmojiBotAgent(AgentProtocolOptions options) : base(options)
    {
        // ============================================================================
        // ENVIRONMENT VARIABLES - Set automatically by scripts/ci/start_samples.py
        // ============================================================================
        // These environment variables are loaded from .env file at repo root:
        //   - FOUNDRY_ENDPOINT: LLM endpoint URL
        //   - FOUNDRY_API_KEY: API key for authentication
        //   - FOUNDRY_MODEL_DEPLOYMENT: Model name (default: gpt-5-nano)
        //   - USE_LLM_RECORDINGS: Set to "true" for test mode (replays recordings)
        //   - RECORD_LLM: Set to "true" to record LLM interactions
        //
        // Developers should NEVER manually set these variables.
        // Use: python3 scripts/ci/start_samples.py emoji-chat --lang dotnet --ui
        // ============================================================================

        // Check if we should use LLM recordings (test mode)
        var useRecordings = Environment.GetEnvironmentVariable("USE_LLM_RECORDINGS");
        _useRecordings = !string.IsNullOrEmpty(useRecordings) && useRecordings.Equals("true", StringComparison.OrdinalIgnoreCase);

        // Find recordings directory (navigate up to repo root)
        var repoRoot = Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(),
            "..", "..", "..", ".."
        ));
        var recordingsDir = Path.Combine(repoRoot, "test-data", "llm-recordings", "emoji-bot");

        if (_useRecordings)
        {
            // Test mode: Use recorded LLM responses
            _model = "gpt-5-nano"; // Default model for recordings
            _player = new LLMPlayer(recordingsDir);
            Console.WriteLine($"▶️  LLM Playback enabled: {recordingsDir}");
            Console.WriteLine("   Using recorded LLM responses (test mode)");
        }
        else
        {
            // Generation mode: Use real LLM and optionally record
            var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_ENDPOINT");
            var apiKey = Environment.GetEnvironmentVariable("FOUNDRY_API_KEY");

            if (!string.IsNullOrEmpty(endpoint) && !string.IsNullOrEmpty(apiKey))
            {
                _model = Environment.GetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT") ?? "gpt-5-nano";

                // Create ChatClient for Foundry
                _chatClient = new ChatClient(
                    credential: new ApiKeyCredential(apiKey),
                    model: _model,
                    options: new OpenAIClientOptions()
                    {
                        Endpoint = new Uri($"{endpoint}/openai/v1/")
                    });

                // Check if LLM recording is enabled
                var recordLlm = Environment.GetEnvironmentVariable("RECORD_LLM");
                if (!string.IsNullOrEmpty(recordLlm) && recordLlm.Equals("true", StringComparison.OrdinalIgnoreCase))
                {
                    Directory.CreateDirectory(recordingsDir);
                    _recorder = new LLMRecorder(recordingsDir);
                    Console.WriteLine($"🔴 LLM Recording enabled: {recordingsDir}");
                    Console.WriteLine($"   Model: {_model}");
                }
                else
                {
                    Console.WriteLine($"🤖 Using LLM: {_model} (recording disabled)");
                }
            }
            else
            {
                Console.WriteLine("⚠️  No LLM credentials found!");
                Console.WriteLine("   Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY environment variables to use LLM.");
                Console.WriteLine("   Or set USE_LLM_RECORDINGS=true to use recorded responses.");
                Console.WriteLine("   EmojiBot will fail without LLM configuration.");
            }
        }

        // Register handler for user messages
        OnUserMessage(HandleUserMessageAsync);
    }

    /// <summary>
    /// Handle user messages and respond with LLM-generated emoji suggestions
    /// </summary>
    private async Task HandleUserMessageAsync(
        IMessageContext<EmojiContext> context,
        Microsoft.Agents.ChatMessage message,
        CancellationToken cancellationToken)
    {
        // Extract text from message contents
        var userMessage = string.Empty;
        if (message is UserMessage um)
        {
            foreach (var content in um.Contents)
            {
                if (content is TextContent tc && !string.IsNullOrEmpty(tc.Text))
                {
                    userMessage += tc.Text;
                }
            }
        }

        // Initialize conversation history if needed
        if (context.Context.ConversationHistory.Count == 0)
        {
            context.Context.ConversationHistory.Add(new SystemChatMessage(@"You are an emoji expert bot. Your responses should:
1. Acknowledge what the user said
2. Suggest 3-5 relevant emojis based on the sentiment, topic, or mood
3. Be friendly and enthusiastic about emojis
4. Keep responses concise (2-3 sentences max)

Examples:
- User: 'I'm happy today!' → 'That's wonderful! 😊 Here are some joyful emojis: 😊 🎉 ☀️ ✨'
- User: 'I love pizza' → 'Pizza is amazing! 🍕 Perfect emojis: 🍕 ❤️ 😋 👨‍🍳'
- User: 'Feeling tired' → 'Hope you get some rest! 😴 Cozy emojis: 😴 💤 🛌 ☕'"));
        }

        // Add user message to history
        context.Context.ConversationHistory.Add(new UserChatMessage(userMessage));

        string response;

        // Use LLM (either real or replayed)
        if (_useRecordings && _player != null)
        {
            // Test mode: Replay recorded response
            var completion = await _player.ReplayAsync(_model, context.Context.ConversationHistory, null, cancellationToken);
            response = string.Join("", completion.Content.Select(c => c.Text));
            context.Context.ConversationHistory.Add(new AssistantChatMessage(response));

            // Send response (non-streaming for playback)
            await context.SendTextAsync(response, cancellationToken);
        }
        else if (_chatClient != null)
        {
            // Generation mode: Use real LLM with streaming
            var chatOptions = new ChatCompletionOptions();
            var streamingResult = _chatClient.CompleteChatStreamingAsync(context.Context.ConversationHistory, chatOptions, cancellationToken);

            var fullResponse = "";
            var responseBuilder = new System.Text.StringBuilder();

            await foreach (var update in streamingResult)
            {
                foreach (var contentPart in update.ContentUpdate)
                {
                    if (!string.IsNullOrEmpty(contentPart.Text))
                    {
                        responseBuilder.Append(contentPart.Text);
                        fullResponse += contentPart.Text;

                        // Emit streaming event via callback WITHOUT adding to Responses
                        // This allows real-time streaming without creating separate messages
                        await context.EmitStreamChunkAsync(contentPart.Text, cancellationToken);
                    }
                }
            }

            response = fullResponse;
            context.Context.ConversationHistory.Add(new AssistantChatMessage(response));

            // Add the complete response to the output (needed for both streaming and wait mode)
            // Use SendMessageAsync instead of SendTextAsync to avoid triggering extra delta events
            await context.SendMessageAsync(new AgentMessage
            {
                Contents = new List<AIContent> { new TextContent { Text = response } }
            }, cancellationToken);

            // Note: Recording is not supported for streaming mode
            // The LLMRecorder expects a non-streaming ChatCompletion object
        }
        else
        {
            throw new InvalidOperationException("LLM is not configured. Please use the startup script in scripts/ci/start_samples.py");
        }
    }

    /// <summary>
    /// Create custom context instance for each run
    /// </summary>
    public override Task<EmojiContext> CreateContextAsync(
        string runId,
        string threadId,
        CancellationToken cancellationToken = default)
    {
        return Task.FromResult(new EmojiContext());
    }
}

/// <summary>
/// Custom context for emoji bot - stores conversation history per run
/// </summary>
public class EmojiContext
{
    public List<OpenAI.Chat.ChatMessage> ConversationHistory { get; set; } = new();
}
