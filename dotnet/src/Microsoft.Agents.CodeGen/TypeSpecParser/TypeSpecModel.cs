namespace Microsoft.Agents.CodeGen.TypeSpecParser;

/// <summary>
/// Represents a parsed TypeSpec file with all models, enums, and unions.
/// This is our intermediate representation (AST) that bridges TypeSpec and C#.
/// </summary>
public class TypeSpecModel
{
    public string Namespace { get; set; } = string.Empty;
    public List<ModelDefinition> Models { get; set; } = new();
    public List<EnumDefinition> Enums { get; set; } = new();
    public List<UnionDefinition> Unions { get; set; } = new();
}

/// <summary>
/// Represents a TypeSpec model (equivalent to C# class).
/// </summary>
public class ModelDefinition
{
    public string Name { get; set; } = string.Empty;
    public string? BaseModel { get; set; }
    public string? Documentation { get; set; }
    public List<PropertyDefinition> Properties { get; set; } = new();
    public List<DecoratorDefinition> Decorators { get; set; } = new();

    // XML-specific metadata
    public string? XmlElementName { get; set; }
    public string? XmlNamespace { get; set; }
    public bool IsXmlRoot { get; set; }
}

/// <summary>
/// Represents a property in a TypeSpec model.
/// </summary>
public class PropertyDefinition
{
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = string.Empty;
    public bool IsOptional { get; set; }
    public bool IsArray { get; set; }
    public string? Documentation { get; set; }
    public List<DecoratorDefinition> Decorators { get; set; } = new();

    // XML-specific metadata
    public bool IsXmlAttribute { get; set; }
    public bool IsXmlElement { get; set; }
    public bool IsXmlText { get; set; }
    public bool IsXmlIgnore { get; set; }
    public string? XmlName { get; set; }
    public object? XmlDefaultValue { get; set; }

    // Content type metadata (for VS Code syntax highlighting)
    public List<string> ContentTypes { get; set; } = new();
}

/// <summary>
/// Represents a TypeSpec enum.
/// </summary>
public class EnumDefinition
{
    public string Name { get; set; } = string.Empty;
    public string? Documentation { get; set; }
    public List<EnumMemberDefinition> Members { get; set; } = new();
}

/// <summary>
/// Represents an enum member.
/// </summary>
public class EnumMemberDefinition
{
    public string Name { get; set; } = string.Empty;
    public string? Value { get; set; }
    public string? Documentation { get; set; }
}

/// <summary>
/// Represents a TypeSpec discriminated union.
/// </summary>
public class UnionDefinition
{
    public string Name { get; set; } = string.Empty;
    public string? Documentation { get; set; }
    public List<string> Variants { get; set; } = new();
    public string? DiscriminatorProperty { get; set; }

    // XML-specific metadata
    public bool IsXmlPolymorphic { get; set; }
}

/// <summary>
/// Represents a TypeSpec decorator (e.g., @xmlAttribute, @key).
/// </summary>
public class DecoratorDefinition
{
    public string Name { get; set; } = string.Empty;
    public Dictionary<string, object?> Arguments { get; set; } = new();
}
