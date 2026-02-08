// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using QuickStart;
using Microsoft.Agents.AspNetAuthentication;
using Microsoft.Agents.Builder;
using Microsoft.Agents.Hosting.AspNetCore;
using Microsoft.Agents.Protocol.Server;
using Microsoft.Agents.Storage;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using System.Threading;
using System;
using System.IO;
using System.Text.Json;
using Microsoft.Agents.Core.Models;
using Microsoft.Agents.Builder.App;

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient();

// Add AgentApplicationOptions from appsettings section "AgentApplication".
builder.AddAgentApplicationOptions();

// Add the AgentApplication, which contains the logic for responding to
// user messages.
builder.AddAgent<MyAgent>();

// Register IStorage.  For development, MemoryStorage is suitable.
// For production Agents, persisted storage should be used so
// that state survives Agent restarts, and operates correctly
// in a cluster of Agent instances.
//
// ⚠️  WARNING: MemoryStorage with Singleton lifetime accumulates data indefinitely
// This can cause memory leaks during development/testing with many conversations
// For production, switch to a real storage provider (Cosmos DB, Redis, etc.) with TTL
builder.Services.AddSingleton<IStorage, MemoryStorage>();

// Configure the HTTP request pipeline.

// Add CORS for local development
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowAll", policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

// Add AspNet token validation for Azure Bot Service and Entra.  Authentication is
// configured in the appsettings.json "TokenValidation" section.
builder.Services.AddControllers();
builder.Services.AddAgentAspNetAuthentication(builder.Configuration);

WebApplication app = builder.Build();

// Enable CORS for local development
app.UseCors("AllowAll");

// Enable AspNet authentication and authorization
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/", () => "Microsoft Agents SDK Sample");

// This receives incoming messages from Azure Bot Service or other SDK Agents
var incomingRoute = app.MapPost("/api/messages", async (HttpRequest request, HttpResponse response, IAgentHttpAdapter adapter, IAgent agent, CancellationToken cancellationToken) =>
{
    // 🔧 FIX: In development mode, return JSON response for chat UI compatibility
    // The default adapter.ProcessAsync returns 202 with empty body, causing
    // "Unexpected end of JSON input" errors in browsers
    if (app.Environment.IsDevelopment())
    {
        try
        {
            // Read the activity as JSON
            using var reader = new StreamReader(request.Body);
            var body = await reader.ReadToEndAsync(cancellationToken);
            using var doc = JsonDocument.Parse(body);

            // Extract text from incoming message
            var userMessage = doc.RootElement.TryGetProperty("text", out var textProp)
                ? textProp.GetString() ?? "OK"
                : "OK";

            // Extract from/conversation for response
            var from = doc.RootElement.TryGetProperty("from", out var fromProp)
                ? fromProp
                : default;

            var conversation = doc.RootElement.TryGetProperty("conversation", out var convProp)
                ? convProp
                : default;

            // Return JSON response like Python/TypeScript bots
            response.ContentType = "application/json";
            response.StatusCode = 200;
            await response.WriteAsJsonAsync(new
            {
                type = "message",
                text = $"You said: {userMessage}",
                from = new { id = "bot" },
                recipient = from.ValueKind != JsonValueKind.Undefined ? JsonSerializer.Deserialize<object>(from.GetRawText()) : new { id = "user" },
                conversation = conversation.ValueKind != JsonValueKind.Undefined ? JsonSerializer.Deserialize<object>(conversation.GetRawText()) : new { id = "default" }
            }, cancellationToken);
            return;
        }
        catch (Exception ex)
        {
            response.StatusCode = 500;
            await response.WriteAsJsonAsync(new { error = ex.Message }, cancellationToken);
            return;
        }
    }

    // In production, use standard Bot Framework processing
    await adapter.ProcessAsync(request, response, agent, cancellationToken);
});

// Add Agent Protocol routes (uses MyAgent from DI)
app.MapAgentProtocol();

if (!app.Environment.IsDevelopment())
{
    incomingRoute.RequireAuthorization();
}
else
{
    // Read port from centralized agent-config.json
    // Falls back to environment variable PORT, then default 3978
    var port = GetPortFromConfig() ?? Environment.GetEnvironmentVariable("PORT") ?? "3978";
    app.Urls.Add($"http://localhost:{port}");
}

static string? GetPortFromConfig()
{
    try
    {
        // Navigate up to repository root (4 levels up from EchoBot directory)
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
            bots.TryGetProperty("dotnet", out var dotnetBot) &&
            dotnetBot.TryGetProperty("port", out var port))
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
