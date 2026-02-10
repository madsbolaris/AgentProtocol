using System.Reflection;
using System.Text.Json;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Attributes;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Agents.Protocol.Hosting.Hooks;
using Microsoft.Agents.Protocol.Hosting.Utilities;

namespace Microsoft.Agents.Protocol.Hosting;

/// <summary>
/// Base class for building Agent Protocol agents.
/// Provides handler registration for messages, tools, and lifecycle events.
/// Automatically discovers methods marked with [Tool] attribute.
/// </summary>
/// <typeparam name="TContext">Type of custom context data</typeparam>
public abstract class AgentProtocolApplication<TContext> where TContext : class
{
    protected readonly AgentProtocolOptions Options;

    // Handler registrations
    private readonly Dictionary<string, ToolCallHandler<TContext>> _toolHandlers = new();
    private readonly Dictionary<string, MethodInfo> _toolMethods = new(); // For attribute-based tools
    private readonly List<MessageHandler<TContext>> _userMessageHandlers = new();
    private readonly List<MessageHandler<TContext>> _systemMessageHandlers = new();
    private readonly List<MessageHandler<TContext>> _agentMessageHandlers = new();

    // Event handlers
    private readonly Dictionary<string, List<CustomEventHandler<TContext>>> _eventHandlers = new();

    // Lifecycle hooks (imperative)
    private readonly List<RunLifecycleHook<TContext>> _onRunStarted = new();
    private readonly List<RunLifecycleHook<TContext>> _onRunCompleted = new();
    private readonly List<ToolLifecycleHook<TContext>> _onToolStart = new();
    private readonly List<ToolLifecycleHook<TContext>> _onToolComplete = new();
    private readonly List<StreamLifecycleHook<TContext>> _onStreamChunk = new();

    // Protocol hooks (declarative)
    private readonly List<ProtocolHook> _protocolHooks = new();

    // Tool definitions
    private readonly Dictionary<string, ToolDefinition> _tools = new();

    protected AgentProtocolApplication(AgentProtocolOptions options)
    {
        Options = options ?? throw new ArgumentNullException(nameof(options));

        // Discover tools via reflection (attribute-based)
        DiscoverAttributeBasedTools();
    }

    #region Handler Registration

    /// <summary>
    /// Register a handler for user messages
    /// </summary>
    protected void OnUserMessage(MessageHandler<TContext> handler)
    {
        _userMessageHandlers.Add(handler);
    }

    /// <summary>
    /// Register a handler for system messages
    /// </summary>
    protected void OnSystemMessage(MessageHandler<TContext> handler)
    {
        _systemMessageHandlers.Add(handler);
    }

    /// <summary>
    /// Register a handler for agent messages
    /// </summary>
    protected void OnAgentMessage(MessageHandler<TContext> handler)
    {
        _agentMessageHandlers.Add(handler);
    }

    /// <summary>
    /// Register a handler for a specific tool/function call
    /// </summary>
    protected void OnToolCall(string toolName, ToolCallHandler<TContext> handler, ToolDefinition? definition = null)
    {
        _toolHandlers[toolName] = handler;
        if (definition != null)
        {
            _tools[toolName] = definition;
        }
    }

    /// <summary>
    /// Register a tool definition without a handler (for tools handled by LLM)
    /// </summary>
    protected void RegisterTool(ToolDefinition tool)
    {
        _tools[tool.Name] = tool;
    }

    /// <summary>
    /// Register an event handler for custom events
    /// </summary>
    protected void OnEvent<TEventContent>(CustomEventHandler<TContext> handler) where TEventContent : AIContent
    {
        var eventType = typeof(TEventContent).Name;
        if (!_eventHandlers.ContainsKey(eventType))
        {
            _eventHandlers[eventType] = new List<CustomEventHandler<TContext>>();
        }
        _eventHandlers[eventType].Add(handler);
    }

    /// <summary>
    /// Register an event handler for a specific event type name
    /// </summary>
    protected void OnEvent<TEventContent>(string eventTypeName, CustomEventHandler<TContext> handler) where TEventContent : AIContent
    {
        if (!_eventHandlers.ContainsKey(eventTypeName))
        {
            _eventHandlers[eventTypeName] = new List<CustomEventHandler<TContext>>();
        }
        _eventHandlers[eventTypeName].Add(handler);
    }

    #endregion

    #region Lifecycle Hooks (Imperative)

    /// <summary>
    /// Called when a run starts
    /// </summary>
    protected void OnRunStarted(RunLifecycleHook<TContext> hook)
    {
        _onRunStarted.Add(hook);
    }

    /// <summary>
    /// Called when a run completes (success, failure, or cancellation)
    /// </summary>
    protected void OnRunCompleted(RunLifecycleHook<TContext> hook)
    {
        _onRunCompleted.Add(hook);
    }

    /// <summary>
    /// Called before a tool is executed
    /// </summary>
    protected void OnToolStart(ToolLifecycleHook<TContext> hook)
    {
        _onToolStart.Add(hook);
    }

    /// <summary>
    /// Called after a tool completes
    /// </summary>
    protected void OnToolComplete(ToolLifecycleHook<TContext> hook)
    {
        _onToolComplete.Add(hook);
    }

    /// <summary>
    /// Called for each streaming chunk
    /// </summary>
    protected void OnStreamChunk(StreamLifecycleHook<TContext> hook)
    {
        _onStreamChunk.Add(hook);
    }

    #endregion

    #region Protocol Hooks (Declarative)

    /// <summary>
    /// Add a Protocol hook (RemoteHook, BlockHook, ModifyHook, etc.)
    /// </summary>
    protected void AddHook(ProtocolHook hook)
    {
        _protocolHooks.Add(hook);
    }

    #endregion

    #region Factory Method for Context

    /// <summary>
    /// Create custom context instance for a run.
    /// Override this to provide custom context creation logic.
    /// </summary>
    public virtual Task<TContext> CreateContextAsync(
        string runId,
        string threadId,
        CancellationToken cancellationToken = default)
    {
        // Default implementation requires parameterless constructor
        var context = Activator.CreateInstance<TContext>();
        return Task.FromResult(context);
    }

    #endregion

    #region Tool Discovery (Attribute-Based)

    /// <summary>
    /// Discover methods marked with [Tool] attribute via reflection.
    /// Automatically generates JSON schemas and registers tools.
    /// </summary>
    private void DiscoverAttributeBasedTools()
    {
        var type = GetType();
        var methods = type.GetMethods(BindingFlags.Public | BindingFlags.Instance)
            .Where(m => m.GetCustomAttribute<ToolAttribute>() != null);

        foreach (var method in methods)
        {
            var toolAttr = method.GetCustomAttribute<ToolAttribute>()!;

            // Determine tool name (use attribute Name property or convert method name to snake_case)
            var toolName = !string.IsNullOrEmpty(toolAttr.Name)
                ? toolAttr.Name
                : ConvertToSnakeCase(method.Name);

            // Generate JSON schema from method signature
            var schema = JsonSchemaGenerator.GenerateFromMethod(method);

            // Create tool definition
            var toolDefinition = new ToolDefinition
            {
                Name = toolName,
                Description = toolAttr.Description,
                ParametersSchema = schema
            };

            // Register tool definition
            _tools[toolName] = toolDefinition;

            // Store method for later invocation
            _toolMethods[toolName] = method;

            // Create handler that invokes the method via reflection
            var handler = CreateToolHandlerFromMethod(method);
            _toolHandlers[toolName] = handler;
        }
    }

    /// <summary>
    /// Create a tool handler that invokes a method via reflection.
    /// </summary>
    private ToolCallHandler<TContext> CreateToolHandlerFromMethod(MethodInfo method)
    {
        return async (context, toolCall, ct) =>
        {
            try
            {
                // Deserialize arguments from JSON
                var parameters = method.GetParameters();
                var args = new object?[parameters.Length];

                // Parse arguments JSON
                JsonDocument? argsDoc = null;
                if (!string.IsNullOrEmpty(toolCall.Arguments))
                {
                    argsDoc = JsonDocument.Parse(toolCall.Arguments);
                }

                for (int i = 0; i < parameters.Length; i++)
                {
                    var param = parameters[i];

                    if (argsDoc != null && argsDoc.RootElement.TryGetProperty(param.Name!, out var jsonValue))
                    {
                        // Deserialize parameter value
                        args[i] = JsonSerializer.Deserialize(jsonValue.GetRawText(), param.ParameterType);
                    }
                    else if (param.HasDefaultValue)
                    {
                        // Use default value
                        args[i] = param.DefaultValue;
                    }
                    else
                    {
                        // Required parameter missing
                        throw new ArgumentException($"Required parameter '{param.Name}' not provided");
                    }
                }

                // Invoke method
                var result = method.Invoke(this, args);

                // Handle async methods
                if (result is Task task)
                {
                    await task;

                    // Get result from Task<T>
                    var resultProperty = task.GetType().GetProperty("Result");
                    result = resultProperty?.GetValue(task);
                }

                // Return result (will be serialized to JSON)
                return result ?? new { success = true };
            }
            catch (TargetInvocationException ex)
            {
                // Unwrap ToolExecutionException
                if (ex.InnerException is ToolExecutionException toolEx)
                {
                    // Return error content that LLM can understand
                    return new
                    {
                        error = true,
                        code = "tool_execution_error",
                        message = toolEx.Message
                    };
                }

                throw;
            }
        };
    }

    /// <summary>
    /// Convert PascalCase to snake_case for tool names.
    /// </summary>
    private static string ConvertToSnakeCase(string text)
    {
        if (string.IsNullOrEmpty(text))
            return text;

        var result = new System.Text.StringBuilder();
        result.Append(char.ToLowerInvariant(text[0]));

        for (int i = 1; i < text.Length; i++)
        {
            var c = text[i];
            if (char.IsUpper(c))
            {
                result.Append('_');
                result.Append(char.ToLowerInvariant(c));
            }
            else
            {
                result.Append(c);
            }
        }

        return result.ToString();
    }

    #endregion

    #region Internal Accessors (for Runner)

    internal IReadOnlyDictionary<string, ToolCallHandler<TContext>> ToolHandlers => _toolHandlers;
    internal IReadOnlyDictionary<string, MethodInfo> ToolMethods => _toolMethods;
    internal IReadOnlyList<MessageHandler<TContext>> UserMessageHandlers => _userMessageHandlers;
    internal IReadOnlyList<MessageHandler<TContext>> SystemMessageHandlers => _systemMessageHandlers;
    internal IReadOnlyList<MessageHandler<TContext>> AgentMessageHandlers => _agentMessageHandlers;
    internal IReadOnlyDictionary<string, List<CustomEventHandler<TContext>>> EventHandlers => _eventHandlers;
    internal IReadOnlyList<RunLifecycleHook<TContext>> RunStartedHooks => _onRunStarted;
    internal IReadOnlyList<RunLifecycleHook<TContext>> RunCompletedHooks => _onRunCompleted;
    internal IReadOnlyList<ToolLifecycleHook<TContext>> ToolStartHooks => _onToolStart;
    internal IReadOnlyList<ToolLifecycleHook<TContext>> ToolCompleteHooks => _onToolComplete;
    internal IReadOnlyList<StreamLifecycleHook<TContext>> StreamChunkHooks => _onStreamChunk;
    internal IReadOnlyList<ProtocolHook> ProtocolHooks => _protocolHooks;
    internal IReadOnlyDictionary<string, ToolDefinition> Tools => _tools;

    #endregion
}
