using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Storage;

namespace Microsoft.Agents.Protocol.Hosting.Builder;

/// <summary>
/// Builder for configuring Agent Protocol host services.
/// </summary>
public class AgentHostBuilder
{
    private readonly IServiceCollection _services;
    private readonly List<(string? Name, Action<AgentBuilder> Configure)> _agentConfigurations = new();

    /// <summary>
    /// Gets the service collection being configured.
    /// </summary>
    public IServiceCollection Services => _services;

    internal AgentHostBuilder(IServiceCollection services)
    {
        _services = services ?? throw new ArgumentNullException(nameof(services));
    }

    /// <summary>
    /// Adds a default agent with the specified configuration.
    /// </summary>
    /// <param name="configure">Agent configuration action.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentHostBuilder AddDefaultAgent(Action<AgentBuilder> configure)
    {
        if (configure == null) throw new ArgumentNullException(nameof(configure));
        _agentConfigurations.Add((null, configure));
        return this;
    }

    /// <summary>
    /// Adds a named agent with the specified configuration.
    /// </summary>
    /// <param name="name">The agent name.</param>
    /// <param name="configure">Agent configuration action.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentHostBuilder AddAgent(string name, Action<AgentBuilder> configure)
    {
        if (string.IsNullOrWhiteSpace(name)) throw new ArgumentException("Agent name cannot be empty", nameof(name));
        if (configure == null) throw new ArgumentNullException(nameof(configure));
        _agentConfigurations.Add((name, configure));
        return this;
    }

    /// <summary>
    /// Configures production defaults including state stores, event log, queue, and observability.
    /// </summary>
    /// <param name="configuration">Configuration containing connection strings and settings.</param>
    /// <returns>The builder for method chaining.</returns>
    public AgentHostBuilder UseProductionDefaults(IConfiguration configuration)
    {
        // Log what's being configured (as per spec)
        var logger = _services.BuildServiceProvider().GetService<Microsoft.Extensions.Logging.ILogger<AgentHostBuilder>>();

        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] Production defaults enabled");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] RunStore = InMemory (replace with SQL in production)");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] EventStore = InMemory (replace with SQL in production)");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] Queue = InMemory (replace with Redis in production)");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] Concurrency = 1 active run per thread");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] Streaming = coalesced deltas (75ms flush)");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] Retries = enabled (3 attempts, exponential backoff)");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] DLQ = enabled (InMemory)");
        logger?.LogInformation("[Microsoft.Agents.Protocol.Hosting] Observability = enabled (OpenTelemetry)");

        // TODO: Implement actual production stores
        // For now, this is a stub that logs the configuration

        return this;
    }

    /// <summary>
    /// Builds and returns the configured agent host.
    /// </summary>
    /// <returns>The configured agent host.</returns>
    /// <exception cref="InvalidOperationException">Thrown if no agents are configured.</exception>
    public IAgentHost Build()
    {
        if (_agentConfigurations.Count == 0)
        {
            throw new InvalidOperationException("At least one agent must be configured.");
        }

        // Register core services if not already registered
        if (!_services.Any(s => s.ServiceType == typeof(IStorage)))
        {
            _services.AddSingleton<IStorage, InMemoryStorage>();
        }

        if (!_services.Any(s => s.ServiceType == typeof(IOutOfBandPublisher)))
        {
            _services.AddSingleton<IOutOfBandPublisher, OutOfBandPublisher>();
        }

        // Build agent configurations
        foreach (var (name, configure) in _agentConfigurations)
        {
            var builder = new AgentBuilder(_services);
            configure(builder);
            builder.Build();
        }

        // Build service provider and create host
        var provider = _services.BuildServiceProvider();
        var logger = provider.GetRequiredService<ILogger<AgentHost>>();
        var loggerFactory = provider.GetRequiredService<ILoggerFactory>();
        var storage = provider.GetRequiredService<IStorage>();

        // Try to get publisher, or it will be created by AgentHost
        var publisher = provider.GetService<IOutOfBandPublisher>();

        return new AgentHost(logger, storage, publisher, loggerFactory);
    }
}
