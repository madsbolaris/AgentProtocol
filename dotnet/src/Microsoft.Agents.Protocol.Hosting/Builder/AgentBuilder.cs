using Microsoft.Extensions.DependencyInjection;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.LLM;
using Microsoft.Agents.Protocol.Model;

namespace Microsoft.Agents.Protocol.Hosting.Builder;

/// <summary>
/// Builder for configuring individual agent behavior.
/// </summary>
public class AgentBuilder
{
    private readonly IServiceCollection _services;
    private string? _llmModel;
    private string? _llmInstructions;
    private Microsoft.Agents.Protocol.Model.IProtocolLLMClient? _llmClient;
    private readonly List<FunctionDefinition> _functions = new();
    private readonly List<UserMessageHandler> _userMessageHandlers = new();
    private readonly List<ReactionHandler> _reactionHandlers = new();

    /// <summary>
    /// Creates a new agent builder.
    /// </summary>
    /// <param name="services">Service collection for dependency injection.</param>
    public AgentBuilder(IServiceCollection services)
    {
        _services = services ?? throw new ArgumentNullException(nameof(services));
    }

    /// <summary>
    /// Configures the LLM to use for this agent (Vercel AI style - accepts string).
    /// Automatically creates an OpenAI client using environment variables:
    /// - FOUNDRY_ENDPOINT: LLM endpoint URL
    /// - FOUNDRY_API_KEY: API key for authentication
    /// </summary>
    /// <param name="model">Model identifier (e.g., "gpt-4", "gpt-4o-mini").</param>
    /// <param name="instructions">System instructions for the agent.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentBuilder UseLLM(string model, string instructions)
    {
        _llmModel = model ?? throw new ArgumentNullException(nameof(model));
        _llmInstructions = instructions ?? throw new ArgumentNullException(nameof(instructions));

        // Auto-create LLM client from environment variables (Vercel AI pattern)
        _llmClient = LLMClientFactory.CreateFromEnvironment(model);

        return this;
    }

    /// <summary>
    /// Configures the LLM to use for this agent (Vercel AI style - accepts provider instance).
    /// Allows explicit provider configuration for advanced scenarios.
    /// </summary>
    /// <param name="client">Pre-configured LLM client instance.</param>
    /// <param name="instructions">System instructions for the agent.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentBuilder UseLLM(Microsoft.Agents.Protocol.Model.IProtocolLLMClient client, string instructions)
    {
        _llmClient = client ?? throw new ArgumentNullException(nameof(client));
        _llmInstructions = instructions ?? throw new ArgumentNullException(nameof(instructions));
        _llmModel = client.ProviderInfo.Model;

        return this;
    }

    /// <summary>
    /// Adds functions/tools that the agent can call.
    /// </summary>
    /// <param name="configure">Function configuration action.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentBuilder AddFunctions(Action<FunctionBuilder> configure)
    {
        if (configure == null) throw new ArgumentNullException(nameof(configure));

        var functionBuilder = new FunctionBuilder();
        configure(functionBuilder);
        _functions.AddRange(functionBuilder.Build());

        return this;
    }

    /// <summary>
    /// Registers a handler for user messages.
    /// </summary>
    /// <param name="handler">The message handler.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentBuilder OnUserMessage(UserMessageHandler handler)
    {
        if (handler == null) throw new ArgumentNullException(nameof(handler));
        _userMessageHandlers.Add(handler);
        return this;
    }

    /// <summary>
    /// Registers a handler for reactions (emoji, likes, etc.).
    /// </summary>
    /// <param name="handler">The reaction handler.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentBuilder OnReaction(ReactionHandler handler)
    {
        if (handler == null) throw new ArgumentNullException(nameof(handler));
        _reactionHandlers.Add(handler);
        return this;
    }

    internal void Build()
    {
        // Register the configured agent in DI
        // This is a simplified version - full implementation would register all handlers
        if (_llmModel != null || _llmClient != null)
        {
            _services.AddSingleton(new AgentConfiguration
            {
                Model = _llmModel,
                Instructions = _llmInstructions,
                LLMClient = _llmClient,
                Functions = _functions,
                UserMessageHandlers = _userMessageHandlers,
                ReactionHandlers = _reactionHandlers
            });
        }
    }
}

/// <summary>
/// Configuration for an agent.
/// </summary>
internal class AgentConfiguration
{
    public string? Model { get; set; }
    public string? Instructions { get; set; }
    public Microsoft.Agents.Protocol.Model.IProtocolLLMClient? LLMClient { get; set; }
    public List<FunctionDefinition> Functions { get; set; } = new();
    public List<UserMessageHandler> UserMessageHandlers { get; set; } = new();
    public List<ReactionHandler> ReactionHandlers { get; set; } = new();
}

/// <summary>
/// Represents a function definition.
/// </summary>
public class FunctionDefinition
{
    public required string Name { get; set; }
    public required string Description { get; set; }
    public required Delegate Implementation { get; set; }
    public Type[] ParameterTypes { get; set; } = Array.Empty<Type>();
}

/// <summary>
/// Handler for user messages with TurnResult return value.
/// </summary>
public delegate Task<TurnResult> UserMessageHandler(
    ChatMessage message,
    IAgentContext context,
    CancellationToken cancellationToken);

/// <summary>
/// Handler for reactions with TurnResult return value.
/// </summary>
public delegate Task<TurnResult> ReactionHandler(
    ReactionContent reaction,
    IAgentContext context,
    CancellationToken cancellationToken);
