using System;
using System.IO;
using System.Text.Json;
using Microsoft.AspNetCore.Builder;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using EmojiChatBot;

var builder = WebApplication.CreateBuilder(args);

// Register Agent Protocol SDK with EmojiChatBot
builder.Services.AddAgentProtocol<EmojiBotAgent, ChatContext>();

var app = builder.Build();

// Map Agent Protocol endpoints (includes /, /health, /api/messages, /runs/wait)
app.MapAgentProtocol<ChatContext>();

// Configure port from agent-config.json
if (app.Environment.IsDevelopment())
{
    var port = GetPortFromConfig() ?? Environment.GetEnvironmentVariable("PORT") ?? "3984";
    app.Urls.Add($"http://localhost:{port}");
    Console.WriteLine($"🤖 EmojiChatBot running on port {port}");
}

app.Run();

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
    catch (Exception ex)
    {
        Console.WriteLine($"Warning: Could not read agent-config.json: {ex.Message}");
    }

    return null;
}

// Make the implicit Program class accessible to integration tests
public partial class Program { }
