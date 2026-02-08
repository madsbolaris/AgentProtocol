using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Citation/// FROM: LLMProxy + Anthropic (search_result_location pattern)/// ADDITION: Not in MAF or Azure Agent API/// M365: Critical for compliance and attribution/// </summary>
    public partial class Citation
    {
        [XmlElement("source")]
        [JsonPropertyName("source")]
        public string Source { get; set; }
        [XmlElement("text")]
        [JsonPropertyName("text")]
        public string Text { get; set; }
        [XmlElement("start")]
        [JsonPropertyName("start")]
        public int Start { get; set; }
        [XmlElement("end")]
        [JsonPropertyName("end")]
        public int End { get; set; }
        [XmlElement("score")]
        [JsonPropertyName("score")]
        public float? Score { get; set; }
    }
}