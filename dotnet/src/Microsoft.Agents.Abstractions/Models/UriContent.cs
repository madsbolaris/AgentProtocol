using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// URI Content/// BASE: Microsoft.Extensions.AI.UriContent/// SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/UriContent.cs/// REPRESENTS: Reference to external content via URI/// XML: &lt;uri&gt;https://example.com&lt;/uri&gt;/// </summary>
    [XmlRoot("uri")]
    public partial class UriContent : AIContentBase
    {
        public override string Kind => "uri";

        [XmlText]
        [JsonPropertyName("uri")]
        public string Uri { get; set; }
    }
}