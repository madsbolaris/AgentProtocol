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

using EmojiChatBot;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Runtime;
using Microsoft.Agents.Protocol.Hosting.Storage;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System.Threading;
using System;
using System.IO;
using System.Text.Json;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient();

builder.Services.AddControllers();

// Register core services
builder.Services.AddSingleton<IStorage, InMemoryStorage>();

// Register the EmojiBotAgent with new hosting package
builder.Services.AddAgentProtocol<EmojiBotAgent, EmojiContext>(options =>
{
    options.Name = "EmojiBot";
    options.Description = "Emoji expert bot powered by AI";
});

WebApplication app = builder.Build();

// Enable CORS for local development
app.UseCors("AgentProtocol");

// AGENT PROTOCOL ROUTES: Modern Agent Protocol routes
// The new hosting package provides ONLY Agent Protocol routes:
// - / (root): Agent info
// - /health: Health check
// - /agent-card: Agent metadata
// - /runs/wait: Create and wait for run completion
// - /runs/stream: Stream run execution with SSE
//
// NOTE: /api/messages is NOT provided by the new hosting package.
// That endpoint is for LEGACY M365 Agents SDK apps (see echo-m365, basic-m365 samples).
app.MapAgentProtocol<EmojiContext>();

// Read port from centralized agent-config.json
// Falls back to environment variable PORT, then default 3984
var port = GetPortFromConfig() ?? Environment.GetEnvironmentVariable("PORT") ?? "3984";
app.Urls.Clear();
app.Urls.Add($"http://localhost:{port}");
Console.WriteLine($"🤖 EmojiChatBot running on port {port}");

// 🔧 FIX: Allow anonymous access for demo/development
// For production deployments, configure authentication in appsettings.json and uncomment:
// if (!app.Environment.IsDevelopment())
// {
//     incomingRoute.RequireAuthorization();
// }

static string? GetPortFromConfig()
{
    try
    {
        // Navigate up to repository root (4 levels up from EmojiChatBot directory)
        var configPath = Path.Combine(
            Directory.GetCurrentDirectory(),
            "..", "..", "..", "..",
            "agent-config.json"
        );

        configPath = Path.GetFullPath(configPath);

        if (!File.Exists(configPath))
        {
            return null;
        }

        var json = File.ReadAllText(configPath);
        using var doc = JsonDocument.Parse(json);

        if (doc.RootElement.TryGetProperty("bots", out var bots) &&
            bots.TryGetProperty("dotnet-emoji-chat", out var emojiBot) &&
            emojiBot.TryGetProperty("port", out var port))
        {
            return port.GetInt32().ToString();
        }
    }
    catch
    {
        // If config reading fails, return null to fall back to environment variable
    }

    return null;
}

app.Run();

// Make the implicit Program class accessible to integration tests
public partial class Program { }
