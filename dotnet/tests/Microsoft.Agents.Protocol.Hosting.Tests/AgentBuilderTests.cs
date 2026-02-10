using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Agents;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Microsoft.Agents.Protocol.Hosting.Core;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class AgentBuilderTests
{
    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenServicesIsNull()
    {
        // Act & Assert
        var act = () => new AgentBuilder(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("services");
    }

    [Fact]
    public void UseLLM_ThrowsArgumentNullException_WhenModelIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act & Assert
        var act = () => builder.UseLLM((string)null!, "instructions");
        act.Should().Throw<ArgumentNullException>().WithParameterName("model");
    }

    [Fact]
    public void UseLLM_ThrowsArgumentNullException_WhenInstructionsIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act & Assert
        var act = () => builder.UseLLM("gpt-4", null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("instructions");
    }

    [Fact]
    public void UseLLM_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act
        var result = builder.UseLLM("gpt-4", "Test instructions");

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void AddFunctions_ThrowsArgumentNullException_WhenConfigureIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act & Assert
        var act = () => builder.AddFunctions(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("configure");
    }

    [Fact]
    public void AddFunctions_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act
        var result = builder.AddFunctions(fb =>
        {
            fb.Add("test", "Test function", () => "result");
        });

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void OnUserMessage_ThrowsArgumentNullException_WhenHandlerIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act & Assert
        var act = () => builder.OnUserMessage(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("handler");
    }

    [Fact]
    public void OnUserMessage_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act
        var result = builder.OnUserMessage((msg, ctx, ct) => Task.FromResult(TurnResult.Continue));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void OnReaction_ThrowsArgumentNullException_WhenHandlerIsNull()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act & Assert
        var act = () => builder.OnReaction(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("handler");
    }

    [Fact]
    public void OnReaction_ReturnsBuilder_ForMethodChaining()
    {
        // Arrange
        var services = new ServiceCollection();
        var builder = new AgentBuilder(services);

        // Act
        var result = builder.OnReaction((reaction, ctx, ct) => Task.FromResult(TurnResult.Continue));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void CanConfigureCompleteAgent()
    {
        // Arrange
        var services = new ServiceCollection();
        services.AddLogging();

        // Act & Assert - should not throw
        var host = services.AddAgentHost()
            .AddDefaultAgent(builder =>
            {
                builder
                    .UseLLM("gpt-4", "You are a helpful assistant")
                    .AddFunctions(fb =>
                    {
                        fb.Add("get_weather", "Get current weather", (string city) => $"Weather in {city}: Sunny");
                    })
                    .OnUserMessage((msg, ctx, ct) => Task.FromResult(TurnResult.Continue))
                    .OnReaction((reaction, ctx, ct) => Task.FromResult(TurnResult.Continue));
            })
            .Build();

        host.Should().NotBeNull();
    }
}
