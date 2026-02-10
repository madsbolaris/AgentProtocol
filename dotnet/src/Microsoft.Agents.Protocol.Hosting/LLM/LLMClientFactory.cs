using System;
using Microsoft.Agents.Protocol.Model;
using Microsoft.Agents.Protocol.Model.OpenAI;

namespace Microsoft.Agents.Protocol.Hosting.LLM;

/// <summary>
/// Factory for creating LLM clients from environment variables.
/// Supports the Vercel AI pattern where you can pass a string (model name) or provider instance.
/// </summary>
public static class LLMClientFactory
{
    /// <summary>
    /// Creates an OpenAI protocol client from environment variables.
    /// Reads FOUNDRY_ENDPOINT, FOUNDRY_API_KEY, and uses the provided model name.
    /// </summary>
    /// <param name="model">Model identifier (e.g., "gpt-4", "gpt-4o-mini").</param>
    /// <param name="options">Optional client configuration.</param>
    /// <returns>Configured OpenAI protocol client.</returns>
    /// <exception cref="InvalidOperationException">Thrown when required environment variables are missing.</exception>
    public static IProtocolLLMClient CreateFromEnvironment(
        string model,
        OpenAIProtocolClientOptions? options = null)
    {
        var endpoint = Environment.GetEnvironmentVariable("FOUNDRY_ENDPOINT");
        var apiKey = Environment.GetEnvironmentVariable("FOUNDRY_API_KEY");

        if (string.IsNullOrEmpty(endpoint))
        {
            throw new InvalidOperationException(
                "FOUNDRY_ENDPOINT environment variable is required when using string model configuration. " +
                "Set this to your LLM endpoint (e.g., 'https://api.openai.com' or Azure/Foundry endpoint).");
        }

        if (string.IsNullOrEmpty(apiKey))
        {
            throw new InvalidOperationException(
                "FOUNDRY_API_KEY environment variable is required when using string model configuration. " +
                "Set this to your API key.");
        }

        // Create OpenAI client with custom endpoint
        var endpointUri = new Uri(endpoint.TrimEnd('/') + "/openai/v1/");

        return new OpenAIProtocolClient(apiKey, endpointUri, model, options);
    }

    /// <summary>
    /// Creates an OpenAI protocol client from environment variables,
    /// reading the model name from FOUNDRY_MODEL_DEPLOYMENT.
    /// </summary>
    /// <param name="options">Optional client configuration.</param>
    /// <returns>Configured OpenAI protocol client.</returns>
    /// <exception cref="InvalidOperationException">Thrown when required environment variables are missing.</exception>
    public static IProtocolLLMClient CreateFromEnvironment(
        OpenAIProtocolClientOptions? options = null)
    {
        var model = Environment.GetEnvironmentVariable("FOUNDRY_MODEL_DEPLOYMENT");

        if (string.IsNullOrEmpty(model))
        {
            throw new InvalidOperationException(
                "FOUNDRY_MODEL_DEPLOYMENT environment variable is required when no model is specified. " +
                "Set this to your model name (e.g., 'gpt-4', 'gpt-4o-mini').");
        }

        return CreateFromEnvironment(model, options);
    }
}
