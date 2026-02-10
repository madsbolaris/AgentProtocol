using System;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Builder;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class FunctionBuilderTests
{
    [Fact]
    public void Add_WithNoParameters_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add("test", "Test function", () => "result");

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Add_WithOneParameter_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add<string>("test", "Test function", (arg) => "result");

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Add_WithTwoParameters_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add<string, int>("test", "Test function", (arg1, arg2) => "result");

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Add_WithThreeParameters_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add<string, int, bool>("test", "Test function", (arg1, arg2, arg3) => "result");

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Add_AsyncWithNoParameters_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add("test", "Test function", () => Task.FromResult("result"));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Add_AsyncWithOneParameter_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add<string>("test", "Test function", (arg) => Task.FromResult("result"));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void Add_AsyncWithTwoParameters_ReturnsFunctionBuilder()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act
        var result = builder.Add<string, int>("test", "Test function", (arg1, arg2) => Task.FromResult("result"));

        // Assert
        result.Should().BeSameAs(builder);
    }

    [Fact]
    public void CanAddMultipleFunctionsInSequence()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act & Assert - should not throw
        builder
            .Add("func1", "First function", () => "result1")
            .Add<string>("func2", "Second function", (arg) => "result2")
            .Add<string, int>("func3", "Third function", (arg1, arg2) => "result3");
    }

    [Fact]
    public void CanAddAsyncFunctions()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act & Assert - should not throw
        builder
            .Add("func1", "Async no params", () => Task.FromResult("result1"))
            .Add<string>("func2", "Async one param", (arg) => Task.FromResult("result2"))
            .Add<string, int>("func3", "Async two params", (arg1, arg2) => Task.FromResult("result3"));
    }

    [Fact]
    public void CanMixSyncAndAsyncFunctions()
    {
        // Arrange
        var builder = new FunctionBuilder();

        // Act & Assert - should not throw
        builder
            .Add("sync", "Sync function", () => "sync")
            .Add("async", "Async function", () => Task.FromResult("async"))
            .Add<string>("sync_param", "Sync with param", (arg) => "result")
            .Add<string>("async_param", "Async with param", (arg) => Task.FromResult("result"));
    }
}
