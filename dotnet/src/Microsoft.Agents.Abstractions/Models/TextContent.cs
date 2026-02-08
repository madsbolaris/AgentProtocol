using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Text Content/// BASE: Microsoft.Extensions.AI.TextContent/// SOURCE: /extensions/src/Libraries/Microsoft.Extensions.AI.Abstractions/Contents/TextContent.cs/// XML: &lt;text&gt;Hello world&lt;/text&gt;/// </summary>
    [XmlRoot("text")]
    public partial class TextContent : AIContentBase
    {
        public override string Kind => "text";

        [XmlText]
        [JsonPropertyName("text")]
        public string Text { get; set; }
    }
}