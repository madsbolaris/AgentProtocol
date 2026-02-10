using System;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Runtime;

namespace Microsoft.Extensions.DependencyInjection;

/// <summary>
/// Extension methods for registering Agent Protocol services.
/// </summary>
public static class AgentProtocolServiceCollectionExtensions
{
    /// <summary>
    /// Registers Agent Protocol services with the specified agent application.
    /// </summary>
    /// <typeparam name="TAgent">The agent application type</typeparam>
    /// <typeparam name="TContext">The context type</typeparam>
    public static IServiceCollection AddAgentProtocol<TAgent, TContext>(
        this IServiceCollection services,
        Action<AgentProtocolOptions>? configure = null)
        where TAgent : AgentProtocolApplication<TContext>
        where TContext : class
    {
        // Register options
        var options = new AgentProtocolOptions();
        configure?.Invoke(options);
        services.AddSingleton(options);

        // Register agent application
        services.AddSingleton<TAgent>();
        services.AddSingleton<AgentProtocolApplication<TContext>>(sp => sp.GetRequiredService<TAgent>());

        // Register runner
        services.AddSingleton<AgentProtocolRunner<TContext>>();

        // Add CORS for development
        services.AddCors(corsOptions =>
        {
            corsOptions.AddPolicy("AgentProtocol", policy =>
            {
                policy.AllowAnyOrigin()
                      .AllowAnyMethod()
                      .AllowAnyHeader();
            });
        });

        return services;
    }
}
