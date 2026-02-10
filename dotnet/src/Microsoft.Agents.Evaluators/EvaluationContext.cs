using System.Collections.Generic;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators;

/// <summary>
/// Context information for evaluation including thread history and metadata.
/// </summary>
public class EvaluationContext
{
    /// <summary>
    /// The evaluation thread being executed.
    /// </summary>
    public EvalThread EvalThread { get; set; } = null!;

    /// <summary>
    /// All messages in the thread up to the current point.
    /// </summary>
    public List<ChatMessage> ThreadHistory { get; set; } = new();

    /// <summary>
    /// The current expectation being evaluated.
    /// </summary>
    public Expect CurrentExpectation { get; set; } = null!;

    /// <summary>
    /// Results from all judges that have executed so far.
    /// Key is the judge variable name (judge.as).
    /// </summary>
    public Dictionary<string, JudgeResult> JudgeResults { get; set; } = new();

    /// <summary>
    /// Additional metadata for the evaluation.
    /// </summary>
    public Dictionary<string, object> Metadata { get; set; } = new();
}
