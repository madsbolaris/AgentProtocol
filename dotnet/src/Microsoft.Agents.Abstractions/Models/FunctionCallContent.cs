using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Function Call Content/// BASE: Microsoft.Extensions.AI.FunctionCallContent/// SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/FunctionCallContent.cs/// REPRESENTS: Agent's request to execute a tool/// XML: &lt;function-call call-id="..." name="..."&gt;{"arg": "value"}&lt;/function-call&gt;/// </summary>
    [XmlRoot("function-call")]
    public partial class FunctionCallContent : AIContentBase
    {
        public override string Kind => "functionCall";

        [XmlAttribute("call-id")]
        [JsonPropertyName("callId")]
        public string CallId { get; set; }
        [XmlAttribute("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [XmlText]
        [JsonPropertyName("arguments")]
        public string Arguments { get; set; }
    }
}