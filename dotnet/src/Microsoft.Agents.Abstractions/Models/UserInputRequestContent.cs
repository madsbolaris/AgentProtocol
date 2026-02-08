using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// XML: &lt;user-input-request request-id="..." prompt="..." input-type="choice" required="true" /&gt;/// </summary>
    [XmlRoot("user-input-request")]
    public partial class UserInputRequestContent : AIContentBase
    {
        public override string Kind => "userInputRequest";

        [XmlAttribute("request-id")]
        [JsonPropertyName("requestId")]
        public string RequestId { get; set; }
        [XmlAttribute("prompt")]
        [JsonPropertyName("prompt")]
        public string Prompt { get; set; }
        [XmlAttribute("input-type")]
        [JsonPropertyName("inputType")]
        public string InputType { get; set; }
        [XmlAttribute("required")]
        [JsonPropertyName("required")]
        public bool Required { get; set; }
    }
}