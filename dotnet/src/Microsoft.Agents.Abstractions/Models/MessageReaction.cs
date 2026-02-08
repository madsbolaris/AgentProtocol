using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Message Reaction (Individual Reaction)/// </summary>
    [XmlType("removed")]
    public partial class MessageReaction
    {
        [XmlElement("type")]
        [JsonPropertyName("type")]
        public string Type { get; set; }
        [XmlElement("user-id")]
        [JsonPropertyName("userId")]
        public string UserId { get; set; }
        [XmlElement("timestamp")]
        [JsonPropertyName("timestamp")]
        public DateTime? Timestamp { get; set; }
    }
}