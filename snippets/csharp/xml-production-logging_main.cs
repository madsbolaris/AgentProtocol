using Serilog;
using Microsoft.Agents.Protocol.Client;

public class ProductionAgentService
{
    private readonly AgentProtocolClient _client;
    private readonly ILogger _logger;

    public ProductionAgentService(string endpoint, ILogger logger)
    {
        // Enable automatic logging to files
        _client = new AgentProtocolClient(
            endpoint,
            enableLogging: true,
            logDirectory: "logs/production"
        );
        _logger = logger;
    }

    public async Task<string> ChatAsync(string userInput, string? threadId = null)
    {
        var conversation = threadId == null
            ? _client.CreateConversation()
            : _client.ResumeConversation(threadId);

        var response = await conversation.SendAsync(userInput).ConfigureAwait(false);

        // Structured logging with message count
        _logger.Information(
            "Conversation turn completed: {ThreadId}, Messages: {Count}",
            conversation.ThreadId,
            conversation.Messages.Count);

        // Optionally stream XML to centralized storage
        await SendToObservabilityPlatform(conversation.ThreadId!, conversation.ToString()).ConfigureAwait(false);

        return response;
    }

    private async Task SendToObservabilityPlatform(string threadId, string xml)
    {
        // Send to Azure Monitor, Datadog, etc.
        await Task.CompletedTask.ConfigureAwait(false);
    }
}
