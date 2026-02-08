using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    [XmlRoot("thread")]
    public partial class Thread
    {
        /// <summary>/// Unique thread identifier./// FROM: Azure Agent API/// GENERATED: Server-generated GUID/// M365: Maps to Conversation Key in Conversation Store/// </summary>
        [XmlAttribute("thread-id")]
        [JsonPropertyName("threadId")]
        public string ThreadId { get; set; }

        /// <summary>/// Thread lifecycle status./// FROM: Activity Protocol (EndOfConversation, ConversationUpdate patterns)/// ADDITION: Not in Azure Agent API/// RATIONALE: Track conversation lifecycle (active, closed, archived)/// STATES:/// - active: Thread is active and accepting messages (default)/// - closed: Conversation ended but retained for history/// - archived: Thread archived and not accepting new messages/// MESSAGING APP PATTERN:/// - Like Teams marking a chat as "closed" or "archived"/// - Like Slack archiving a channel/// - Like email conversation being "closed"/// ACTIVITY PROTOCOL MAPPING:/// - EndOfConversation activity → Thread.status = "closed"/// - ConversationUpdate with end reason → Thread.status = "closed"/// </summary>
        [XmlAttribute("status")]
        [JsonPropertyName("status")]
        public ThreadStatus? Status { get; set; }

        /// <summary>/// Channel information for multi-channel routing./// @usage/// Use Cases:/// - Route responses to correct channel/// - Store channel-specific conversation IDs for correlation/// - Enable channel-specific features (Teams adaptive cards, Slack blocks, etc.)/// - Track which platform the conversation originated from/// NOT SERIALIZED: Used for API routing only/// </summary>
        [XmlIgnore]
        [JsonIgnore]
        public ChannelInfo? ChannelInfo { get; set; }

        /// <summary>/// Participants in this thread./// ADDITION: Not in Azure Agent API/// RATIONALE: Critical for group conversations/// MESSAGING APP REQUIREMENT:/// - Every conversation has participants/// - Enables: 1:1, group chats, channels/// - Supports adding/removing participants/// M365: Maps to conversation participants in Teams/Outlook/// NOT SERIALIZED: Participant info included in individual messages/// </summary>
        [XmlIgnore]
        [JsonIgnore]
        public List<Participant> Participants { get; set; }

        /// <summary>/// Messages in this thread./// FROM: Azure Agent API (Thread.messages)/// M365: Stored in Conversation Store as Canonical Events/// XML: Direct children of &lt;thread&gt;, serialized as role-specific elements/// </summary>
        [XmlArray("messages"), XmlArrayItem("chat-message")]
        [JsonPropertyName("messages")]
        public List<ChatMessage> Messages { get; set; }

        /// <summary>/// Custom metadata for the thread./// FROM: Azure Agent API/// M365: Can store conversation metadata (topic, participants, etc.)/// NOT SERIALIZED: Used for API metadata only/// </summary>
        [XmlIgnore]
        [JsonIgnore]
        public Dictionary<string, object> Metadata { get; set; }

        /// <summary>/// Timestamp when thread was created./// </summary>
        [XmlAttribute("created-at")]
        [JsonPropertyName("createdAt")]
        public DateTime CreatedAt { get; set; }

        /// <summary>/// Timestamp of last message./// </summary>
        [XmlAttribute("last-message-at")]
        [JsonPropertyName("lastMessageAt")]
        public DateTime? LastMessageAt { get; set; }

        /// <summary>/// Timestamp of last activity (message, event, or status change)./// ADDITION: For proactive messaging Phase 2 (polling support)/// RATIONALE: Enables polling pattern for clients without webhook capability/// - Updated when: new message, new event, status change, participant change/// - Allows: GET /threads?updatedSince={timestamp} for polling/// PROACTIVE MESSAGING SUPPORT:/// - Phase 1 (Webhooks): POST notification to subscriber webhook URL/// - Phase 2 (Polling): Client polls GET /threads?updatedSince={lastActivityAt}/// - Phase 3 (SSE): Real-time push via GET /threads/{threadId}/events (SSE stream)/// PATTERN: Like GitHub's "updated_at" field for issue polling/// </summary>
        [XmlAttribute("last-activity-at")]
        [JsonPropertyName("lastActivityAt")]
        public DateTime? LastActivityAt { get; set; }

        /// <summary>/// Number of unread messages/events for subscribed clients./// ADDITION: For proactive messaging Phase 2 (polling support)/// RATIONALE: Enables notification badge counts/// - Incremented on: new message, new event (role="channel" excluded by client preference)/// - Reset by: Client marks thread as read via POST /threads/{threadId}/read/// PATTERN: Like messaging app unread counts (Teams, Slack, WhatsApp)/// </summary>
        [XmlAttribute("unread-count")]
        [JsonPropertyName("unreadCount")]
        public int? UnreadCount { get; set; }
    }
}