using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    [XmlRoot("message-reaction")]
    public partial class MessageReactionContent : AIContentBase
    {
        public override string Kind => "messageReaction";

        [XmlAttribute("referenced-message-id")]
        [JsonPropertyName("referencedMessageId")]
        public string ReferencedMessageId { get; set; }
        [XmlElement("added")]
        [JsonPropertyName("reactionsAdded")]
        public List<MessageReaction> ReactionsAdded { get; set; }
        [XmlElement("removed")]
        [JsonPropertyName("reactionsRemoved")]
        public List<MessageReaction> ReactionsRemoved { get; set; }
    }
}