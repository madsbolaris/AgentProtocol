using System.Reflection;
using Microsoft.Agents.Protocol.Hosting.Attributes;

namespace Microsoft.Agents.Protocol.Hosting.Utilities;

/// <summary>
/// Generates JSON schemas from C# method signatures and types.
/// Used for automatic tool schema generation from [Tool] methods.
/// </summary>
public static class JsonSchemaGenerator
{
    /// <summary>
    /// Generate JSON schema from a method signature.
    /// </summary>
    public static object GenerateFromMethod(MethodInfo method)
    {
        var parameters = method.GetParameters();
        var properties = new Dictionary<string, object>();
        var required = new List<string>();

        foreach (var param in parameters)
        {
            var description = param.GetCustomAttribute<DescriptionAttribute>()?.Description ?? "";

            var propertySchema = new Dictionary<string, object>
            {
                ["type"] = GetJsonType(param.ParameterType),
                ["description"] = description
            };

            properties[param.Name!] = propertySchema;

            if (!param.HasDefaultValue)
            {
                required.Add(param.Name!);
            }
        }

        return new Dictionary<string, object>
        {
            ["type"] = "object",
            ["properties"] = properties,
            ["required"] = required.ToArray()
        };
    }

    /// <summary>
    /// Generate JSON schema from a C# type.
    /// </summary>
    public static object GenerateFromType(Type type)
    {
        if (IsSimpleType(type))
        {
            return new Dictionary<string, object>
            {
                ["type"] = GetJsonType(type)
            };
        }

        // Complex type - generate object schema
        var properties = new Dictionary<string, object>();
        var required = new List<string>();

        foreach (var prop in type.GetProperties(BindingFlags.Public | BindingFlags.Instance))
        {
            var description = prop.GetCustomAttribute<DescriptionAttribute>()?.Description ?? "";

            var propertySchema = new Dictionary<string, object>
            {
                ["type"] = GetJsonType(prop.PropertyType),
                ["description"] = description
            };

            properties[ToCamelCase(prop.Name)] = propertySchema;

            // If property is not nullable and has no default, mark as required
            if (!IsNullableType(prop.PropertyType))
            {
                required.Add(ToCamelCase(prop.Name));
            }
        }

        return new Dictionary<string, object>
        {
            ["type"] = "object",
            ["properties"] = properties,
            ["required"] = required.ToArray()
        };
    }

    /// <summary>
    /// Map C# type to JSON schema type.
    /// </summary>
    private static string GetJsonType(Type type)
    {
        // Handle nullable types
        var underlyingType = Nullable.GetUnderlyingType(type) ?? type;

        // Handle enums
        if (underlyingType.IsEnum)
        {
            return "string"; // Enums are represented as strings
        }

        // Map primitive types
        return Type.GetTypeCode(underlyingType) switch
        {
            TypeCode.String => "string",
            TypeCode.Int16 or TypeCode.Int32 or TypeCode.Int64 or
            TypeCode.UInt16 or TypeCode.UInt32 or TypeCode.UInt64 or
            TypeCode.Byte or TypeCode.SByte => "integer",
            TypeCode.Single or TypeCode.Double or TypeCode.Decimal => "number",
            TypeCode.Boolean => "boolean",
            TypeCode.DateTime => "string", // ISO 8601 string
            _ => IsCollectionType(underlyingType) ? "array" : "object"
        };
    }

    /// <summary>
    /// Check if type is a simple/primitive type.
    /// </summary>
    private static bool IsSimpleType(Type type)
    {
        var underlyingType = Nullable.GetUnderlyingType(type) ?? type;

        return underlyingType.IsPrimitive ||
               underlyingType.IsEnum ||
               underlyingType == typeof(string) ||
               underlyingType == typeof(decimal) ||
               underlyingType == typeof(DateTime) ||
               underlyingType == typeof(DateTimeOffset) ||
               underlyingType == typeof(TimeSpan) ||
               underlyingType == typeof(Guid);
    }

    /// <summary>
    /// Check if type is nullable.
    /// </summary>
    private static bool IsNullableType(Type type)
    {
        return !type.IsValueType || Nullable.GetUnderlyingType(type) != null;
    }

    /// <summary>
    /// Check if type is a collection type.
    /// </summary>
    private static bool IsCollectionType(Type type)
    {
        return type.IsArray ||
               (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(List<>)) ||
               (type.IsGenericType && type.GetGenericTypeDefinition() == typeof(IEnumerable<>)) ||
               typeof(System.Collections.IEnumerable).IsAssignableFrom(type);
    }

    /// <summary>
    /// Convert PascalCase to camelCase.
    /// </summary>
    private static string ToCamelCase(string text)
    {
        if (string.IsNullOrEmpty(text) || char.IsLower(text[0]))
            return text;

        return char.ToLowerInvariant(text[0]) + text.Substring(1);
    }
}
