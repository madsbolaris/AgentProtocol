using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.Agents;

namespace Microsoft.Agents.Evaluators;

/// <summary>
/// Runs evaluations from EvalThread definitions.
/// </summary>
public class EvalRunner
{
    private readonly JudgeAgentRegistry _judgeRegistry;
    private readonly IAgentRunner? _agentRunner;

    public EvalRunner(JudgeAgentRegistry? judgeRegistry = null, IAgentRunner? agentRunner = null)
    {
        _judgeRegistry = judgeRegistry ?? new JudgeAgentRegistry();
        _agentRunner = agentRunner;
    }

    /// <summary>
    /// Executes an evaluation thread.
    /// </summary>
    public async Task<EvalResult> RunAsync(EvalThread evalThread, CancellationToken cancellationToken = default)
    {
        var startTime = DateTime.UtcNow;

        var result = new EvalResult
        {
            ThreadId = evalThread.ThreadId,
            Description = evalThread.Description,
            Timestamp = startTime
        };

        var context = new EvaluationContext
        {
            EvalThread = evalThread,
            ThreadHistory = new List<ChatMessage>(),
            JudgeResults = new Dictionary<string, JudgeResult>()
        };

        var repeatCount = evalThread.Repeat ?? 1;
        var allRunResults = new List<EvalRunResult>();

        for (var run = 0; run < repeatCount; run++)
        {
            var runResult = await ExecuteSingleRunAsync(evalThread, context, run + 1, cancellationToken);
            allRunResults.Add(runResult);

            // Reset context for next run
            if (run < repeatCount - 1)
            {
                context.ThreadHistory.Clear();
                context.JudgeResults.Clear();
            }
        }

        // Aggregate results
        result.Runs = allRunResults;
        result.TotalRuns = allRunResults.Count;
        result.PassedRuns = allRunResults.Count(r => r.Passed);
        result.FailedRuns = allRunResults.Count(r => !r.Passed);
        result.Passed = AggregatePassResults(allRunResults, evalThread);

        var endTime = DateTime.UtcNow;
        var totalDuration = (endTime - startTime).TotalMilliseconds;
        result.TotalDurationMs = (int)totalDuration;
        result.AvgDurationMs = allRunResults.Count > 0 ? (float)totalDuration / allRunResults.Count : 0;

        // Count total asserts
        result.TotalAsserts = allRunResults.Sum(r => r.Expects?.Sum(e => e.Asserts?.Count ?? 0) ?? 0);
        result.PassedAsserts = allRunResults.Sum(r => r.Expects?.Sum(e => e.Asserts?.Count(a => a.Passed) ?? 0) ?? 0);
        result.FailedAsserts = result.TotalAsserts - result.PassedAsserts;

        return result;
    }

    private async Task<EvalRunResult> ExecuteSingleRunAsync(
        EvalThread evalThread,
        EvaluationContext context,
        int runNumber,
        CancellationToken cancellationToken)
    {
        var startTime = DateTime.UtcNow;

        var runResult = new EvalRunResult
        {
            RunNumber = runNumber
        };

        try
        {
            if (evalThread.Elements == null || evalThread.Elements.Count == 0)
            {
                runResult.Error = "No elements in eval thread";
                return runResult;
            }

            foreach (var element in evalThread.Elements)
            {
                if (element is ChatMessage message)
                {
                    context.ThreadHistory.Add(message);
                }
                else if (element is Expect expectation)
                {
                    var expectResult = await EvaluateExpectationAsync(expectation, context, cancellationToken);
                    runResult.Expects ??= new List<ExpectResult>();
                    runResult.Expects.Add(expectResult);

                    if (!expectResult.Passed)
                    {
                        runResult.Passed = false;
                    }
                }
                else if (element is EvalRun)
                {
                    // EvalRun configuration is processed at the thread level
                }
            }

            runResult.Passed = runResult.Expects?.All(r => r.Passed) ?? true;
        }
        catch (Exception ex)
        {
            runResult.Error = ex.Message;
            runResult.Passed = false;
        }
        finally
        {
            var endTime = DateTime.UtcNow;
            runResult.DurationMs = (int)(endTime - startTime).TotalMilliseconds;
        }

        return runResult;
    }

    private async Task<ExpectResult> EvaluateExpectationAsync(
        Expect expectation,
        EvaluationContext context,
        CancellationToken cancellationToken)
    {
        var expectResult = new ExpectResult
        {
            Name = expectation.Name
        };

        context.CurrentExpectation = expectation;

        try
        {
            // Get actual output (last agent message in history)
            var actualOutput = context.ThreadHistory
                .LastOrDefault(m => m is AgentMessage) as AgentMessage;

            if (actualOutput == null)
            {
                expectResult.Passed = false;
                return expectResult;
            }

            // Run all judges
            var judgeResultsList = new List<JudgeResult>();
            var judgeResultsDict = new Dictionary<string, JudgeResult>();

            if (expectation.Judges != null)
            {
                foreach (var judge in expectation.Judges)
                {
                    var judgeAgent = _judgeRegistry.GetJudge(judge.Agent);
                    if (judgeAgent == null)
                    {
                        var errorResult = new JudgeResult
                        {
                            Agent = judge.Agent,
                            As = judge.As ?? judge.Agent,
                            Passed = false,
                            Score = 0.0f,
                            Error = $"Judge agent '{judge.Agent}' not found"
                        };
                        judgeResultsList.Add(errorResult);
                        judgeResultsDict[judge.As ?? judge.Agent] = errorResult;
                        continue;
                    }

                    var judgeResult = await judgeAgent.EvaluateAsync(
                        actualOutput,
                        expectation.ReferenceOutput,
                        judge,
                        context,
                        cancellationToken);

                    judgeResult.Agent = judge.Agent;
                    judgeResult.As = judge.As ?? judge.Agent;

                    var varName = judge.As ?? judge.Agent;
                    judgeResultsList.Add(judgeResult);
                    judgeResultsDict[varName] = judgeResult;
                    context.JudgeResults[varName] = judgeResult;
                }
            }

            expectResult.Judges = judgeResultsList;

            // Evaluate assertions
            var assertResults = new List<AssertResult>();
            if (expectation.Asserts != null)
            {
                foreach (var assert in expectation.Asserts)
                {
                    var assertResult = EvaluateAssertion(assert, judgeResultsDict);
                    assertResults.Add(assertResult);
                }
            }

            expectResult.Asserts = assertResults;
            expectResult.Passed = (assertResults.Count == 0 || assertResults.All(a => a.Passed)) &&
                                  judgeResultsList.All(j => string.IsNullOrEmpty(j.Error));
        }
        catch (Exception ex)
        {
            expectResult.Passed = false;
        }

        return expectResult;
    }

    private AssertResult EvaluateAssertion(Assert assert, Dictionary<string, JudgeResult> judgeResults)
    {
        var assertResult = new AssertResult
        {
            Expression = assert.Expression
        };

        try
        {
            // Simple expression evaluation
            // In production, this should use a CEL evaluator
            var expression = assert.Expression?.Trim() ?? string.Empty;

            // Handle simple cases
            if (expression.Contains(".passed"))
            {
                var varName = expression.Split('.')[0].Trim();
                if (judgeResults.TryGetValue(varName, out var judgeResult))
                {
                    assertResult.Passed = judgeResult.Passed;
                    assertResult.Value = judgeResult.Passed;
                }
                else
                {
                    assertResult.Passed = false;
                    assertResult.Value = false;
                    assertResult.Error = $"Judge result '{varName}' not found";
                }
            }
            else if (expression.Contains(".score"))
            {
                var parts = expression.Split(new[] { ' ', '>', '<', '=', '&', '|' }, StringSplitOptions.RemoveEmptyEntries);
                var varName = parts[0].Split('.')[0].Trim();

                if (judgeResults.TryGetValue(varName, out var judgeResult))
                {
                    // Simplified evaluation - in production use CEL
                    assertResult.Passed = judgeResult.Score >= 0.7f;
                    assertResult.Value = assertResult.Passed;
                }
                else
                {
                    assertResult.Passed = false;
                    assertResult.Value = false;
                    assertResult.Error = $"Judge result '{varName}' not found";
                }
            }
            else
            {
                // For complex expressions, we'd use a CEL evaluator
                // For now, just check if all referenced judges passed
                var passed = true;
                foreach (var judgeResult in judgeResults.Values)
                {
                    if (!judgeResult.Passed)
                    {
                        passed = false;
                        break;
                    }
                }
                assertResult.Passed = passed;
                assertResult.Value = passed;
            }
        }
        catch (Exception ex)
        {
            assertResult.Passed = false;
            assertResult.Value = false;
            assertResult.Error = $"Assert evaluation failed: {ex.Message}";
        }

        return assertResult;
    }

    private bool AggregatePassResults(List<EvalRunResult> runResults, EvalThread evalThread)
    {
        if (runResults.Count == 0)
            return false;

        // If no repeat, just return the single result
        if (runResults.Count == 1)
            return runResults[0].Passed;

        // Calculate pass rate
        var passCount = runResults.Count(r => r.Passed);
        var passRate = (float)passCount / runResults.Count;

        // Check against minPassRate from asserts (if any)
        // For now, use 100% as default
        var requiredPassRate = 1.0f;

        return passRate >= requiredPassRate;
    }
}

/// <summary>
/// Interface for running the actual agent to get responses.
/// This is optional - evaluations can also use pre-recorded responses.
/// </summary>
public interface IAgentRunner
{
    Task<ChatMessage> RunAgentAsync(List<ChatMessage> history, CancellationToken cancellationToken);
}
