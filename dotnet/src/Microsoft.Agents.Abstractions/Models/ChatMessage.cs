using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    [XmlInclude(typeof(SystemMessage)), XmlInclude(typeof(DeveloperMessage)), XmlInclude(typeof(AgentMessage)), XmlInclude(typeof(UserMessage)), XmlInclude(typeof(ToolMessage)), XmlInclude(typeof(ChannelMessage)), JsonPolymorphic(TypeDiscriminatorPropertyName = "role"), JsonDerivedType(typeof(SystemMessage), "system"), JsonDerivedType(typeof(DeveloperMessage), "developer"), JsonDerivedType(typeof(AgentMessage), "agent"), JsonDerivedType(typeof(UserMessage), "user"), JsonDerivedType(typeof(ToolMessage), "tool"), JsonDerivedType(typeof(ChannelMessage), "channel")]
    public abstract partial class ChatMessage
    {
        [XmlAttribute("message-id")]
        [JsonPropertyName("messageId")]
        public string MessageId { get; set; }
        [XmlAttribute("parent-message-id")]
        [JsonPropertyName("parentMessageId")]
        public string ParentMessageId { get; set; }
        [XmlIgnore]
        public string ThreadId { get; set; }
        [XmlIgnore]
        public List<AIContent> Contents { get; set; }
        [XmlIgnore]
        public string Text { get; set; }
        [XmlAttribute("author-name")]
        [JsonPropertyName("authorName")]
        public string AuthorName { get; set; }
        [XmlIgnore]
        public string UserId { get; set; }
        [XmlIgnore]
        public string AgentId { get; set; }
        [XmlIgnore]
        public string CompletionId { get; set; }
        [XmlAttribute("created-at")]
        [JsonPropertyName("createdAt")]
        public DateTime CreatedAt { get; set; }
        [XmlIgnore]
        public DateTime? CompletedAt { get; set; }
        [XmlIgnore]
        public Dictionary<string, object> Metadata { get; set; }
        [XmlIgnore]
        public object RawRepresentation { get; set; }
        [XmlIgnore, JsonPropertyName("role")]
        public abstract ChatRole Role { get; }
    }
}