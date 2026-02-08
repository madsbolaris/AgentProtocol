using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// XML: &lt;file uri="..." filename="..." mime-type="..." size-bytes="1024" /&gt;/// </summary>
    [XmlRoot("file")]
    public partial class FileContent : AIContentBase
    {
        public override string Kind => "file";

        [XmlAttribute("uri")]
        [JsonPropertyName("uri")]
        public string Uri { get; set; }
        [XmlAttribute("filename")]
        [JsonPropertyName("filename")]
        public string Filename { get; set; }
        [XmlAttribute("mime-type")]
        [JsonPropertyName("mimeType")]
        public string MimeType { get; set; }
        [XmlAttribute("size-bytes")]
        [JsonPropertyName("sizeBytes")]
        public long SizeBytes { get; set; }
    }
}