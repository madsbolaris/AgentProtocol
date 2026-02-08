// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using FunctionToolsSample;
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

// Load environment variables from .env file in repository root
try
{
    var envPath = Path.Combine(
        Directory.GetCurrentDirectory(),
        "..", "..", "..", "..",
        ".env"
    );
    envPath = Path.GetFullPath(envPath);
    if (File.Exists(envPath))
    {
        DotNetEnv.Env.Load(envPath);
        Console.WriteLine($"Loaded .env from: {envPath}");
    }
}
catch (Exception ex)
{
    Console.WriteLine($"Warning: Could not load .env file: {ex.Message}");
}

WebApplicationBuilder builder = WebApplication.CreateBuilder(args);

builder.Services.AddHttpClient();

// Add AgentApplicationOptions from appsettings section "AgentApplication".
builder.AddAgentApplicationOptions();

// Add the FunctionToolsAgent, which contains the logic for responding to
// user messages with function calling capabilities.
builder.AddAgent<FunctionToolsAgent>();

// Register IStorage.  For development, MemoryStorage is suitable.
// For production Agents, persisted storage should be used so
// that state survives Agent restarts, and operates correctly
// in a cluster of Agent instances.
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

app.MapGet("/", () => "Microsoft Agents SDK - Basic M365 Agent Sample");

// This receives incoming messages from Azure Bot Service or other SDK Agents
var incomingRoute = app.MapPost("/api/messages", async (HttpRequest request, HttpResponse response, IAgentHttpAdapter adapter, IAgent agent, CancellationToken cancellationToken) =>
{
    await adapter.ProcessAsync(request, response, agent, cancellationToken);
});

// Add Agent Protocol routes (uses FunctionToolsAgent from DI)
app.MapAgentProtocol();

if (!app.Environment.IsDevelopment())
{
    incomingRoute.RequireAuthorization();
}
else
{
    // Read port from centralized agent-config.json
    // Falls back to environment variable PORT, then default 3981
    var port = GetPortFromConfig() ?? Environment.GetEnvironmentVariable("PORT") ?? "3981";
    app.Urls.Add($"http://localhost:{port}");
}

static string? GetPortFromConfig()
{
    try
    {
        // Navigate up to repository root (4 levels up from FunctionToolsAgent directory)
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
            bots.TryGetProperty("dotnet-basic-m365", out var dotnetBot) &&
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
