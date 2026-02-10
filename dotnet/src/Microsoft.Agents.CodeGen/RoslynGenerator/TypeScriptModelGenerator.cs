using System.Text;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates TypeScript type definitions from TypeSpec definitions.
/// Produces clean, idiomatic TypeScript with JSDoc comments.
/// </summary>
public class TypeScriptModelGenerator
{
    private readonly string _rootNamespace;
    private Dictionary<string, string> _typeLocations = new();
    private string _currentDirectory = "";

    public TypeScriptModelGenerator(string rootNamespace = "")
    {
        _rootNamespace = rootNamespace;
    }

    public void SetTypeLocations(Dictionary<string, string> typeLocations)
    {
        _typeLocations = typeLocations;
    }

    public List<string> GenerateModels(TypeSpecModel typeSpec, string outputDirectory)
    {
        var generatedFiles = new List<string>();

        Directory.CreateDirectory(outputDirectory);

        // Extract the current directory name (common, messages, or content)
        _currentDirectory = Path.GetFileName(outputDirectory);

        // Generate enums
        foreach (var enumDef in typeSpec.Enums)
        {
            var filePath = Path.Combine(outputDirectory, $"{enumDef.Name}.ts");
            var code = GenerateEnum(enumDef);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate model interfaces
        foreach (var modelDef in typeSpec.Models)
        {
            var filePath = Path.Combine(outputDirectory, $"{modelDef.Name}.ts");
            var code = GenerateModel(modelDef, typeSpec);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate union types
        foreach (var unionDef in typeSpec.Unions)
        {
            var filePath = Path.Combine(outputDirectory, $"{unionDef.Name}.ts");
            var code = GenerateUnion(unionDef);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate index.ts barrel export
        var indexPath = Path.Combine(outputDirectory, "index.ts");
        var indexCode = GenerateIndexFile(typeSpec);
        File.WriteAllText(indexPath, indexCode);
        generatedFiles.Add(indexPath);

        return generatedFiles;
    }

    private string GenerateEnum(EnumDefinition enumDef)
    {
        var sb = new StringBuilder();

        // Add JSDoc comment
        if (!string.IsNullOrWhiteSpace(enumDef.Documentation))
        {
            sb.AppendLine("/**");
            sb.AppendLine($" * {enumDef.Documentation}");
            sb.AppendLine(" */");
        }

        // Generate string literal union type (more idiomatic than enum in modern TS)
        sb.AppendLine($"export type {enumDef.Name} =");
        for (int i = 0; i < enumDef.Members.Count; i++)
        {
            var member = enumDef.Members[i];
            var value = member.Value ?? NamingConventions.ToCamelCase(member.Name);

            if (i == enumDef.Members.Count - 1)
            {
                sb.AppendLine($"  | '{value}';");
            }
            else
            {
                sb.AppendLine($"  | '{value}'");
            }
        }

        sb.AppendLine();

        // Also generate const object for runtime access
        sb.AppendLine($"export const {enumDef.Name}Values = {{");
        foreach (var member in enumDef.Members)
        {
            var pascalName = NamingConventions.ToPascalCase(member.Name);
            var value = member.Value ?? NamingConventions.ToCamelCase(member.Name);
            sb.AppendLine($"  {pascalName}: '{value}' as const,");
        }
        sb.AppendLine($"}} as const;");

        return sb.ToString();
    }

    private string GenerateModel(ModelDefinition modelDef, TypeSpecModel? typeSpec = null)
    {
        var sb = new StringBuilder();

        // Collect imports for referenced types
        var imports = CollectImports(modelDef, typeSpec);

        // Remove self-import (can happen with recursive types like JSONSchema)
        imports.Remove(modelDef.Name);

        if (imports.Any())
        {
            foreach (var import in imports)
            {
                var importPath = GetImportPath(import);
                sb.AppendLine($"import {{ {import} }} from '{importPath}';");
            }
            sb.AppendLine();
        }

        // Add JSDoc comment
        if (!string.IsNullOrWhiteSpace(modelDef.Documentation))
        {
            sb.AppendLine("/**");
            sb.AppendLine($" * {modelDef.Documentation}");
            sb.AppendLine(" */");
        }

        // Check if this model is a union variant
        // Union variants should NOT extend the union type in TypeScript (causes circular reference)
        bool isUnionVariant = typeSpec != null &&
                              !string.IsNullOrWhiteSpace(modelDef.BaseModel) &&
                              typeSpec.Unions.Any(u => u.Name == modelDef.BaseModel);

        // Generate interface or type declaration
        // Only add extends clause for regular inheritance, NOT for union variants
        var extendsClause = !string.IsNullOrWhiteSpace(modelDef.BaseModel) && !isUnionVariant
            ? $" extends {modelDef.BaseModel}"
            : "";

        sb.AppendLine($"export interface {modelDef.Name}{extendsClause} {{");

        // Generate properties
        foreach (var prop in modelDef.Properties)
        {
            // Add property JSDoc comment
            if (!string.IsNullOrWhiteSpace(prop.Documentation))
            {
                sb.AppendLine("  /**");
                sb.AppendLine($"   * {prop.Documentation}");
                sb.AppendLine("   */");
            }

            var tsType = MapTypeSpecTypeToTypeScript(prop.Type, prop.IsArray);
            var optionalMarker = prop.IsOptional ? "?" : "";
            var propertyName = NamingConventions.ToCamelCase(prop.Name);

            sb.AppendLine($"  {propertyName}{optionalMarker}: {tsType};");
        }

        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateUnion(UnionDefinition unionDef)
    {
        var sb = new StringBuilder();

        // Import all variant types
        foreach (var variant in unionDef.Variants)
        {
            var importPath = GetImportPath(variant);
            sb.AppendLine($"import {{ {variant} }} from '{importPath}';");
        }
        sb.AppendLine();

        // Add JSDoc comment
        if (!string.IsNullOrWhiteSpace(unionDef.Documentation))
        {
            sb.AppendLine("/**");
            sb.AppendLine($" * {unionDef.Documentation}");
            sb.AppendLine(" */");
        }

        // Generate discriminated union type
        sb.Append($"export type {unionDef.Name} =");
        for (int i = 0; i < unionDef.Variants.Count; i++)
        {
            var variant = unionDef.Variants[i];
            if (i == 0)
            {
                sb.AppendLine($" {variant}");
            }
            else if (i == unionDef.Variants.Count - 1)
            {
                sb.AppendLine($"  | {variant};");
            }
            else
            {
                sb.AppendLine($"  | {variant}");
            }
        }

        return sb.ToString();
    }

    private string GenerateIndexFile(TypeSpecModel typeSpec)
    {
        var sb = new StringBuilder();
        sb.AppendLine("/**");
        sb.AppendLine(" * Generated TypeScript types from TypeSpec definitions");
        sb.AppendLine(" * DO NOT EDIT MANUALLY");
        sb.AppendLine(" */");
        sb.AppendLine();

        // Export all enums
        foreach (var enumDef in typeSpec.Enums)
        {
            sb.AppendLine($"export * from './{enumDef.Name}';");
        }

        // Export all models
        foreach (var modelDef in typeSpec.Models)
        {
            sb.AppendLine($"export * from './{modelDef.Name}';");
        }

        // Export all unions
        foreach (var unionDef in typeSpec.Unions)
        {
            sb.AppendLine($"export * from './{unionDef.Name}';");
        }

        return sb.ToString();
    }

    private string GetImportPath(string typeName)
    {
        // If we don't have location info, use same directory
        if (!_typeLocations.ContainsKey(typeName) || string.IsNullOrEmpty(_currentDirectory))
        {
            return $"./{typeName}";
        }

        var targetDirectory = _typeLocations[typeName];

        // Same directory - use relative import
        if (targetDirectory == _currentDirectory)
        {
            return $"./{typeName}";
        }

        // Different directory - use cross-directory import
        return $"../{targetDirectory}/{typeName}";
    }

    private HashSet<string> CollectImports(ModelDefinition modelDef, TypeSpecModel? typeSpec = null)
    {
        var imports = new HashSet<string>();

        // Add base model import (but not for union variants, as they don't extend the union)
        if (!string.IsNullOrWhiteSpace(modelDef.BaseModel))
        {
            bool isUnionVariant = typeSpec != null &&
                                  typeSpec.Unions.Any(u => u.Name == modelDef.BaseModel);

            if (!isUnionVariant)
            {
                imports.Add(modelDef.BaseModel);
            }
        }

        // Add imports for complex property types
        foreach (var prop in modelDef.Properties)
        {
            var baseType = prop.Type;

            // Skip primitive types
            if (TypeMapper.IsSimpleType(baseType))
                continue;

            // Skip Record<T> types
            if (baseType.StartsWith("Record<"))
                continue;

            // Skip literal string types (start with quotes)
            if (baseType.StartsWith("\"") || baseType.StartsWith("'"))
                continue;

            // Skip built-in TypeScript types
            if (baseType == "unknown" || baseType == "any" || baseType == "never")
                continue;

            // Extract type from Array<T> syntax
            if (baseType.StartsWith("Array<") && baseType.EndsWith(">"))
            {
                var innerType = baseType.Substring(6, baseType.Length - 7);
                if (!TypeMapper.IsSimpleType(innerType) && !innerType.StartsWith("Record<"))
                {
                    imports.Add(innerType);
                }
                continue;
            }

            // Skip other generic types (contain < or [)
            if (baseType.Contains('<') || baseType.Contains('['))
                continue;

            // Add complex type
            imports.Add(baseType);
        }

        return imports;
    }

    /// <summary>
    /// Maps TypeSpec types to TypeScript types.
    /// </summary>
    public static string MapTypeSpecTypeToTypeScript(string typeSpecType, bool isArray)
    {
        var baseType = typeSpecType switch
        {
            "string" => "string",
            "int32" => "number",
            "int64" => "number",
            "float32" => "number",
            "float64" => "number",
            "boolean" => "boolean",
            "bytes" => "Uint8Array",
            "utcDateTime" => "string", // ISO 8601 string
            "unknown" => "unknown",
            _ when typeSpecType.StartsWith("Record<") => "Record<string, unknown>",
            _ when typeSpecType.StartsWith("\"") => "string", // Literal type
            _ => typeSpecType // Custom type (model/enum/union name)
        };

        return isArray ? $"{baseType}[]" : baseType;
    }
}
