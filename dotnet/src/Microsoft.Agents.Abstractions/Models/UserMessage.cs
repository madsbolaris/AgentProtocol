using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// User message./// </summary>
    [XmlRoot("user")]
    public partial class UserMessage : ChatMessage
    {
        public override ChatRole Role => ChatRole.User;

        [XmlAttribute("user-id")]
        public string? UserId { get; set; }
        [XmlElement("text", Type = typeof(TextContent)), XmlElement("image", Type = typeof(ImageContent)), XmlElement("audio", Type = typeof(AudioContent)), XmlElement("video", Type = typeof(VideoContent)), XmlElement("file", Type = typeof(FileContent)), XmlElement("transcript", Type = typeof(TranscriptContent))]
        public List<AIContent> Contents { get; set; } = new List<AIContent>();
    }
}