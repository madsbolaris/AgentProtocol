using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    /// <summary>/// Developer message./// </summary>
    [XmlRoot("developer")]
    public partial class DeveloperMessage : ChatMessage
    {
        public override ChatRole Role => ChatRole.Developer;

        [XmlText]
        public string Content { get; set; }
    }
}