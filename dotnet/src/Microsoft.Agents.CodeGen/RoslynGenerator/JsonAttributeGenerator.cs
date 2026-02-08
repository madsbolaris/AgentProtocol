using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Adds JSON serialization attributes to C# declarations.
/// Handles [JsonPropertyName], [JsonIgnore], etc.
/// </summary>
public class JsonAttributeGenerator
{
    public PropertyDeclarationSyntax AddPropertyJsonAttributes(
        PropertyDeclarationSyntax property,
        PropertyDefinition propDef)
    {
        var attributes = new List<AttributeSyntax>();

        // Determine JSON name (use camelCase for JSON, PascalCase for C#)
        var jsonName = NamingConventions.ToCamelCase(propDef.Name);

        // Check decorators for explicit JSON mapping
        bool isJsonIgnore = false;
        foreach (var decorator in propDef.Decorators)
        {
            switch (decorator.Name)
            {
                case "xmlIgnore":
                case "jsonIgnore":
                    isJsonIgnore = true;
                    break;
                case "jsonName":
                    if (decorator.Arguments.TryGetValue("value", out var name))
                    {
                        jsonName = name?.ToString() ?? jsonName;
                    }
                    break;
            }
        }

        // Add appropriate JSON attribute
        if (isJsonIgnore)
        {
            // Add [JsonIgnore] attribute
            attributes.Add(Attribute(ParseName("JsonIgnore")));
        }
        else
        {
            // Add [JsonPropertyName] attribute
            var jsonPropertyNameAttr = Attribute(
                ParseName("JsonPropertyName"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(jsonName)
                            )
                        )
                    )
                )
            );
            attributes.Add(jsonPropertyNameAttr);
        }

        if (attributes.Any())
        {
            property = property.AddAttributeLists(
                AttributeList(SeparatedList(attributes))
            );
        }

        return property;
    }
}
