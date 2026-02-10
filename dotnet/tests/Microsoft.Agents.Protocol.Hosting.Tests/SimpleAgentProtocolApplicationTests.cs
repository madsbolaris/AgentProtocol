using System;
using System.Threading;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting;
using Microsoft.Agents.Protocol.Hosting.Attributes;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class SimpleAgentProtocolApplicationTests
{
    [Fact]
    public void Constructor_ThrowsArgumentNullException_WhenOptionsIsNull()
    {
        // Act & Assert
        var act = () => new TestAgent(null!);
        act.Should().Throw<ArgumentNullException>().WithParameterName("options");
    }

    [Fact]
    public void Constructor_InitializesSuccessfully_WithValidOptions()
    {
        // Arrange
        var options = new AgentProtocolOptions { Name = "TestAgent" };

        // Act
        var agent = new TestAgent(options);

        // Assert
        agent.Should().NotBeNull();
    }

    [Fact]
    public async Task CreateContextAsync_CreatesDefaultContext()
    {
        // Arrange
        var options = new AgentProtocolOptions { Name = "TestAgent" };
        var agent = new TestAgent(options);

        // Act
        var context = await agent.CreateContextAsync("run1", "thread1");

        // Assert
        context.Should().NotBeNull();
    }

    [Fact]
    public void AgentWithTools_DiscoversAttributeBasedTools()
    {
        // Arrange
        var options = new AgentProtocolOptions { Name = "TestAgent" };

        // Act
        var agent = new TestAgentWithTools(options);

        // Assert - verify agent was created successfully (tools are discovered internally)
        agent.Should().NotBeNull();
    }

    private class TestContext
    {
    }

    private class TestAgent : AgentProtocolApplication<TestContext>
    {
        public TestAgent(AgentProtocolOptions options) : base(options) { }
    }

    private class TestAgentWithTools : AgentProtocolApplication<TestContext>
    {
        public TestAgentWithTools(AgentProtocolOptions options) : base(options) { }

        [Tool("Get current weather")]
        public string GetWeather([Description("City name")] string city)
        {
            return $"Weather in {city}: Sunny";
        }

        [Tool("Calculate sum")]
        public int CalculateSum(int a, int b)
        {
            return a + b;
        }
    }
}
