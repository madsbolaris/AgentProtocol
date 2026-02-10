using System;
using System.Text.Json;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that checks if actual output matches a regular expression pattern.
/// </summary>
public class TextRegexJudge : JudgeAgentBase
{
    public override string AgentName => "text_regex";

    protected override Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        var actualText = GetTextContent(actualOutput);

        if (string.IsNullOrWhiteSpace(judge.Args))
        {
            return Task.FromResult(Failure(0.0f, "No regex pattern specified in args"));
        }

        string? pattern = null;
        RegexOptions options = RegexOptions.None;

        try
        {
            // Try to parse as JSON
            var argsDoc = JsonDocument.Parse(judge.Args);
            if (argsDoc.RootElement.TryGetProperty("pattern", out var patternElement))
            {
                pattern = patternElement.GetString();
            }
            if (argsDoc.RootElement.TryGetProperty("flags", out var flagsElement))
            {
                var flags = flagsElement.GetString();
                if (flags?.Contains('i') == true)
                    options |= RegexOptions.IgnoreCase;
                if (flags?.Contains('m') == true)
                    options |= RegexOptions.Multiline;
                if (flags?.Contains('s') == true)
                    options |= RegexOptions.Singleline;
            }
        }
        catch
        {
            // If not JSON, treat as plain pattern
            pattern = judge.Args;
        }

        if (string.IsNullOrWhiteSpace(pattern))
        {
            return Task.FromResult(Failure(0.0f, "Invalid or empty pattern"));
        }

        try
        {
            var regex = new Regex(pattern, options | RegexOptions.Compiled);
            var match = regex.Match(actualText);

            if (match.Success)
            {
                var groups = new System.Collections.Generic.Dictionary<string, string>();
                foreach (var groupName in regex.GetGroupNames())
                {
                    if (groupName != "0") // Skip the entire match group
                    {
                        groups[groupName] = match.Groups[groupName].Value;
                    }
                }

                return Task.FromResult(new JudgeResult
                {
                    Passed = true,
                    Score = 1.0f,
                    Details = new System.Collections.Generic.Dictionary<string, object>
                    {
                        ["matched_text"] = match.Value,
                        ["match_index"] = match.Index,
                        ["groups"] = groups
                    }
                });
            }

            return Task.FromResult(Failure(0.0f, $"Pattern '{pattern}' not found in output"));
        }
        catch (Exception ex)
        {
            return Task.FromResult(Failure(0.0f, $"Invalid regex pattern: {ex.Message}"));
        }
    }
}
