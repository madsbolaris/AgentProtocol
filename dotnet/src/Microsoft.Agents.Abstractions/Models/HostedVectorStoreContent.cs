using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    [XmlRoot("hosted-vector-store")]
    public partial class HostedVectorStoreContent : AIContentBase
    {
        public override string Kind => "hostedVectorStore";

        [XmlAttribute("vector-store-id")]
        [JsonPropertyName("vectorStoreId")]
        public string VectorStoreId { get; set; }
        [XmlAttribute("name")]
        [JsonPropertyName("name")]
        public string Name { get; set; }
        [XmlAttribute("document-count")]
        [JsonPropertyName("documentCount")]
        public int DocumentCount { get; set; }
    }
}