using System;
using System.Collections.Generic;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Core;

namespace Microsoft.Agents.Protocol.Hosting.Runtime;

/// <summary>
/// Executes agent protocol runs by orchestrating message handling,
/// tool execution, and lifecycle hooks.
/// </summary>
internal class AgentProtocolRunner<TContext> where TContext : class
{
    private readonly AgentProtocolApplication<TContext> _application;
    private readonly AgentProtocolOptions _options;

    public AgentProtocolRunner(
        AgentProtocolApplication<TContext> application,
        AgentProtocolOptions options)
    {
        _application = application ?? throw new ArgumentNullException(nameof(application));
        _options = options ?? throw new ArgumentNullException(nameof(options));
    }

    /// <summary>
    /// Execute a run with the given messages.
    /// </summary>
    public async Task<RunResult> ExecuteRunAsync(
        RunRequest request,
        CancellationToken cancellationToken = default)
    {
        var runId = request.RunId ?? Guid.NewGuid().ToString();
        var threadId = request.ThreadId ?? Guid.NewGuid().ToString();

        // Create context for this run
        var context = await _application.CreateContextAsync(runId, threadId, cancellationToken);

        // Create run context
        var runContext = new RunContextImpl<TContext>(
            runId,
            threadId,
            request.JournalId,
            context,
            request.Messages ?? new List<ChatMessage>());

        // Execute run started hooks
        foreach (var hook in _application.RunStartedHooks)
        {
            await hook(runContext, cancellationToken);
        }

        var responses = new List<ChatMessage>();

        try
        {
            // Process each message
            foreach (var message in request.Messages ?? Enumerable.Empty<ChatMessage>())
            {
                var messageResponses = await ProcessMessageAsync(
                    runContext,
                    message,
                    cancellationToken);

                responses.AddRange(messageResponses);
            }

            // Execute run completed hooks
            foreach (var hook in _application.RunCompletedHooks)
            {
                await hook(runContext, cancellationToken);
            }

            return new RunResult
            {
                RunId = runId,
                ThreadId = threadId,
                Status = "completed",
                Messages = responses
            };
        }
        catch (Exception ex)
        {
            // Execute run completed hooks (with error)
            foreach (var hook in _application.RunCompletedHooks)
            {
                await hook(runContext, cancellationToken);
            }

            return new RunResult
            {
                RunId = runId,
                ThreadId = threadId,
                Status = "failed",
                Error = ex.Message,
                Messages = responses
            };
        }
    }

    /// <summary>
    /// Process a single message and return responses.
    /// </summary>
    private async Task<List<ChatMessage>> ProcessMessageAsync(
        RunContextImpl<TContext> runContext,
        ChatMessage message,
        CancellationToken cancellationToken)
    {
        var responses = new List<ChatMessage>();
        var messageContext = new MessageContextImpl<TContext>(runContext, message, responses);

        // Route to appropriate handler based on message role
        if (message is UserMessage)
        {
            foreach (var handler in _application.UserMessageHandlers)
            {
                await handler(messageContext, message, cancellationToken);
            }
        }
        else if (message is SystemMessage)
        {
            foreach (var handler in _application.SystemMessageHandlers)
            {
                await handler(messageContext, message, cancellationToken);
            }
        }
        else if (message is AgentMessage agentMsg)
        {
            // Process agent messages (including tool calls)
            await ProcessAgentMessageAsync(messageContext, agentMsg, cancellationToken);
        }

        // Check for tool calls in message content
        await ProcessToolCallsAsync(messageContext, message, cancellationToken);

        // Check for events in message content
        await ProcessEventsAsync(messageContext, message, cancellationToken);

        return responses;
    }

    /// <summary>
    /// Process agent messages.
    /// </summary>
    private async Task ProcessAgentMessageAsync(
        MessageContextImpl<TContext> messageContext,
        AgentMessage agentMessage,
        CancellationToken cancellationToken)
    {
        foreach (var handler in _application.AgentMessageHandlers)
        {
            await handler(messageContext, agentMessage, cancellationToken);
        }
    }

    /// <summary>
    /// Process tool calls in message content.
    /// </summary>
    private async Task ProcessToolCallsAsync(
        MessageContextImpl<TContext> messageContext,
        ChatMessage message,
        CancellationToken cancellationToken)
    {
        // Look for FunctionCallContent in message
        var toolCalls = (message as AgentMessage)?.Contents
            ?.OfType<FunctionCallContent>()
            .ToList() ?? new List<FunctionCallContent>();

        foreach (var toolCall in toolCalls)
        {
            await ExecuteToolCallAsync(messageContext, toolCall, cancellationToken);
        }
    }

    /// <summary>
    /// Execute a single tool call.
    /// </summary>
    private async Task ExecuteToolCallAsync(
        MessageContextImpl<TContext> messageContext,
        FunctionCallContent toolCall,
        CancellationToken cancellationToken)
    {
        var toolName = toolCall.Name;

        if (!_application.ToolHandlers.TryGetValue(toolName, out var handler))
        {
            // Tool not found - return error
            var errorResult = new FunctionResultContent
            {
                CallId = toolCall.CallId,
                Name = toolName,
                Result = JsonSerializer.Serialize(new { error = "Tool not found", toolName })
            };

            messageContext.Responses.Add(new ToolMessage
            {
                Contents = new List<AIContent> { errorResult }
            });
            return;
        }

        // Create tool context
        var toolContext = new ToolCallContextImpl<TContext>(
            messageContext.RunContext,
            messageContext.Message,
            toolCall);

        // Execute tool start hooks
        foreach (var hook in _application.ToolStartHooks)
        {
            await hook(toolContext, null, cancellationToken);
        }

        object? result = null;
        try
        {
            // Execute tool handler
            result = await handler(toolContext, toolCall, cancellationToken);

            // Execute tool complete hooks
            foreach (var hook in _application.ToolCompleteHooks)
            {
                await hook(toolContext, result, cancellationToken);
            }

            // Add result to responses
            var resultContent = new FunctionResultContent
            {
                CallId = toolCall.CallId,
                Name = toolName,
                Result = JsonSerializer.Serialize(result)
            };

            messageContext.Responses.Add(new ToolMessage
            {
                Contents = new List<AIContent> { resultContent }
            });
        }
        catch (Exception ex)
        {
            // Execute tool complete hooks (with error)
            foreach (var hook in _application.ToolCompleteHooks)
            {
                await hook(toolContext, null, cancellationToken);
            }

            // Add error to responses
            var errorResult = new FunctionResultContent
            {
                CallId = toolCall.CallId,
                Name = toolName,
                Result = JsonSerializer.Serialize(new { error = ex.Message })
            };

            messageContext.Responses.Add(new ToolMessage
            {
                Contents = new List<AIContent> { errorResult }
            });
        }
    }

    /// <summary>
    /// Process events in message content.
    /// </summary>
    private async Task ProcessEventsAsync(
        MessageContextImpl<TContext> messageContext,
        ChatMessage message,
        CancellationToken cancellationToken)
    {
        // Look for EventContent or MessageReactionContent in message
        var events = (message as AgentMessage)?.Contents
            ?.Where(c => c is EventContent or MessageReactionContent)
            .ToList() ?? new List<AIContent>();

        foreach (var eventContent in events)
        {
            var eventTypeName = eventContent.GetType().Name;

            if (_application.EventHandlers.TryGetValue(eventTypeName, out var handlers))
            {
                foreach (var handler in handlers)
                {
                    await handler(messageContext, eventContent, cancellationToken);
                }
            }
        }
    }
}

/// <summary>
/// Request for executing a run.
/// </summary>
public class RunRequest
{
    public string? RunId { get; set; }
    public string? ThreadId { get; set; }
    public string? JournalId { get; set; }
    public List<ChatMessage>? Messages { get; set; }
}

/// <summary>
/// Result of executing a run.
/// </summary>
public class RunResult
{
    public required string RunId { get; set; }
    public required string ThreadId { get; set; }
    public required string Status { get; set; }
    public string? Error { get; set; }
    public List<ChatMessage> Messages { get; set; } = new();
}
