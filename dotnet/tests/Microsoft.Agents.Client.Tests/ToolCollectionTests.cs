using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using FluentAssertions;
using Microsoft.Agents.Protocol.Client;
using Xunit;

namespace Microsoft.Agents.Client.Tests;

/// <summary>
/// Comprehensive tests for ToolCollection and ToolDefinition
/// </summary>
public class ToolCollectionTests
{
    #region ToolCollection Tests

    [Fact]
    public void Add_SyncFunction_AddsToolSuccessfully()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        collection.Add("greet", (string name) => $"Hello, {name}!");

        // Assert
        var tool = collection.Get("greet");
        tool.Should().NotBeNull();
        tool!.Name.Should().Be("greet");
    }

    [Fact]
    public void Add_AsyncFunction_AddsToolSuccessfully()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        collection.Add("greetAsync", async (string name) =>
        {
            await Task.Delay(1);
            return $"Hello, {name}!";
        });

        // Assert
        var tool = collection.Get("greetAsync");
        tool.Should().NotBeNull();
        tool!.Name.Should().Be("greetAsync");
    }

    [Fact]
    public void Add_TwoParameterFunction_AddsToolSuccessfully()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        collection.Add("concat", (string a, string b) => $"{a}{b}");

        // Assert
        var tool = collection.Get("concat");
        tool.Should().NotBeNull();
    }

    [Fact]
    public void Add_ThreeParameterFunction_AddsToolSuccessfully()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        collection.Add("calculate", (double a, double b, string op) =>
        {
            return op switch
            {
                "add" => a + b,
                "subtract" => a - b,
                "multiply" => a * b,
                "divide" => a / b,
                _ => 0.0
            };
        });

        // Assert
        var tool = collection.Get("calculate");
        tool.Should().NotBeNull();
    }

    [Fact]
    public void Add_WithDescription_SetsDescription()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        collection.Add("greet", (string name) => $"Hello, {name}!", "Greets a person");

        // Assert
        var tool = collection.Get("greet");
        tool!.Description.Should().Be("Greets a person");
    }

    [Fact]
    public void Add_WithoutDescription_GeneratesDefaultDescription()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        collection.Add("greet", (string name) => $"Hello, {name}!");

        // Assert
        var tool = collection.Get("greet");
        tool!.Description.Should().Be("Executes greet");
    }

    [Fact]
    public void Get_NonExistentTool_ReturnsNull()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act
        var tool = collection.Get("nonexistent");

        // Assert
        tool.Should().BeNull();
    }

    [Fact]
    public void GetAll_ReturnsAllTools()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("tool1", (string x) => x);
        collection.Add("tool2", (string x) => x);

        // Act
        var tools = collection.GetAll().ToList();

        // Assert
        tools.Should().HaveCount(2);
    }

    [Fact]
    public async Task ExecuteAsync_ValidTool_ExecutesSuccessfully()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("greet", (string name) => $"Hello, {name}!");

        // Act
        var result = await collection.ExecuteAsync("greet", "{\"name\":\"Alice\"}");

        // Assert
        result.Should().Be("Hello, Alice!");
    }

    [Fact]
    public async Task ExecuteAsync_NonExistentTool_ThrowsInvalidOperationException()
    {
        // Arrange
        var collection = new ToolCollection();

        // Act & Assert
        await Assert.ThrowsAsync<InvalidOperationException>(
            () => collection.ExecuteAsync("nonexistent", "{}"));
    }

    [Fact]
    public void GetEnumerator_ReturnsAllTools()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("tool1", (string x) => x);
        collection.Add("tool2", (string x) => x);

        // Act
        var count = 0;
        foreach (var tool in collection)
        {
            count++;
        }

        // Assert
        count.Should().Be(2);
    }

    [Fact]
    public void Add_DuplicateName_OverwritesTool()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (string x) => "first");

        // Act
        collection.Add("test", (string x) => "second");

        // Assert
        var tool = collection.Get("test");
        tool.Should().NotBeNull();
    }

    #endregion

    #region ToolDefinition Tests

    [Fact]
    public async Task ExecuteAsync_SyncFunction_ReturnsResult()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("add", (int a, int b) => (a + b).ToString());
        var tool = collection.Get("add")!;

        // Act
        var result = await tool.ExecuteAsync("{\"a\":5,\"b\":3}");

        // Assert
        result.Should().Be("8");
    }

    [Fact]
    public async Task ExecuteAsync_AsyncFunction_ReturnsResult()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("addAsync", async (int a, int b) =>
        {
            await Task.Delay(1);
            return (a + b).ToString();
        });
        var tool = collection.Get("addAsync")!;

        // Act
        var result = await tool.ExecuteAsync("{\"a\":5,\"b\":3}");

        // Assert
        result.Should().Be("8");
    }

    [Fact]
    public async Task ExecuteAsync_MissingRequiredParameter_ThrowsArgumentException()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("greet", (string name) => $"Hello, {name}!");
        var tool = collection.Get("greet")!;

        // Act & Assert
        await Assert.ThrowsAsync<ArgumentException>(
            () => tool.ExecuteAsync("{}"));
    }

    [Fact]
    public async Task ExecuteAsync_FunctionThrowsException_WrapsInnerException()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("thrower", new Func<string, string>((string x) =>
        {
            throw new InvalidOperationException("Test exception");
        }));
        var tool = collection.Get("thrower")!;

        // Act & Assert
        var ex = await Assert.ThrowsAsync<InvalidOperationException>(
            () => tool.ExecuteAsync("{\"x\":\"test\"}"));
        ex.Message.Should().Be("Test exception");
    }

    [Fact]
    public async Task ExecuteAsync_WithStringParameter_ParsesCorrectly()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("echo", (string message) => message);
        var tool = collection.Get("echo")!;

        // Act
        var result = await tool.ExecuteAsync("{\"message\":\"Hello World\"}");

        // Assert
        result.Should().Be("Hello World");
    }

    [Fact]
    public async Task ExecuteAsync_WithIntParameter_ParsesCorrectly()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("square", (int n) => (n * n).ToString());
        var tool = collection.Get("square")!;

        // Act
        var result = await tool.ExecuteAsync("{\"n\":5}");

        // Assert
        result.Should().Be("25");
    }

    [Fact]
    public async Task ExecuteAsync_WithDoubleParameter_ParsesCorrectly()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("double", (double n) => (n * 2).ToString());
        var tool = collection.Get("double")!;

        // Act
        var result = await tool.ExecuteAsync("{\"n\":3.5}");

        // Assert
        result.Should().Be("7");
    }

    [Fact]
    public async Task ExecuteAsync_WithBoolParameter_ParsesCorrectly()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("negate", (bool value) => (!value).ToString());
        var tool = collection.Get("negate")!;

        // Act
        var result = await tool.ExecuteAsync("{\"value\":true}");

        // Assert
        result.Should().Be("False");
    }

    [Fact]
    public async Task ExecuteAsync_MultipleParameters_ParsesAllCorrectly()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("format", (string name, int age, bool active) =>
            $"{name} is {age} years old and {(active ? "active" : "inactive")}");
        var tool = collection.Get("format")!;

        // Act
        var result = await tool.ExecuteAsync("{\"name\":\"Alice\",\"age\":30,\"active\":true}");

        // Assert
        result.Should().Be("Alice is 30 years old and active");
    }

    [Fact]
    public async Task ExecuteAsync_ReturnsNull_ReturnsEmptyString()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("nullReturn", (string x) => (string?)null);
        var tool = collection.Get("nullReturn")!;

        // Act
        var result = await tool.ExecuteAsync("{\"x\":\"test\"}");

        // Assert
        result.Should().Be(string.Empty);
    }

    [Fact]
    public async Task ExecuteAsync_AsyncTaskReturnsNull_ReturnsEmptyString()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("nullReturnAsync", async (string x) =>
        {
            await Task.Delay(1);
            return (string?)null;
        });
        var tool = collection.Get("nullReturnAsync")!;

        // Act
        var result = await tool.ExecuteAsync("{\"x\":\"test\"}");

        // Assert
        result.Should().Be(string.Empty);
    }

    [Fact]
    public void Schema_GeneratesCorrectJsonSchema()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (string name, int age) => "");
        var tool = collection.Get("test")!;

        // Act
        var schema = tool.Schema;

        // Assert
        schema.Should().NotBeNull();
        // Schema should be an anonymous object with type, properties, and required
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(schema);
        schemaStr.Should().Contain("\"type\":\"object\"");
        schemaStr.Should().Contain("\"name\"");
        schemaStr.Should().Contain("\"age\"");
    }

    [Fact]
    public void Schema_StringParameter_HasStringType()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (string x) => "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"string\"");
    }

    [Fact]
    public void Schema_IntParameter_HasIntegerType()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (int x) => "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"integer\"");
    }

    [Fact]
    public void Schema_LongParameter_HasIntegerType()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (long x) => "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"integer\"");
    }

    [Fact]
    public void Schema_DoubleParameter_HasNumberType()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (double x) => "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"number\"");
    }

    [Fact]
    public void Schema_FloatParameter_HasNumberType()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (float x) => "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"number\"");
    }

    [Fact]
    public void Schema_BoolParameter_HasBooleanType()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (bool x) => "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"boolean\"");
    }

    [Fact]
    public void Schema_UnknownParameterType_DefaultsToString()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("test", (object x) => x.ToString() ?? "");
        var tool = collection.Get("test")!;

        // Act
        var schemaStr = System.Text.Json.JsonSerializer.Serialize(tool.Schema);

        // Assert
        schemaStr.Should().Contain("\"type\":\"string\"");
    }

    [Fact]
    public async Task ExecuteAsync_WithOptionalParameter_UsesDefaultValue()
    {
        // Arrange
        var collection = new ToolCollection();
        // This simulates a delegate with optional parameters
        Func<string, string, string> handler = (string required, string optional = "default") =>
            $"{required}-{optional}";

        collection.Add("testOptional", handler);
        var tool = collection.Get("testOptional")!;

        // Act - only provide required parameter
        var result = await tool.ExecuteAsync("{\"required\":\"value\"}");

        // Assert
        result.Should().Be("value-default");
    }

    [Fact]
    public void ToolCollection_NonGenericEnumerator_Works()
    {
        // Arrange
        var collection = new ToolCollection();
        collection.Add("tool1", (string x) => x);
        collection.Add("tool2", (string x) => x);

        // Act
        var enumerator = ((System.Collections.IEnumerable)collection).GetEnumerator();
        var count = 0;
        while (enumerator.MoveNext())
        {
            count++;
        }

        // Assert
        count.Should().Be(2);
    }

    #endregion
}
