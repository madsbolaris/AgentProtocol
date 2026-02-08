using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// XML: &lt;document title="..." document-id="..." source="..." mime-type="..."&gt;&lt;content&gt;...&lt;/content&gt;&lt;/document&gt;/// </summary>
    [XmlRoot("document")]
    public partial class DocumentContent : AIContentBase
    {
        public override string Kind => "document";

        [XmlAttribute("title")]
        [JsonPropertyName("title")]
        public string Title { get; set; }
        [XmlAttribute("document-id")]
        [JsonPropertyName("documentId")]
        public string DocumentId { get; set; }
        [XmlAttribute("source")]
        [JsonPropertyName("source")]
        public string Source { get; set; }
        [XmlAttribute("mime-type")]
        [JsonPropertyName("mimeType")]
        public string MimeType { get; set; }
        [XmlElement("content")]
        [JsonPropertyName("content")]
        public string Content { get; set; }
    }
}