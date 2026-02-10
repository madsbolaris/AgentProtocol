using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using FluentAssertions;
using Microsoft.Agents.Protocol.Hosting.Attributes;
using Microsoft.Agents.Protocol.Hosting.Utilities;
using Xunit;

namespace Microsoft.Agents.Protocol.Hosting.Tests;

public class JsonSchemaGeneratorTests
{
    [Fact]
    public void GenerateFromMethod_GeneratesSchema_ForSimpleParameters()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.SimpleMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        schema.Should().NotBeNull();
        string type = (string)schema!["type"];
        type.Should().Be("object");

        var properties = schema["properties"] as IDictionary<string, object>;
        properties.Should().NotBeNull();
        properties.Should().ContainKey("name");
        properties.Should().ContainKey("age");
    }

    [Fact]
    public void GenerateFromMethod_IncludesRequiredParameters()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.SimpleMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var required = schema!["required"] as string[];
        required.Should().NotBeNull();
        required.Should().Contain("name");
        required.Should().Contain("age");
    }

    [Fact]
    public void GenerateFromMethod_ExcludesOptionalParameters_FromRequired()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.MethodWithOptionalParam))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var required = schema!["required"] as string[];
        required.Should().NotBeNull();
        required.Should().Contain("required");
        required.Should().NotContain("optional");
    }

    [Fact]
    public void GenerateFromMethod_IncludesDescriptions_FromAttribute()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.MethodWithDescription))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        properties.Should().ContainKey("city");

        var cityProp = properties!["city"] as IDictionary<string, object>;
        string description = (string)cityProp!["description"];
        description.Should().Be("The name of the city");
    }

    [Fact]
    public void GenerateFromMethod_MapsStringType()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.StringMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        var textProp = properties!["text"] as IDictionary<string, object>;
        string type = (string)textProp!["type"];
        type.Should().Be("string");
    }

    [Fact]
    public void GenerateFromMethod_MapsIntegerType()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.IntMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        var valueProp = properties!["value"] as IDictionary<string, object>;
        string type = (string)valueProp!["type"];
        type.Should().Be("integer");
    }

    [Fact]
    public void GenerateFromMethod_MapsNumberType()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.DoubleMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        var valueProp = properties!["value"] as IDictionary<string, object>;
        string type = (string)valueProp!["type"];
        type.Should().Be("number");
    }

    [Fact]
    public void GenerateFromMethod_MapsBooleanType()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.BoolMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        var valueProp = properties!["value"] as IDictionary<string, object>;
        string type = (string)valueProp!["type"];
        type.Should().Be("boolean");
    }

    [Fact]
    public void GenerateFromType_GeneratesSchema_ForSimpleType()
    {
        // Arrange
        var type = typeof(string);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        schema.Should().NotBeNull();
        string schemaType = (string)schema!["type"];
        schemaType.Should().Be("string");
    }

    [Fact]
    public void GenerateFromType_GeneratesSchema_ForComplexType()
    {
        // Arrange
        var type = typeof(TestDto);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        schema.Should().NotBeNull();
        string schemaType = (string)schema!["type"];
        schemaType.Should().Be("object");

        var properties = schema["properties"] as IDictionary<string, object>;
        properties.Should().NotBeNull();
        properties.Should().ContainKey("name");
        properties.Should().ContainKey("age");
    }

    [Fact]
    public void GenerateFromType_UsesCamelCase_ForPropertyNames()
    {
        // Arrange
        var type = typeof(TestDto);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        properties!.Keys.Should().Contain("name");
        properties.Keys.Should().Contain("age");
        properties.Keys.Should().NotContain("Name");
        properties.Keys.Should().NotContain("Age");
    }

    [Fact]
    public void GenerateFromType_MarksNonNullableTypes_AsRequired()
    {
        // Arrange
        var type = typeof(TestDto);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        var required = schema!["required"] as string[];
        required.Should().Contain("age"); // int is not nullable
    }

    [Fact]
    public void GenerateFromType_HandlesNullableTypes()
    {
        // Arrange
        var type = typeof(int?);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        string schemaType = (string)schema!["type"];
        schemaType.Should().Be("integer");
    }

    [Fact]
    public void GenerateFromType_HandlesEnumTypes()
    {
        // Arrange
        var type = typeof(TestEnum);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        string schemaType = (string)schema!["type"];
        schemaType.Should().Be("string");
    }

    [Fact]
    public void GenerateFromType_HandlesDateTimeTypes()
    {
        // Arrange
        var type = typeof(DateTime);

        // Act
        var schema = JsonSchemaGenerator.GenerateFromType(type) as IDictionary<string, object>;

        // Assert
        string schemaType = (string)schema!["type"];
        schemaType.Should().Be("string");
    }

    [Fact]
    public void GenerateFromType_HandlesArrayTypes()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.ArrayMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        var valuesProp = properties!["values"] as IDictionary<string, object>;
        string type = (string)valuesProp!["type"];
        type.Should().Be("array");
    }

    [Fact]
    public void GenerateFromType_HandlesListTypes()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.ListMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        var properties = schema!["properties"] as IDictionary<string, object>;
        var valuesProp = properties!["values"] as IDictionary<string, object>;
        string type = (string)valuesProp!["type"];
        type.Should().Be("array");
    }

    [Fact]
    public void GenerateFromMethod_HandlesMethodWithNoParameters()
    {
        // Arrange
        var method = typeof(TestMethods).GetMethod(nameof(TestMethods.NoParamsMethod))!;

        // Act
        var schema = JsonSchemaGenerator.GenerateFromMethod(method) as IDictionary<string, object>;

        // Assert
        schema.Should().NotBeNull();
        var properties = schema!["properties"] as IDictionary<string, object>;
        properties.Should().BeEmpty();

        var required = schema["required"] as string[];
        required.Should().BeEmpty();
    }

    // Test helper classes
    public static class TestMethods
    {
        public static void SimpleMethod(string name, int age) { }
        public static void MethodWithOptionalParam(string required, string optional = "default") { }
        public static void MethodWithDescription([Description("The name of the city")] string city) { }
        public static void StringMethod(string text) { }
        public static void IntMethod(int value) { }
        public static void DoubleMethod(double value) { }
        public static void BoolMethod(bool value) { }
        public static void ArrayMethod(int[] values) { }
        public static void ListMethod(List<string> values) { }
        public static void NoParamsMethod() { }
    }

    public class TestDto
    {
        public string? Name { get; set; }
        public int Age { get; set; }

        [Description("Email address")]
        public string? Email { get; set; }
    }

    public enum TestEnum
    {
        Value1,
        Value2,
        Value3
    }
}
