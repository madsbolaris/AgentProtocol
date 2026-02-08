using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;audio uri="..." mime-type="..." duration="15" /&gt;/// </summary>
    [XmlRoot("audio")]
    public partial class AudioContent : AIContentBase
    {
        public override string Kind => "audio";

        [XmlAttribute("uri")]
        [JsonPropertyName("uri")]
        public string Uri { get; set; }
        [XmlAttribute("mime-type")]
        [JsonPropertyName("mimeType")]
        public string MimeType { get; set; }
        [XmlAttribute("duration")]
        [JsonPropertyName("duration")]
        public int Duration { get; set; }
    }
}