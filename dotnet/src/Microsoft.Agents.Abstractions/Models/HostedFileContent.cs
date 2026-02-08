using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents
{
    [XmlRoot("hosted-file")]
    public partial class HostedFileContent : AIContentBase
    {
        public override string Kind => "hostedFile";

        [XmlAttribute("file-id")]
        [JsonPropertyName("fileId")]
        public string FileId { get; set; }
        [XmlAttribute("filename")]
        [JsonPropertyName("filename")]
        public string Filename { get; set; }
        [XmlAttribute("media-type")]
        [JsonPropertyName("mediaType")]
        public string MediaType { get; set; }
        [XmlAttribute("size-bytes")]
        [JsonPropertyName("sizeBytes")]
        public long SizeBytes { get; set; }
    }
}