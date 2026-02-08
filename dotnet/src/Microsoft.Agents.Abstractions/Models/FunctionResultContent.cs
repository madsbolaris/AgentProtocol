using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Function Result Content/// BASE: Microsoft.Extensions.AI.FunctionResultContent/// SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/FunctionResultContent.cs/// REPRESENTS: Result of tool execution/// XML: &lt;function-result call-id="..." name="..."&gt;{"result": "value"}&lt;/function-result&gt;/// </summary>
    [XmlRoot("function-result")]
    public partial class FunctionResultContent : AIContentBase
    {
        public override string Kind => "functionResult";

        [XmlAttribute("call-id")]
        [JsonPropertyName("callId")]
        public string CallId { get; set; }
        [XmlAttribute("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [XmlText]
        [JsonPropertyName("result")]
        public string Result { get; set; }
    }
}