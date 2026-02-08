using System;
using System.Net;
using System.Net.Http;
using System.Text.Json;
using RichardSzalay.MockHttp;

namespace Microsoft.Agents.Client.Tests.TestHelpers;

/// <summary>
/// Helper class for creating mock HTTP clients for testing
/// </summary>
public static class MockHttpClientFactory
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase,
        DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
    };

    /// <summary>
    /// Creates a mock HTTP message handler
    /// </summary>
    public static MockHttpMessageHandler CreateMockHandler()
    {
        return new MockHttpMessageHandler();
    }

    /// <summary>
    /// Creates an HttpClient with a mock handler
    /// </summary>
    public static HttpClient CreateMockHttpClient(MockHttpMessageHandler handler, string baseUrl = "https://api.example.com")
    {
        var client = handler.ToHttpClient();
        client.BaseAddress = new Uri(baseUrl);
        return client;
    }

    /// <summary>
    /// Sets up a mock response for a request
    /// </summary>
    public static void SetupMockResponse<T>(
        MockHttpMessageHandler handler,
        HttpMethod method,
        string url,
        T responseData,
        HttpStatusCode statusCode = HttpStatusCode.OK)
    {
        var json = JsonSerializer.Serialize(responseData, JsonOptions);
        handler
            .When(method, url)
            .Respond(statusCode, "application/json", json);
    }

    /// <summary>
    /// Sets up a mock POST response
    /// </summary>
    public static void SetupPostResponse<T>(
        MockHttpMessageHandler handler,
        string url,
        T responseData,
        HttpStatusCode statusCode = HttpStatusCode.Created)
    {
        SetupMockResponse(handler, HttpMethod.Post, url, responseData, statusCode);
    }

    /// <summary>
    /// Sets up a mock GET response
    /// </summary>
    public static void SetupGetResponse<T>(
        MockHttpMessageHandler handler,
        string url,
        T responseData,
        HttpStatusCode statusCode = HttpStatusCode.OK)
    {
        SetupMockResponse(handler, HttpMethod.Get, url, responseData, statusCode);
    }

    /// <summary>
    /// Sets up a mock PATCH response
    /// </summary>
    public static void SetupPatchResponse<T>(
        MockHttpMessageHandler handler,
        string url,
        T responseData,
        HttpStatusCode statusCode = HttpStatusCode.OK)
    {
        SetupMockResponse(handler, HttpMethod.Patch, url, responseData, statusCode);
    }

    /// <summary>
    /// Sets up a mock DELETE response
    /// </summary>
    public static void SetupDeleteResponse(
        MockHttpMessageHandler handler,
        string url,
        HttpStatusCode statusCode = HttpStatusCode.NoContent)
    {
        handler
            .When(HttpMethod.Delete, url)
            .Respond(statusCode);
    }
}
