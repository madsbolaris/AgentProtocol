using System.Xml;
using System.Xml.Schema;
using System.Xml.Serialization;
using Microsoft.Agents.CodeGen.TypeSpecParser;
using Microsoft.Agents.CodeGen.Utilities;

namespace Microsoft.Agents.CodeGen.XmlSchemaGenerator;

/// <summary>
/// Generates XML Schema (XSD) from TypeSpec definitions.
/// Provides validation and IDE support for XML files.
/// </summary>
public class XsdGenerator
{
    public string GenerateSchema(TypeSpecModel typeSpec, string outputDirectory)
    {
        var schema = new XmlSchema
        {
            TargetNamespace = "http://schemas.agent.ai/messages/v1",
            ElementFormDefault = XmlSchemaForm.Qualified
        };

        // Add namespace imports
        var xsNamespace = new XmlSerializerNamespaces();
        xsNamespace.Add("xs", "http://www.w3.org/2001/XMLSchema");

        // Generate complex types for each model
        foreach (var model in typeSpec.Models)
        {
            var complexType = CreateComplexType(model);
            schema.Items.Add(complexType);

            // Add root element if this is an XML root
            if (model.IsXmlRoot && !string.IsNullOrWhiteSpace(model.XmlElementName))
            {
                var element = new XmlSchemaElement
                {
                    Name = model.XmlElementName,
                    SchemaTypeName = new XmlQualifiedName(model.Name, schema.TargetNamespace)
                };
                schema.Items.Add(element);
            }
        }

        // Generate simple types for enums
        foreach (var enumDef in typeSpec.Enums)
        {
            var simpleType = CreateSimpleType(enumDef);
            schema.Items.Add(simpleType);
        }

        // Write schema to file
        var schemaFile = Path.Combine(outputDirectory, "messages.xsd");
        using var writer = XmlWriter.Create(schemaFile, new XmlWriterSettings
        {
            Indent = true,
            IndentChars = "  "
        });
        schema.Write(writer);

        return schemaFile;
    }

    private XmlSchemaComplexType CreateComplexType(ModelDefinition model)
    {
        var complexType = new XmlSchemaComplexType
        {
            Name = model.Name
        };

        var sequence = new XmlSchemaSequence();

        foreach (var prop in model.Properties)
        {
            if (!prop.IsXmlAttribute)
            {
                var element = new XmlSchemaElement
                {
                    Name = NamingConventions.ToKebabCase(prop.Name),
                    SchemaTypeName = MapTypeToXsdType(prop.Type),
                    MinOccurs = prop.IsOptional ? 0 : 1,
                    MaxOccurs = prop.IsArray ? decimal.MaxValue : 1
                };
                sequence.Items.Add(element);
            }
        }

        complexType.Particle = sequence;

        // Add attributes
        foreach (var prop in model.Properties)
        {
            if (prop.IsXmlAttribute)
            {
                var attribute = new XmlSchemaAttribute
                {
                    Name = NamingConventions.ToKebabCase(prop.Name),
                    SchemaTypeName = MapTypeToXsdType(prop.Type),
                    Use = prop.IsOptional ? XmlSchemaUse.Optional : XmlSchemaUse.Required
                };
                complexType.Attributes.Add(attribute);
            }
        }

        return complexType;
    }

    private XmlSchemaSimpleType CreateSimpleType(EnumDefinition enumDef)
    {
        var simpleType = new XmlSchemaSimpleType
        {
            Name = enumDef.Name
        };

        var restriction = new XmlSchemaSimpleTypeRestriction
        {
            BaseTypeName = new XmlQualifiedName("string", "http://www.w3.org/2001/XMLSchema")
        };

        foreach (var member in enumDef.Members)
        {
            restriction.Facets.Add(new XmlSchemaEnumerationFacet
            {
                Value = NamingConventions.ToCamelCase(member.Name)
            });
        }

        simpleType.Content = restriction;
        return simpleType;
    }

    private XmlQualifiedName MapTypeToXsdType(string typeSpecType)
    {
        var xsdType = typeSpecType switch
        {
            "string" => "string",
            "int32" => "int",
            "int64" => "long",
            "float32" => "float",
            "float64" => "double",
            "boolean" => "boolean",
            "utcDateTime" => "dateTime",
            "bytes" => "base64Binary",
            _ => "string"
        };

        return new XmlQualifiedName(xsdType, "http://www.w3.org/2001/XMLSchema");
    }
}
