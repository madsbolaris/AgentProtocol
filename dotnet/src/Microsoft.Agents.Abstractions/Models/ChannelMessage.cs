using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Channel message./// </summary>
    [XmlRoot("channel")]
    public partial class ChannelMessage : ChatMessage
    {
        public override ChatRole Role => ChatRole.Channel;

        [XmlElement("event", Type = typeof(EventContent)), XmlElement("trace", Type = typeof(TraceContent)), XmlElement("action", Type = typeof(ActionContent))]
        public List<AIContent> Contents { get; set; } = new List<AIContent>();
    }
}