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
    private readonly TestingChatClient? _testingClient;
    private readonly string _model = "gpt-5-nano";

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

        // Check mode from environment variables
        var useRecordings = Environment.GetEnvironmentVariable("USE_LLM_RECORDINGS");
        var playbackMode = !string.IsNullOrEmpty(useRecordings) && useRecordings.Equals("true", StringComparison.OrdinalIgnoreCase);

        var recordLlm = Environment.GetEnvironmentVariable("RECORD_LLM");
        var recordMode = !string.IsNullOrEmpty(recordLlm) && recordLlm.Equals("true", StringComparison.OrdinalIgnoreCase);

        // Find recordings directory (navigate up to repo root)
        var repoRoot = Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(),
            "..", "..", "..", ".."
        ));
        var recordingsDir = Path.Combine(repoRoot, "test-data", "llm-recordings", "emoji-chat");

        // Create real OpenAI client if needed (for normal or recording mode)
        ChatClient? realClient = null;
        if (!playbackMode)
        {
            var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_ENDPOINT");
            var apiKey = Environment.GetEnvironmentVariable("FOUNDRY_API_KEY");

            if (!string.IsNullOrEmpty(endpoint) && !string.IsNullOrEmpty(apiKey))
            {
                _model = Environment.GetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT") ?? "gpt-5-nano";

                // Create ChatClient for Foundry
                realClient = new ChatClient(
                    credential: new ApiKeyCredential(apiKey),
                    model: _model,
                    options: new OpenAIClientOptions()
                    {
                        Endpoint = new Uri($"{endpoint}/openai/v1/")
                    });
            }
            else
            {
                Console.WriteLine("⚠️  No LLM credentials found!");
                Console.WriteLine("   Set FOUNDRY_ENDPOINT and FOUNDRY_API_KEY environment variables to use LLM.");
                Console.WriteLine("   Or set USE_LLM_RECORDINGS=true to use recorded responses.");
                Console.WriteLine("   EmojiBot will fail without LLM configuration.");
            }
        }
        else
        {
            _model = "gpt-5-nano"; // Default model for recordings
        }

        // Create TestingChatClient wrapper (handles both recording and playback)
        if (realClient != null || playbackMode)
        {
            _testingClient = new TestingChatClient(
                realClient: realClient,
                recordingsDir: recordingsDir,
                modelId: _model,
                recordMode: recordMode,
                playbackMode: playbackMode
            );
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

        // Use TestingChatClient (handles recording/playback automatically)
        if (_testingClient != null)
        {
            // Call LLM (transparently handles recording/playback)
            var chatOptions = new ChatCompletionOptions();
            var completion = await _testingClient.CompleteChatAsync(
                context.Context.ConversationHistory,
                chatOptions,
                cancellationToken
            );

            response = string.Join("", completion.Content.Select(c => c.Text));
            context.Context.ConversationHistory.Add(new AssistantChatMessage(response));

            // Send response
            await context.SendTextAsync(response, cancellationToken);
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
