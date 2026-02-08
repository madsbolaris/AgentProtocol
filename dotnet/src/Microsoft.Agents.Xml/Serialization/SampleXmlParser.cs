using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Xml.Linq;
using Microsoft.Agents;

namespace Microsoft.Agents.Xml.Serialization;

/// <summary>
/// Parses the complete sample.xml file which contains tools section + messages.
/// </summary>
public class SampleXmlParser
{
    private readonly MessageSerializer _messageSerializer;

    public SampleXmlParser()
    {
        _messageSerializer = new MessageSerializer();
    }

    /// <summary>
    /// Parses sample.xml and returns both tools and messages.
    /// </summary>
    public SampleXmlDocument ParseFile(string filePath)
    {
        var content = File.ReadAllText(filePath);
        return Parse(content);
    }

    /// <summary>
    /// Parses XML string and returns both tools and messages.
    /// </summary>
    public SampleXmlDocument Parse(string xml)
    {
        var doc = XDocument.Parse(xml);
        var result = new SampleXmlDocument();

        // Extract tools section
        var toolsElement = doc.Descendants("tools").FirstOrDefault();
        if (toolsElement != null)
        {
            result.Tools = ParseTools(toolsElement);
        }

        // Extract message elements (everything except tools)
        var messageElements = doc.Descendants()
            .Where(e => e.Parent == doc.Root || e.Parent == null)
            .Where(e => e.Name.LocalName != "tools")
            .Where(e => !e.Name.LocalName.StartsWith("!")) // Skip comments
            .ToList();

        // Handle case where there's no root, or messages are direct children
        if (doc.Root != null && doc.Root.Name.LocalName != "tools")
        {
            // Check if root has message children
            messageElements = doc.Root.Elements()
                .Where(e => e.Name.LocalName != "tools")
                .ToList();
        }

        // Deserialize each message
        foreach (var element in messageElements)
        {
            try
            {
                var messageXml = element.ToString();
                var message = _messageSerializer.Deserialize(messageXml);
                result.Messages.Add(message);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Failed to parse message {element.Name}: {ex.Message}");
                // Continue parsing other messages
            }
        }

        return result;
    }

    private List<ToolDefinition> ParseTools(XElement toolsElement)
    {
        var tools = new List<ToolDefinition>();

        foreach (var toolElement in toolsElement.Elements("tool"))
        {
            var tool = new ToolDefinition
            {
                Name = toolElement.Attribute("name")?.Value ?? "",
                Description = toolElement.Attribute("description")?.Value
            };

            // Parse input parameters
            foreach (var inputElement in toolElement.Elements("input"))
            {
                var input = new ToolInputParameter
                {
                    Name = inputElement.Attribute("name")?.Value ?? "",
                    Type = inputElement.Attribute("type")?.Value ?? "text",
                    Required = bool.Parse(inputElement.Attribute("required")?.Value ?? "false"),
                    Value = inputElement.Attribute("value")?.Value,
                    Placeholder = inputElement.Attribute("placeholder")?.Value
                };

                tool.Inputs.Add(input);
            }

            tools.Add(tool);
        }

        return tools;
    }
}

/// <summary>
/// Represents the complete parsed sample.xml document.
/// </summary>
public class SampleXmlDocument
{
    /// <summary>
    /// Tool definitions from the &lt;tools&gt; section.
    /// </summary>
    public List<ToolDefinition> Tools { get; set; } = new();

    /// <summary>
    /// Conversation messages.
    /// </summary>
    public List<ChatMessage> Messages { get; set; } = new();
}

/// <summary>
/// Represents a tool definition.
/// </summary>
public class ToolDefinition
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public List<ToolInputParameter> Inputs { get; set; } = new();
}

/// <summary>
/// Represents a tool input parameter.
/// </summary>
public class ToolInputParameter
{
    public string Name { get; set; } = string.Empty;
    public string Type { get; set; } = "text";
    public bool Required { get; set; }
    public string? Value { get; set; }
    public string? Placeholder { get; set; }
}
