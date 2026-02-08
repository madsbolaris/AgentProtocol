namespace Microsoft.Agents.CodeGen;

/// <summary>
/// Specifies the serialization formats for generated code.
/// Multiple modes can be combined using bitwise OR.
/// </summary>
[Flags]
public enum SerializationMode
{
    /// <summary>
    /// No serialization attributes
    /// </summary>
    None = 0,

    /// <summary>
    /// Generate XML serialization attributes (XmlRoot, XmlElement, etc.)
    /// </summary>
    Xml = 1,

    /// <summary>
    /// Generate JSON serialization attributes (JsonPropertyName, etc.)
    /// </summary>
    Json = 2,

    /// <summary>
    /// Generate both XML and JSON serialization attributes
    /// </summary>
    Both = Xml | Json
}
