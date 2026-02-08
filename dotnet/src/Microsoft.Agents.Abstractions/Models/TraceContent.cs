using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;trace name="..." label="..." severity="information" timestamp="..."&gt;{value}&lt;/trace&gt;/// </summary>
    [XmlRoot("trace")]
    public partial class TraceContent : AIContentBase
    {
        public override string Kind => "trace";

        [XmlAttribute("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [XmlAttribute("label")]
        [JsonPropertyName("label")]
        public string Label { get; set; }
        [XmlAttribute("severity")]
        [JsonPropertyName("severity")]
        public string Severity { get; set; }
        [XmlAttribute("timestamp")]
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        [XmlText]
        [JsonPropertyName("value")]
        public string Value { get; set; }
    }
}