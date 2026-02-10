using System;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that checks if actual output exactly matches the reference output.
/// </summary>
public class TextExactMatchJudge : JudgeAgentBase
{
    public override string AgentName => "text_exact_match";

    protected override Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        var actualText = GetTextContent(actualOutput).Trim();
        var referenceText = GetTextContent(referenceOutput).Trim();

        if (string.IsNullOrEmpty(referenceText))
        {
            return Task.FromResult(Failure(0.0f, "Reference output is empty"));
        }

        // Check for case-sensitive flag in args
        var caseSensitive = true;
        if (!string.IsNullOrWhiteSpace(judge.Args))
        {
            if (judge.Args.Contains("case_sensitive=false", StringComparison.OrdinalIgnoreCase) ||
                judge.Args.Contains("\"caseSensitive\":false", StringComparison.OrdinalIgnoreCase))
            {
                caseSensitive = false;
            }
        }

        var comparison = caseSensitive ? StringComparison.Ordinal : StringComparison.OrdinalIgnoreCase;
        var matches = string.Equals(actualText, referenceText, comparison);

        if (matches)
        {
            return Task.FromResult(Success(1.0f, "Exact match"));
        }

        // Calculate similarity score for partial credit
        var similarityScore = CalculateLevenshteinSimilarity(actualText, referenceText);

        return Task.FromResult(new JudgeResult
        {
            Passed = false,
            Score = similarityScore,
            Details = new System.Collections.Generic.Dictionary<string, object>
            {
                ["reason"] = "Text does not match exactly",
                ["actual_length"] = actualText.Length,
                ["reference_length"] = referenceText.Length,
                ["similarity"] = similarityScore
            }
        });
    }

    private static float CalculateLevenshteinSimilarity(string s1, string s2)
    {
        if (string.IsNullOrEmpty(s1) && string.IsNullOrEmpty(s2))
            return 1.0f;
        if (string.IsNullOrEmpty(s1) || string.IsNullOrEmpty(s2))
            return 0.0f;

        var maxLength = Math.Max(s1.Length, s2.Length);
        var distance = LevenshteinDistance(s1, s2);
        return 1.0f - ((float)distance / maxLength);
    }

    private static int LevenshteinDistance(string s1, string s2)
    {
        var matrix = new int[s1.Length + 1, s2.Length + 1];

        for (var i = 0; i <= s1.Length; i++)
            matrix[i, 0] = i;
        for (var j = 0; j <= s2.Length; j++)
            matrix[0, j] = j;

        for (var i = 1; i <= s1.Length; i++)
        {
            for (var j = 1; j <= s2.Length; j++)
            {
                var cost = s1[i - 1] == s2[j - 1] ? 0 : 1;
                matrix[i, j] = Math.Min(
                    Math.Min(matrix[i - 1, j] + 1, matrix[i, j - 1] + 1),
                    matrix[i - 1, j - 1] + cost
                );
            }
        }

        return matrix[s1.Length, s2.Length];
    }
}
