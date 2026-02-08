using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Adds XML serialization attributes to C# declarations.
/// Handles [XmlRoot], [XmlElement], [XmlAttribute], etc.
/// </summary>
public class XmlAttributeGenerator
{
    public ClassDeclarationSyntax AddXmlAttributes(ClassDeclarationSyntax classDecl, ModelDefinition modelDef)
    {
        var attributes = new List<AttributeSyntax>();

        // Add [XmlRoot] for root elements
        if (modelDef.IsXmlRoot && !string.IsNullOrWhiteSpace(modelDef.XmlElementName))
        {
            var xmlRootAttr = Attribute(
                ParseName("XmlRoot"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(modelDef.XmlElementName)
                            )
                        )
                    )
                )
            );
            attributes.Add(xmlRootAttr);
        }
        // Add [XmlType] for non-root elements
        else if (!string.IsNullOrWhiteSpace(modelDef.XmlElementName))
        {
            var xmlTypeAttr = Attribute(
                ParseName("XmlType"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(modelDef.XmlElementName)
                            )
                        )
                    )
                )
            );
            attributes.Add(xmlTypeAttr);
        }

        if (attributes.Any())
        {
            classDecl = classDecl.AddAttributeLists(
                AttributeList(SeparatedList(attributes))
            );
        }

        return classDecl;
    }

    public PropertyDeclarationSyntax AddPropertyXmlAttributes(
        PropertyDeclarationSyntax property,
        PropertyDefinition propDef)
    {
        var attributes = new List<AttributeSyntax>();

        // Determine XML name (use kebab-case for XML, PascalCase for C#)
        var xmlName = NamingConventions.ToKebabCase(propDef.Name);

        // Check decorators for explicit XML mapping
        foreach (var decorator in propDef.Decorators)
        {
            switch (decorator.Name)
            {
                case "xmlIgnore":
                    propDef.IsXmlIgnore = true;
                    break;
                case "xmlAttribute":
                    propDef.IsXmlAttribute = true;
                    if (decorator.Arguments.TryGetValue("value", out var attrName))
                    {
                        xmlName = attrName?.ToString() ?? xmlName;
                    }
                    break;
                case "xmlElement":
                    propDef.IsXmlElement = true;
                    if (decorator.Arguments.TryGetValue("value", out var elemName))
                    {
                        xmlName = elemName?.ToString() ?? xmlName;
                    }
                    break;
            }
        }

        // Add appropriate XML attribute
        if (propDef.IsXmlIgnore)
        {
            // Add [XmlIgnore] attribute
            attributes.Add(Attribute(ParseName("XmlIgnore")));
        }
        else if (propDef.IsXmlAttribute)
        {
            var xmlAttr = Attribute(
                ParseName("XmlAttribute"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(xmlName)
                            )
                        )
                    )
                )
            );
            attributes.Add(xmlAttr);
        }
        else if (propDef.IsArray)
        {
            // For arrays, use [XmlArray] and [XmlArrayItem]
            var xmlArrayAttr = Attribute(
                ParseName("XmlArray"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(xmlName)
                            )
                        )
                    )
                )
            );
            attributes.Add(xmlArrayAttr);

            // Add [XmlArrayItem] for the item type
            var itemType = NamingConventions.ToKebabCase(propDef.Type);
            var xmlArrayItemAttr = Attribute(
                ParseName("XmlArrayItem"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(itemType)
                            )
                        )
                    )
                )
            );
            attributes.Add(xmlArrayItemAttr);
        }
        else
        {
            // Default to [XmlElement]
            var xmlElemAttr = Attribute(
                ParseName("XmlElement"),
                AttributeArgumentList(
                    SingletonSeparatedList(
                        AttributeArgument(
                            LiteralExpression(
                                SyntaxKind.StringLiteralExpression,
                                Literal(xmlName)
                            )
                        )
                    )
                )
            );
            attributes.Add(xmlElemAttr);
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
