using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// XML: &lt;action name="button_clicked" text="Refresh" timestamp="..."&gt;{value}&lt;/action&gt;/// </summary>
    [XmlRoot("action")]
    public partial class ActionContent : AIContentBase
    {
        public override string Kind => "action";

        [XmlAttribute("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [XmlAttribute("text")]
        [JsonPropertyName("text")]
        public string Text { get; set; }
        [XmlAttribute("timestamp")]
        [JsonPropertyName("timestamp")]
        public DateTime Timestamp { get; set; }
        [XmlText]
        [JsonPropertyName("value")]
        public string Value { get; set; }
    }
}