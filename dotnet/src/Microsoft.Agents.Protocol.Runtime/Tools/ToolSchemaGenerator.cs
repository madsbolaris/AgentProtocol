// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.

using System;
using System.Collections.Generic;
using System.Reflection;

namespace Microsoft.Agents.Protocol.Runtime.Tools;

/// <summary>
/// Generates JSON schemas from .NET methods using reflection.
/// Shared utility across Client and Hosting SDKs for consistent schema generation.
/// </summary>
public static class ToolSchemaGenerator
{
    /// <summary>
    /// Generates a JSON schema from a delegate's parameters.
    /// </summary>
    /// <param name="handler">The delegate to analyze</param>
    /// <returns>JSON schema object</returns>
    public static object GenerateSchema(Delegate handler)
    {
        if (handler == null)
            throw new ArgumentNullException(nameof(handler));

        var method = handler.Method;
        var parameters = method.GetParameters();

        var properties = new Dictionary<string, object>();
        var required = new List<string>();

        foreach (var param in parameters)
        {
            if (param.Name == null) continue;

            properties[param.Name] = new
            {
                type = GetJsonType(param.ParameterType),
                description = $"Parameter {param.Name}"
            };

            if (!param.IsOptional && !param.HasDefaultValue)
            {
                required.Add(param.Name);
            }
        }

        return new
        {
            type = "object",
            properties,
            required
        };
    }

    /// <summary>
    /// Maps .NET types to JSON schema types.
    /// </summary>
    private static string GetJsonType(Type type)
    {
        // Handle nullable types
        var underlyingType = Nullable.GetUnderlyingType(type) ?? type;

        // Handle enums
        if (underlyingType.IsEnum)
            return "string";

        // Handle arrays and collections
        if (underlyingType.IsArray ||
            (underlyingType.IsGenericType && underlyingType.GetGenericTypeDefinition() == typeof(List<>)))
            return "array";

        // Map primitive types
        return Type.GetTypeCode(underlyingType) switch
        {
            TypeCode.String => "string",
            TypeCode.Int16 or TypeCode.Int32 or TypeCode.Int64 or
            TypeCode.UInt16 or TypeCode.UInt32 or TypeCode.UInt64 or
            TypeCode.Byte or TypeCode.SByte => "integer",
            TypeCode.Single or TypeCode.Double or TypeCode.Decimal => "number",
            TypeCode.Boolean => "boolean",
            TypeCode.DateTime => "string",
            _ => "object"
        };
    }
}
