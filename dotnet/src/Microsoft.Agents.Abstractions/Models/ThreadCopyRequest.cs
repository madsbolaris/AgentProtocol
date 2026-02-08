using System;
using System.Collections.Generic;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Thread Copy Request/// @usage/// Use Cases:/// - "Try this approach instead" → Copy thread, continue with different strategy/// - Testing agents: Same input conversation, multiple agent configurations/// - Template threads: Copy starter thread for new conversations/// - Conversation variations: Explore what-if scenarios/// </summary>
    public partial class ThreadCopyRequest
    {
        /// <summary>/// Whether to include full message history in copied thread./// @usage/// Use Cases:/// - true: Branch from specific conversation point (A/B testing, variations)/// - false: Reuse thread template/structure without history/// </summary>
        [XmlElement("include-history")]
        [JsonPropertyName("includeHistory")]
        public bool? IncludeHistory { get; set; }

        /// <summary>/// Metadata for the new copied thread./// OPTIONAL: Override or add metadata to distinguish copy from original/// COMMON FIELDS:/// - original_thread_id: Reference to source thread/// - copy_reason: Why this thread was copied/// - variant_name: For A/B testing variants/// MERGE BEHAVIOR:/// - Merges with original thread metadata/// - New values override original values for same keys/// </summary>
        [XmlElement("metadata")]
        [JsonPropertyName("metadata")]
        public Dictionary<string, object> Metadata { get; set; }
    }
}