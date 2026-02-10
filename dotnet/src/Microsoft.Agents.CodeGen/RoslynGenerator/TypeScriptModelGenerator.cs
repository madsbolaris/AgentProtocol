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

    public TypeScriptModelGenerator(string rootNamespace = "")
    {
        _rootNamespace = rootNamespace;
    }

    public List<string> GenerateModels(TypeSpecModel typeSpec, string outputDirectory)
    {
        var generatedFiles = new List<string>();

        Directory.CreateDirectory(outputDirectory);

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
            var code = GenerateModel(modelDef);
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

    private string GenerateModel(ModelDefinition modelDef)
    {
        var sb = new StringBuilder();

        // Collect imports for referenced types
        var imports = CollectImports(modelDef);
        if (imports.Any())
        {
            foreach (var import in imports)
            {
                sb.AppendLine($"import {{ {import} }} from './{import}';");
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

        // Generate interface or type declaration
        var extendsClause = !string.IsNullOrWhiteSpace(modelDef.BaseModel)
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
            sb.AppendLine($"import {{ {variant} }} from './{variant}';");
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

    private HashSet<string> CollectImports(ModelDefinition modelDef)
    {
        var imports = new HashSet<string>();

        // Add base model import
        if (!string.IsNullOrWhiteSpace(modelDef.BaseModel))
        {
            imports.Add(modelDef.BaseModel);
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

            // Skip generic/array types (contain < or [)
            if (baseType.Contains('<') || baseType.Contains('['))
                continue;

            // Skip built-in TypeScript types
            if (baseType == "unknown" || baseType == "any" || baseType == "never")
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
