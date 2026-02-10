using System;
using System.Linq;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators.Judges;

/// <summary>
/// Judge that validates tool/function call parameters.
/// </summary>
public class ToolCallMatchJudge : JudgeAgentBase
{
    public override string AgentName => "tool_call_match";

    protected override Task<JudgeResult> EvaluateInternalAsync(
        ChatMessage actualOutput,
        ChatMessage referenceOutput,
        Judge judge,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        // Find function call in actual output
        var actualFunctionCall = actualOutput?.Contents?
            .OfType<FunctionCallContent>()
            .FirstOrDefault();

        if (actualFunctionCall == null)
        {
            return Task.FromResult(Failure(0.0f, "No function call found in actual output"));
        }

        // Find reference function call
        var referenceFunctionCall = referenceOutput?.Contents?
            .OfType<FunctionCallContent>()
            .FirstOrDefault();

        if (referenceFunctionCall == null)
        {
            return Task.FromResult(Failure(0.0f, "No function call found in reference output"));
        }

        var issues = new System.Collections.Generic.List<string>();
        var checks = 0;
        var passed = 0;

        // Check function name
        checks++;
        if (actualFunctionCall.Name == referenceFunctionCall.Name)
        {
            passed++;
        }
        else
        {
            issues.Add($"Function name mismatch: expected '{referenceFunctionCall.Name}', got '{actualFunctionCall.Name}'");
        }

        // Check arguments if specified
        if (!string.IsNullOrWhiteSpace(judge.Args))
        {
            try
            {
                var expectedArgs = JsonSerializer.Deserialize<JsonElement>(judge.Args);
                var actualArgs = string.IsNullOrWhiteSpace(actualFunctionCall.Arguments)
                    ? JsonDocument.Parse("{}").RootElement
                    : JsonSerializer.Deserialize<JsonElement>(actualFunctionCall.Arguments);

                foreach (var prop in expectedArgs.EnumerateObject())
                {
                    checks++;
                    if (actualArgs.TryGetProperty(prop.Name, out var actualValue))
                    {
                        if (JsonElementEquals(prop.Value, actualValue))
                        {
                            passed++;
                        }
                        else
                        {
                            issues.Add($"Argument '{prop.Name}': expected {prop.Value}, got {actualValue}");
                        }
                    }
                    else
                    {
                        issues.Add($"Missing argument: '{prop.Name}'");
                    }
                }
            }
            catch (Exception ex)
            {
                return Task.FromResult(Failure(0.0f, $"Failed to parse args: {ex.Message}"));
            }
        }

        var score = checks > 0 ? (float)passed / checks : 0.0f;
        var allPassed = passed == checks;

        return Task.FromResult(new JudgeResult
        {
            Passed = allPassed,
            Score = score,
            Details = new System.Collections.Generic.Dictionary<string, object>
            {
                ["function_name"] = actualFunctionCall.Name,
                ["checks_passed"] = passed,
                ["checks_total"] = checks,
                ["issues"] = issues
            }
        });
    }

    private static bool JsonElementEquals(JsonElement a, JsonElement b)
    {
        if (a.ValueKind != b.ValueKind)
            return false;

        return a.ValueKind switch
        {
            JsonValueKind.String => a.GetString() == b.GetString(),
            JsonValueKind.Number => Math.Abs(a.GetDouble() - b.GetDouble()) < 0.0001,
            JsonValueKind.True or JsonValueKind.False => a.GetBoolean() == b.GetBoolean(),
            JsonValueKind.Null => true,
            _ => a.GetRawText() == b.GetRawText()
        };
    }
}
