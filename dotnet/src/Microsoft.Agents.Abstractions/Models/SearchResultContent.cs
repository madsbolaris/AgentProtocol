using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;search-result title="..." url="..." score="0.94"&gt;&lt;snippet&gt;...&lt;/snippet&gt;&lt;/search-result&gt;/// </summary>
    [XmlRoot("search-result")]
    public partial class SearchResultContent : AIContentBase
    {
        public override string Kind => "searchResult";

        [XmlAttribute("title")]
        [JsonPropertyName("title")]
        public string Title { get; set; }
        [XmlAttribute("url")]
        [JsonPropertyName("url")]
        public string Url { get; set; }
        [XmlAttribute("score")]
        [JsonPropertyName("score")]
        public float Score { get; set; }
        [XmlElement("snippet")]
        [JsonPropertyName("snippet")]
        public string Snippet { get; set; }
    }
}