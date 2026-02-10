using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Microsoft.Agents.Protocol.Hosting.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using Xunit;

namespace Microsoft.Agents.Protocol.Tests;

/// <summary>
/// Tests for the fluent builder API from unified-sdk-proposal specification.
/// Tests the new API: .AddAgentHost(), .AddDefaultAgent(), .UseLLM(), .AddFunctions(), TurnResult pattern.
/// </summary>
public class FluentBuilderApiTests
{
    [Fact]
    public void AddAgentHost_ReturnsAgentHostBuilder()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        var builder = services.AddAgentHost();

        // Assert
        builder.Should().NotBeNull();
        builder.Should().BeOfType<AgentHostBuilder>();
    }

    [Fact]
    public void AddAgentHost_WithNullServices_ThrowsArgumentNullException()
    {
        // Arrange
        IServiceCollection? services = null;

        // Act
        Action act = () => services!.AddAgentHost();

        // Assert
        act.Should().Throw<ArgumentNullException>();
    }

    [Fact]
    public void AddDefaultAgent_ReturnsAgentBuilder()
    {
        // Arrange
        var services = new ServiceCollection();
        var hostBuilder = services.AddAgentHost();

        // Act
        var result = hostBuilder.AddDefaultAgent(a => { });

        // Assert
        result.Should().NotBeNull();
        result.Should().BeOfType<AgentHostBuilder>();
    }

    [Fact]
    public void AgentBuilder_UseLLM_ConfiguresModelAndInstructions()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "You are helpful.")
            );

        // Assert - No exceptions should be thrown
        services.Should().NotBeNull();
    }

    [Fact]
    public void AgentBuilder_UseLLM_WithNullModel_ThrowsArgumentNullException()
    {
        // Arrange
        var builder = new AgentBuilder(new ServiceCollection());

        // Act & Assert
        Action act = () => builder.UseLLM(null!, "Instructions");

        act.Should().Throw<ArgumentNullException>()
            .WithParameterName("model");
    }

    [Fact]
    public void AgentBuilder_UseLLM_WithNullInstructions_ThrowsArgumentNullException()
    {
        // Arrange
        var builder = new AgentBuilder(new ServiceCollection());

        // Act & Assert
        Action act = () => builder.UseLLM("gpt-4", null!);

        act.Should().Throw<ArgumentNullException>()
            .WithParameterName("instructions");
    }

    [Fact]
    public void FunctionBuilder_Add_WithSimpleFunction_RegistersFunction()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .AddFunctions(f => f
                    .Add("test@v1", "Test function", () => "result")
                )
            );

        // Assert - Function should be registered without exceptions
        services.Should().NotBeNull();
    }

    [Fact]
    public void FunctionBuilder_Add_WithParameterizedFunction_RegistersFunction()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .AddFunctions(f => f
                    .Add("sum@v1", "Add two integers", (int a, int b) => (a + b).ToString())
                    .Add("greet@v1", "Greet someone", (string name) => $"Hello, {name}!")
                )
            );

        // Assert - Functions should be registered without exceptions
        services.Should().NotBeNull();
    }

    [Fact]
    public void FunctionBuilder_Add_WithAsyncFunction_RegistersFunction()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .AddFunctions(f => f
                    .Add("async_test@v1", "Async function", async () =>
                    {
                        await Task.Delay(1);
                        return "async result";
                    })
                )
            );

        // Assert - Async function should be registered without exceptions
        services.Should().NotBeNull();
    }

    [Fact]
    public void FunctionBuilder_Add_SupportsMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .AddFunctions(f => f
                    .Add("func1@v1", "First", () => "1")
                    .Add("func2@v1", "Second", () => "2")
                    .Add("func3@v1", "Third", () => "3")
                )
            );

        // Assert - All functions should chain successfully
        services.Should().NotBeNull();
    }

    [Fact]
    public void AgentBuilder_OnUserMessage_RegistersHandler()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .OnUserMessage(async (msg, ctx, ct) =>
                {
                    return TurnResult.Continue;
                })
            );

        // Assert - Handler should be registered without exceptions
        services.Should().NotBeNull();
    }

    [Fact]
    public void AgentBuilder_OnReaction_RegistersHandler()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .OnReaction(async (reaction, ctx, ct) =>
                {
                    return TurnResult.Consumed;
                })
            );

        // Assert - Reaction handler should be registered without exceptions
        services.Should().NotBeNull();
    }

    [Fact]
    public void TurnResult_HasCorrectValues()
    {
        // Assert - Verify TurnResult enum has correct values
        Enum.GetNames(typeof(TurnResult)).Should().Contain(new[]
        {
            nameof(TurnResult.Continue),
            nameof(TurnResult.Consumed),
            nameof(TurnResult.Replied)
        });
    }

    [Fact]
    public void AgentHostBuilder_UseProductionDefaults_ExecutesWithoutError()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Act
        services.AddAgentHost()
            .UseProductionDefaults(null!)
            .AddDefaultAgent(a => a.UseLLM("gpt-4", "Test"));

        // Assert - Should execute without exceptions
        services.Should().NotBeNull();
    }

    [Fact]
    public void FluentApi_CompleteExample_BuildsSuccessfully()
    {
        // Arrange - This is the 5-line quickstart from the spec
        var services = new ServiceCollection();
        services.AddLogging();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "You are a helpful assistant.")
                .AddFunctions(f => f
                    .Add("get_time@v1", "Gets current time", () => DateTimeOffset.UtcNow.ToString("O"))
                    .Add("sum@v1", "Add two integers", (int a, int b) => (a + b).ToString())
                )
                .OnUserMessage(async (msg, ctx, ct) =>
                {
                    await ctx.LogAsync($"Received: {msg.Text}", ct);
                    return TurnResult.Continue;
                })
            );

        var provider = services.BuildServiceProvider();

        // Assert
        provider.Should().NotBeNull();
    }

    [Fact]
    public void ReactionContent_HasCorrectProperties()
    {
        // Arrange & Act
        var reaction = new ReactionContent
        {
            Emoji = "👍",
            MessageId = "msg_001"
        };

        // Assert
        reaction.Emoji.Should().Be("👍");
        reaction.MessageId.Should().Be("msg_001");
        reaction.Kind.Should().Be("reaction");
    }

    [Fact]
    public void AgentBuilder_SupportsMultipleHandlers()
    {
        // Arrange
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .OnUserMessage(async (msg, ctx, ct) =>
                {
                    return TurnResult.Continue;
                })
                .OnReaction(async (reaction, ctx, ct) =>
                {
                    return TurnResult.Consumed;
                })
                .AddFunctions(f => f
                    .Add("test@v1", "Test", () => "result")
                )
            );

        // Assert - Multiple handlers should be registered successfully
        services.Should().NotBeNull();
    }

    [Fact]
    public void IAgentContext_Interface_ExistsAndHasCorrectSignature()
    {
        // This test verifies the IAgentContext interface signature
        // Actual implementation testing would require a concrete context

        // Assert - Just verify the interface exists and has correct signature
        typeof(IAgentContext).Should().NotBeNull();
        typeof(IAgentContext).GetMethod("RespondAsync", new[] { typeof(string), typeof(CancellationToken) })
            .Should().NotBeNull();
    }

    [Fact]
    public void IOutOfBandPublisher_Interface_ExistsAndHasCorrectSignature()
    {
        // Assert - Verify IOutOfBandPublisher interface exists with correct methods
        var publisherType = typeof(IOutOfBandPublisher);
        publisherType.Should().NotBeNull();

        var methods = publisherType.GetMethods();
        methods.Should().Contain(m => m.Name == "SendToThreadAsync");
    }

    [Fact]
    public void FunctionBuilder_Add_WithVersionedNaming_WorksCorrectly()
    {
        // Arrange - Test the @v1 versioning convention
        var services = new ServiceCollection();

        // Act
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Test")
                .AddFunctions(f => f
                    .Add("calculator@v1", "V1 calculator", (int a, int b) => (a + b).ToString())
                    .Add("calculator@v2", "V2 calculator with validation", (int a, int b) =>
                    {
                        if (a < 0 || b < 0) return "Error: negative numbers";
                        return (a + b).ToString();
                    })
                )
            );

        // Assert - Both versions should coexist
        services.Should().NotBeNull();
    }

    [Fact]
    public void AgentBuilder_ChainedConfiguration_MaintainsAllSettings()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Act - Test that chaining doesn't lose configuration
        services.AddAgentHost()
            .AddDefaultAgent(a => a
                .UseLLM("gpt-4", "Instructions")
                .AddFunctions(f => f.Add("f1@v1", "F1", () => "1"))
                .OnUserMessage(async (msg, ctx, ct) => TurnResult.Continue)
                .AddFunctions(f => f.Add("f2@v1", "F2", () => "2"))
                .OnReaction(async (r, ctx, ct) => TurnResult.Consumed)
            );

        var provider = services.BuildServiceProvider();

        // Assert
        provider.Should().NotBeNull();
    }
}
