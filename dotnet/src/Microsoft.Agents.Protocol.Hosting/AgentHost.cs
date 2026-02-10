using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Storage;
using Microsoft.Extensions.Logging;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Implementation of IAgentHost for managing agent lifecycle.
/// </summary>
public class AgentHost : IAgentHost
{
    private readonly ILogger<AgentHost> _logger;
    private readonly IStorage _storage;
    private readonly IOutOfBandPublisher _publisher;
    private bool _isRunning = false;
    private readonly object _lock = new();
    private readonly Stopwatch _uptime = new();

    /// <summary>
    /// Creates a new AgentHost instance.
    /// </summary>
    /// <param name="logger">Logger instance.</param>
    /// <param name="storage">Storage implementation.</param>
    /// <param name="publisher">Out-of-band publisher.</param>
    /// <param name="loggerFactory">Logger factory for creating additional loggers.</param>
    public AgentHost(
        ILogger<AgentHost> logger,
        IStorage? storage = null,
        IOutOfBandPublisher? publisher = null,
        ILoggerFactory? loggerFactory = null)
    {
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _storage = storage ?? new InMemoryStorage();

        if (publisher == null && loggerFactory != null)
        {
            var publisherLogger = loggerFactory.CreateLogger<OutOfBandPublisher>();
            _publisher = new OutOfBandPublisher(publisherLogger);
        }
        else
        {
            _publisher = publisher ?? throw new ArgumentNullException(nameof(publisher),
                "Either publisher or loggerFactory must be provided");
        }
    }

    /// <inheritdoc/>
    public Task StartAsync(int port = 3000, CancellationToken cancellationToken = default)
    {
        lock (_lock)
        {
            if (_isRunning)
            {
                throw new InvalidOperationException("Agent host is already running.");
            }

            _isRunning = true;
            _uptime.Start();
        }

        _logger.LogInformation("Agent host started on port {Port}", port);
        return Task.CompletedTask;
    }

    /// <inheritdoc/>
    public async Task StopAsync(StopOptions? options = null, CancellationToken cancellationToken = default)
    {
        lock (_lock)
        {
            if (!_isRunning)
            {
                return;
            }

            _isRunning = false;
            _uptime.Stop();
        }

        options ??= new StopOptions();

        if (options.GracePeriodMs > 0)
        {
            _logger.LogInformation("Waiting {GracePeriod}ms for active runs to complete", options.GracePeriodMs);
            await Task.Delay(options.GracePeriodMs, cancellationToken);
        }

        if (options.FinishQueued)
        {
            _logger.LogInformation("Finishing queued tasks before shutdown");
            // In a real implementation, this would drain the queue
        }

        _logger.LogInformation("Agent host stopped");
    }

    /// <inheritdoc/>
    public async Task<HealthCheck> CheckHealthAsync(CancellationToken cancellationToken = default)
    {
        var health = new HealthCheck
        {
            UptimeMs = _uptime.ElapsedMilliseconds,
            Checks = new()
        };

        // Check server status
        lock (_lock)
        {
            health.Checks["server"] = _isRunning;
        }

        // Check storage
        try
        {
            health.Checks["storage"] = await _storage.CheckHealthAsync();
        }
        catch
        {
            health.Checks["storage"] = false;
        }

        // Check queue (stub - always true for now)
        health.Checks["queue"] = true;

        // Check LLM connection (optional check - true if not implemented)
        health.Checks["llmConnection"] = true;

        // Determine overall status based on critical checks
        // Server, storage, and queue are critical. LLM connection is informational.
        var criticalChecks = new[] { "server", "storage", "queue" };
        var allCriticalHealthy = criticalChecks.All(key =>
            health.Checks.ContainsKey(key) && health.Checks[key]);

        health.Status = allCriticalHealthy ? "healthy" : "degraded";

        return health;
    }

    /// <inheritdoc/>
    public IOutOfBandPublisher GetPublisher()
    {
        return _publisher;
    }

    /// <inheritdoc/>
    public async Task<MessageResponse> ProcessMessageAsync(
        string message,
        string? threadId = null,
        CancellationToken cancellationToken = default)
    {
        threadId ??= $"thread-{Guid.NewGuid():N}";
        var runId = $"run-{Guid.NewGuid():N}";

        _logger.LogInformation("Processing message in thread {ThreadId}, run {RunId}", threadId, runId);

        // In a real implementation, this would:
        // 1. Create a run
        // 2. Process the message through the agent
        // 3. Return the response

        // For now, return a stub response
        await Task.Delay(10, cancellationToken); // Simulate processing

        return new MessageResponse
        {
            Type = "text",
            Text = "Echo: " + message,
            ThreadId = threadId,
            RunId = runId
        };
    }
}
