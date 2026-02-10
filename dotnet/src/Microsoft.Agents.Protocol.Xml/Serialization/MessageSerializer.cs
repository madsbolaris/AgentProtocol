using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using System.Xml.Linq;
using System.Xml.Serialization;
using Microsoft.Agents;
using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Xml;

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

        // Post-process: Add Contents elements
        // Contents property doesn't have XML serialization attributes (conflicts with JSON)
        // So we serialize them manually here
        xml = AddContentsToXml(xml, message);

        return xml;
    }

    /// <summary>
    /// Serializes multiple messages to XML string with root element.
    /// </summary>
    public string SerializeMany(IEnumerable<ChatMessage> messages, string? rootElement = null)
    {
        using var stringWriter = new StringWriter();

        // Use Fragment conformance level when there's a root element
        var settings = new XmlWriterSettings
        {
            Indent = _writerSettings.Indent,
            IndentChars = _writerSettings.IndentChars,
            OmitXmlDeclaration = string.IsNullOrEmpty(rootElement) ? _writerSettings.OmitXmlDeclaration : true,
            Encoding = _writerSettings.Encoding,
            ConformanceLevel = string.IsNullOrEmpty(rootElement) ? ConformanceLevel.Document : ConformanceLevel.Fragment
        };

        using var xmlWriter = XmlWriter.Create(stringWriter, settings);

        if (!string.IsNullOrEmpty(rootElement))
        {
            xmlWriter.WriteStartElement(rootElement);
        }

        foreach (var message in messages)
        {
            // Serialize each message individually and parse as XDocument
            var messageXml = Serialize(message);
            var doc = XDocument.Parse(messageXml);
            doc.Root?.WriteTo(xmlWriter);
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

        // Extract Contents elements for messages that have AIContent
        // XmlElement attributes are commented out in generated models due to JSON conflict
        // So we parse Contents manually here
        ExtractContents(xml, message);

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
        var xml = SerializeMany(messages, rootElement);
        File.WriteAllText(filePath, xml);
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
    /// Allows known AIContent element types since they're parsed manually.
    /// </summary>
    private void OnUnknownElement(object? sender, XmlElementEventArgs e)
    {
        // Allow known AIContent element types - these are parsed manually in ExtractContents()
        var knownContentElements = new HashSet<string>(StringComparer.OrdinalIgnoreCase)
        {
            "text", "image", "audio", "video", "file", "document",
            "function-call", "function-result", "thinking",
            "adaptive-card", "suggested-actions", "action",
            "transcript", "error", "refusal", "data",
            "uri", "hosted-file", "hosted-vector-store",
            "message-reaction", "message-update", "message-delete",
            "event", "trace", "typing-indicator", "user-input-request",
            "content-filter-result", "search-result"
        };

        if (knownContentElements.Contains(e.Element.Name))
        {
            // Silently ignore - these will be handled by ExtractContents()
            return;
        }

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

    /// <summary>
    /// Adds Contents elements to serialized XML.
    /// Handles text, image, audio, video, file, function-call, function-result, thinking, etc.
    /// </summary>
    private string AddContentsToXml(string xml, ChatMessage message)
    {
        if (message.Contents == null || message.Contents.Count == 0)
        {
            return xml;
        }

        try
        {
            var doc = XDocument.Parse(xml);
            var root = doc.Root;
            if (root == null) return xml;

            // Serialize each content element
            foreach (var content in message.Contents)
            {
                XElement? contentElement = content switch
                {
                    TextContent text => SerializeTextContent(text),
                    ImageContent image => SerializeImageContent(image),
                    AudioContent audio => SerializeAudioContent(audio),
                    VideoContent video => SerializeVideoContent(video),
                    FileContent file => SerializeFileContent(file),
                    FunctionCallContent funcCall => SerializeFunctionCallContent(funcCall),
                    FunctionResultContent funcResult => SerializeFunctionResultContent(funcResult),
                    TextReasoningContent thinking => SerializeThinkingContent(thinking),
                    _ => null // Unsupported content type
                };

                if (contentElement != null)
                {
                    root.Add(contentElement);
                }
            }

            return doc.ToString();
        }
        catch (Exception)
        {
            // If adding contents fails, return original XML
            return xml;
        }
    }

    private XElement SerializeTextContent(TextContent text)
    {
        var elem = new XElement("text", text.Text ?? "");
        if (!string.IsNullOrEmpty(text.Audience))
        {
            elem.SetAttributeValue("audience", text.Audience);
        }
        return elem;
    }

    private XElement SerializeImageContent(ImageContent image)
    {
        var elem = new XElement("image");
        if (!string.IsNullOrEmpty(image.Uri))
        {
            elem.SetAttributeValue("uri", image.Uri);
        }
        if (!string.IsNullOrEmpty(image.Alt))
        {
            elem.SetAttributeValue("alt", image.Alt);
        }
        if (!string.IsNullOrEmpty(image.MimeType))
        {
            elem.SetAttributeValue("mime-type", image.MimeType);
        }
        return elem;
    }

    private XElement SerializeAudioContent(AudioContent audio)
    {
        var elem = new XElement("audio");
        if (!string.IsNullOrEmpty(audio.Uri))
        {
            elem.SetAttributeValue("uri", audio.Uri);
        }
        if (!string.IsNullOrEmpty(audio.MimeType))
        {
            elem.SetAttributeValue("mime-type", audio.MimeType);
        }
        return elem;
    }

    private XElement SerializeVideoContent(VideoContent video)
    {
        var elem = new XElement("video");
        if (!string.IsNullOrEmpty(video.Uri))
        {
            elem.SetAttributeValue("uri", video.Uri);
        }
        if (!string.IsNullOrEmpty(video.MimeType))
        {
            elem.SetAttributeValue("mime-type", video.MimeType);
        }
        return elem;
    }

    private XElement SerializeFileContent(FileContent file)
    {
        var elem = new XElement("file");
        if (!string.IsNullOrEmpty(file.Uri))
        {
            elem.SetAttributeValue("uri", file.Uri);
        }
        if (!string.IsNullOrEmpty(file.Filename))
        {
            elem.SetAttributeValue("filename", file.Filename);
        }
        if (!string.IsNullOrEmpty(file.MimeType))
        {
            elem.SetAttributeValue("mime-type", file.MimeType);
        }
        return elem;
    }

    private XElement SerializeFunctionCallContent(FunctionCallContent funcCall)
    {
        var elem = new XElement("function-call", funcCall.Arguments ?? "");
        if (!string.IsNullOrEmpty(funcCall.CallId))
        {
            elem.SetAttributeValue("call-id", funcCall.CallId);
        }
        if (!string.IsNullOrEmpty(funcCall.Name))
        {
            elem.SetAttributeValue("name", funcCall.Name);
        }
        if (!string.IsNullOrEmpty(funcCall.Audience))
        {
            elem.SetAttributeValue("audience", funcCall.Audience);
        }
        return elem;
    }

    private XElement SerializeFunctionResultContent(FunctionResultContent funcResult)
    {
        var elem = new XElement("function-result", funcResult.Result ?? "");
        if (!string.IsNullOrEmpty(funcResult.CallId))
        {
            elem.SetAttributeValue("call-id", funcResult.CallId);
        }
        if (!string.IsNullOrEmpty(funcResult.Name))
        {
            elem.SetAttributeValue("name", funcResult.Name);
        }
        return elem;
    }

    private XElement SerializeThinkingContent(TextReasoningContent thinking)
    {
        var elem = new XElement("thinking", thinking.Text ?? "");
        // Use audience attribute from AIContentBase for visibility control
        if (!string.IsNullOrEmpty(thinking.Audience))
        {
            elem.SetAttributeValue("audience", thinking.Audience);
        }
        return elem;
    }

    /// <summary>
    /// Extracts AIContent elements from XML and populates message.Contents.
    /// Handles text, image, audio, video, file, function-call, function-result, etc.
    /// </summary>
    private void ExtractContents(string xml, ChatMessage message)
    {
        try
        {
            var doc = System.Xml.Linq.XDocument.Parse(xml);
            var root = doc.Root;
            if (root == null) return;

            // Initialize Contents list if null
            if (message.Contents == null)
            {
                message.Contents = new List<AIContent>();
            }

            // Parse text elements
            foreach (var elem in root.Descendants("text"))
            {
                var textContent = new TextContent
                {
                    Text = elem.Value ?? ""
                };
                if (elem.Attribute("audience") != null)
                {
                    textContent.Audience = elem.Attribute("audience")!.Value;
                }
                message.Contents.Add(textContent);
            }

            // Parse image elements
            foreach (var elem in root.Descendants("image"))
            {
                var imageContent = new ImageContent
                {
                    Uri = elem.Attribute("uri")?.Value ?? ""
                };
                if (elem.Attribute("alt") != null || elem.Attribute("alt-text") != null)
                {
                    imageContent.Alt = elem.Attribute("alt")?.Value ?? elem.Attribute("alt-text")?.Value;
                }
                if (elem.Attribute("mime-type") != null)
                {
                    imageContent.MimeType = elem.Attribute("mime-type")!.Value;
                }
                message.Contents.Add(imageContent);
            }

            // Parse function-call elements
            foreach (var elem in root.Descendants("function-call"))
            {
                var funcContent = new FunctionCallContent
                {
                    CallId = elem.Attribute("call-id")?.Value ?? "",
                    Name = elem.Attribute("name")?.Value ?? "",
                    Arguments = elem.Value?.Trim() ?? ""
                };
                message.Contents.Add(funcContent);
            }

            // Parse function-result elements
            foreach (var elem in root.Descendants("function-result"))
            {
                var resultContent = new FunctionResultContent
                {
                    CallId = elem.Attribute("call-id")?.Value ?? "",
                    Name = elem.Attribute("name")?.Value ?? "",
                    Result = elem.Value?.Trim() ?? ""
                };
                message.Contents.Add(resultContent);
            }

            // Parse thinking elements
            foreach (var elem in root.Descendants("thinking"))
            {
                var thinkingContent = new TextReasoningContent
                {
                    Text = elem.Value ?? ""
                };
                // Read audience attribute from AIContentBase
                if (elem.Attribute("audience") != null)
                {
                    thinkingContent.Audience = elem.Attribute("audience")!.Value;
                }
                message.Contents.Add(thinkingContent);
            }

            // Parse audio elements
            foreach (var elem in root.Descendants("audio"))
            {
                var audioContent = new AudioContent
                {
                    Uri = elem.Attribute("uri")?.Value ?? ""
                };
                if (elem.Attribute("mime-type") != null)
                {
                    audioContent.MimeType = elem.Attribute("mime-type")!.Value;
                }
                message.Contents.Add(audioContent);
            }

            // Parse video elements
            foreach (var elem in root.Descendants("video"))
            {
                var videoContent = new VideoContent
                {
                    Uri = elem.Attribute("uri")?.Value ?? ""
                };
                if (elem.Attribute("mime-type") != null)
                {
                    videoContent.MimeType = elem.Attribute("mime-type")!.Value;
                }
                message.Contents.Add(videoContent);
            }

            // Parse file elements
            foreach (var elem in root.Descendants("file"))
            {
                var fileContent = new FileContent
                {
                    Uri = elem.Attribute("uri")?.Value ?? "",
                    Filename = elem.Attribute("filename")?.Value ?? ""
                };
                if (elem.Attribute("mime-type") != null)
                {
                    fileContent.MimeType = elem.Attribute("mime-type")!.Value;
                }
                message.Contents.Add(fileContent);
            }
        }
        catch (Exception)
        {
            // If parsing fails, leave Contents as-is (empty or whatever XmlSerializer gave us)
            // This maintains backwards compatibility
        }
    }
}
