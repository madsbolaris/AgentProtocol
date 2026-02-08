using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// XML: &lt;transcript text="..." language="en" confidence="0.98" speaker="..." /&gt;/// </summary>
    [XmlRoot("transcript")]
    public partial class TranscriptContent : AIContentBase
    {
        public override string Kind => "transcript";

        [XmlAttribute("text")]
        [JsonPropertyName("text")]
        public string Text { get; set; }
        [XmlAttribute("language")]
        [JsonPropertyName("language")]
        public string Language { get; set; }
        [XmlAttribute("confidence")]
        [JsonPropertyName("confidence")]
        public float Confidence { get; set; }
        [XmlAttribute("speaker")]
        [JsonPropertyName("speaker")]
        public string Speaker { get; set; }
    }
}