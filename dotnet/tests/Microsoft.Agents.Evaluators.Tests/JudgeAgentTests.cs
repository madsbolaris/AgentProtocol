using System.Collections.Generic;
using System.Threading.Tasks;
using Microsoft.Agents;
using Microsoft.Agents.Evaluators;
using Microsoft.Agents.Evaluators.Judges;
using Xunit;
using XunitAssert = Xunit.Assert;

namespace Microsoft.Agents.Evaluators.Tests;

/// <summary>
/// Tests for individual judge agent implementations.
/// </summary>
public class JudgeAgentTests
{
    [Fact]
    public async Task TextContainsJudge_FindsExpectedText()
    {
        // Arrange
        var judge = new TextContainsJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "The answer is 42" }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "42" }
            }
        };
        var judgeConfig = new Judge { Agent = "text_contains" };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.True(result.Passed);
        XunitAssert.Equal(1.0f, result.Score);
    }

    [Fact]
    public async Task TextContainsJudge_HandlesMultipleSearchTerms()
    {
        // Arrange
        var judge = new TextContainsJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "The capital of France is Paris and it has great weather." }
            }
        };
        var reference = new AgentMessage();
        var judgeConfig = new Judge
        {
            Agent = "text_contains",
            Args = "[\"Paris\", \"France\"]"
        };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.True(result.Passed);
        XunitAssert.Equal(1.0f, result.Score);
    }

    [Fact]
    public async Task TextContainsJudge_FailsWhenTextMissing()
    {
        // Arrange
        var judge = new TextContainsJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "The answer is 100" }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "42" }
            }
        };
        var judgeConfig = new Judge { Agent = "text_contains" };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.False(result.Passed);
        XunitAssert.Equal(0.0f, result.Score);
    }

    [Fact]
    public async Task TextExactMatchJudge_MatchesExactly()
    {
        // Arrange
        var judge = new TextExactMatchJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Hello World" }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Hello World" }
            }
        };
        var judgeConfig = new Judge { Agent = "text_exact_match" };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.True(result.Passed);
        XunitAssert.Equal(1.0f, result.Score);
    }

    [Fact]
    public async Task TextExactMatchJudge_FailsOnMismatch()
    {
        // Arrange
        var judge = new TextExactMatchJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Hello World!" }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Hello World" }
            }
        };
        var judgeConfig = new Judge { Agent = "text_exact_match" };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.False(result.Passed);
        XunitAssert.True(result.Score > 0.8f); // Should have high similarity score
    }

    [Fact]
    public async Task TextRegexJudge_MatchesPattern()
    {
        // Arrange
        var judge = new TextRegexJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "My UUID is 123e4567-e89b-12d3-a456-426614174000" }
            }
        };
        var reference = new AgentMessage();
        var judgeConfig = new Judge
        {
            Agent = "text_regex",
            Args = "{\"pattern\": \"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\", \"flags\": \"i\"}"
        };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.True(result.Passed);
        XunitAssert.Equal(1.0f, result.Score);
    }

    [Fact]
    public async Task TextRegexJudge_FailsWhenPatternNotFound()
    {
        // Arrange
        var judge = new TextRegexJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "No UUID here" }
            }
        };
        var reference = new AgentMessage();
        var judgeConfig = new Judge
        {
            Agent = "text_regex",
            Args = "{\"pattern\": \"[0-9a-f]{8}-[0-9a-f]{4}\"}"
        };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.False(result.Passed);
        XunitAssert.Equal(0.0f, result.Score);
    }

    [Fact]
    public async Task ToolCallMatchJudge_MatchesFunctionName()
    {
        // Arrange
        var judge = new ToolCallMatchJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new FunctionCallContent
                {
                    Name = "get_weather",
                    CallId = "call-001",
                    Arguments = "{\"location\": \"San Francisco\"}"
                }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new FunctionCallContent
                {
                    Name = "get_weather"
                }
            }
        };
        var judgeConfig = new Judge { Agent = "tool_call_match" };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.True(result.Passed);
        XunitAssert.True(result.Score >= 1.0f);
    }

    [Fact]
    public async Task ToolCallMatchJudge_ValidatesArguments()
    {
        // Arrange
        var judge = new ToolCallMatchJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new FunctionCallContent
                {
                    Name = "get_weather",
                    CallId = "call-001",
                    Arguments = "{\"location\": \"San Francisco\", \"units\": \"fahrenheit\"}"
                }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new FunctionCallContent { Name = "get_weather" }
            }
        };
        var judgeConfig = new Judge
        {
            Agent = "tool_call_match",
            Args = "{\"location\": \"San Francisco\", \"units\": \"fahrenheit\"}"
        };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        XunitAssert.True(result.Passed);
        XunitAssert.Equal(1.0f, result.Score);
    }

    [Fact]
    public async Task SemanticSimilarityJudge_PassesForSimilarText()
    {
        // Arrange
        var judge = new SemanticSimilarityJudge();
        var actual = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "The capital of France is Paris." }
            }
        };
        var reference = new AgentMessage
        {
            Contents = new List<AIContent>
            {
                new TextContent { Text = "Paris is the capital city of France." }
            }
        };
        var judgeConfig = new Judge { Agent = "semantic_similarity" };
        var context = new EvaluationContext();

        // Act
        var result = await judge.EvaluateAsync(actual, reference, judgeConfig, context);

        // Assert
        // With our simplified implementation, similar texts should pass
        XunitAssert.True(result.Score > 0.5f);
    }

    [Fact]
    public void JudgeAgentRegistry_RegistersAllJudges()
    {
        // Arrange & Act
        var registry = new JudgeAgentRegistry();

        // Assert - check that common judges are registered
        XunitAssert.NotNull(registry.GetJudge("text_contains"));
        XunitAssert.NotNull(registry.GetJudge("text_exact_match"));
        XunitAssert.NotNull(registry.GetJudge("text_regex"));
        XunitAssert.NotNull(registry.GetJudge("tool_call_match"));
        XunitAssert.NotNull(registry.GetJudge("semantic_similarity"));
        XunitAssert.NotNull(registry.GetJudge("file_exists"));
        XunitAssert.NotNull(registry.GetJudge("file_min_bytes"));
    }

    [Fact]
    public void JudgeAgentRegistry_ReturnsNullForUnknownJudge()
    {
        // Arrange
        var registry = new JudgeAgentRegistry();

        // Act
        var judge = registry.GetJudge("unknown_judge");

        // Assert
        XunitAssert.Null(judge);
    }
}
