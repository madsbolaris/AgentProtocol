using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators;

/// <summary>
/// Interface for judge agents that evaluate agent outputs against expected behavior.
/// </summary>
public interface IJudgeAgent
{
    /// <summary>
    /// Gets the name of this judge agent (e.g., "text_contains", "semantic_similarity").
    /// </summary>
    string AgentName { get; }

    /// <summary>
    /// Evaluates the actual output against the reference output and judge parameters.
    /// </summary>
    /// <param name="actualOutput">The actual agent output to evaluate</param>
    /// <param name="referenceOutput">The expected/reference output for comparison</param>
    /// <param name="judge">The judge configuration including scope and args</param>
    /// <param name="context">The full evaluation context including thread history</param>
    /// <param name="cancellationToken">Cancellation token</param>
    /// <returns>Judge result containing pass/fail, score, and details</returns>
    Task<JudgeResult> EvaluateAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken = default);
}
