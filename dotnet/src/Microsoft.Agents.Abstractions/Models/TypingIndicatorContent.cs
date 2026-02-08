using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;typing-indicator from="user_123" status="typing" timestamp="..." /&gt;/// </summary>
    [XmlRoot("typing-indicator")]
    public partial class TypingIndicatorContent : AIContentBase
    {
        public override string Kind => "typingIndicator";

        [XmlAttribute("from")]
        [JsonPropertyName("from")]
        public string From { get; set; }
        [XmlAttribute("timestamp")]
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
    }
}