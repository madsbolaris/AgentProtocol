using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Content Filter Result Content/// FROM: Azure Agent API (ContentFilterResultContent)/// ADDITION: Not in MAF/// RATIONALE: Azure content moderation results/// M365: Compliance and audit requirements/// XML: &lt;content-filter-result filtered="true" category="hate" severity="medium" /&gt;/// </summary>
    [XmlRoot("filter-result")]
    public partial class ContentFilterResultContent : AIContentBase
    {
        public override string Kind => "contentFilterResult";

        [XmlAttribute("filtered")]
        [JsonPropertyName("filtered")]
        public bool Filtered { get; set; }
        [XmlAttribute("category")]
        [JsonPropertyName("category")]
        public string Category { get; set; }
        [XmlAttribute("severity")]
        [JsonPropertyName("severity")]
        public string Severity { get; set; }
    }
}