using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    public partial class Participant
    {
        /// <summary>/// Participant identifier./// - For users: Entra User ID (Object ID)/// - For agents: Agent ID (Service Principal Object ID)/// - For system: "system"/// ALIGNMENT: Maps to ChatMessage.userId (if type=user) or ChatMessage.agentId (if type=agent)/// </summary>
        [XmlElement("id")]
        [JsonPropertyName("id")]
        public string Id { get; set; }

        /// <summary>/// Display name./// ALIGNMENT: Maps to ChatMessage.authorName/// </summary>
        [XmlElement("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }

        /// <summary>/// Role in the conversation./// EXAMPLES: "user", "assistant", "system"/// FROM: OpenAI LLM APIs - standard conversation roles/// NOTE: This is the same as ChatRole for participants/// - Participant identifies WHO is in the conversation/// - role identifies their function (user, assistant, system)/// </summary>
        [XmlElement("role")]
        [JsonPropertyName("role")]
        public string Role { get; set; }

        /// <summary>/// Participant metadata./// FLEXIBLE: Avatar URL, status, preferences, etc./// </summary>
        [XmlElement("metadata")]
        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
    }
}