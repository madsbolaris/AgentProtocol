using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that evaluates semantic similarity between outputs.
/// This is a stub implementation - in production, this would call an LLM or embedding service.
/// </summary>
public class SemanticSimilarityJudge : JudgeAgentBase
{
    public override string AgentName => "semantic_similarity";

    protected override Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        var actualText = GetTextContent(actualOutput);
        var referenceText = GetTextContent(referenceOutput);

        if (string.IsNullOrWhiteSpace(actualText) || string.IsNullOrWhiteSpace(referenceText))
        {
            return Task.FromResult(Failure(0.0f, "Empty actual or reference text"));
        }

        // Simplified similarity check - in production this would use embeddings or LLM
        // For now, we'll use a basic heuristic:
        // 1. Check word overlap
        // 2. Check length similarity
        // 3. Check for key phrases

        var actualWords = actualText.ToLowerInvariant()
            .Split(new[] { ' ', '\n', '\r', '\t', '.', ',', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);
        var referenceWords = referenceText.ToLowerInvariant()
            .Split(new[] { ' ', '\n', '\r', '\t', '.', ',', '!', '?' }, StringSplitOptions.RemoveEmptyEntries);

        var actualSet = new System.Collections.Generic.HashSet<string>(actualWords);
        var referenceSet = new System.Collections.Generic.HashSet<string>(referenceWords);

        var intersection = actualSet.Intersect(referenceSet).Count();
        var union = actualSet.Union(referenceSet).Count();

        var jaccardSimilarity = union > 0 ? (float)intersection / union : 0.0f;

        // Adjust for length difference
        var lengthRatio = Math.Min(actualText.Length, referenceText.Length) /
                         (float)Math.Max(actualText.Length, referenceText.Length);

        var score = (jaccardSimilarity * 0.7f) + (lengthRatio * 0.3f);

        // Threshold for passing (can be configured via args)
        var threshold = 0.7f;
        if (!string.IsNullOrWhiteSpace(judge.Args))
        {
            if (float.TryParse(judge.Args, out var customThreshold))
            {
                threshold = customThreshold;
            }
        }

        var passed = score >= threshold;

        return Task.FromResult(new JudgeResult
        {
            Passed = passed,
            Score = score,
            Details = new System.Collections.Generic.Dictionary<string, object>
            {
                ["jaccard_similarity"] = jaccardSimilarity,
                ["length_ratio"] = lengthRatio,
                ["threshold"] = threshold,
                ["note"] = "This is a simplified similarity check. Production should use embeddings or LLM."
            }
        });
    }
}
