namespace Microsoft.Agents.CodeGen.Utilities;

/// <summary>
/// Strategy for handling nullable types in generated C# code.
/// </summary>
public enum NullableStrategy
{
    /// <summary>
    /// Default behavior: nullable for optional reference types and value types
    /// </summary>
    Default,

    /// <summary>
    /// Force non-nullable types (used for XmlAttribute scenarios where nullable value types aren't supported)
    /// </summary>
    ForceNonNullable,

    /// <summary>
    /// Force nullable types regardless of other factors
    /// </summary>
    ForceNullable
}

/// <summary>
/// Maps TypeSpec types to C# types with support for arrays and nullable types.
/// Consolidated from multiple generators to ensure consistency.
/// </summary>
public static class TypeMapper
{
    /// <summary>
    /// Maps a TypeSpec type to its C# equivalent.
    /// </summary>
    /// <param name="typeSpecType">TypeSpec type name (e.g., "string", "int32", "utcDateTime")</param>
    /// <param name="isArray">Whether this is an array type</param>
    /// <param name="isOptional">Whether this is an optional type</param>
    /// <param name="strategy">Strategy for handling nullable types</param>
    /// <returns>C# type string (e.g., "string", "int?", "List&lt;string&gt;")</returns>
    public static string MapTypeSpecTypeToCSharp(
        string typeSpecType,
        bool isArray,
        bool isOptional,
        NullableStrategy strategy = NullableStrategy.Default)
    {
        var baseType = MapBaseType(typeSpecType);

        // Handle array types
        if (isArray)
        {
            baseType = $"List<{baseType}>";
        }

        // Handle nullable types based on strategy
        if (isOptional && ShouldBeNullable(baseType, strategy))
        {
            baseType += "?";
        }

        return baseType;
    }

    /// <summary>
    /// Maps TypeSpec base types to C# base types.
    /// </summary>
    private static string MapBaseType(string typeSpecType)
    {
        return typeSpecType switch
        {
            "string" => "string",
            "int32" => "int",
            "int64" => "long",
            "float32" => "float",
            "float64" => "double",
            "boolean" => "bool",
            "bytes" => "byte[]",
            "utcDateTime" => "DateTime",
            "unknown" => "object",
            _ when typeSpecType.StartsWith("Record<") => "Dictionary<string, object>",
            _ when typeSpecType.StartsWith("\"") => "string", // Literal type becomes string
            _ => typeSpecType // Custom type (model/enum name)
        };
    }

    /// <summary>
    /// Determines if a type should be nullable based on the strategy.
    /// </summary>
    private static bool ShouldBeNullable(string csharpType, NullableStrategy strategy)
    {
        // Handle strategy overrides
        if (strategy == NullableStrategy.ForceNullable)
            return true;

        if (strategy == NullableStrategy.ForceNonNullable)
            return false;

        // Default strategy: don't make reference types or collections nullable
        // (they're already nullable in C#)
        if (IsReferenceType(csharpType))
            return false;

        // Value types (int, bool, DateTime, etc.) should be nullable when optional
        return true;
    }

    /// <summary>
    /// Determines if a C# type is a reference type.
    /// </summary>
    private static bool IsReferenceType(string csharpType)
    {
        // Reference types and collections don't need nullable modifier
        return csharpType.Contains("string") ||
               csharpType.Contains("List<") ||
               csharpType.Contains("Dictionary<") ||
               csharpType.Contains("[]") ||
               csharpType == "object";
    }

    /// <summary>
    /// Checks if a TypeSpec type is a simple (primitive) type.
    /// Used for determining XML attribute vs element serialization.
    /// </summary>
    /// <param name="typeSpecType">TypeSpec type name</param>
    /// <returns>True if the type is a primitive type</returns>
    public static bool IsSimpleType(string typeSpecType)
    {
        return typeSpecType is "string" or "int32" or "int64" or
               "float32" or "float64" or "boolean" or "utcDateTime" or "bytes";
    }
}
