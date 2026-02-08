using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Anonymous Connection/// ALIGNED WITH: Agent Schema AnonymousConnection/// SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)/// RATIONALE: No authentication required (public endpoints)/// </summary>
    public partial class AnonymousConnection
    {
        /// <summary>/// Connection type discriminator./// ALIGNED WITH: Agent Schema Connection.kind/// </summary>
        [XmlElement("kind")]
        [JsonPropertyName("kind")]
        public string Kind { get; set; }

        /// <summary>/// Usage transparency description./// ALIGNED WITH: Agent Schema Connection.usageDescription/// </summary>
        [XmlElement("usage-description")]
        [JsonPropertyName("usageDescription")]
        public string UsageDescription { get; set; }
    }
}