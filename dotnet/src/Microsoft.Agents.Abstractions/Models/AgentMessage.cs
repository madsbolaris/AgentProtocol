using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Agent message./// </summary>
    [XmlRoot("agent")]
    public partial class AgentMessage : ChatMessage
    {
        public override ChatRole Role => ChatRole.Agent;

        [XmlAttribute("agent-id")]
        public string? AgentId { get; set; }
        [XmlAttribute("completion-id")]
        public string? CompletionId { get; set; }
        [XmlAttribute("completed-at")]
        public DateTime? CompletedAt { get; set; }
        [XmlElement("text", Type = typeof(TextContent)), XmlElement("thinking", Type = typeof(TextReasoningContent)), XmlElement("function-call", Type = typeof(FunctionCallContent)), XmlElement("image", Type = typeof(ImageContent)), XmlElement("adaptive-card", Type = typeof(AdaptiveCardContent)), XmlElement("user-input-request", Type = typeof(UserInputRequestContent)), XmlElement("suggested-actions", Type = typeof(SuggestedActionsContent)), XmlElement("document", Type = typeof(DocumentContent))]
        public List<AIContent> Contents { get; set; } = new List<AIContent>();
    }
}