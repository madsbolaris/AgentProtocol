using System;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Thread Cleanup Strategy/// @usage/// Use Cases:/// - keep: Chat conversations, multi-turn interactions/// - delete: Extraction tasks, one-shot queries, stateless APIs/// </summary>
    public enum ThreadCleanup
    {
        Keep,
        Delete
    }
}