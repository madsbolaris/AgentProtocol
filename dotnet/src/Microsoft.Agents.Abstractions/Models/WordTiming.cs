using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Word Timing/// ADDITION: For synchronized transcript playback/// PURPOSE: Word-level timestamps for highlighting during audio/video playback/// </summary>
    public partial class WordTiming
    {
        [XmlElement("word")]
        [JsonPropertyName("word")]
        public string Word { get; set; }
        [XmlElement("start")]
        [JsonPropertyName("start")]
        public float Start { get; set; }
        [XmlElement("end")]
        [JsonPropertyName("end")]
        public float End { get; set; }
        [XmlElement("confidence")]
        [JsonPropertyName("confidence")]
        public float? Confidence { get; set; }
    }
}