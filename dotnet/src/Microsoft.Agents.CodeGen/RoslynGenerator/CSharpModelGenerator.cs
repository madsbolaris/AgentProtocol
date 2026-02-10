using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Formatting;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates C# model classes from TypeSpec definitions using Roslyn.
/// Produces clean, idiomatic C# with XML and/or JSON serialization attributes.
/// </summary>
public class CSharpModelGenerator
{
    private readonly string _rootNamespace;
    private readonly SerializationMode _serializationMode;
    private readonly XmlAttributeGenerator _xmlAttributeGenerator;
    private readonly JsonAttributeGenerator _jsonAttributeGenerator;

    public CSharpModelGenerator(string rootNamespace, SerializationMode serializationMode = SerializationMode.Both)
    {
        _rootNamespace = rootNamespace;
        _serializationMode = serializationMode;
        _xmlAttributeGenerator = new XmlAttributeGenerator();
        _jsonAttributeGenerator = new JsonAttributeGenerator();
    }

    public List<string> GenerateModels(TypeSpecModel typeSpec, string outputDirectory)
    {
        var generatedFiles = new List<string>();

        Directory.CreateDirectory(outputDirectory);

        // Generate enums
        foreach (var enumDef in typeSpec.Enums)
        {
            var filePath = Path.Combine(outputDirectory, $"{enumDef.Name}.cs");
            var code = GenerateEnum(enumDef);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate model classes
        foreach (var modelDef in typeSpec.Models)
        {
            var filePath = Path.Combine(outputDirectory, $"{modelDef.Name}.cs");
            var code = GenerateModel(modelDef);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        // Generate union base classes
        foreach (var unionDef in typeSpec.Unions)
        {
            var filePath = Path.Combine(outputDirectory, $"{unionDef.Name}.cs");
            var code = GenerateUnion(unionDef);
            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        return generatedFiles;
    }

    private string GenerateEnum(EnumDefinition enumDef)
    {
        // Create enum members
        var members = enumDef.Members.Select(m =>
            EnumMemberDeclaration(Identifier(NamingConventions.ToPascalCase(m.Name)))
        ).ToArray();

        // Create enum declaration
        var enumDecl = EnumDeclaration(enumDef.Name)
            .AddModifiers(Token(SyntaxKind.PublicKeyword))
            .AddMembers(members);

        // Add XML comment (always generate one for public enums)
        var enumDocumentation = !string.IsNullOrWhiteSpace(enumDef.Documentation)
            ? enumDef.Documentation
            : $"{enumDef.Name} enumeration.";

        enumDecl = enumDecl.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(enumDocumentation));

        // Create compilation unit with appropriate usings
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
                    .AddMembers(enumDecl)
            );

        return CodeGenerationUtilities.FormatCode(compilationUnit);
    }

    private string GenerateModel(ModelDefinition modelDef)
    {
        // Create properties with XML attributes
        var properties = modelDef.Properties.Select(p => GenerateProperty(p)).ToArray();

        // Create class declaration
        var classDecl = ClassDeclaration(modelDef.Name)
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.PartialKeyword)
            )
            .AddMembers(properties);

        // Special case: AIContentBase should extend AIContent and override Kind
        if (modelDef.Name == "AIContentBase")
        {
            // Make it abstract and extend AIContent
            classDecl = classDecl.WithModifiers(
                TokenList(
                    Token(SyntaxKind.PublicKeyword),
                    Token(SyntaxKind.AbstractKeyword),
                    Token(SyntaxKind.PartialKeyword)
                )
            );
            // Add base class
            classDecl = classDecl.AddBaseListTypes(
                SimpleBaseType(ParseTypeName("AIContent"))
            );
            // Add override abstract Kind property for discriminator
            // NOTE: Add [JsonIgnore] to prevent conflict with JsonPolymorphic discriminator
            var kindAttributes = new List<AttributeSyntax>
            {
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
            };

            // Add JsonIgnore to prevent conflict with polymorphic discriminator
            if (_serializationMode.HasFlag(SerializationMode.Json))
            {
                kindAttributes.Add(Attribute(ParseName("JsonIgnore")));
            }

            var kindProperty = PropertyDeclaration(
                    ParseTypeName("string"),
                    Identifier("Kind")
                )
                .AddModifiers(
                    Token(SyntaxKind.PublicKeyword),
                    Token(SyntaxKind.OverrideKeyword),
                    Token(SyntaxKind.AbstractKeyword)
                )
                .AddAccessorListAccessors(
                    AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                        .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
                )
                .AddAttributeLists(
                    kindAttributes.Select(attr => AttributeList(SingletonSeparatedList(attr))).ToArray()
                );
            classDecl = classDecl.AddMembers(kindProperty);
        }

        // Add serialization attributes based on mode
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            classDecl = _xmlAttributeGenerator.AddXmlAttributes(classDecl, modelDef);
        }

        // Add XML comment (always generate one for public classes)
        var classDocumentation = !string.IsNullOrWhiteSpace(modelDef.Documentation)
            ? modelDef.Documentation
            : $"Represents a {NamingConventions.ToKebabCase(modelDef.Name)}.";

        classDecl = classDecl.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(classDocumentation));

        // Create compilation unit with appropriate usings
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

    private PropertyDeclarationSyntax GenerateProperty(PropertyDefinition propDef)
    {
        // Map TypeSpec types to C# types
        var csharpType = TypeMapper.MapTypeSpecTypeToCSharp(propDef.Type, propDef.IsArray, propDef.IsOptional);

        // Create property with getter/setter
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
            property = _xmlAttributeGenerator.AddPropertyXmlAttributes(property, propDef);
        }

        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            property = _jsonAttributeGenerator.AddPropertyJsonAttributes(property, propDef);
        }

        // Add XML comment (always generate one for public properties)
        var documentation = !string.IsNullOrWhiteSpace(propDef.Documentation)
            ? propDef.Documentation
            : $"Gets or sets the {NamingConventions.ToKebabCase(propDef.Name)}.";

        property = property.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(documentation));

        return property;
    }

    private string GenerateUnion(UnionDefinition unionDef)
    {
        // For now, generate an abstract base class
        // Variants will derive from this
        var classDecl = ClassDeclaration(unionDef.Name)
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.AbstractKeyword),
                Token(SyntaxKind.PartialKeyword)
            );

        // Add discriminator property if specified
        if (!string.IsNullOrWhiteSpace(unionDef.DiscriminatorProperty))
        {
            var discriminatorProp = PropertyDeclaration(
                    ParseTypeName("string"),
                    Identifier(NamingConventions.ToPascalCase(unionDef.DiscriminatorProperty))
                )
                .AddModifiers(Token(SyntaxKind.PublicKeyword), Token(SyntaxKind.AbstractKeyword))
                .AddAccessorListAccessors(
                    AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                        .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
                );

            classDecl = classDecl.AddMembers(discriminatorProp);
        }

        // Add XML comment
        if (!string.IsNullOrWhiteSpace(unionDef.Documentation))
        {
            classDecl = classDecl.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(unionDef.Documentation));
        }

        // Create compilation unit with appropriate usings
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

        return CodeGenerationUtilities.FormatCode(compilationUnit);
    }

}
