using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Xml;
using System.Xml.Linq;
using System.Xml.Serialization;
using Microsoft.Agents;

namespace Microsoft.Agents.Protocol.Xml;

/// <summary>
/// Serializes and deserializes EvalThread instances to/from XML.
/// Handles heterogeneous thread elements (ChatMessage, Expect, EvalRun, Review).
/// </summary>
public class EvalXmlSerializer
{
    private readonly MessageSerializer _messageSerializer;
    private readonly Dictionary<Type, XmlSerializer> _serializerCache = new();
    private readonly XmlWriterSettings _writerSettings;
    private readonly XmlReaderSettings _readerSettings;

    public EvalXmlSerializer()
    {
        _messageSerializer = new MessageSerializer();

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
    /// Serializes an EvalThread to XML string.
    /// </summary>
    public string Serialize(EvalThread evalThread)
    {
        using var stringWriter = new StringWriter();
        using var xmlWriter = XmlWriter.Create(stringWriter, _writerSettings);

        WriteEvalThread(xmlWriter, evalThread);

        xmlWriter.Flush();
        return stringWriter.ToString();
    }

    /// <summary>
    /// Deserializes an EvalThread from XML string.
    /// </summary>
    public EvalThread Deserialize(string xml)
    {
        // Preprocess EvalXML to wrap raw block content in CDATA
        var preprocessedXml = EvalXmlPreprocessor.Preprocess(xml);

        using var stringReader = new StringReader(preprocessedXml);
        using var xmlReader = XmlReader.Create(stringReader, _readerSettings);

        xmlReader.MoveToContent();
        return ReadEvalThread(xmlReader);
    }

    /// <summary>
    /// Serializes EvalThread to file.
    /// </summary>
    public void SerializeToFile(EvalThread evalThread, string filePath)
    {
        using var fileStream = new FileStream(filePath, FileMode.Create);
        using var xmlWriter = XmlWriter.Create(fileStream, _writerSettings);

        WriteEvalThread(xmlWriter, evalThread);

        xmlWriter.Flush();
    }

    /// <summary>
    /// Deserializes EvalThread from file.
    /// </summary>
    public EvalThread DeserializeFromFile(string filePath)
    {
        // Read file content and preprocess
        var xml = File.ReadAllText(filePath);
        var preprocessedXml = EvalXmlPreprocessor.Preprocess(xml);

        using var stringReader = new StringReader(preprocessedXml);
        using var xmlReader = XmlReader.Create(stringReader, _readerSettings);

        xmlReader.MoveToContent();
        return ReadEvalThread(xmlReader);
    }

    private void WriteEvalThread(XmlWriter writer, EvalThread evalThread)
    {
        writer.WriteStartElement("thread");

        // Write attributes that exist on the regenerated model
        if (!string.IsNullOrEmpty(evalThread.Description))
        {
            writer.WriteAttributeString("desc", evalThread.Description);
        }

        if (evalThread.Repeat.HasValue)
        {
            writer.WriteAttributeString("repeat", evalThread.Repeat.Value.ToString());
        }

        // Write elements (messages, expects, runs, reviews)
        if (evalThread.Elements != null)
        {
            foreach (var element in evalThread.Elements)
            {
                WriteElement(writer, element);
            }
        }

        writer.WriteEndElement(); // thread
    }

    private void WriteElement(XmlWriter writer, ThreadElement element)
    {
        // Use runtime type checking since the generated types don't inherit from ThreadElement
        var elementType = element.GetType();

        if (typeof(ChatMessage).IsAssignableFrom(elementType))
        {
            // Use MessageSerializer for ChatMessage
            var messageXml = _messageSerializer.Serialize((ChatMessage)(object)element);
            var doc = XDocument.Parse(messageXml);
            doc.Root?.WriteTo(writer);
        }
        else if (elementType.Name == "Expect")
        {
            WriteExpect(writer, (Expect)(object)element);
        }
        else if (elementType.Name == "EvalRun")
        {
            WriteEvalRun(writer, (EvalRun)(object)element);
        }
        else if (elementType.Name == "Review")
        {
            WriteReview(writer, (Review)(object)element);
        }
        else
        {
            throw new InvalidOperationException(
                $"Unsupported thread element type: {element.GetType().Name}");
        }
    }

    private void WriteExpect(XmlWriter writer, Expect expect)
    {
        writer.WriteStartElement("expect");

        if (!string.IsNullOrEmpty(expect.Name))
        {
            writer.WriteAttributeString("name", expect.Name);
        }

        // Write reference output (agent message)
        if (expect.ReferenceOutput != null)
        {
            var messageXml = _messageSerializer.Serialize(expect.ReferenceOutput);
            var doc = XDocument.Parse(messageXml);
            doc.Root?.WriteTo(writer);
        }

        // Write judges
        foreach (var judge in expect.Judges)
        {
            WriteJudge(writer, judge);
        }

        // Write asserts
        foreach (var assert in expect.Asserts)
        {
            WriteAssert(writer, assert);
        }

        writer.WriteEndElement(); // expect
    }

    private void WriteEvalRun(XmlWriter writer, EvalRun run)
    {
        writer.WriteStartElement("run");

        if (run.MaxSteps.HasValue)
        {
            writer.WriteAttributeString("maxSteps", run.MaxSteps.Value.ToString());
        }

        if (run.TimeoutMs.HasValue)
        {
            writer.WriteAttributeString("timeoutMs", run.TimeoutMs.Value.ToString());
        }

        writer.WriteEndElement(); // run
    }

    private void WriteReview(XmlWriter writer, Review review)
    {
        writer.WriteStartElement("review");

        // Write judges
        foreach (var judge in review.Judges)
        {
            WriteJudge(writer, judge);
        }

        // Write asserts
        foreach (var assert in review.Asserts)
        {
            WriteAssert(writer, assert);
        }

        writer.WriteEndElement(); // review
    }

    private void WriteJudge(XmlWriter writer, Judge judge)
    {
        writer.WriteStartElement("judge");

        writer.WriteAttributeString("agent", judge.Agent);
        writer.WriteAttributeString("as", judge.As);

        if (judge.Scope.HasValue)
        {
            writer.WriteAttributeString("scope", judge.Scope.Value.ToString());
        }

        if (!string.IsNullOrEmpty(judge.Args))
        {
            writer.WriteString(judge.Args);
        }

        writer.WriteEndElement(); // judge
    }

    private void WriteAssert(XmlWriter writer, Assert assert)
    {
        writer.WriteStartElement("assert");

        if (assert.MinPassRate.HasValue)
        {
            writer.WriteAttributeString("minPassRate", assert.MinPassRate.Value.ToString("0.0##"));
        }

        writer.WriteString(assert.Expression);

        writer.WriteEndElement(); // assert
    }

    private EvalThread ReadEvalThread(XmlReader reader)
    {
        var evalThread = new EvalThread
        {
            Elements = new List<ThreadElement>()
        };

        // Read attributes - only read properties that exist on regenerated model
        if (reader.HasAttributes)
        {
            evalThread.Description = reader.GetAttribute("desc");

            var repeatAttr = reader.GetAttribute("repeat");
            if (!string.IsNullOrEmpty(repeatAttr) && int.TryParse(repeatAttr, out var repeat))
            {
                evalThread.Repeat = repeat;
            }
        }

        // Read child elements
        if (!reader.IsEmptyElement)
        {
            reader.Read();

            while (reader.NodeType != XmlNodeType.EndElement)
            {
                if (reader.NodeType == XmlNodeType.Element)
                {
                    var element = ReadElement(reader);
                    if (element != null)
                    {
                        evalThread.Elements.Add(element);
                    }
                }
                else
                {
                    reader.Read();
                }
            }
        }

        return evalThread;
    }

    private ThreadElement? ReadElement(XmlReader reader)
    {
        var elementName = reader.LocalName;

        // Cast results to ThreadElement via object since generated types don't inherit from ThreadElement
        return elementName.ToLower() switch
        {
            "user" or "agent" or "assistant" or "tool" or "system" or "developer" or "channel"
                => (ThreadElement)(object)ReadChatMessage(reader),
            "expect" => (ThreadElement)(object)ReadExpect(reader),
            "run" => (ThreadElement)(object)ReadEvalRun(reader),
            "review" => (ThreadElement)(object)ReadReview(reader),
            _ => throw new InvalidOperationException($"Unknown thread element: {elementName}")
        };
    }

    private ChatMessage ReadChatMessage(XmlReader reader)
    {
        // Extract the message element as XML string and use MessageSerializer
        var messageXml = reader.ReadOuterXml();
        return _messageSerializer.Deserialize(messageXml);
    }

    private Expect ReadExpect(XmlReader reader)
    {
        var expect = new Expect
        {
            Name = reader.GetAttribute("name"),
            Judges = new List<Judge>(),
            Asserts = new List<Assert>()
        };

        if (!reader.IsEmptyElement)
        {
            reader.Read();

            while (reader.NodeType != XmlNodeType.EndElement)
            {
                if (reader.NodeType == XmlNodeType.Element)
                {
                    var elementName = reader.LocalName;

                    switch (elementName.ToLower())
                    {
                        case "agent":
                        case "assistant":
                            expect.ReferenceOutput = ReadChatMessage(reader);
                            break;

                        case "judge":
                            expect.Judges.Add(ReadJudge(reader));
                            break;

                        case "assert":
                            expect.Asserts.Add(ReadAssert(reader));
                            break;

                        default:
                            reader.Skip();
                            break;
                    }
                }
                else
                {
                    reader.Read();
                }
            }
        }

        reader.ReadEndElement(); // expect
        return expect;
    }

    private EvalRun ReadEvalRun(XmlReader reader)
    {
        var run = new EvalRun();

        var maxStepsAttr = reader.GetAttribute("maxSteps");
        if (!string.IsNullOrEmpty(maxStepsAttr) && int.TryParse(maxStepsAttr, out var maxSteps))
        {
            run.MaxSteps = maxSteps;
        }

        var timeoutAttr = reader.GetAttribute("timeoutMs");
        if (!string.IsNullOrEmpty(timeoutAttr) && int.TryParse(timeoutAttr, out var timeout))
        {
            run.TimeoutMs = timeout;
        }

        if (!reader.IsEmptyElement)
        {
            reader.Skip();
        }
        else
        {
            reader.Read();
        }

        return run;
    }

    private Review ReadReview(XmlReader reader)
    {
        var review = new Review();

        if (!reader.IsEmptyElement)
        {
            reader.Read();

            while (reader.NodeType != XmlNodeType.EndElement)
            {
                if (reader.NodeType == XmlNodeType.Element)
                {
                    var elementName = reader.LocalName;

                    switch (elementName.ToLower())
                    {
                        case "judge":
                            review.Judges.Add(ReadJudge(reader));
                            break;

                        case "assert":
                            review.Asserts.Add(ReadAssert(reader));
                            break;

                        default:
                            reader.Skip();
                            break;
                    }
                }
                else
                {
                    reader.Read();
                }
            }
        }

        reader.ReadEndElement(); // review
        return review;
    }

    private Judge ReadJudge(XmlReader reader)
    {
        var judge = new Judge
        {
            Agent = reader.GetAttribute("agent") ?? string.Empty,
            As = reader.GetAttribute("as") ?? string.Empty
        };

        var scopeAttr = reader.GetAttribute("scope");
        if (!string.IsNullOrEmpty(scopeAttr) && Enum.TryParse<JudgeScope>(scopeAttr, out var scope))
        {
            judge.Scope = scope;
        }

        // Read args (inner text)
        if (!reader.IsEmptyElement)
        {
            judge.Args = reader.ReadElementContentAsString();
        }
        else
        {
            reader.Read();
        }

        return judge;
    }

    private Assert ReadAssert(XmlReader reader)
    {
        var assert = new Assert();

        var minPassRateAttr = reader.GetAttribute("minPassRate");
        if (!string.IsNullOrEmpty(minPassRateAttr) && float.TryParse(minPassRateAttr, out var minPassRate))
        {
            assert.MinPassRate = minPassRate;
        }

        // Read expression (inner text)
        assert.Expression = reader.ReadElementContentAsString();

        return assert;
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
}
