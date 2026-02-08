using System.Text;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates TypeScript content types with discriminated unions and type guards.
/// Handles the AIContent union and all 29+ content type variants.
/// </summary>
public class TypeScriptContentTypeGenerator
{
    private readonly string _rootNamespace;

    public TypeScriptContentTypeGenerator(string rootNamespace = "")
    {
        _rootNamespace = rootNamespace;
    }

    /// <summary>
    /// Generates AIContent union type and all derived content types.
    /// </summary>
    public List<string> GenerateContentTypes(
        UnionDefinition aiContentUnion,
        List<ModelDefinition> contentModels,
        string outputDirectory)
    {
        var generatedFiles = new List<string>();

        Directory.CreateDirectory(outputDirectory);

        // Generate base interface for content types
        var baseInterfaceFile = Path.Combine(outputDirectory, "AIContentBase.ts");
        var baseCode = GenerateBaseInterface(aiContentUnion);
        File.WriteAllText(baseInterfaceFile, baseCode);
        generatedFiles.Add(baseInterfaceFile);

        // Generate each content type interface
        foreach (var contentModel in contentModels)
        {
            var filePath = Path.Combine(outputDirectory, $"{contentModel.Name}.ts");
            var code = GenerateContentTypeInterface(contentModel);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate union type and type guards
        var unionFile = Path.Combine(outputDirectory, $"{aiContentUnion.Name}.ts");
        var unionCode = GenerateUnionAndTypeGuards(aiContentUnion, contentModels);
        File.WriteAllText(unionFile, unionCode);
        generatedFiles.Add(unionFile);

        // Generate index file
        var indexFile = Path.Combine(outputDirectory, "index.ts");
        var indexCode = GenerateIndexFile(aiContentUnion, contentModels);
        File.WriteAllText(indexFile, indexCode);
        generatedFiles.Add(indexFile);

        return generatedFiles;
    }

    private string GenerateBaseInterface(UnionDefinition union)
    {
        var sb = new StringBuilder();

        sb.AppendLine("/**");
        sb.AppendLine(" * Base interface for all content types.");
        sb.AppendLine(" * Contains the discriminator property 'kind' and optional audience.");
        sb.AppendLine(" */");
        sb.AppendLine("export interface AIContentBase {");
        sb.AppendLine("  /** Content type discriminator */");
        sb.AppendLine("  kind: string;");
        sb.AppendLine();
        sb.AppendLine("  /** Target audience for this content (user, agent, or both) */");
        sb.AppendLine("  audience?: 'user' | 'agent';");
        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateContentTypeInterface(ModelDefinition contentModel)
    {
        var sb = new StringBuilder();

        // Import base interface
        sb.AppendLine("import { AIContentBase } from './AIContentBase';");

        // Import referenced types
        var imports = CollectImports(contentModel);
        foreach (var import in imports)
        {
            sb.AppendLine($"import {{ {import} }} from './{import}';");
        }

        if (imports.Any())
        {
            sb.AppendLine();
        }

        // Add JSDoc comment
        if (!string.IsNullOrWhiteSpace(contentModel.Documentation))
        {
            sb.AppendLine("/**");
            sb.AppendLine($" * {contentModel.Documentation}");
            sb.AppendLine(" */");
        }

        // Generate interface extending base
        sb.AppendLine($"export interface {contentModel.Name} extends AIContentBase {{");

        // Add kind discriminator as literal type
        var kindValue = GetKindValue(contentModel.Name);
        sb.AppendLine($"  kind: '{kindValue}';");

        // Generate properties (excluding 'kind' and 'audience' which are in base)
        foreach (var prop in contentModel.Properties)
        {
            if (prop.Name == "kind" || prop.Name == "audience")
                continue;

            // Add property JSDoc comment
            if (!string.IsNullOrWhiteSpace(prop.Documentation))
            {
                sb.AppendLine();
                sb.AppendLine("  /**");
                sb.AppendLine($"   * {prop.Documentation}");
                sb.AppendLine("   */");
            }

            var tsType = TypeScriptModelGenerator.MapTypeSpecTypeToTypeScript(prop.Type, prop.IsArray);
            var optionalMarker = prop.IsOptional ? "?" : "";
            var propertyName = NamingConventions.ToCamelCase(prop.Name);

            sb.AppendLine($"  {propertyName}{optionalMarker}: {tsType};");
        }

        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateUnionAndTypeGuards(UnionDefinition union, List<ModelDefinition> contentModels)
    {
        var sb = new StringBuilder();

        // Import all content types
        foreach (var model in contentModels)
        {
            sb.AppendLine($"import {{ {model.Name} }} from './{model.Name}';");
        }
        sb.AppendLine();

        // Add JSDoc comment
        if (!string.IsNullOrWhiteSpace(union.Documentation))
        {
            sb.AppendLine("/**");
            sb.AppendLine($" * {union.Documentation}");
            sb.AppendLine(" * Discriminated union of all content types.");
            sb.AppendLine(" */");
        }

        // Generate discriminated union type
        sb.Append($"export type {union.Name} =");
        for (int i = 0; i < contentModels.Count; i++)
        {
            var model = contentModels[i];
            if (i == 0)
            {
                sb.AppendLine($" {model.Name}");
            }
            else if (i == contentModels.Count - 1)
            {
                sb.AppendLine($"  | {model.Name};");
            }
            else
            {
                sb.AppendLine($"  | {model.Name}");
            }
        }

        sb.AppendLine();
        sb.AppendLine("// Type guards");
        sb.AppendLine();

        // Generate type guard for each content type
        foreach (var model in contentModels)
        {
            var kindValue = GetKindValue(model.Name);
            var functionName = $"is{model.Name}";

            sb.AppendLine("/**");
            sb.AppendLine($" * Type guard to check if content is {model.Name}");
            sb.AppendLine(" */");
            sb.AppendLine($"export function {functionName}(content: {union.Name}): content is {model.Name} {{");
            sb.AppendLine($"  return content.kind === '{kindValue}';");
            sb.AppendLine("}");
            sb.AppendLine();
        }

        // Generate helper function to create content
        sb.AppendLine("/**");
        sb.AppendLine(" * Helper to filter content by kind");
        sb.AppendLine(" */");
        sb.AppendLine($"export function filterContentByKind<K extends {union.Name}['kind']>(");
        sb.AppendLine($"  contents: {union.Name}[],");
        sb.AppendLine("  kind: K");
        sb.AppendLine($"): Extract<{union.Name}, {{ kind: K }}>[] {{");
        sb.AppendLine("  return contents.filter((c) => c.kind === kind) as any;");
        sb.AppendLine("}");
        sb.AppendLine();

        // Generate helper to filter by audience
        sb.AppendLine("/**");
        sb.AppendLine(" * Helper to filter content by audience");
        sb.AppendLine(" */");
        sb.AppendLine($"export function filterContentByAudience(");
        sb.AppendLine($"  contents: {union.Name}[],");
        sb.AppendLine("  audience: 'user' | 'agent'");
        sb.AppendLine($"): {union.Name}[] {{");
        sb.AppendLine("  return contents.filter((c) => !c.audience || c.audience === audience);");
        sb.AppendLine("}");

        return sb.ToString();
    }

    private string GenerateIndexFile(UnionDefinition union, List<ModelDefinition> contentModels)
    {
        var sb = new StringBuilder();

        sb.AppendLine("/**");
        sb.AppendLine(" * Content types - discriminated union with type guards");
        sb.AppendLine(" * Generated from TypeSpec definitions");
        sb.AppendLine(" */");
        sb.AppendLine();

        // Export base interface
        sb.AppendLine("export * from './AIContentBase';");

        // Export all content types
        foreach (var model in contentModels)
        {
            sb.AppendLine($"export * from './{model.Name}';");
        }

        // Export union and type guards
        sb.AppendLine($"export * from './{union.Name}';");

        return sb.ToString();
    }

    private HashSet<string> CollectImports(ModelDefinition modelDef)
    {
        var imports = new HashSet<string>();

        foreach (var prop in modelDef.Properties)
        {
            var baseType = prop.Type;

            // Skip primitive types
            if (TypeMapper.IsSimpleType(baseType))
                continue;

            // Skip discriminator and audience
            if (prop.Name == "kind" || prop.Name == "audience")
                continue;

            // Skip Record<T> types
            if (baseType.StartsWith("Record<"))
                continue;

            // Add complex type
            if (!baseType.EndsWith("Content") || baseType != "AIContentBase")
            {
                imports.Add(baseType);
            }
        }

        return imports;
    }

    /// <summary>
    /// Converts a content type name to its kind value.
    /// E.g., "TextContent" -> "text"
    /// </summary>
    private string GetKindValue(string contentTypeName)
    {
        if (contentTypeName.EndsWith("Content"))
        {
            var kindName = contentTypeName.Substring(0, contentTypeName.Length - "Content".Length);
            return NamingConventions.ToCamelCase(kindName);
        }
        return NamingConventions.ToCamelCase(contentTypeName);
    }
}
