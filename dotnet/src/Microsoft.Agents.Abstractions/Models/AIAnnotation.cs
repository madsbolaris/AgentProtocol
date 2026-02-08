using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// AI Annotation/// BASE: Microsoft.Extensions.AI.AIAnnotation (base class for annotations)/// SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/AIAnnotation.cs/// REPRESENTS: Metadata attached to content (e.g., citations)/// </summary>
    public partial class AIAnnotation
    {
        [XmlElement("type")]
        [JsonPropertyName("type")]
        public string Type { get; set; }
        [XmlElement("data")]
        [JsonPropertyName("data")]
        public Dictionary<string, object> Data { get; set; }
    }
}