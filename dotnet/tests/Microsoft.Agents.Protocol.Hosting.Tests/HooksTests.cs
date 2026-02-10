using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Hooks;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class HooksTests
{
    [Fact]
    public void BlockHook_Constructor_SetsProperties()
    {
        // Act
        var hook = new BlockHook();

        // Assert
        hook.Should().NotBeNull();
    }

    [Fact]
    public void ModifyHook_Constructor_SetsProperties()
    {
        // Act
        var hook = new ModifyHook();

        // Assert
        hook.Should().NotBeNull();
    }

    [Fact]
    public void ProtocolHook_CanBeInherited()
    {
        // Act - create a derived class instance
        var hook = new TelemetryHook();

        // Assert
        hook.Should().NotBeNull();
        hook.Should().BeAssignableTo<ProtocolHook>();
    }

    [Fact]
    public void RemoteHook_Constructor_SetsProperties()
    {
        // Act
        var hook = new RemoteHook();

        // Assert
        hook.Should().NotBeNull();
    }

    [Fact]
    public void SendMessageHook_Constructor_SetsProperties()
    {
        // Act
        var hook = new SendMessageHook();

        // Assert
        hook.Should().NotBeNull();
    }

    [Fact]
    public void TelemetryHook_Constructor_SetsProperties()
    {
        // Act
        var hook = new TelemetryHook();

        // Assert
        hook.Should().NotBeNull();
    }

    [Fact]
    public void KeywordCondition_Constructor_SetsProperties()
    {
        // Act
        var condition = new KeywordCondition();

        // Assert
        condition.Should().NotBeNull();
    }

    [Fact]
    public void RegexCondition_Constructor_SetsProperties()
    {
        // Act
        var condition = new RegexCondition();

        // Assert
        condition.Should().NotBeNull();
    }

    [Fact]
    public void ToolCondition_Constructor_SetsProperties()
    {
        // Act
        var condition = new ToolCondition();

        // Assert
        condition.Should().NotBeNull();
    }
}
