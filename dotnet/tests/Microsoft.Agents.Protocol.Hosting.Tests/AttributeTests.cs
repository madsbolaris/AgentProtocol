using System;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Attributes;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class AttributeTests
{
    [Fact]
    public void ToolAttribute_Constructor_SetsDescription()
    {
        // Act
        var attr = new ToolAttribute("Test description");

        // Assert
        attr.Description.Should().Be("Test description");
    }

    [Fact]
    public void ToolAttribute_Constructor_ThrowsArgumentException_WhenDescriptionIsNull()
    {
        // Act & Assert
        var act = () => new ToolAttribute(null!);
        act.Should().Throw<ArgumentException>()
            .WithParameterName("description")
            .WithMessage("*cannot be empty*");
    }

    [Fact]
    public void ToolAttribute_Constructor_ThrowsArgumentException_WhenDescriptionIsEmpty()
    {
        // Act & Assert
        var act = () => new ToolAttribute(string.Empty);
        act.Should().Throw<ArgumentException>()
            .WithParameterName("description")
            .WithMessage("*cannot be empty*");
    }

    [Fact]
    public void ToolAttribute_Constructor_ThrowsArgumentException_WhenDescriptionIsWhitespace()
    {
        // Act & Assert
        var act = () => new ToolAttribute("   ");
        act.Should().Throw<ArgumentException>()
            .WithParameterName("description")
            .WithMessage("*cannot be empty*");
    }

    [Fact]
    public void ToolAttribute_Name_CanBeSet()
    {
        // Arrange
        var attr = new ToolAttribute("Test");

        // Act
        attr.Name = "custom_name";

        // Assert
        attr.Name.Should().Be("custom_name");
    }

    [Fact]
    public void ToolAttribute_Name_DefaultsToNull()
    {
        // Arrange & Act
        var attr = new ToolAttribute("Test");

        // Assert
        attr.Name.Should().BeNull();
    }

    [Fact]
    public void ToolAttribute_CanBeAppliedToMethod()
    {
        // Arrange
        var method = typeof(TestClass).GetMethod(nameof(TestClass.TestMethod))!;

        // Act
        var attrs = method.GetCustomAttributes(typeof(ToolAttribute), false);

        // Assert
        attrs.Should().HaveCount(1);
        var toolAttr = attrs[0] as ToolAttribute;
        toolAttr.Should().NotBeNull();
        toolAttr!.Description.Should().Be("Test tool");
    }

    [Fact]
    public void ToolAttribute_CanHaveCustomName()
    {
        // Arrange
        var method = typeof(TestClass).GetMethod(nameof(TestClass.TestMethodWithName))!;

        // Act
        var attrs = method.GetCustomAttributes(typeof(ToolAttribute), false);

        // Assert
        attrs.Should().HaveCount(1);
        var toolAttr = attrs[0] as ToolAttribute;
        toolAttr.Should().NotBeNull();
        toolAttr!.Name.Should().Be("custom_tool");
    }

    [Fact]
    public void DescriptionAttribute_Constructor_SetsDescription()
    {
        // Act
        var attr = new DescriptionAttribute("Parameter description");

        // Assert
        attr.Description.Should().Be("Parameter description");
    }

    [Fact]
    public void DescriptionAttribute_CanBeAppliedToParameter()
    {
        // Arrange
        var method = typeof(TestClass).GetMethod(nameof(TestClass.MethodWithDescription))!;
        var param = method.GetParameters()[0];

        // Act
        var attrs = param.GetCustomAttributes(typeof(DescriptionAttribute), false);

        // Assert
        attrs.Should().HaveCount(1);
        var descAttr = attrs[0] as DescriptionAttribute;
        descAttr.Should().NotBeNull();
        descAttr!.Description.Should().Be("The name parameter");
    }

    [Fact]
    public void ToolExecutionException_Constructor_SetsMessage()
    {
        // Act
        var ex = new ToolExecutionException("Test error");

        // Assert
        ex.Message.Should().Be("Test error");
    }

    [Fact]
    public void ToolExecutionException_Constructor_WithInnerException_SetsProperties()
    {
        // Arrange
        var inner = new InvalidOperationException("Inner error");

        // Act
        var ex = new ToolExecutionException("Test error", inner);

        // Assert
        ex.Message.Should().Be("Test error");
        ex.InnerException.Should().Be(inner);
    }

    [Fact]
    public void ToolExecutionException_CanBeThrown()
    {
        // Act & Assert
        Action act = () => throw new ToolExecutionException("Tool failed");
        act.Should().Throw<ToolExecutionException>()
            .WithMessage("Tool failed");
    }

    [Fact]
    public void ToolExecutionException_CanBeCaught()
    {
        // Arrange
        var thrown = false;
        var caught = false;

        // Act
        try
        {
            thrown = true;
            throw new ToolExecutionException("Tool error");
        }
        catch (ToolExecutionException)
        {
            caught = true;
        }

        // Assert
        thrown.Should().BeTrue();
        caught.Should().BeTrue();
    }

    // Test helper classes
    private class TestClass
    {
        [Tool("Test tool")]
        public void TestMethod()
        {
        }

        [Tool("Test tool with name", Name = "custom_tool")]
        public void TestMethodWithName()
        {
        }

        public void MethodWithDescription([Description("The name parameter")] string name)
        {
        }
    }
}
