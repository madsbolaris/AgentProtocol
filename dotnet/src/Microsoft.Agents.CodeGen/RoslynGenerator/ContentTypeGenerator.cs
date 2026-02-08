using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Formatting;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates AIContent and derived content type classes with proper serialization.
/// Handles XmlText, XmlInclude, discriminators, JSON attributes, and annotation flattening.
/// </summary>
public class ContentTypeGenerator
{
    private readonly string _rootNamespace;
    private readonly SerializationMode _serializationMode;
    private readonly XmlAttributeGenerator _xmlAttributeGenerator;
    private readonly JsonAttributeGenerator _jsonAttributeGenerator;

    public ContentTypeGenerator(string rootNamespace, SerializationMode serializationMode = SerializationMode.Both)
    {
        _rootNamespace = rootNamespace;
        _serializationMode = serializationMode;
        _xmlAttributeGenerator = new XmlAttributeGenerator();
        _jsonAttributeGenerator = new JsonAttributeGenerator();
    }

    /// <summary>
    /// Generates AIContent base class and all derived content types.
    /// </summary>
    public List<string> GenerateContentTypes(
        UnionDefinition aiContentUnion,
        List<ModelDefinition> contentModels,
        string outputDirectory)
    {
        var generatedFiles = new List<string>();

        // Generate base AIContent class with XmlInclude for all variants
        var baseClassFile = GenerateBaseAIContent(aiContentUnion, contentModels, outputDirectory);
        generatedFiles.Add(baseClassFile);

        // Generate each content type
        foreach (var contentModel in contentModels)
        {
            var filePath = Path.Combine(outputDirectory, $"{contentModel.Name}.cs");
            var code = GenerateContentType(contentModel, aiContentUnion);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        return generatedFiles;
    }

    private string GenerateBaseAIContent(
        UnionDefinition union,
        List<ModelDefinition> contentModels,
        string outputDirectory)
    {
        var classAttributes = new List<AttributeSyntax>();

        // Create [XmlInclude] for all content types (if XML serialization is enabled)
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            var xmlIncludeAttributes = contentModels
                .Select(model =>
                    Attribute(
                        ParseName("XmlInclude"),
                        AttributeArgumentList(
                            SingletonSeparatedList(
                                AttributeArgument(
                                    TypeOfExpression(ParseTypeName(model.Name))
                                )
                            )
                        )
                    )
                ).ToList();
            classAttributes.AddRange(xmlIncludeAttributes);
        }

        // Add [JsonPolymorphic] and [JsonDerivedType] for JSON serialization
        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            // Add [JsonPolymorphic(TypeDiscriminatorPropertyName = "kind")]
            classAttributes.Add(
                Attribute(
                    ParseName("JsonPolymorphic"),
                    AttributeArgumentList(
                        SingletonSeparatedList(
                            AttributeArgument(
                                LiteralExpression(
                                    SyntaxKind.StringLiteralExpression,
                                    Literal("kind")
                                )
                            )
                            .WithNameEquals(NameEquals(IdentifierName("TypeDiscriminatorPropertyName")))
                        )
                    )
                )
            );

            // Add [JsonDerivedType] for each content type
            foreach (var model in contentModels)
            {
                var kindValue = NamingConventions.ToKebabCase(model.Name.Replace("Content", ""));
                classAttributes.Add(
                    Attribute(
                        ParseName("JsonDerivedType"),
                        AttributeArgumentList(
                            SeparatedList(new[]
                            {
                                AttributeArgument(TypeOfExpression(ParseTypeName(model.Name))),
                                AttributeArgument(
                                    LiteralExpression(
                                        SyntaxKind.StringLiteralExpression,
                                        Literal(kindValue)
                                    )
                                )
                            })
                        )
                    )
                );
            }
        }

        // Create abstract Kind property (discriminator)
        var kindPropertyAttrs = new List<AttributeSyntax>();
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            kindPropertyAttrs.Add(
                Attribute(
                    ParseName("XmlAttribute"),
                    AttributeArgumentList(
                        SingletonSeparatedList(
                            AttributeArgument(
                                LiteralExpression(
                                    SyntaxKind.StringLiteralExpression,
                                    Literal("kind")
                                )
                            )
                        )
                    )
                )
            );
        }

        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            kindPropertyAttrs.Add(
                Attribute(
                    ParseName("JsonPropertyName"),
                    AttributeArgumentList(
                        SingletonSeparatedList(
                            AttributeArgument(
                                LiteralExpression(
                                    SyntaxKind.StringLiteralExpression,
                                    Literal("kind")
                                )
                            )
                        )
                    )
                )
            );
        }

        var kindProperty = PropertyDeclaration(
                ParseTypeName("string"),
                Identifier("Kind")
            )
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.AbstractKeyword)
            )
            .AddAccessorListAccessors(
                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            );

        if (kindPropertyAttrs.Any())
        {
            kindProperty = kindProperty.AddAttributeLists(
                AttributeList(SeparatedList(kindPropertyAttrs))
            );
        }

        var classDecl = ClassDeclaration("AIContent")
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.AbstractKeyword),
                Token(SyntaxKind.PartialKeyword)
            )
            .AddMembers(kindProperty);

        if (classAttributes.Any())
        {
            classDecl = classDecl.AddAttributeLists(
                AttributeList(SeparatedList(classAttributes))
            );
        }

        // Add documentation
        var doc = "Base class for all AI content types. Supports polymorphic XML and JSON serialization.";
        classDecl = classDecl.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(doc));

        // Build usings based on serialization mode
        var usings = new List<UsingDirectiveSyntax> { UsingDirective(ParseName("System")) };
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            usings.Add(UsingDirective(ParseName("System.Xml.Serialization")));
        }
        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            usings.Add(UsingDirective(ParseName("System.Text.Json.Serialization")));
        }

        var compilationUnit = CompilationUnit()
            .AddUsings(usings.ToArray())
            .AddMembers(
                NamespaceDeclaration(ParseName(_rootNamespace))
                    .AddMembers(classDecl)
            );

        var filePath = Path.Combine(outputDirectory, "AIContent.cs");
        var code = CodeGenerationUtilities.FormatCode(compilationUnit);
        File.WriteAllText(filePath, code);

        return filePath;
    }

    private string GenerateContentType(ModelDefinition model, UnionDefinition union)
    {
        // Determine XML element name from model
        var xmlElementName = NamingConventions.ToKebabCase(model.Name.Replace("Content", ""));

        // Find the 'kind' discriminator value
        var kindProperty = model.Properties.FirstOrDefault(p => p.Name == "kind");
        var kindValue = kindProperty?.Type.Trim('"') ?? xmlElementName;

        // Determine base class from model definition (default to AIContent if not specified)
        var baseClassName = !string.IsNullOrEmpty(model.BaseModel) ? model.BaseModel : "AIContent";

        var classDecl = ClassDeclaration(model.Name)
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.PartialKeyword)
            )
            .AddBaseListTypes(
                SimpleBaseType(ParseTypeName(baseClassName))
            );

        // Add [XmlRoot] attribute if XML serialization is enabled
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            classDecl = classDecl.AddAttributeLists(
                AttributeList(
                    SingletonSeparatedList(
                        Attribute(
                            ParseName("XmlRoot"),
                            AttributeArgumentList(
                                SingletonSeparatedList(
                                    AttributeArgument(
                                        LiteralExpression(
                                            SyntaxKind.StringLiteralExpression,
                                            Literal(xmlElementName)
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            );
        }

        // Add Kind property override
        var kindOverride = PropertyDeclaration(
                ParseTypeName("string"),
                Identifier("Kind")
            )
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.OverrideKeyword)
            )
            .WithExpressionBody(
                ArrowExpressionClause(
                    LiteralExpression(
                        SyntaxKind.StringLiteralExpression,
                        Literal(kindValue)
                    )
                )
            )
            .WithSemicolonToken(Token(SyntaxKind.SemicolonToken));

        classDecl = classDecl.AddMembers(kindOverride);

        // Add properties (excluding 'kind' since we added it as override)
        foreach (var prop in model.Properties.Where(p => p.Name != "kind"))
        {
            var property = GenerateContentProperty(prop, model);
            classDecl = classDecl.AddMembers(property);
        }

        // Add documentation
        if (!string.IsNullOrWhiteSpace(model.Documentation))
        {
            classDecl = classDecl.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(model.Documentation));
        }

        // Build usings based on serialization mode
        var usings = new List<UsingDirectiveSyntax>
        {
            UsingDirective(ParseName("System")),
            UsingDirective(ParseName("System.Collections.Generic"))
        };

        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            usings.Add(UsingDirective(ParseName("System.Xml.Serialization")));
        }

        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            usings.Add(UsingDirective(ParseName("System.Text.Json.Serialization")));
        }

        var compilationUnit = CompilationUnit()
            .AddUsings(usings.ToArray())
            .AddMembers(
                NamespaceDeclaration(ParseName(_rootNamespace))
                    .AddMembers(classDecl)
            );

        return CodeGenerationUtilities.FormatCode(compilationUnit);
    }

    private PropertyDeclarationSyntax GenerateContentProperty(PropertyDefinition propDef, ModelDefinition parentModel)
    {
        // XmlAttribute doesn't support nullable value types in .NET XmlSerializer
        // Check if this property will use XmlAttribute (either explicitly or via fallback for simple types)
        var willUseXmlAttribute = propDef.IsXmlAttribute ||
                                  (!propDef.IsXmlIgnore && !propDef.IsXmlText && !propDef.IsXmlElement &&
                                   TypeMapper.IsSimpleType(propDef.Type) && !ShouldUseXmlText(propDef, parentModel));
        var makeNullable = propDef.IsOptional && !willUseXmlAttribute;
        var strategy = willUseXmlAttribute ? NullableStrategy.ForceNonNullable : NullableStrategy.Default;
        var csharpType = TypeMapper.MapTypeSpecTypeToCSharp(propDef.Type, propDef.IsArray, makeNullable, strategy);

        var property = PropertyDeclaration(
                ParseTypeName(csharpType),
                Identifier(NamingConventions.ToPascalCase(propDef.Name))
            )
            .AddModifiers(Token(SyntaxKind.PublicKeyword))
            .AddAccessorListAccessors(
                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken)),
                AccessorDeclaration(SyntaxKind.SetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            );

        // Add serialization attributes based on mode
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            var xmlAttribute = DetermineXmlAttribute(propDef, parentModel);
            if (xmlAttribute != null)
            {
                property = property.AddAttributeLists(
                    AttributeList(SingletonSeparatedList(xmlAttribute))
                );
            }
        }

        // Add JSON attribute if JSON serialization is enabled
        if (_serializationMode.HasFlag(SerializationMode.Json) && !propDef.IsXmlIgnore)
        {
            property = _jsonAttributeGenerator.AddPropertyJsonAttributes(property, propDef);
        }

        // Add default initializer for certain properties
        if (propDef.IsOptional && NeedsDefaultValue(propDef))
        {
            property = property
                .WithInitializer(
                    EqualsValueClause(GetDefaultValue(propDef))
                )
                .WithSemicolonToken(Token(SyntaxKind.SemicolonToken));
        }

        return property;
    }

    private AttributeSyntax? DetermineXmlAttribute(PropertyDefinition propDef, ModelDefinition parentModel)
    {
        // Use decorator flags if present
        if (propDef.IsXmlIgnore)
        {
            return Attribute(ParseName("XmlIgnore"));
        }

        if (propDef.IsXmlText)
        {
            return Attribute(ParseName("XmlText"));
        }

        // Get XML name from decorator or generate from property name
        var xmlName = propDef.XmlName ?? NamingConventions.ToKebabCase(propDef.Name);

        // Use decorator-specified attribute type
        if (propDef.IsXmlAttribute)
        {
            return Attribute(
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
        }

        if (propDef.IsXmlElement)
        {
            return Attribute(
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
        }

        // Legacy heuristics (fallback for properties without decorators)

        // Special case: properties that should be XmlText based on pattern
        if (ShouldUseXmlText(propDef, parentModel))
        {
            return Attribute(ParseName("XmlText"));
        }

        // Special case: nested annotations should be flattened (ignore the nested object)
        if (propDef.Name == "annotations" || propDef.Name == "additionalProperties")
        {
            return Attribute(ParseName("XmlIgnore"));
        }

        // Default: use XmlAttribute for simple types, XmlElement for complex types
        if (TypeMapper.IsSimpleType(propDef.Type))
        {
            return Attribute(
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
        }

        // Complex types use XmlElement
        return Attribute(
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
    }

    private bool ShouldUseXmlText(PropertyDefinition propDef, ModelDefinition parentModel)
    {
        // Content types that should use inner text:
        // - TextContent.text
        // - TextReasoningContent.text (thinking)
        // - FunctionCallContent.arguments (JSON)
        // - FunctionResultContent.result (JSON)
        // - SystemMessage.content
        // - DeveloperMessage.content

        var contentName = parentModel.Name.ToLower();
        var propName = propDef.Name.ToLower();

        return (contentName.Contains("text") && propName == "text") ||
               (contentName.Contains("reasoning") && propName == "text") ||
               (contentName.Contains("functioncall") && propName == "arguments") ||
               (contentName.Contains("functionresult") && propName == "result") ||
               (propName == "content" && propDef.Type == "string");
    }

    private bool NeedsDefaultValue(PropertyDefinition propDef)
    {
        return propDef.Name == "exposed" && propDef.Type == "boolean";
    }

    private ExpressionSyntax GetDefaultValue(PropertyDefinition propDef)
    {
        if (propDef.Name == "exposed")
        {
            return LiteralExpression(SyntaxKind.FalseLiteralExpression);
        }

        return LiteralExpression(SyntaxKind.NullLiteralExpression);
    }
}
