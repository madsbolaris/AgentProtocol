using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Protocol.Sdk.Core;

/// <summary>
/// Handler for user, system, or agent messages
/// </summary>
public delegate Task MessageHandler<TContext>(
    IMessageContext<TContext> context,
    ChatMessage message,
    CancellationToken cancellationToken) where TContext : class;

/// <summary>
/// Handler for tool/function calls
/// </summary>
/// <returns>Result object that will be serialized and sent back to the LLM</returns>
public delegate Task<object> ToolCallHandler<TContext>(
    IToolCallContext<TContext> context,
    FunctionCallContent toolCall,
    CancellationToken cancellationToken) where TContext : class;

/// <summary>
/// Lifecycle hook for run events
/// </summary>
public delegate Task RunLifecycleHook<TContext>(
    IRunContext<TContext> context,
    CancellationToken cancellationToken) where TContext : class;

/// <summary>
/// Lifecycle hook for tool execution events
/// </summary>
public delegate Task ToolLifecycleHook<TContext>(
    IToolCallContext<TContext> context,
    object? result,
    CancellationToken cancellationToken) where TContext : class;

/// <summary>
/// Lifecycle hook for streaming events
/// </summary>
public delegate Task StreamLifecycleHook<TContext>(
    IStreamContext<TContext> context,
    AgentMessageDelta delta,
    CancellationToken cancellationToken) where TContext : class;

/// <summary>
/// Handler for custom events.
/// Used to augment LLM understanding with domain-specific knowledge.
/// </summary>
public delegate Task CustomEventHandler<TContext>(
    IMessageContext<TContext> context,
    AIContent eventContent,
    CancellationToken cancellationToken) where TContext : class;
