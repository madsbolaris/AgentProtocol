// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Reflection;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;

namespace Microsoft.Agents.Protocol.Runtime.Tools;

/// <summary>
/// Executes tools/functions with JSON arguments.
/// Shared utility across Client and Hosting SDKs for consistent tool execution.
/// </summary>
/// <remarks>
/// This class provides centralized tool execution logic, eliminating duplication
/// between Client SDK's ToolDefinition.ExecuteAsync and Hosting SDK's function
/// execution. Handles both synchronous and asynchronous functions, parameter
/// binding, and error handling.
/// </remarks>
public static class ToolExecutor
{
    /// <summary>
    /// Executes a tool handler with JSON arguments.
    /// </summary>
    /// <param name="handler">The delegate to execute</param>
    /// <param name="argumentsJson">JSON-encoded arguments</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Tool execution result</returns>
    /// <exception cref="ArgumentNullException">If handler or argumentsJson is null</exception>
    /// <exception cref="ArgumentException">If required parameter is missing</exception>
    /// <exception cref="JsonException">If JSON is invalid</exception>
    /// <example>
    /// <code>
    /// Func&lt;string, int, string&gt; handler = (name, age) =&gt; $"{name} is {age}";
    /// string json = "{\"name\": \"Alice\", \"age\": 30}";
    /// var result = await ToolExecutor.ExecuteAsync(handler, json);
    /// // result == "Alice is 30"
    /// </code>
    /// </example>
    public static async Task<object> ExecuteAsync(
        Delegate handler,
        string argumentsJson,
        CancellationToken cancellationToken = default)
    {
        if (handler == null)
            throw new ArgumentNullException(nameof(handler));

        if (string.IsNullOrEmpty(argumentsJson))
            throw new ArgumentNullException(nameof(argumentsJson));

        var method = handler.Method;
        var parameters = method.GetParameters();

        // Parse JSON arguments
        JsonDocument jsonDoc;
        try
        {
            jsonDoc = JsonDocument.Parse(argumentsJson);
        }
        catch (JsonException ex)
        {
            throw new ArgumentException($"Invalid JSON arguments: {ex.Message}", nameof(argumentsJson), ex);
        }

        using (jsonDoc)
        {
            var args = new object?[parameters.Length];

            // Bind parameters from JSON
            for (int i = 0; i < parameters.Length; i++)
            {
                var param = parameters[i];
                if (param.Name == null)
                    continue;

                if (jsonDoc.RootElement.TryGetProperty(param.Name, out var value))
                {
                    try
                    {
                        args[i] = JsonSerializer.Deserialize(value.GetRawText(), param.ParameterType);
                    }
                    catch (JsonException ex)
                    {
                        throw new ArgumentException(
                            $"Failed to deserialize parameter '{param.Name}' to type {param.ParameterType.Name}: {ex.Message}",
                            nameof(argumentsJson),
                            ex);
                    }
                }
                else if (param.IsOptional || param.HasDefaultValue)
                {
                    args[i] = param.DefaultValue;
                }
                else
                {
                    throw new ArgumentException(
                        $"Missing required parameter: {param.Name}",
                        nameof(argumentsJson));
                }
            }

            // Invoke the handler
            object? result;
            try
            {
                result = handler.DynamicInvoke(args);
            }
            catch (TargetInvocationException ex)
            {
                // Unwrap the inner exception to preserve original exception type
                if (ex.InnerException != null)
                    throw ex.InnerException;
                throw;
            }

            // Handle async results
            if (result is Task task)
            {
                await task.WaitAsync(cancellationToken);

                // Extract result from Task<T>
                var resultProperty = task.GetType().GetProperty("Result");
                return resultProperty?.GetValue(task) ?? string.Empty;
            }

            return result ?? string.Empty;
        }
    }

    /// <summary>
    /// Executes a tool handler with JSON arguments and returns a string result.
    /// </summary>
    /// <param name="handler">The delegate to execute</param>
    /// <param name="argumentsJson">JSON-encoded arguments</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>String representation of the result</returns>
    /// <example>
    /// <code>
    /// Func&lt;int, int, int&gt; handler = (a, b) =&gt; a + b;
    /// string json = "{\"a\": 5, \"b\": 3}";
    /// var result = await ToolExecutor.ExecuteAsStringAsync(handler, json);
    /// // result == "8"
    /// </code>
    /// </example>
    public static async Task<string> ExecuteAsStringAsync(
        Delegate handler,
        string argumentsJson,
        CancellationToken cancellationToken = default)
    {
        var result = await ExecuteAsync(handler, argumentsJson, cancellationToken);

        return result switch
        {
            string s => s,
            null => string.Empty,
            _ => result.ToString() ?? string.Empty
        };
    }
}
