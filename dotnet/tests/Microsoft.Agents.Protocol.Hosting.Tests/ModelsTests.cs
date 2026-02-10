using System.Collections.Generic;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class ModelsTests
{
    [Fact]
    public void HealthCheck_DefaultConstructor_InitializesProperties()
    {
        // Act
        var healthCheck = new HealthCheck();

        // Assert
        healthCheck.Status.Should().Be("unknown");
        healthCheck.Checks.Should().NotBeNull();
        healthCheck.Checks.Should().BeEmpty();
        healthCheck.UptimeMs.Should().Be(0);
    }

    [Fact]
    public void HealthCheck_CanSetStatus()
    {
        // Arrange
        var healthCheck = new HealthCheck();

        // Act
        healthCheck.Status = "healthy";

        // Assert
        healthCheck.Status.Should().Be("healthy");
    }

    [Fact]
    public void HealthCheck_CanAddChecks()
    {
        // Arrange
        var healthCheck = new HealthCheck();

        // Act
        healthCheck.Checks["server"] = true;
        healthCheck.Checks["storage"] = false;

        // Assert
        healthCheck.Checks.Should().HaveCount(2);
        healthCheck.Checks["server"].Should().BeTrue();
        healthCheck.Checks["storage"].Should().BeFalse();
    }

    [Fact]
    public void HealthCheck_CanSetUptime()
    {
        // Arrange
        var healthCheck = new HealthCheck();

        // Act
        healthCheck.UptimeMs = 12345;

        // Assert
        healthCheck.UptimeMs.Should().Be(12345);
    }

    [Fact]
    public void MessageResponse_DefaultConstructor_InitializesProperties()
    {
        // Act
        var response = new MessageResponse();

        // Assert
        response.Type.Should().Be("text");
        response.Text.Should().BeNull();
        response.ThreadId.Should().BeNull();
        response.RunId.Should().BeNull();
    }

    [Fact]
    public void MessageResponse_CanSetType()
    {
        // Arrange
        var response = new MessageResponse();

        // Act
        response.Type = "image";

        // Assert
        response.Type.Should().Be("image");
    }

    [Fact]
    public void MessageResponse_CanSetText()
    {
        // Arrange
        var response = new MessageResponse();

        // Act
        response.Text = "Hello, World!";

        // Assert
        response.Text.Should().Be("Hello, World!");
    }

    [Fact]
    public void MessageResponse_CanSetThreadId()
    {
        // Arrange
        var response = new MessageResponse();

        // Act
        response.ThreadId = "thread-123";

        // Assert
        response.ThreadId.Should().Be("thread-123");
    }

    [Fact]
    public void MessageResponse_CanSetRunId()
    {
        // Arrange
        var response = new MessageResponse();

        // Act
        response.RunId = "run-456";

        // Assert
        response.RunId.Should().Be("run-456");
    }

    [Fact]
    public void StopOptions_DefaultConstructor_InitializesProperties()
    {
        // Act
        var options = new StopOptions();

        // Assert
        options.GracePeriodMs.Should().Be(30000);
        options.FinishQueued.Should().BeFalse();
    }

    [Fact]
    public void StopOptions_CanSetGracePeriodMs()
    {
        // Arrange
        var options = new StopOptions();

        // Act
        options.GracePeriodMs = 5000;

        // Assert
        options.GracePeriodMs.Should().Be(5000);
    }

    [Fact]
    public void StopOptions_CanSetFinishQueued()
    {
        // Arrange
        var options = new StopOptions();

        // Act
        options.FinishQueued = true;

        // Assert
        options.FinishQueued.Should().BeTrue();
    }

    [Fact]
    public void TurnResult_HasExpectedValues()
    {
        // Assert
        TurnResult.Continue.Should().Be(TurnResult.Continue);
        TurnResult.Consumed.Should().Be(TurnResult.Consumed);
        TurnResult.Replied.Should().Be(TurnResult.Replied);
    }

    [Fact]
    public void TurnResult_ValuesAreDistinct()
    {
        // Assert
        TurnResult.Continue.Should().NotBe(TurnResult.Consumed);
        TurnResult.Continue.Should().NotBe(TurnResult.Replied);
        TurnResult.Consumed.Should().NotBe(TurnResult.Replied);
    }

    [Fact]
    public void AgentProtocolOptions_DefaultConstructor_InitializesProperties()
    {
        // Act
        var options = new AgentProtocolOptions();

        // Assert
        options.Name.Should().Be("Agent");
        options.Description.Should().BeNull();
        options.Instructions.Should().BeNull();
        options.Model.Should().BeNull();
        options.LLMClient.Should().BeNull();
        options.EnableStreaming.Should().BeTrue();
        options.MaxToolIterations.Should().Be(10);
        options.RunTimeout.Should().BeNull();
        options.IncludeConversationHistory.Should().BeTrue();
        options.MaxHistoryLength.Should().Be(100);
        options.Metadata.Should().NotBeNull();
        options.Metadata.Should().BeEmpty();
    }

    [Fact]
    public void AgentProtocolOptions_CanSetName()
    {
        // Arrange
        var options = new AgentProtocolOptions();

        // Act
        options.Name = "TestAgent";

        // Assert
        options.Name.Should().Be("TestAgent");
    }

    [Fact]
    public void AgentProtocolOptions_CanSetDescription()
    {
        // Arrange
        var options = new AgentProtocolOptions();

        // Act
        options.Description = "Test description";

        // Assert
        options.Description.Should().Be("Test description");
    }

    [Fact]
    public void AgentProtocolOptions_CanSetModel()
    {
        // Arrange
        var options = new AgentProtocolOptions();

        // Act
        options.Model = "gpt-4";

        // Assert
        options.Model.Should().Be("gpt-4");
    }

    [Fact]
    public void AgentProtocolOptions_CanSetMaxToolIterations()
    {
        // Arrange
        var options = new AgentProtocolOptions();

        // Act
        options.MaxToolIterations = 20;

        // Assert
        options.MaxToolIterations.Should().Be(20);
    }

    [Fact]
    public void AgentProtocolOptions_CanAddMetadata()
    {
        // Arrange
        var options = new AgentProtocolOptions();

        // Act
        options.Metadata["key1"] = "value1";
        options.Metadata["key2"] = 42;

        // Assert
        options.Metadata.Should().HaveCount(2);
        options.Metadata["key1"].Should().Be("value1");
        options.Metadata["key2"].Should().Be(42);
    }
}
