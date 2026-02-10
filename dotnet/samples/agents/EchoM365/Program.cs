// Copyright (c) Microsoft. All rights reserved.

// Sample that shows how to create an Agent Framework agent that is hosted using the M365 Agent SDK.
// The agent can then be consumed from various M365 channels.
// See the README.md for more information.

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
using System;
using System.Threading;

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
builder.Services.AddSingleton<IStorage, MemoryStorage>();

// Configure the HTTP request pipeline.

// Add AspNet token validation for Azure Bot Service and Entra.  Authentication is
// configured in the appsettings.json "TokenValidation" section.
builder.Services.AddControllers();
builder.Services.AddAgentAspNetAuthentication(builder.Configuration);

// Add CORS for Agent Protocol endpoints
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader()
              .WithExposedHeaders("*");
    });
});

WebApplication app = builder.Build();

// Enable CORS
app.UseCors();

// Enable AspNet authentication and authorization
app.UseAuthentication();
app.UseAuthorization();

app.MapGet("/", () => "Microsoft Agents SDK Sample");

// ==================================================================================
// LEGACY ENDPOINT - DO NOT MODIFY
// This is the Bot Framework /api/messages endpoint for backwards compatibility.
// It receives incoming messages from Azure Bot Service or other M365 channels.
// For Agent Protocol functionality, use the routes added by MapAgentProtocol below.
// ==================================================================================
var incomingRoute = app.MapPost("/api/messages", async (HttpRequest request, HttpResponse response, IAgentHttpAdapter adapter, IAgent agent, CancellationToken cancellationToken) => await adapter.ProcessAsync(request, response, agent, cancellationToken));

// AGENT PROTOCOL EXTENSION: Add Agent Protocol routes
app.MapAgentProtocol();

if (!app.Environment.IsDevelopment())
{
    incomingRoute.RequireAuthorization();
}
else
{
    // Hardcoded for brevity and ease of testing.
    // In production, this should be set in configuration.
    var port = Environment.GetEnvironmentVariable("PORT") ?? "3978";
    app.Urls.Add($"http://localhost:{port}");
}

app.Run();

// Make the implicit Program class accessible to integration tests
public partial class Program { }
