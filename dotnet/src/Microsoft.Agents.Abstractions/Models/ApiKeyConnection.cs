using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// API Key Connection/// ALIGNED WITH: Agent Schema ApiKeyConnection/// SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)/// RATIONALE: API key-based authentication/// MESSAGING APP PATTERN:/// - Like Slack/Teams bot tokens/// - Simple key-based auth/// </summary>
    public partial class ApiKeyConnection
    {
        /// <summary>/// Connection type discriminator./// ALIGNED WITH: Agent Schema Connection.kind/// </summary>
        [XmlElement("kind")]
        [JsonPropertyName("kind")]
        public string Kind { get; set; }

        /// <summary>/// API key value./// ALIGNED WITH: Agent Schema ApiKeyConnection.key/// EXAMPLES:/// - "sk-proj-abc123..." (OpenAI)/// - "xoxb-..." (Slack)/// - Bearer token/// </summary>
        [XmlElement("key")]
        [JsonPropertyName("key")]
        public string Key { get; set; }

        /// <summary>/// Optional header name./// DEFAULT: "Authorization"/// EXAMPLES:/// - "Authorization" (most common)/// - "X-API-Key" (some APIs)/// - "X-Custom-Auth" (custom auth)/// </summary>
        [XmlElement("header-name")]
        [JsonPropertyName("headerName")]
        public string HeaderName { get; set; }

        /// <summary>/// Usage transparency description./// ALIGNED WITH: Agent Schema Connection.usageDescription/// </summary>
        [XmlElement("usage-description")]
        [JsonPropertyName("usageDescription")]
        public string UsageDescription { get; set; }
    }
}