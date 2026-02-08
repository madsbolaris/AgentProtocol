using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Base model for all AI content types./// Provides common properties for audience filtering, encryption, and extensibility./// RATIONALE: DRY principle - common properties inherited by all 29+ content types/// PROPERTIES:/// - audience: Content-level audience filtering (e.g., reasoning visible to assistant only)/// - encryption: Content-level encryption metadata/// - additionalProperties: Client-side extensibility (not serialized to XML)/// </summary>
    public abstract partial class AIContentBase
    {
        /// <summary>/// Target audience filter (comma-separated roles)./// Controls which roles should see this content:/// - Omitted/null: Visible to all roles (default)/// - "user": Human-only content (UI hints, summaries)/// - "agent": Agent-only content (reasoning, internal context)/// - "user,agent": Explicitly visible to both/// EXAMPLES:/// - &lt;thinking audience="agent"&gt;reasoning here&lt;/thinking&gt;/// - &lt;text audience="user"&gt;User-facing summary&lt;/text&gt;/// - &lt;adaptive-card audience="user" /&gt;/// </summary>
        [XmlAttribute("audience")]
        [JsonPropertyName("audience")]
        public string Audience { get; set; }

        /// <summary>/// Encryption information (simplified as string for XML)./// Contains encryption key reference and metadata./// RATIONALE: Simplified from complex EncryptionInfo object for XML compatibility/// FORMAT: JSON string or key reference/// </summary>
        [XmlAttribute("encryption")]
        [JsonPropertyName("encryption")]
        public string Encryption { get; set; }

        /// <summary>/// Additional properties for extensibility./// NOT SERIALIZED: Client-side metadata, transient state./// EXAMPLES:/// - Tracking IDs, correlation data/// - Client-specific rendering hints/// - Temporary computation results/// </summary>
        [XmlIgnore]
        [JsonIgnore]
        public Dictionary<string, object> AdditionalProperties { get; set; }
        [XmlAttribute("kind")]
        public abstract string Kind { get; }
    }
}