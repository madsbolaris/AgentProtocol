using System;
using System.Xml;
using System.Xml.Serialization;
using Microsoft.Agents.Abstractions.Models;
using Xunit;

namespace Microsoft.Agents.Xml.Tests;

/// <summary>
/// Auto-generated enum value tests.
/// Tests that all enum values serialize and deserialize correctly.
/// </summary>
public class GeneratedEnumValueTests
{
    #region ChatRole Enum Tests

    [Fact]
    public void Test_ChatRole_System_Value()
    {
        // Arrange: Get enum value
        var enumValue = ChatRole.System;

        // Act: Serialize to string
        var serialized = enumValue.ToString();

        // Assert: Value serializes correctly
        Assert.NotNull(serialized);
        Assert.NotEmpty(serialized);

        // Act: Parse back
        var parsed = Enum.Parse<ChatRole>(serialized);

        // Assert: Round-trip successful
        Assert.Equal(enumValue, parsed);
    }

    [Fact]
    public void Test_ChatRole_Developer_Value()
    {
        // Arrange: Get enum value
        var enumValue = ChatRole.Developer;

        // Act: Serialize to string
        var serialized = enumValue.ToString();

        // Assert: Value serializes correctly
        Assert.NotNull(serialized);
        Assert.NotEmpty(serialized);

        // Act: Parse back
        var parsed = Enum.Parse<ChatRole>(serialized);

        // Assert: Round-trip successful
        Assert.Equal(enumValue, parsed);
    }

    [Fact]
    public void Test_ChatRole_Agent_Value()
    {
        // Arrange: Get enum value
        var enumValue = ChatRole.Agent;

        // Act: Serialize to string
        var serialized = enumValue.ToString();

        // Assert: Value serializes correctly
        Assert.NotNull(serialized);
        Assert.NotEmpty(serialized);

        // Act: Parse back
        var parsed = Enum.Parse<ChatRole>(serialized);

        // Assert: Round-trip successful
        Assert.Equal(enumValue, parsed);
    }

    [Fact]
    public void Test_ChatRole_User_Value()
    {
        // Arrange: Get enum value
        var enumValue = ChatRole.User;

        // Act: Serialize to string
        var serialized = enumValue.ToString();

        // Assert: Value serializes correctly
        Assert.NotNull(serialized);
        Assert.NotEmpty(serialized);

        // Act: Parse back
        var parsed = Enum.Parse<ChatRole>(serialized);

        // Assert: Round-trip successful
        Assert.Equal(enumValue, parsed);
    }

    [Fact]
    public void Test_ChatRole_Tool_Value()
    {
        // Arrange: Get enum value
        var enumValue = ChatRole.Tool;

        // Act: Serialize to string
        var serialized = enumValue.ToString();

        // Assert: Value serializes correctly
        Assert.NotNull(serialized);
        Assert.NotEmpty(serialized);

        // Act: Parse back
        var parsed = Enum.Parse<ChatRole>(serialized);

        // Assert: Round-trip successful
        Assert.Equal(enumValue, parsed);
    }

    [Fact]
    public void Test_ChatRole_Channel_Value()
    {
        // Arrange: Get enum value
        var enumValue = ChatRole.Channel;

        // Act: Serialize to string
        var serialized = enumValue.ToString();

        // Assert: Value serializes correctly
        Assert.NotNull(serialized);
        Assert.NotEmpty(serialized);

        // Act: Parse back
        var parsed = Enum.Parse<ChatRole>(serialized);

        // Assert: Round-trip successful
        Assert.Equal(enumValue, parsed);
    }

    [Fact]
    public void Test_ChatRole_AllValuesAreValid()
    {
        // Arrange: Get all enum values
        var allValues = Enum.GetValues<ChatRole>();

        // Assert: Each value can be serialized and deserialized
        foreach (var value in allValues)
        {
            var serialized = value.ToString();
            Assert.NotNull(serialized);
            var parsed = Enum.Parse<ChatRole>(serialized);
            Assert.Equal(value, parsed);
        }
    }

    #endregion

}