using Microsoft.Extensions.DependencyInjection;
using Microsoft.Agents.Protocol.Hosting.Builder;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Extension methods for registering Agent Protocol host services.
/// </summary>
public static class ServiceCollectionExtensions
{
    /// <summary>
    /// Adds Agent Protocol host services with fluent configuration API.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <returns>Agent host builder for fluent configuration.</returns>
    public static AgentHostBuilder AddAgentHost(this IServiceCollection services)
    {
        if (services == null) throw new ArgumentNullException(nameof(services));

        // Register logging if not already present
        if (!services.Any(s => s.ServiceType == typeof(Microsoft.Extensions.Logging.ILoggerFactory)))
        {
            services.AddLogging();
        }

        // Register core services
        // Storage and Publisher will be registered in Build() if not already present

        var builder = new AgentHostBuilder(services);
        return builder;
    }

    /// <summary>
    /// Adds Agent Protocol services with fluent builder configuration (Vercel AI style).
    /// Use this for the simplified builder API that matches TypeScript/Python patterns.
    /// </summary>
    /// <param name="services">The service collection.</param>
    /// <param name="configure">Configuration action for the agent host.</param>
    /// <returns>The service collection for method chaining.</returns>
    public static IServiceCollection AddAgentProtocol(
        this IServiceCollection services,
        Action<AgentHostBuilder> configure)
    {
        if (services == null) throw new ArgumentNullException(nameof(services));
        if (configure == null) throw new ArgumentNullException(nameof(configure));

        var builder = services.AddAgentHost();
        configure(builder);
        builder.Build();

        return services;
    }
}
