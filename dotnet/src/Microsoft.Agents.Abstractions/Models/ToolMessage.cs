using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Tool message./// </summary>
    [XmlRoot("tool")]
    public partial class ToolMessage : ChatMessage
    {
        public override ChatRole Role => ChatRole.Tool;

        [XmlAttribute("call-id")]
        public string? CallId { get; set; }
        [XmlAttribute("name")]
        public string? Name { get; set; }
        [XmlElement("function-result", Type = typeof(FunctionResultContent)), XmlElement("error", Type = typeof(ErrorContent))]
        public List<AIContent> Contents { get; set; } = new List<AIContent>();
    }
}