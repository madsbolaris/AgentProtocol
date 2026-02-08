using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using System.Xml.Serialization;
using Microsoft.Agents;
using Microsoft.Agents.Abstractions.Models;

namespace Microsoft.Agents.Xml.Serialization;

/// <summary>
/// Serializes and deserializes ChatMessage instances to/from XML.
/// Handles polymorphic message types (SystemMessage, UserMessage, etc.).
/// </summary>
public class MessageSerializer
{
    private readonly Dictionary<Type, XmlSerializer> _serializerCache = new();
    private readonly XmlWriterSettings _writerSettings;
    private readonly XmlReaderSettings _readerSettings;

    public MessageSerializer()
    {
        _writerSettings = new XmlWriterSettings
        {
            Indent = true,
            IndentChars = "  ",
            OmitXmlDeclaration = false,
            Encoding = Encoding.UTF8
        };

        _readerSettings = new XmlReaderSettings
        {
            IgnoreWhitespace = false,
            IgnoreComments = true
        };
    }

    /// <summary>
    /// Serializes a single message to XML string.
    /// </summary>
    public string Serialize(ChatMessage message)
    {
        using var stringWriter = new StringWriter();
        using var xmlWriter = XmlWriter.Create(stringWriter, _writerSettings);

        var serializer = GetSerializer(message.GetType());
        serializer.Serialize(xmlWriter, message);
        xmlWriter.Flush();

        var xml = stringWriter.ToString();

        // Post-process: Add inner text for SystemMessage and DeveloperMessage
        // These use inner text content which conflicts with [XmlAttribute] from base class
        // So we handle it manually here
        if (message is SystemMessage systemMessage && !string.IsNullOrEmpty(systemMessage.Content))
        {
            xml = AddInnerTextToElement(xml, "system", systemMessage.Content);
        }
        else if (message is DeveloperMessage developerMessage && !string.IsNullOrEmpty(developerMessage.Content))
        {
            xml = AddInnerTextToElement(xml, "developer", developerMessage.Content);
        }

        return xml;
    }

    /// <summary>
    /// Serializes multiple messages to XML string with root element.
    /// </summary>
    public string SerializeMany(IEnumerable<ChatMessage> messages, string? rootElement = null)
    {
        using var stringWriter = new StringWriter();
        using var xmlWriter = XmlWriter.Create(stringWriter, _writerSettings);

        if (!string.IsNullOrEmpty(rootElement))
        {
            xmlWriter.WriteStartElement(rootElement);
        }

        foreach (var message in messages)
        {
            var serializer = GetSerializer(message.GetType());
            serializer.Serialize(xmlWriter, message);
        }

        if (!string.IsNullOrEmpty(rootElement))
        {
            xmlWriter.WriteEndElement();
        }

        xmlWriter.Flush();
        return stringWriter.ToString();
    }

    /// <summary>
    /// Deserializes a single message from XML string.
    /// Automatically detects message type from root element.
    /// Auto-generates message-id if not provided.
    /// Throws on unsupported attributes.
    /// </summary>
    public ChatMessage Deserialize(string xml)
    {
        using var stringReader = new StringReader(xml);
        using var xmlReader = XmlReader.Create(stringReader, _readerSettings);

        // Read to the first element to detect type
        xmlReader.MoveToContent();
        var elementName = xmlReader.LocalName;

        var messageType = GetMessageTypeFromElementName(elementName);
        var serializer = GetSerializer(messageType);

        // Hook up event to catch unknown attributes
        serializer.UnknownAttribute += OnUnknownAttribute;
        serializer.UnknownElement += OnUnknownElement;

        var message = (ChatMessage)serializer.Deserialize(xmlReader)!;

        // Unhook events
        serializer.UnknownAttribute -= OnUnknownAttribute;
        serializer.UnknownElement -= OnUnknownElement;

        // Extract inner text for SystemMessage and DeveloperMessage
        // These use inner text content which conflicts with [XmlAttribute] from base class
        // So we handle it manually here
        if (message is SystemMessage systemMessage)
        {
            var content = ExtractInnerText(xml, "system");
            if (content != null)
            {
                systemMessage.Content = content;
            }
        }
        else if (message is DeveloperMessage developerMessage)
        {
            var content = ExtractInnerText(xml, "developer");
            if (content != null)
            {
                developerMessage.Content = content;
            }
        }

        // Auto-generate message-id if missing
        if (string.IsNullOrEmpty(message.MessageId))
        {
            message.MessageId = $"msg_{Guid.NewGuid():N}";
        }

        return message;
    }

    /// <summary>
    /// Deserializes multiple messages from XML string.
    /// </summary>
    public List<ChatMessage> DeserializeMany(string xml, string? rootElement = null)
    {
        var messages = new List<ChatMessage>();

        using var stringReader = new StringReader(xml);
        using var xmlReader = XmlReader.Create(stringReader, _readerSettings);

        xmlReader.MoveToContent();

        // Skip root element if provided
        if (!string.IsNullOrEmpty(rootElement))
        {
            xmlReader.ReadStartElement(rootElement);
        }

        while (xmlReader.NodeType != XmlNodeType.EndElement && xmlReader.NodeType != XmlNodeType.None)
        {
            if (xmlReader.NodeType == XmlNodeType.Element)
            {
                var elementName = xmlReader.LocalName;
                var messageType = GetMessageTypeFromElementName(elementName);
                var serializer = GetSerializer(messageType);

                // Hook up event to catch unknown attributes
                serializer.UnknownAttribute += OnUnknownAttribute;
                serializer.UnknownElement += OnUnknownElement;

                var message = (ChatMessage)serializer.Deserialize(xmlReader)!;

                // Unhook events
                serializer.UnknownAttribute -= OnUnknownAttribute;
                serializer.UnknownElement -= OnUnknownElement;

                // Auto-generate message-id if missing
                if (string.IsNullOrEmpty(message.MessageId))
                {
                    message.MessageId = $"msg_{Guid.NewGuid():N}";
                }

                messages.Add(message);
            }
            else
            {
                xmlReader.Read();
            }
        }

        return messages;
    }

    /// <summary>
    /// Serializes message to file.
    /// </summary>
    public void SerializeToFile(ChatMessage message, string filePath)
    {
        using var fileStream = new FileStream(filePath, FileMode.Create);
        using var xmlWriter = XmlWriter.Create(fileStream, _writerSettings);

        var serializer = GetSerializer(message.GetType());
        serializer.Serialize(xmlWriter, message);
    }

    /// <summary>
    /// Serializes multiple messages to file.
    /// </summary>
    public void SerializeManyToFile(IEnumerable<ChatMessage> messages, string filePath, string? rootElement = "messages")
    {
        using var fileStream = new FileStream(filePath, FileMode.Create);
        using var xmlWriter = XmlWriter.Create(fileStream, _writerSettings);

        if (!string.IsNullOrEmpty(rootElement))
        {
            xmlWriter.WriteStartElement(rootElement);
        }

        foreach (var message in messages)
        {
            var serializer = GetSerializer(message.GetType());
            serializer.Serialize(xmlWriter, message);
        }

        if (!string.IsNullOrEmpty(rootElement))
        {
            xmlWriter.WriteEndElement();
        }

        xmlWriter.Flush();
    }

    /// <summary>
    /// Deserializes message from file.
    /// Auto-generates message-id if not provided.
    /// Throws on unsupported attributes.
    /// </summary>
    public ChatMessage DeserializeFromFile(string filePath)
    {
        using var fileStream = new FileStream(filePath, FileMode.Open);
        using var xmlReader = XmlReader.Create(fileStream, _readerSettings);

        xmlReader.MoveToContent();
        var elementName = xmlReader.LocalName;

        var messageType = GetMessageTypeFromElementName(elementName);
        var serializer = GetSerializer(messageType);

        // Hook up event to catch unknown attributes
        serializer.UnknownAttribute += OnUnknownAttribute;
        serializer.UnknownElement += OnUnknownElement;

        var message = (ChatMessage)serializer.Deserialize(xmlReader)!;

        // Unhook events
        serializer.UnknownAttribute -= OnUnknownAttribute;
        serializer.UnknownElement -= OnUnknownElement;

        // Auto-generate message-id if missing
        if (string.IsNullOrEmpty(message.MessageId))
        {
            message.MessageId = $"msg_{Guid.NewGuid():N}";
        }

        return message;
    }

    /// <summary>
    /// Deserializes multiple messages from file.
    /// </summary>
    public List<ChatMessage> DeserializeManyFromFile(string filePath, string? rootElement = null)
    {
        var xml = File.ReadAllText(filePath);
        return DeserializeMany(xml, rootElement);
    }

    private XmlSerializer GetSerializer(Type type)
    {
        if (!_serializerCache.TryGetValue(type, out var serializer))
        {
            serializer = new XmlSerializer(type);
            _serializerCache[type] = serializer;
        }

        return serializer;
    }

    private Type GetMessageTypeFromElementName(string elementName)
    {
        return elementName.ToLower() switch
        {
            "system" => typeof(SystemMessage),
            "developer" => typeof(DeveloperMessage),
            "user" => typeof(UserMessage),
            "agent" => typeof(AgentMessage),
            "assistant" => typeof(AgentMessage), // Backwards compatibility alias
            "tool" => typeof(ToolMessage),
            "channel" => typeof(ChannelMessage),
            _ => throw new InvalidOperationException($"Unknown message type: {elementName}")
        };
    }

    /// <summary>
    /// Event handler for unknown XML attributes - throws to enforce strict schema validation.
    /// </summary>
    private void OnUnknownAttribute(object? sender, XmlAttributeEventArgs e)
    {
        throw new InvalidOperationException(
            $"Unknown attribute '{e.Attr.Name}' on element '<{e.ObjectBeingDeserialized.GetType().Name}>' at line {e.LineNumber}. " +
            $"This attribute is not defined in the TypeSpec schema. " +
            $"Supported attributes can be found in the generated model classes."
        );
    }

    /// <summary>
    /// Event handler for unknown XML elements - throws to enforce strict schema validation.
    /// </summary>
    private void OnUnknownElement(object? sender, XmlElementEventArgs e)
    {
        throw new InvalidOperationException(
            $"Unknown element '<{e.Element.Name}>' at line {e.LineNumber}. " +
            $"This element is not defined in the TypeSpec schema. " +
            $"Supported elements can be found in the generated model classes."
        );
    }

    /// <summary>
    /// Adds inner text content to an XML element.
    /// Converts self-closing tags to opening/closing tags with content.
    /// </summary>
    private string AddInnerTextToElement(string xml, string elementName, string content)
    {
        // Handle both self-closing and regular closing tags
        var selfClosingPattern = $"<{elementName}([^>]*)\\s*/>";
        var closingPattern = $"<{elementName}([^>]*)>\\s*</{elementName}>";

        // Replace self-closing tag: <element /> → <element>content</element>
        if (System.Text.RegularExpressions.Regex.IsMatch(xml, selfClosingPattern))
        {
            xml = System.Text.RegularExpressions.Regex.Replace(
                xml,
                selfClosingPattern,
                $"<{elementName}$1>{EscapeXmlText(content)}</{elementName}>"
            );
        }
        // Replace empty element: <element></element> → <element>content</element>
        else if (System.Text.RegularExpressions.Regex.IsMatch(xml, closingPattern))
        {
            xml = System.Text.RegularExpressions.Regex.Replace(
                xml,
                closingPattern,
                $"<{elementName}$1>{EscapeXmlText(content)}</{elementName}>"
            );
        }

        return xml;
    }

    /// <summary>
    /// Escapes special XML characters in text content.
    /// </summary>
    private string EscapeXmlText(string text)
    {
        return text
            .Replace("&", "&amp;")
            .Replace("<", "&lt;")
            .Replace(">", "&gt;");
    }

    /// <summary>
    /// Extracts inner text from an XML element after deserialization.
    /// </summary>
    private string? ExtractInnerText(string xml, string elementName)
    {
        var pattern = $"<{elementName}[^>]*>([^<]*)</{elementName}>";
        var match = System.Text.RegularExpressions.Regex.Match(xml, pattern);

        if (match.Success)
        {
            return UnescapeXmlText(match.Groups[1].Value);
        }

        return null;
    }

    /// <summary>
    /// Unescapes XML entities in text content.
    /// </summary>
    private string UnescapeXmlText(string text)
    {
        return text
            .Replace("&lt;", "<")
            .Replace("&gt;", ">")
            .Replace("&amp;", "&");
    }
}
