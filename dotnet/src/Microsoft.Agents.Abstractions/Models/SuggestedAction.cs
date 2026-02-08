using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Suggested Action/// Represents a single quick reply button/action/// </summary>
    [XmlType("action")]
    public partial class SuggestedAction
    {
        [XmlAttribute("title")]
        [JsonPropertyName("title")]
        public string Title { get; set; }
        [XmlAttribute("type")]
        [JsonPropertyName("actionType")]
        public string ActionType { get; set; }
        [XmlAttribute("value")]
        [JsonPropertyName("value")]
        public string Value { get; set; }
        [XmlAttribute("text")]
        [JsonPropertyName("text")]
        public string Text { get; set; }
    }
}