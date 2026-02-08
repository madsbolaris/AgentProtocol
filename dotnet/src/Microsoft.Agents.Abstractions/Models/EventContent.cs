using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;event name="..." timestamp="..."&gt;{value}&lt;/event&gt;/// </summary>
    [XmlRoot("event")]
    public partial class EventContent : AIContentBase
    {
        public override string Kind => "event";

        [XmlAttribute("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [XmlAttribute("timestamp")]
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        [XmlText]
        [JsonPropertyName("value")]
        public string Value { get; set; }
    }
}