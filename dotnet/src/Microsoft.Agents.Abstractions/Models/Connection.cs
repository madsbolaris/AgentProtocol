using System;
using System.Xml.Serialization;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Abstractions.Models
{
    /// <summary>/// Connection - Authentication Configuration/// @usage/// Rationale:/// - Agent Schema provides richer connection model/// - Supports multiple connection types (reference, remote, API key, anonymous)/// - Includes authority (user vs system) for consent flows/// - Provides usageDescription for transparency/// </summary>
    public abstract partial class Connection
    {
        public abstract string Kind { get; }
    }
}