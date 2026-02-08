using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// System message./// </summary>
    [XmlRoot("system")]
    public partial class SystemMessage : ChatMessage
    {
        public override ChatRole Role => ChatRole.System;

        [XmlText]
        public string Content { get; set; }
    }
}