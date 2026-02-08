using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Data Content/// BASE: Microsoft.Extensions.AI.DataContent/// SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/DataContent.cs/// REPRESENTS: Arbitrary structured data/// XML: &lt;data uri="..." mime-type="..."&gt;base64data&lt;/data&gt;/// </summary>
    [XmlRoot("data")]
    public partial class DataContent : AIContentBase
    {
        public override string Kind => "data";

        [XmlAttribute("uri")]
        [JsonPropertyName("uri")]
        public string Uri { get; set; }
        [XmlAttribute("mime-type")]
        [JsonPropertyName("mimeType")]
        public string MimeType { get; set; }
        [XmlText]
        [JsonPropertyName("value")]
        public string Value { get; set; }
    }
}