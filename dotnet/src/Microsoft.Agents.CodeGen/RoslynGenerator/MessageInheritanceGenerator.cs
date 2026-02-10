using Microsoft.CodeAnalysis;
using Microsoft.CodeAnalysis.CSharp;
using Microsoft.CodeAnalysis.CSharp.Syntax;
using Microsoft.CodeAnalysis.Formatting;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;
using static Microsoft.CodeAnalysis.CSharp.SyntaxFactory;

namespace Microsoft.Agents.CodeGen.RoslynGenerator;

/// <summary>
/// Generates role-specific message classes from ChatMessage + ChatRole enum.
/// Creates SystemMessage, UserMessage, AgentMessage, etc. with proper serialization attributes.
/// </summary>
public class MessageInheritanceGenerator
{
    private readonly string _rootNamespace;
    private readonly SerializationMode _serializationMode;
    private readonly XmlAttributeGenerator _xmlAttributeGenerator;
    private readonly JsonAttributeGenerator _jsonAttributeGenerator;

    public MessageInheritanceGenerator(string rootNamespace, SerializationMode serializationMode = SerializationMode.Both)
    {
        _rootNamespace = rootNamespace;
        _serializationMode = serializationMode;
        _xmlAttributeGenerator = new XmlAttributeGenerator();
        _jsonAttributeGenerator = new JsonAttributeGenerator();
    }

    /// <summary>
    /// Generates role-specific message classes from ChatMessage base model.
    /// </summary>
    public List<string> GenerateRoleMessages(
        ModelDefinition chatMessageModel,
        EnumDefinition chatRoleEnum,
        string outputDirectory)
    {
        var generatedFiles = new List<string>();

        // First, generate abstract base ChatMessage class
        var baseClassFile = GenerateBaseChatMessage(chatMessageModel, chatRoleEnum, outputDirectory);
        generatedFiles.Add(baseClassFile);

        // Then generate concrete role-specific classes
        foreach (var role in chatRoleEnum.Members)
        {
            var roleClassName = $"{NamingConventions.ToPascalCase(role.Name)}Message";
            var filePath = Path.Combine(outputDirectory, $"{roleClassName}.cs");

            var code = GenerateRoleSpecificMessage(
                chatMessageModel,
                role.Name,
                roleClassName,
                chatRoleEnum.Name
            );

            File.WriteAllText(filePath, code);
            generatedFiles.Add(filePath);
        }

        return generatedFiles;
    }

    private string GenerateBaseChatMessage(
        ModelDefinition model,
        EnumDefinition roleEnum,
        string outputDirectory)
    {
        var classAttributes = new List<AttributeSyntax>();

        // Create XmlInclude attributes for XML serialization
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            var xmlIncludeAttributes = roleEnum.Members
                .Select(role =>
                    Attribute(
                        ParseName("XmlInclude"),
                        AttributeArgumentList(
                            SingletonSeparatedList(
                                AttributeArgument(
                                    TypeOfExpression(
                                        ParseTypeName($"{NamingConventions.ToPascalCase(role.Name)}Message")
                                    )
                                )
                            )
                        )
                    )
                ).ToList();
            classAttributes.AddRange(xmlIncludeAttributes);
        }

        // Add JSON polymorphic attributes for JSON serialization
        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            // Add [JsonPolymorphic(TypeDiscriminatorPropertyName = "role")]
            classAttributes.Add(
                Attribute(
                    ParseName("JsonPolymorphic"),
                    AttributeArgumentList(
                        SingletonSeparatedList(
                            AttributeArgument(
                                LiteralExpression(
                                    SyntaxKind.StringLiteralExpression,
                                    Literal("role")
                                )
                            )
                            .WithNameEquals(NameEquals(IdentifierName("TypeDiscriminatorPropertyName")))
                        )
                    )
                )
            );

            // Add [JsonDerivedType] for each role-specific message
            foreach (var role in roleEnum.Members)
            {
                var roleValue = NamingConventions.ToKebabCase(role.Name);
                classAttributes.Add(
                    Attribute(
                        ParseName("JsonDerivedType"),
                        AttributeArgumentList(
                            SeparatedList(new[]
                            {
                                AttributeArgument(TypeOfExpression(ParseTypeName($"{NamingConventions.ToPascalCase(role.Name)}Message"))),
                                AttributeArgument(
                                    LiteralExpression(
                                        SyntaxKind.StringLiteralExpression,
                                        Literal(roleValue)
                                    )
                                )
                            })
                        )
                    )
                );
            }
        }

        // Generate properties (exclude 'role' since it's determined by subclass)
        var properties = model.Properties
            .Where(p => p.Name != "role")
            .Select(p => GenerateProperty(p))
            .ToArray();

        // Add abstract Role property with appropriate serialization attributes
        // NOTE: For JSON, use [JsonIgnore] to prevent conflict with JsonPolymorphic discriminator
        var rolePropertyAttrs = new List<AttributeSyntax>();
        if (_serializationMode.HasFlag(SerializationMode.Xml))
        {
            rolePropertyAttrs.Add(Attribute(ParseName("XmlIgnore")));
        }
        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            // Add [JsonIgnore] instead of [JsonPropertyName] to prevent conflict
            // with the JsonPolymorphic(TypeDiscriminatorPropertyName = "role") discriminator
            rolePropertyAttrs.Add(Attribute(ParseName("JsonIgnore")));
        }

        var roleProperty = PropertyDeclaration(
                ParseTypeName(roleEnum.Name),
                Identifier("Role")
            )
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.AbstractKeyword)
            )
            .AddAccessorListAccessors(
                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            );

        if (rolePropertyAttrs.Any())
        {
            roleProperty = roleProperty.AddAttributeLists(
                AttributeList(SeparatedList(rolePropertyAttrs))
            );
        }

        var classDecl = ClassDeclaration("ChatMessage")
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.AbstractKeyword),
                Token(SyntaxKind.PartialKeyword)
            )
            .AddMembers(properties)
            .AddMembers(roleProperty);

        // Add base class if ChatMessage is part of a union (e.g., ThreadElement)
        if (!string.IsNullOrWhiteSpace(model.BaseModel))
        {
            classDecl = classDecl.AddBaseListTypes(
                SimpleBaseType(ParseTypeName(model.BaseModel))
            );
        }

        if (classAttributes.Any())
        {
            classDecl = classDecl.AddAttributeLists(
                AttributeList(SeparatedList(classAttributes))
            );
        }

        // Add XML comment
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
            .WithLeadingTrivia(CodeGenerationUtilities.CreateAutoGeneratedHeader())
            .AddUsings(usings.ToArray())
            .AddMembers(
                NamespaceDeclaration(ParseName(_rootNamespace))
                    .AddMembers(classDecl)
            );

        var filePath = Path.Combine(outputDirectory, "ChatMessage.cs");
        var code = CodeGenerationUtilities.FormatCode(compilationUnit);
        File.WriteAllText(filePath, code);

        return filePath;
    }

    private string GenerateRoleSpecificMessage(
        ModelDefinition baseModel,
        string roleName,
        string className,
        string roleEnumName)
    {
        var xmlElementName = roleName.ToLower();

        // Determine which properties are role-specific
        var roleSpecificProps = GetRoleSpecificProperties(roleName);

        var classDecl = ClassDeclaration(className)
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.PartialKeyword)
            )
            .AddBaseListTypes(
                SimpleBaseType(ParseTypeName("ChatMessage"))
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

        // Add Role property override (documentation inherited from base class)
        var roleProperty = PropertyDeclaration(
                ParseTypeName(roleEnumName),
                Identifier("Role")
            )
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.OverrideKeyword)
            )
            .WithExpressionBody(
                ArrowExpressionClause(
                    MemberAccessExpression(
                        SyntaxKind.SimpleMemberAccessExpression,
                        ParseName(roleEnumName),
                        IdentifierName(NamingConventions.ToPascalCase(roleName))
                    )
                )
            )
            .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            .WithLeadingTrivia(
                Trivia(
                    PragmaWarningDirectiveTrivia(
                        Token(SyntaxKind.DisableKeyword),
                        SeparatedList<ExpressionSyntax>(new[] {
                            (ExpressionSyntax)IdentifierName("CS1591")
                        }),
                        true
                    )
                ),
                CarriageReturnLineFeed
            )
            .WithTrailingTrivia(
                CarriageReturnLineFeed,
                Trivia(
                    PragmaWarningDirectiveTrivia(
                        Token(SyntaxKind.RestoreKeyword),
                        SeparatedList<ExpressionSyntax>(new[] {
                            (ExpressionSyntax)IdentifierName("CS1591")
                        }),
                        true
                    )
                ),
                CarriageReturnLineFeed
            );

        // Add [JsonIgnore] if JSON serialization is enabled
        // Attributes don't inherit in C#, so we must add it to every override
        if (_serializationMode.HasFlag(SerializationMode.Json))
        {
            roleProperty = roleProperty.AddAttributeLists(
                AttributeList(SingletonSeparatedList(Attribute(ParseName("JsonIgnore"))))
            );
        }

        classDecl = classDecl.AddMembers(roleProperty);

        // Add role-specific properties
        foreach (var prop in roleSpecificProps)
        {
            classDecl = classDecl.AddMembers(prop);
        }

        // Add ShouldSerialize methods for nullable value type XML attributes
        var shouldSerializeMethods = GenerateShouldSerializeMethodsForRole(roleName, roleSpecificProps);
        foreach (var method in shouldSerializeMethods)
        {
            classDecl = classDecl.AddMembers(method);
        }

        // Add Content/Contents property based on role
        if (NeedsSimpleTextContent(roleName))
        {
            // System and Developer use simple text content
            var textProp = PropertyDeclaration(
                    ParseTypeName("string"),
                    Identifier("Content")
                )
                .AddModifiers(Token(SyntaxKind.PublicKeyword))
                .AddAccessorListAccessors(
                    AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                        .WithSemicolonToken(Token(SyntaxKind.SemicolonToken)),
                    AccessorDeclaration(SyntaxKind.SetAccessorDeclaration)
                        .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
                )
                .AddAttributeLists(
                    AttributeList(
                        SingletonSeparatedList(
                            Attribute(ParseName("XmlText"))
                        )
                    )
                );

            classDecl = classDecl.AddMembers(textProp);
        }
        else
        {
            // Other roles use Contents collection with polymorphic content
            var contentsProp = CreateContentsProperty(roleName);
            classDecl = classDecl.AddMembers(contentsProp);
        }

        // Add XML documentation
        var doc = $"{NamingConventions.ToPascalCase(roleName)} message.";
        classDecl = classDecl.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(doc));

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
            .WithLeadingTrivia(CodeGenerationUtilities.CreateAutoGeneratedHeader())
            .AddUsings(usings.ToArray())
            .AddMembers(
                NamespaceDeclaration(ParseName(_rootNamespace))
                    .AddMembers(classDecl)
            );

        return CodeGenerationUtilities.FormatCode(compilationUnit);
    }

    private PropertyDeclarationSyntax[] GetRoleSpecificProperties(string roleName)
    {
        var properties = new List<PropertyDeclarationSyntax>();

        switch (roleName.ToLower())
        {
            case "user":
                properties.Add(CreateAttributeProperty("UserId", "user-id", "string", nullable: true));
                break;

            case "agent":
                properties.Add(CreateAttributeProperty("AgentId", "agent-id", "string", nullable: true));
                properties.Add(CreateAttributeProperty("CompletionId", "completion-id", "string", nullable: true));
                properties.Add(CreateAttributeProperty("CompletedAt", "completed-at", "DateTime", nullable: true));
                break;

            case "tool":
                properties.Add(CreateAttributeProperty("CallId", "call-id", "string", nullable: true));
                properties.Add(CreateAttributeProperty("Name", "name", "string", nullable: true));
                break;
        }

        return properties.ToArray();
    }

    private PropertyDeclarationSyntax CreateAttributeProperty(
        string propertyName,
        string xmlName,
        string typeName,
        bool nullable = false)
    {
        var type = nullable ? $"{typeName}?" : typeName;

        var property = PropertyDeclaration(
                ParseTypeName(type),
                Identifier(propertyName)
            )
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.NewKeyword)
            )
            .AddAccessorListAccessors(
                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken)),
                AccessorDeclaration(SyntaxKind.SetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            )
            .AddAttributeLists(
                AttributeList(
                    SingletonSeparatedList(
                        Attribute(
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
                        )
                    )
                )
            );

        // Add XML documentation
        var documentation = $"Gets or sets the {xmlName}.";
        property = property.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(documentation));

        return property;
    }

    private IEnumerable<MethodDeclarationSyntax> GenerateShouldSerializeMethodsForRole(
        string roleName,
        PropertyDeclarationSyntax[] properties)
    {
        var methods = new List<MethodDeclarationSyntax>();

        // Determine which properties are nullable value types with XmlAttribute
        var nullableValueTypeProps = new Dictionary<string, string>
        {
            ["agent"] = "CompletedAt" // Agent role has CompletedAt as nullable DateTime
        };

        if (!nullableValueTypeProps.ContainsKey(roleName.ToLower()))
        {
            return methods;
        }

        var propertyName = nullableValueTypeProps[roleName.ToLower()];

        // Generate: public bool ShouldSerializeCompletedAt() => CompletedAt.HasValue;
        var methodName = $"ShouldSerialize{propertyName}";

        var method = MethodDeclaration(
                ParseTypeName("bool"),
                Identifier(methodName)
            )
            .AddModifiers(Token(SyntaxKind.PublicKeyword))
            .WithExpressionBody(
                ArrowExpressionClause(
                    MemberAccessExpression(
                        SyntaxKind.SimpleMemberAccessExpression,
                        IdentifierName(propertyName),
                        IdentifierName("HasValue")
                    )
                )
            )
            .WithSemicolonToken(Token(SyntaxKind.SemicolonToken));

        methods.Add(method);

        return methods;
    }

    private bool NeedsSimpleTextContent(string roleName)
    {
        return roleName.ToLower() is "system" or "developer";
    }

    private PropertyDeclarationSyntax CreateContentsProperty(string roleName)
    {
        // Create [XmlElement] attributes for each content type this role can have
        var contentTypes = GetContentTypesForRole(roleName);

        var attributes = contentTypes
            .Select(ct =>
                Attribute(
                    ParseName("XmlElement"),
                    AttributeArgumentList(
                        SeparatedList(new[] {
                            AttributeArgument(
                                LiteralExpression(
                                    SyntaxKind.StringLiteralExpression,
                                    Literal(ct.XmlName)
                                )
                            ),
                            AttributeArgument(
                                TypeOfExpression(ParseTypeName(ct.TypeName))
                            )
                            .WithNameEquals(NameEquals(IdentifierName("Type")))
                        })
                    )
                )
            ).ToList();

        var property = PropertyDeclaration(
                ParseTypeName("List<AIContent>"),
                Identifier("Contents")
            )
            .AddModifiers(
                Token(SyntaxKind.PublicKeyword),
                Token(SyntaxKind.NewKeyword)
            )
            .AddAccessorListAccessors(
                AccessorDeclaration(SyntaxKind.GetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken)),
                AccessorDeclaration(SyntaxKind.SetAccessorDeclaration)
                    .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            )
            .WithInitializer(
                EqualsValueClause(
                    ObjectCreationExpression(ParseTypeName("List<AIContent>"))
                        .WithArgumentList(ArgumentList())
                )
            )
            .WithSemicolonToken(Token(SyntaxKind.SemicolonToken))
            .AddAttributeLists(
                AttributeList(SeparatedList(attributes))
            );

        // Add XML documentation
        var documentation = $"Gets or sets the content items for this {roleName} message.";
        property = property.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(documentation));

        return property;
    }

    private List<(string XmlName, string TypeName)> GetContentTypesForRole(string roleName)
    {
        return roleName.ToLower() switch
        {
            "user" => new List<(string, string)>
            {
                ("text", "TextContent"),
                ("image", "ImageContent"),
                ("audio", "AudioContent"),
                ("video", "VideoContent"),
                ("file", "FileContent"),
                ("transcript", "TranscriptContent"),
            },
            "agent" => new List<(string, string)>
            {
                ("text", "TextContent"),
                ("thinking", "TextReasoningContent"),
                ("function-call", "FunctionCallContent"),
                ("image", "ImageContent"),
                ("adaptive-card", "AdaptiveCardContent"),
                ("user-input-request", "UserInputRequestContent"),
                ("suggested-actions", "SuggestedActionsContent"),
                ("document", "DocumentContent"),
            },
            "tool" => new List<(string, string)>
            {
                ("function-result", "FunctionResultContent"),
                ("error", "ErrorContent"),
            },
            "channel" => new List<(string, string)>
            {
                ("event", "EventContent"),
                ("trace", "TraceContent"),
                ("action", "ActionContent"),
            },
            _ => new List<(string, string)>
            {
                ("text", "TextContent"),
            }
        };
    }

    private PropertyDeclarationSyntax GenerateProperty(PropertyDefinition propDef)
    {
        // XmlAttribute doesn't support nullable value types in .NET XmlSerializer
        // So for optional value types with XmlAttribute, we use non-nullable
        var makeNullable = propDef.IsOptional && !propDef.IsXmlAttribute;
        var csharpType = TypeMapper.MapTypeSpecTypeToCSharp(propDef.Type, propDef.IsArray, makeNullable);

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

        // Determine XML attribute based on decorators
        AttributeSyntax? xmlAttribute = null;

        if (propDef.IsXmlIgnore)
        {
            xmlAttribute = Attribute(ParseName("XmlIgnore"));
        }
        else if (propDef.IsXmlAttribute)
        {
            // Use explicit XML name from decorator or generate from property name
            var xmlName = propDef.XmlName ?? NamingConventions.ToKebabCase(propDef.Name);
            xmlAttribute = Attribute(
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
        else if (propDef.IsXmlElement)
        {
            var xmlName = propDef.XmlName ?? NamingConventions.ToKebabCase(propDef.Name);
            xmlAttribute = Attribute(
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
        else
        {
            // Default: use XmlAttribute for serialized properties
            var xmlName = propDef.XmlName ?? NamingConventions.ToKebabCase(propDef.Name);
            xmlAttribute = Attribute(
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

        // Add serialization attributes based on mode
        if (_serializationMode.HasFlag(SerializationMode.Xml) && xmlAttribute != null)
        {
            property = property.AddAttributeLists(
                AttributeList(SingletonSeparatedList(xmlAttribute))
            );
        }

        // Add JSON attribute if JSON serialization is enabled
        if (_serializationMode.HasFlag(SerializationMode.Json) && !propDef.IsXmlIgnore)
        {
            property = _jsonAttributeGenerator.AddPropertyJsonAttributes(property, propDef);
        }

        // Add XML documentation
        var documentation = !string.IsNullOrWhiteSpace(propDef.Documentation)
            ? propDef.Documentation
            : $"Gets or sets the {NamingConventions.ToKebabCase(propDef.Name)}.";

        property = property.WithLeadingTrivia(CodeGenerationUtilities.CreateXmlComment(documentation));

        return property;
    }
}
