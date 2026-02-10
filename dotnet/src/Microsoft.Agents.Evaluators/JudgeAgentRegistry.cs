using System;
using System.Collections.Generic;
using Microsoft.Agents.Evaluators.Judges;

namespace Microsoft.Agents.Evaluators;

/// <summary>
/// Registry of available judge agents.
/// </summary>
public class JudgeAgentRegistry
{
    private readonly Dictionary<string, IJudgeAgent> _judges = new();

    public JudgeAgentRegistry()
    {
        // Register deterministic judges
        Register(new TextContainsJudge());
        Register(new TextExactMatchJudge());
        Register(new TextRegexJudge());
        Register(new ToolCallMatchJudge());
        Register(new FileExistsJudge());
        Register(new FileMinBytesJudge());

        // Register LLM-based judges
        Register(new SemanticSimilarityJudge());
    }

    /// <summary>
    /// Registers a judge agent.
    /// </summary>
    public void Register(IJudgeAgent judge)
    {
        _judges[judge.AgentName] = judge;
    }

    /// <summary>
    /// Gets a judge agent by name.
    /// </summary>
    public IJudgeAgent? GetJudge(string agentName)
    {
        return _judges.TryGetValue(agentName, out var judge) ? judge : null;
    }

    /// <summary>
    /// Gets all registered judge names.
    /// </summary>
    public IEnumerable<string> GetRegisteredJudgeNames()
    {
        return _judges.Keys;
    }
}
