using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;adaptive-card version="1.5" fallback-text="..."&gt;{"type":"AdaptiveCard",...}&lt;/adaptive-card&gt;/// </summary>
    [XmlRoot("adaptive-card")]
    public partial class AdaptiveCardContent : AIContentBase
    {
        public override string Kind => "adaptiveCard";

        [XmlAttribute("version")]
        [JsonPropertyName("version")]
        public string Version { get; set; }
        [XmlAttribute("fallback-text")]
        [JsonPropertyName("fallbackText")]
        public string FallbackText { get; set; }
        [XmlText]
        [JsonPropertyName("card")]
        public string Card { get; set; }
    }
}