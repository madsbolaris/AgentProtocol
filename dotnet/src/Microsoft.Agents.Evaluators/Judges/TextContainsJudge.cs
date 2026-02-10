using System;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that checks if actual output contains specific text strings.
/// </summary>
public class TextContainsJudge : JudgeAgentBase
{
    public override string AgentName => "text_contains";

    protected override Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        var actualText = GetTextContent(actualOutput);

        // Parse args to get the text to search for
        string[]? searchTexts = null;

        if (!string.IsNullOrWhiteSpace(judge.Args))
        {
            try
            {
                // Try to parse as JSON array
                searchTexts = JsonSerializer.Deserialize<string[]>(judge.Args);
            }
            catch
            {
                // If not JSON, treat as comma-separated list
                searchTexts = judge.Args.Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries);
            }
        }

        if (searchTexts == null || searchTexts.Length == 0)
        {
            // If no args, check if actual contains any text from reference
            var referenceText = GetTextContent(referenceOutput);
            if (string.IsNullOrWhiteSpace(referenceText))
            {
                return Task.FromResult(Failure(0.0f, "No search text specified in args or reference output"));
            }
            searchTexts = new[] { referenceText };
        }

        var found = 0;
        var missing = new System.Collections.Generic.List<string>();

        foreach (var searchText in searchTexts)
        {
            if (actualText.Contains(searchText, StringComparison.OrdinalIgnoreCase))
            {
                found++;
            }
            else
            {
                missing.Add(searchText);
            }
        }

        var score = (float)found / searchTexts.Length;
        var passed = found == searchTexts.Length;

        var result = new JudgeResult
        {
            Passed = passed,
            Score = score,
            Details = new System.Collections.Generic.Dictionary<string, object>
            {
                ["found"] = found,
                ["total"] = searchTexts.Length,
                ["missing"] = missing
            }
        };

        if (!passed)
        {
            result.Details["reason"] = $"Missing {missing.Count} required text(s): {string.Join(", ", missing)}";
        }

        return Task.FromResult(result);
    }
}
