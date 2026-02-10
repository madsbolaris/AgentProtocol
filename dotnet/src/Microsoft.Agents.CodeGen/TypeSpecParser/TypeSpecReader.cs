using System.Text.RegularExpressions;

namespace Microsoft.Agents.CodeGen.TypeSpecParser;

/// <summary>
/// Parses TypeSpec files into an intermediate representation.
/// This is a simple regex-based parser for now. In production, you'd use
/// the official TypeSpec compiler API or a proper parser generator.
/// </summary>
public class TypeSpecReader
{
    public async Task<TypeSpecModel> ParseFileAsync(string filePath)
    {
        var content = await File.ReadAllTextAsync(filePath);
        return ParseContent(content);
    }

    public TypeSpecModel ParseContent(string content)
    {
        var model = new TypeSpecModel();

        // Extract namespace
        var namespaceMatch = Regex.Match(content, @"namespace\s+([\w.]+);");
        if (namespaceMatch.Success)
        {
            model.Namespace = namespaceMatch.Groups[1].Value;
        }

        // Parse enums
        model.Enums = ParseEnums(content);

        // Parse models
        model.Models = ParseModels(content);

        // Parse unions
        model.Unions = ParseUnions(content);

        // Link union variants to their base classes
        LinkUnionVariants(model);

        return model;
    }

    private List<EnumDefinition> ParseEnums(string content)
    {
        var enums = new List<EnumDefinition>();
        var enumPattern = @"enum\s+(\w+)\s*\{([^}]+)\}";
        var matches = Regex.Matches(content, enumPattern, RegexOptions.Singleline);

        foreach (Match match in matches)
        {
            var enumDef = new EnumDefinition
            {
                Name = match.Groups[1].Value,
                Documentation = ExtractDocumentation(content, match.Index)
            };

            // Parse enum members
            var membersText = match.Groups[2].Value;
            var lines = membersText.Split('\n');

            foreach (var line in lines)
            {
                var trimmed = line.Trim();

                // Skip empty lines and comments
                if (string.IsNullOrWhiteSpace(trimmed) ||
                    trimmed.StartsWith("/**") ||
                    trimmed.StartsWith("*") ||
                    trimmed.StartsWith("*/") ||
                    trimmed.StartsWith("//"))
                {
                    continue;
                }

                // Parse member: name or name = value
                var memberPattern = @"^(\w+)(?:\s*=\s*[""']?(\w+)[""']?)?\s*,?\s*$";
                var memberMatch = Regex.Match(trimmed, memberPattern);

                if (memberMatch.Success)
                {
                    enumDef.Members.Add(new EnumMemberDefinition
                    {
                        Name = memberMatch.Groups[1].Value,
                        Value = memberMatch.Groups[2].Success ? memberMatch.Groups[2].Value : null
                    });
                }
            }

            enums.Add(enumDef);
        }

        return enums;
    }

    private List<ModelDefinition> ParseModels(string content)
    {
        var models = new List<ModelDefinition>();
        // Pattern to find model declarations
        var modelStartPattern = @"model\s+(\w+)(?:\s+extends\s+(\w+))?\s*\{";
        var matches = Regex.Matches(content, modelStartPattern);

        foreach (Match match in matches)
        {
            var modelName = match.Groups[1].Value;
            var baseModel = match.Groups[2].Success ? match.Groups[2].Value : null;

            // Find the matching closing brace by counting braces
            var startIndex = match.Index + match.Length;
            var braceCount = 1;
            var endIndex = startIndex;

            while (endIndex < content.Length && braceCount > 0)
            {
                if (content[endIndex] == '{')
                    braceCount++;
                else if (content[endIndex] == '}')
                    braceCount--;
                endIndex++;
            }

            if (braceCount == 0)
            {
                // Extract the content between braces
                var propertiesText = content.Substring(startIndex, endIndex - startIndex - 1);

                var modelDef = new ModelDefinition
                {
                    Name = modelName,
                    BaseModel = baseModel,
                    Documentation = ExtractDocumentation(content, match.Index),
                    Decorators = ExtractDecorators(content, match.Index)
                };

                // Analyze decorators for XML metadata
                ApplyXmlDecorators(modelDef);

                // Parse properties
                modelDef.Properties = ParseProperties(propertiesText);

                models.Add(modelDef);
            }
        }

        return models;
    }

    private List<PropertyDefinition> ParseProperties(string propertiesText)
    {
        var properties = new List<PropertyDefinition>();
        var lines = propertiesText.Split('\n');

        var decoratorBuffer = new List<DecoratorDefinition>();
        var documentationBuffer = new List<string>();

        for (int i = 0; i < lines.Length; i++)
        {
            var line = lines[i];
            var trimmed = line.Trim();

            // Skip empty lines
            if (string.IsNullOrWhiteSpace(trimmed))
            {
                continue;
            }

            // Collect documentation comments
            if (trimmed.StartsWith("/**") || trimmed.StartsWith("*") || trimmed.StartsWith("*/"))
            {
                if (trimmed.StartsWith("/**"))
                {
                    documentationBuffer.Clear();
                }
                if (!trimmed.StartsWith("/**") && !trimmed.StartsWith("*/"))
                {
                    documentationBuffer.Add(trimmed.TrimStart('*').Trim());
                }
                continue;
            }

            // Skip line comments
            if (trimmed.StartsWith("//"))
            {
                continue;
            }

            // Check for decorators
            if (trimmed.StartsWith("@"))
            {
                var decoratorPattern = @"@(\w+)(?:\(([^)]*)\))?";
                var match = Regex.Match(trimmed, decoratorPattern);
                if (match.Success)
                {
                    var decorator = new DecoratorDefinition
                    {
                        Name = match.Groups[1].Value,
                        Arguments = new Dictionary<string, object?>()
                    };

                    if (match.Groups[2].Success)
                    {
                        var arg = match.Groups[2].Value.Trim('"', '\'');
                        decorator.Arguments["value"] = arg;
                    }

                    decoratorBuffer.Add(decorator);
                }
                continue;
            }

            // Parse property definition: name?: type;
            var propPattern = @"(\w+)(\?)?:\s*([\w\[\]<>|""']+)(?:\s*=\s*(.+?))?;";
            var propMatch = Regex.Match(trimmed, propPattern);

            if (propMatch.Success)
            {
                var propDef = new PropertyDefinition
                {
                    Name = propMatch.Groups[1].Value,
                    IsOptional = propMatch.Groups[2].Success,
                    Type = propMatch.Groups[3].Value,
                    Decorators = new List<DecoratorDefinition>(decoratorBuffer),
                    Documentation = documentationBuffer.Count > 0
                        ? string.Join("\n", documentationBuffer)
                        : null
                };

                // Check if array type
                propDef.IsArray = propDef.Type.EndsWith("[]");
                if (propDef.IsArray)
                {
                    propDef.Type = propDef.Type.TrimEnd('[', ']');
                }

                // Apply XML decorators
                ApplyXmlPropertyDecorators(propDef);

                properties.Add(propDef);

                // Clear buffers for next property
                decoratorBuffer.Clear();
                documentationBuffer.Clear();
            }
        }

        return properties;
    }

    private void ApplyXmlPropertyDecorators(PropertyDefinition property)
    {
        foreach (var decorator in property.Decorators)
        {
            switch (decorator.Name)
            {
                case "xmlAttribute":
                    property.IsXmlAttribute = true;
                    if (decorator.Arguments.TryGetValue("value", out var attrName))
                    {
                        property.XmlName = attrName?.ToString();
                    }
                    break;
                case "xmlElement":
                    property.IsXmlElement = true;
                    if (decorator.Arguments.TryGetValue("value", out var elemName))
                    {
                        property.XmlName = elemName?.ToString();
                    }
                    break;
                case "xmlText":
                    property.IsXmlText = true;
                    break;
                case "xmlIgnore":
                    property.IsXmlIgnore = true;
                    break;
                case "xmlDefault":
                    if (decorator.Arguments.TryGetValue("value", out var defaultVal))
                    {
                        property.XmlDefaultValue = defaultVal;
                    }
                    break;
                case "contentType":
                    if (decorator.Arguments.TryGetValue("value", out var contentTypeArg))
                    {
                        var contentTypeStr = contentTypeArg?.ToString() ?? "";

                        // Handle array syntax: ["powerfx", "cel"]
                        if (contentTypeStr.StartsWith("[") && contentTypeStr.EndsWith("]"))
                        {
                            // Parse array of content types
                            var arrayContent = contentTypeStr.Trim('[', ']');
                            var types = arrayContent.Split(',')
                                .Select(t => t.Trim().Trim('"', '\''))
                                .Where(t => !string.IsNullOrWhiteSpace(t))
                                .ToList();
                            property.ContentTypes.AddRange(types);
                        }
                        else
                        {
                            // Single content type
                            var cleanType = contentTypeStr.Trim('"', '\'');
                            if (!string.IsNullOrWhiteSpace(cleanType))
                            {
                                property.ContentTypes.Add(cleanType);
                            }
                        }
                    }
                    break;
            }
        }
    }

    private List<UnionDefinition> ParseUnions(string content)
    {
        var unions = new List<UnionDefinition>();

        // Pattern 1: Discriminated unions with @discriminator decorator
        var discriminatedPattern = @"@discriminator\([""'](\w+)[""']\)\s*union\s+(\w+)\s*\{([^}]+)\}";
        var discriminatedMatches = Regex.Matches(content, discriminatedPattern, RegexOptions.Singleline);

        foreach (Match match in discriminatedMatches)
        {
            var unionDef = new UnionDefinition
            {
                DiscriminatorProperty = match.Groups[1].Value,
                Name = match.Groups[2].Value,
                Documentation = ExtractDocumentation(content, match.Index),
                IsXmlPolymorphic = true
            };

            // Parse variants
            var variantsText = match.Groups[3].Value;
            ParseVariants(variantsText, unionDef);
            unions.Add(unionDef);
        }

        // Pattern 2: Simple unions without discriminator (e.g., union ThreadElement { ... })
        var simplePattern = @"(?<!@discriminator\([^)]+\)\s*)union\s+(\w+)\s*\{([^}]+)\}";
        var simpleMatches = Regex.Matches(content, simplePattern, RegexOptions.Singleline);

        foreach (Match match in simpleMatches)
        {
            var name = match.Groups[1].Value;

            // Skip if already added as discriminated union
            if (unions.Any(u => u.Name == name))
                continue;

            var unionDef = new UnionDefinition
            {
                DiscriminatorProperty = "",  // No discriminator
                Name = name,
                Documentation = ExtractDocumentation(content, match.Index),
                IsXmlPolymorphic = false
            };

            // Parse variants
            var variantsText = match.Groups[2].Value;
            ParseVariants(variantsText, unionDef);
            unions.Add(unionDef);
        }

        return unions;
    }

    private void ParseVariants(string variantsText, UnionDefinition unionDef)
    {
        // Remove commented lines before parsing
        var lines = variantsText.Split(new[] { '\r', '\n' }, StringSplitOptions.RemoveEmptyEntries);
        var activeLines = lines
            .Select(line => line.Trim())
            .Where(line => !line.StartsWith("//"))  // Skip commented lines
            .ToList();

        var cleanedText = string.Join(" ", activeLines);

        var variantPattern = @"(\w+)\s*,?";
        var variantMatches = Regex.Matches(cleanedText, variantPattern);

        foreach (Match variantMatch in variantMatches)
        {
            var variant = variantMatch.Groups[1].Value.Trim();
            if (!string.IsNullOrWhiteSpace(variant))
            {
                unionDef.Variants.Add(variant);
            }
        }
    }

    private void LinkUnionVariants(TypeSpecModel model)
    {
        // For each union, set the BaseModel property on its variant models
        foreach (var union in model.Unions)
        {
            foreach (var variantName in union.Variants)
            {
                var variantModel = model.Models.FirstOrDefault(m => m.Name == variantName);
                if (variantModel != null && string.IsNullOrWhiteSpace(variantModel.BaseModel))
                {
                    // Only set BaseModel if it's not already set (don't override explicit extends)
                    variantModel.BaseModel = union.Name;
                }
            }
        }
    }

    private string? ExtractDocumentation(string content, int position)
    {
        // Look backwards for /** ... */ comment
        var before = content.Substring(Math.Max(0, position - 500), Math.Min(500, position));
        var docMatch = Regex.Match(before, @"/\*\*(.+?)\*/", RegexOptions.Singleline | RegexOptions.RightToLeft);

        if (docMatch.Success)
        {
            return docMatch.Groups[1].Value
                .Split('\n')
                .Select(line => line.Trim().TrimStart('*').Trim())
                .Where(line => !string.IsNullOrWhiteSpace(line))
                .Aggregate((a, b) => a + "\n" + b);
        }

        return null;
    }

    private List<DecoratorDefinition> ExtractDecorators(string content, int position)
    {
        var decorators = new List<DecoratorDefinition>();
        var before = content.Substring(Math.Max(0, position - 200), Math.Min(200, position));

        // Match decorators like @xmlRoot("message") or @key
        var decoratorPattern = @"@(\w+)(?:\(([^)]*)\))?";
        var matches = Regex.Matches(before, decoratorPattern);

        foreach (Match match in matches)
        {
            decorators.Add(new DecoratorDefinition
            {
                Name = match.Groups[1].Value,
                Arguments = new Dictionary<string, object?>
                {
                    { "value", match.Groups[2].Success ? match.Groups[2].Value.Trim('"', '\'') : null }
                }
            });
        }

        return decorators;
    }

    private void ApplyXmlDecorators(ModelDefinition model)
    {
        foreach (var decorator in model.Decorators)
        {
            switch (decorator.Name)
            {
                case "xmlRoot":
                case "xmlElement":
                    model.IsXmlRoot = decorator.Name == "xmlRoot";
                    if (decorator.Arguments.TryGetValue("value", out var xmlName))
                    {
                        model.XmlElementName = xmlName?.ToString();
                    }
                    break;
                case "xmlNamespace":
                    if (decorator.Arguments.TryGetValue("value", out var ns))
                    {
                        model.XmlNamespace = ns?.ToString();
                    }
                    break;
            }
        }
    }
}
