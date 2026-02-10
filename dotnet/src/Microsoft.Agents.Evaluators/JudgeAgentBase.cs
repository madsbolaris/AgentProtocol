using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators;

/// <summary>
/// Base class for judge agent implementations providing common functionality.
/// </summary>
public abstract class JudgeAgentBase : IJudgeAgent
{
    /// <inheritdoc/>
    public abstract string AgentName { get; }

    /// <inheritdoc/>
    public async Task<JudgeResult> EvaluateAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken = default)
    {
        try
        {
            return await EvaluateInternalAsync(actualOutput, referenceOutput, judge, context, cancellationToken);
        }
        catch (Exception ex)
        {
            return new JudgeResult
            {
                Passed = false,
                Score = 0.0f,
                Error = $"Judge {AgentName} failed: {ex.Message}",
                Details = new System.Collections.Generic.Dictionary<string, object>
                {
                    ["exception"] = ex.ToString()
                }
            };
        }
    }

    /// <summary>
    /// Internal evaluation method to be implemented by derived classes.
    /// </summary>
    protected abstract Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken);

    /// <summary>
    /// Extracts text content from a message.
    /// </summary>
    protected string GetTextContent(ChatMessage message)
    {
        if (message?.Contents == null)
            return string.Empty;

        var textContents = message.Contents
            .OfType<TextContent>()
            .Select(t => t.Text)
            .Where(t => !string.IsNullOrEmpty(t));

        return string.Join("\n", textContents);
    }

    /// <summary>
    /// Creates a successful judge result.
    /// </summary>
    protected JudgeResult Success(float score = 1.0f, string? message = null)
    {
        return new JudgeResult
        {
            Passed = true,
            Score = score,
            Details = message != null
                ? new System.Collections.Generic.Dictionary<string, object> { ["message"] = message }
                : null
        };
    }

    /// <summary>
    /// Creates a failed judge result.
    /// </summary>
    protected JudgeResult Failure(float score = 0.0f, string? reason = null)
    {
        return new JudgeResult
        {
            Passed = false,
            Score = score,
            Details = reason != null
                ? new System.Collections.Generic.Dictionary<string, object> { ["reason"] = reason }
                : null
        };
    }
}
