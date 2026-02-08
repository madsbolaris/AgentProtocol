using Microsoft.Agents.Xml.Generated.Models;
using AgentThread = Microsoft.Agents.Xml.Generated.Models.Thread;

namespace Microsoft.Agents.Xml.Validation;

/// <summary>
/// Provides context for validation operations, enabling cross-message and thread-level validation.
/// </summary>
public class ValidationContext
{
    /// <summary>
    /// Gets the registry of all messages in the thread, keyed by message-id.
    /// </summary>
    public Dictionary<string, ChatMessage> MessageRegistry { get; } = new();

    /// <summary>
    /// Gets the registry of all function calls, keyed by call-id.
    /// </summary>
    public Dictionary<string, FunctionCallContent> FunctionCallRegistry { get; } = new();

    /// <summary>
    /// Gets the registry of all function results, keyed by call-id.
    /// </summary>
    public Dictionary<string, FunctionResultContent> FunctionResultRegistry { get; } = new();

    /// <summary>
    /// Gets the thread being validated, if available.
    /// </summary>
    public AgentThread? Thread { get; set; }

    /// <summary>
    /// Registers a message in the context.
    /// </summary>
    public void RegisterMessage(ChatMessage message)
    {
        if (!string.IsNullOrEmpty(message.MessageId))
        {
            MessageRegistry[message.MessageId] = message;
        }
    }

    /// <summary>
    /// Registers a function call in the context.
    /// </summary>
    public void RegisterFunctionCall(FunctionCallContent functionCall)
    {
        if (!string.IsNullOrEmpty(functionCall.CallId))
        {
            FunctionCallRegistry[functionCall.CallId] = functionCall;
        }
    }

    /// <summary>
    /// Registers a function result in the context.
    /// </summary>
    public void RegisterFunctionResult(FunctionResultContent functionResult)
    {
        if (!string.IsNullOrEmpty(functionResult.CallId))
        {
            FunctionResultRegistry[functionResult.CallId] = functionResult;
        }
    }

    /// <summary>
    /// Checks if a message with the given ID exists in the registry.
    /// </summary>
    public bool MessageExists(string messageId)
    {
        return MessageRegistry.ContainsKey(messageId);
    }

    /// <summary>
    /// Checks if a function call with the given call-id exists in the registry.
    /// </summary>
    public bool FunctionCallExists(string callId)
    {
        return FunctionCallRegistry.ContainsKey(callId);
    }

    /// <summary>
    /// Checks if a function result with the given call-id exists in the registry.
    /// </summary>
    public bool FunctionResultExists(string callId)
    {
        return FunctionResultRegistry.ContainsKey(callId);
    }

    /// <summary>
    /// Gets a message by its message-id.
    /// </summary>
    public ChatMessage? GetMessage(string messageId)
    {
        return MessageRegistry.TryGetValue(messageId, out var message) ? message : null;
    }

    /// <summary>
    /// Gets a function call by its call-id.
    /// </summary>
    public FunctionCallContent? GetFunctionCall(string callId)
    {
        return FunctionCallRegistry.TryGetValue(callId, out var call) ? call : null;
    }

    /// <summary>
    /// Gets a function result by its call-id.
    /// </summary>
    public FunctionResultContent? GetFunctionResult(string callId)
    {
        return FunctionResultRegistry.TryGetValue(callId, out var result) ? result : null;
    }
}
