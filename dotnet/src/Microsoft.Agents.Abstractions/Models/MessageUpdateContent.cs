using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Message Update Content (Message Edit)/// FROM: Activity Protocol messageUpdate activity/// ADDITION: Not in MAF or Azure Agent API/// REPRESENTS: Update to an existing message/// MESSAGING APP PATTERN:/// - Like editing a message in Slack or Teams/// - Message ID references the message to update/// - Updated content provided in separate ChatMessage/// XML: &lt;message-update message-id="msg_123" reason="typo_fix" /&gt;/// </summary>
    [XmlRoot("message-update")]
    public partial class MessageUpdateContent : AIContentBase
    {
        public override string Kind => "messageUpdate";

        [XmlAttribute("message-id")]
        [JsonPropertyName("messageId")]
        public string MessageId { get; set; }
        [XmlAttribute("reason")]
        [JsonPropertyName("reason")]
        public string Reason { get; set; }
    }
}