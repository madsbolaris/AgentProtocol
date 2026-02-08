using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// XML: &lt;suggested-actions&gt;&lt;action title="Yes" type="message" value="yes" /&gt;&lt;/suggested-actions&gt;/// </summary>
    [XmlRoot("suggested-actions")]
    public partial class SuggestedActionsContent : AIContentBase
    {
        public override string Kind => "suggestedActions";

        [XmlElement("action")]
        [JsonPropertyName("actions")]
        public List<SuggestedAction> Actions { get; set; }
    }
}