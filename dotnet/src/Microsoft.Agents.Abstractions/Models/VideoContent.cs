using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Video Content/// FROM: Azure Agent API (VideoContent)/// ADDITION: Not in MAF/// Represents video data that can be included in messages./// M365: Multi-modal scenarios (video input, video responses, screen recordings)/// XML: &lt;video uri="..." mime-type="..." width="1920" height="1080" duration="120" frame-rate="30" /&gt;/// </summary>
    [XmlRoot("video")]
    public partial class VideoContent : AIContentBase
    {
        public override string Kind => "video";

        [XmlAttribute("uri")]
        [JsonPropertyName("uri")]
        public string Uri { get; set; }
        [XmlAttribute("mime-type")]
        [JsonPropertyName("mimeType")]
        public string MimeType { get; set; }
        [XmlAttribute("width")]
        [JsonPropertyName("width")]
        public int Width { get; set; }
        [XmlAttribute("height")]
        [JsonPropertyName("height")]
        public int Height { get; set; }
        [XmlAttribute("duration")]
        [JsonPropertyName("duration")]
        public int Duration { get; set; }
        [XmlAttribute("frame-rate")]
        [JsonPropertyName("frameRate")]
        public int FrameRate { get; set; }
    }
}