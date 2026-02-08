using System;
using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace Microsoft.Agents.Protocol.Models.Common;

/// <summary>
/// Connection - Authentication Configuration
/// Supports multiple connection types (reference, remote, API key, anonymous)
/// </summary>
[JsonPolymorphic(TypeDiscriminatorPropertyName = "kind")]
[JsonDerivedType(typeof(ReferenceConnection), "reference")]
[JsonDerivedType(typeof(RemoteConnection), "remote")]
[JsonDerivedType(typeof(ApiKeyConnection), "key")]
[JsonDerivedType(typeof(AnonymousConnection), "anonymous")]
public abstract class Connection
{
    /// <summary>
    /// Authorization level (user or system)
    /// </summary>
    [JsonPropertyName("authority")]
    public string? Authority { get; set; }

    /// <summary>
    /// Usage transparency description shown to users for consent
    /// </summary>
    [JsonPropertyName("usageDescription")]
    public string? UsageDescription { get; set; }
}

/// <summary>
/// Reference Connection - Named connection reference to pre-configured connections
/// </summary>
public class ReferenceConnection : Connection
{
    /// <summary>
    /// Connection reference name
    /// </summary>
    [JsonPropertyName("name")]
    public required string Name { get; set; }
}

/// <summary>
/// API Key Connection - API key-based authentication
/// </summary>
public class ApiKeyConnection : Connection
{
    /// <summary>
    /// API key value
    /// </summary>
    [JsonPropertyName("key")]
    public required string Key { get; set; }

    /// <summary>
    /// Optional header name (defaults to "Authorization")
    /// </summary>
    [JsonPropertyName("headerName")]
    public string? HeaderName { get; set; } = "Authorization";
}

/// <summary>
/// Remote Connection - Remote service connection with endpoint and credentials
/// </summary>
public class RemoteConnection : Connection
{
    /// <summary>
    /// Service endpoint URL
    /// </summary>
    [JsonPropertyName("endpoint")]
    public required string Endpoint { get; set; }

    /// <summary>
    /// Authentication credentials (flexible format)
    /// </summary>
    [JsonPropertyName("credentials")]
    public Dictionary<string, object>? Credentials { get; set; }
}

/// <summary>
/// Anonymous Connection - No authentication required
/// </summary>
public class AnonymousConnection : Connection
{
}
