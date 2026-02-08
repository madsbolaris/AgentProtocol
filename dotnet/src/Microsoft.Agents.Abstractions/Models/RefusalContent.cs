using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Refusal Content/// FROM: Azure Agent API (RefusalContent)/// ADDITION: Not in MAF/// RATIONALE: Model refuses to complete request (safety/policy)/// M365: Compliance and content policy tracking/// XML: &lt;refusal reason="..."&gt;Detailed refusal message&lt;/refusal&gt;/// </summary>
    [XmlRoot("refusal")]
    public partial class RefusalContent : AIContentBase
    {
        public override string Kind => "refusal";

        [XmlAttribute("reason")]
        [JsonPropertyName("reason")]
        public string Reason { get; set; }
    }
}