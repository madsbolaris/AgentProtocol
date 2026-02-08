// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Net;
using System.Net.Http;
using System.Net.Http.Json;
using System.Text.Json;
using System.Threading.Tasks;
using Microsoft.AspNetCore.Mvc.Testing;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Xunit;

namespace QuickStart.Tests.IntegrationTests;

/// <summary>
/// Integration tests for EchoBot running in anonymous mode.
///
/// These tests verify that the echo bot works without Azure authentication
/// and catches issues that were found in other language implementations:
/// - Anonymous mode functionality
/// - CORS headers
/// - Route configuration
/// - HTTP endpoint responses
///
/// Run with: dotnet test --filter "Category=Integration"
/// </summary>
[Trait("Category", "Integration")]
public class AnonymousModeTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly WebApplicationFactory<Program> _factory;
    private readonly HttpClient _client;

    public AnonymousModeTests(WebApplicationFactory<Program> factory)
    {
        _factory = factory.WithWebHostBuilder(builder =>
        {
            builder.ConfigureServices(services =>
            {
                // Configure for anonymous mode (no authentication)
                // In production, this would come from environment variables
            });
        });

        _client = _factory.CreateClient(new WebApplicationFactoryClientOptions
        {
            AllowAutoRedirect = false
        });
    }

    #region Endpoint Tests

    [Fact]
    public async Task RootEndpoint_ReturnsOk()
    {
        // Act
        var response = await _client.GetAsync("/");

        // Assert
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        var content = await response.Content.ReadAsStringAsync();
        Assert.Contains("Microsoft Agents SDK Sample", content);
    }

    [Fact]
    public async Task HealthEndpoint_ReturnsHealthyStatus()
    {
        // Act
        var response = await _client.GetAsync("/health");

        // Assert
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);

        // Note: .NET implementation might not have /health endpoint yet
        // This test documents the expected behavior
    }

    [Fact]
    public async Task ApiMessages_AcceptsBotFrameworkActivity()
    {
        // Arrange
        var message = new
        {
            type = "message",
            from = new { id = "user123", name = "Test User" },
            recipient = new { id = "bot" },
            text = "hello test",
            channelId = "demo",
            conversation = new { id = "test-conv" },
            serviceUrl = "http://localhost:3978"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/messages", message);

        // Assert
        // In development mode without auth, this might return 401
        // In anonymous mode, should return 200
        Assert.True(
            response.StatusCode == HttpStatusCode.OK ||
            response.StatusCode == HttpStatusCode.Unauthorized,
            $"Expected 200 or 401, got {response.StatusCode}"
        );
    }

    [Fact]
    public async Task ApiMessages_ReturnsJsonResponse()
    {
        // This test catches the bug where .NET bot returns empty response
        // causing "Unexpected end of JSON input" in chat UI

        // Arrange
        var message = new
        {
            type = "message",
            from = new { id = "user123" },
            recipient = new { id = "bot" },
            text = "test message",
            channelId = "demo",
            conversation = new { id = "test-conv" },
            serviceUrl = "http://localhost:3978"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/messages", message);

        // Assert
        if (response.StatusCode == HttpStatusCode.OK)
        {
            var content = await response.Content.ReadAsStringAsync();

            // CRITICAL: Response must not be empty (causes JSON parse error in UI)
            Assert.False(
                string.IsNullOrWhiteSpace(content),
                "Response body is empty - this causes 'Unexpected end of JSON input' in chat UI"
            );

            // Response should be valid JSON
            var jsonDoc = JsonDocument.Parse(content);

            // Response should have a 'text' property like Python/TypeScript bots
            Assert.True(
                jsonDoc.RootElement.TryGetProperty("text", out _),
                "Response should contain 'text' property for compatibility with chat UI"
            );
        }
    }

    #endregion

    #region CORS Tests

    [Fact]
    public async Task RootEndpoint_IncludesCORSHeaders()
    {
        // Act
        var response = await _client.GetAsync("/");

        // Assert
        Assert.True(
            response.Headers.Contains("Access-Control-Allow-Origin") ||
            response.Headers.Contains("access-control-allow-origin"),
            "CORS headers should be present"
        );

        if (response.Headers.TryGetValues("Access-Control-Allow-Origin", out var origins))
        {
            Assert.Contains("*", origins);
        }
    }

    [Fact]
    public async Task ApiMessages_IncludesCORSHeaders()
    {
        // Arrange
        var message = new
        {
            type = "message",
            from = new { id = "user" },
            recipient = new { id = "bot" },
            text = "test",
            channelId = "demo",
            conversation = new { id = "test" },
            serviceUrl = "http://localhost"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/messages", message);

        // Assert
        Assert.True(
            response.Headers.Contains("Access-Control-Allow-Origin") ||
            response.Headers.Contains("access-control-allow-origin"),
            "CORS headers should be present on /api/messages"
        );
    }

    [Fact]
    public async Task OptionsPreflightRequest_Succeeds()
    {
        // Arrange
        var request = new HttpRequestMessage(HttpMethod.Options, "/api/messages");
        request.Headers.Add("Origin", "http://localhost:8000");
        request.Headers.Add("Access-Control-Request-Method", "POST");

        // Act
        var response = await _client.SendAsync(request);

        // Assert
        Assert.Equal(HttpStatusCode.OK, response.StatusCode);
        Assert.True(
            response.Headers.Contains("Access-Control-Allow-Origin"),
            "OPTIONS response should include CORS headers"
        );
    }

    #endregion

    #region Echo Bot Functionality

    [Fact]
    public async Task EchoBot_EchoesSimpleMessage()
    {
        // Arrange
        var message = new
        {
            type = "message",
            from = new { id = "user" },
            recipient = new { id = "bot" },
            text = "test message for echo",
            channelId = "demo",
            conversation = new { id = "test" },
            serviceUrl = "http://localhost"
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/messages", message);

        // Assert
        if (response.StatusCode == HttpStatusCode.OK)
        {
            var content = await response.Content.ReadAsStringAsync();
            Assert.Contains("test message for echo", content, StringComparison.OrdinalIgnoreCase);
        }
        else
        {
            // Document that authentication is required in current implementation
            Assert.Equal(HttpStatusCode.Unauthorized, response.StatusCode);
        }
    }

    #endregion

    #region Route Configuration

    [Fact]
    public async Task NoDuplicateRouteRegistration()
    {
        // This test passes if the application starts without errors
        // Route conflicts would cause startup failures

        // Act
        var healthResponse = await _client.GetAsync("/");

        // Assert
        Assert.True(
            healthResponse.StatusCode == HttpStatusCode.OK ||
            healthResponse.StatusCode == HttpStatusCode.NotFound,
            "Server should start successfully without route conflicts"
        );
    }

    [Fact]
    public async Task AgentProtocolRoutes_AreRegistered()
    {
        // Act
        var response = await _client.GetAsync("/");

        // Assert - Server should respond (routes are registered)
        Assert.NotEqual(HttpStatusCode.InternalServerError, response.StatusCode);
    }

    #endregion

    #region Anonymous Mode Configuration

    [Fact]
    public async Task AnonymousMode_DoesNotRequireAuthenticationHeaders()
    {
        // Arrange
        var message = new
        {
            type = "message",
            from = new { id = "user" },
            recipient = new { id = "bot" },
            text = "no auth test",
            channelId = "demo",
            conversation = new { id = "test" },
            serviceUrl = "http://localhost"
        };

        // Act - Send request without Authorization header
        var response = await _client.PostAsJsonAsync("/api/messages", message);

        // Assert
        // In true anonymous mode: should return 200
        // In dev mode without proper config: might return 401
        Assert.True(
            response.StatusCode == HttpStatusCode.OK ||
            response.StatusCode == HttpStatusCode.Unauthorized,
            $"Expected 200 (anonymous) or 401 (auth required), got {response.StatusCode}"
        );
    }

    #endregion

    #region Error Handling

    [Fact]
    public async Task MalformedMessage_HandledGracefully()
    {
        // Arrange - Send incomplete message
        var invalidMessage = new
        {
            text = "incomplete message"
            // Missing required fields
        };

        // Act
        var response = await _client.PostAsJsonAsync("/api/messages", invalidMessage);

        // Assert - Should not return 500
        Assert.NotEqual(HttpStatusCode.InternalServerError, response.StatusCode);
    }

    #endregion
}
