using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Reference Connection/// ALIGNED WITH: Agent Schema ReferenceConnection/// SOURCE: https://github.com/microsoft/AgentSchema (agentschema/model/connection.tsp)/// RATIONALE: Named connection reference to pre-configured connections/// MESSAGING APP PATTERN:/// - Like referencing a stored bot token by name/// - Avoids credential duplication/// - Enables connection reuse/// </summary>
    public partial class ReferenceConnection
    {
        /// <summary>/// Connection type discriminator./// ALIGNED WITH: Agent Schema Connection.kind/// </summary>
        [XmlElement("kind")]
        [JsonPropertyName("kind")]
        public string Kind { get; set; }

        /// <summary>/// Connection reference name./// ALIGNED WITH: Agent Schema ReferenceConnection.name/// EXAMPLES: "myOpenAIConnection", "productionDB", "mcpServer"/// </summary>
        [XmlElement("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }

        /// <summary>/// Usage transparency description./// ALIGNED WITH: Agent Schema Connection.usageDescription/// RATIONALE: Shown to users for consent/transparency/// EXAMPLE: "Access your OneDrive files to search for relevant documents"/// </summary>
        [XmlElement("usage-description")]
        [JsonPropertyName("usageDescription")]
        public string UsageDescription { get; set; }
    }
}